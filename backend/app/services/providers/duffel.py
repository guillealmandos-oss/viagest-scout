from __future__ import annotations

import re
from datetime import datetime

import httpx

from app.schemas.common import SearchRequestInput
from app.services.providers.base import BaseFlightProvider


class DuffelFlightProvider(BaseFlightProvider):
    provider_name = "duffel"

    CABIN_MAP = {
        "ECONOMY": "economy",
        "PREMIUM_ECONOMY": "premium_economy",
        "BUSINESS": "business",
        "FIRST": "first",
    }

    async def search_offers(self, search_input: SearchRequestInput) -> list[dict]:
        self.reset_last_request_metadata()
        if not self.settings.duffel_api_token:
            raise RuntimeError("Duffel token is missing. Set DUFFEL_API_TOKEN to enable live search.")

        request_body = {
            "data": {
                "cabin_class": self.CABIN_MAP.get(search_input.cabin_class, "economy"),
                "max_connections": 1,
                "slices": self._build_slices(search_input),
                "passengers": [{"type": "adult"} for _ in range(search_input.passengers)],
            }
        }

        async with httpx.AsyncClient(base_url=self.settings.duffel_base_url, timeout=self.get_timeout_seconds()) as client:
            response = await client.post(
                "/air/offer_requests?return_offers=true&view=offers",
                headers=self._headers(),
                json=request_body,
            )
            self.capture_response_metadata(response)
            response.raise_for_status()
            payload = response.json()

        offers = payload.get("data", {}).get("offers", [])
        return [self._map_offer(offer) for offer in offers]

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.duffel_api_token}",
            "Duffel-Version": self.settings.duffel_version,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
        }

    def _build_slices(self, search_input: SearchRequestInput) -> list[dict]:
        slices = [
            {
                "origin": search_input.origin,
                "destination": search_input.destination,
                "departure_date": search_input.departure_date.isoformat(),
            }
        ]
        if search_input.return_date:
            slices.append(
                {
                    "origin": search_input.destination,
                    "destination": search_input.origin,
                    "departure_date": search_input.return_date.isoformat(),
                }
            )
        return slices

    def _map_offer(self, offer: dict) -> dict:
        segments: list[dict] = []
        airlines: set[str] = set()

        for slice_payload in offer.get("slices", []):
            for segment in slice_payload.get("segments", []):
                airline_code = (
                    segment.get("operating_carrier", {}).get("iata_code")
                    or segment.get("marketing_carrier", {}).get("iata_code")
                    or offer.get("owner", {}).get("iata_code")
                    or "ZZ"
                )
                airlines.add(airline_code)
                segments.append(
                    {
                        "origin": self._airport_code(segment.get("origin")),
                        "destination": self._airport_code(segment.get("destination")),
                        "departure_at": segment.get("departing_at"),
                        "arrival_at": segment.get("arriving_at"),
                        "airline": airline_code,
                        "flight_number": segment.get("marketing_carrier_flight_number")
                        or segment.get("operating_carrier_flight_number")
                        or segment.get("flight_number")
                        or "N/A",
                        "cabin_class": self._extract_cabin_class(offer),
                        "duration_minutes": self._duration_minutes(segment),
                    }
                )

        route_label = f"{segments[0]['origin']}-{segments[-1]['destination']}" if segments else "Duffel"
        owner_name = offer.get("owner", {}).get("name", "Duffel")

        return {
            "id": offer["id"],
            "offer_code": offer["id"],
            "provider_name": self.provider_name,
            "title": f"Duffel {owner_name} {route_label}",
            "title_key": "provider.duffel.option_title",
            "title_params": {
                "owner_name": owner_name,
                "route_label": route_label,
            },
            "total_price": float(offer.get("total_amount") or 0),
            "currency": offer.get("total_currency") or self.settings.default_currency,
            "baggage_included": self._extract_baggage_flag(offer),
            "flexibility_label": self._build_flexibility_label(offer),
            "flexibility_code": self._build_flexibility_code(offer),
            "self_transfer": False,
            "segments": segments,
            "cash_miles_hint": self._build_miles_hint(sorted(airlines), offer),
            "cash_miles_hint_key": self._build_miles_hint_key(sorted(airlines)),
            "cash_miles_hint_params": self._build_miles_hint_params(sorted(airlines), offer),
        }

    def _airport_code(self, airport_payload: dict | None) -> str:
        if not airport_payload:
            return "N/A"
        return airport_payload.get("iata_code") or airport_payload.get("iata_city_code") or "N/A"

    def _extract_cabin_class(self, offer: dict) -> str:
        cabin = offer.get("cabin_class") or offer.get("passenger_identity_documents_required")
        if isinstance(cabin, str):
            return cabin.upper()
        return "ECONOMY"

    def _extract_baggage_flag(self, offer: dict) -> bool:
        for passenger in offer.get("passengers", []):
            for baggage in passenger.get("baggages", []):
                if baggage.get("type") in {"checked", "checked_bag"}:
                    return True
        services = offer.get("available_services") or []
        return any(service.get("type") == "baggage" for service in services)

    def _build_flexibility_label(self, offer: dict) -> str:
        flexibility_code = self._build_flexibility_code(offer)
        label_map = {
            "total": "Flexible total",
            "semi": "Semi flexible",
            "partial_refund": "Reembolsable parcial",
            "basic": "Basica",
        }
        return label_map[flexibility_code]

    def _build_flexibility_code(self, offer: dict) -> str:
        conditions = offer.get("conditions") or {}
        change_allowed = self._condition_allowed(conditions.get("change_before_departure"))
        refund_allowed = self._condition_allowed(conditions.get("refund_before_departure"))

        if change_allowed and refund_allowed:
            return "total"
        if change_allowed:
            return "semi"
        if refund_allowed:
            return "partial_refund"
        return "basic"

    def _condition_allowed(self, condition: dict | None) -> bool:
        if not condition:
            return False
        return bool(condition.get("allowed") or condition.get("available"))

    def _build_miles_hint(self, airlines: list[str], offer: dict) -> str:
        params = self._build_miles_hint_params(airlines, offer)
        if airlines:
            return f"Revisar si {params['airlines']} o {params['owner']} ofrece mejor valor de millas en tramos largos."
        return f"Revisar si {params['owner']} tiene buen canje o acumulacion para esta ruta."

    def _build_miles_hint_key(self, airlines: list[str]) -> str:
        if airlines:
            return "provider.duffel.miles_hint.airlines"
        return "provider.duffel.miles_hint.owner"

    def _build_miles_hint_params(self, airlines: list[str], offer: dict) -> dict[str, str]:
        owner = offer.get("owner", {}).get("name", "la aerolinea")
        return {
            "airlines": ", ".join(airlines),
            "owner": owner,
        }

    def _duration_minutes(self, segment: dict) -> int:
        if segment.get("duration"):
            parsed = self._parse_iso_duration(segment["duration"])
            if parsed:
                return parsed

        departing_at = segment.get("departing_at")
        arriving_at = segment.get("arriving_at")
        if departing_at and arriving_at:
            start = datetime.fromisoformat(departing_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(arriving_at.replace("Z", "+00:00"))
            return max(0, int((end - start).total_seconds() // 60))
        return 0

    def _parse_iso_duration(self, value: str) -> int:
        matched = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", value)
        if not matched:
            return 0
        hours = int(matched.group(1) or 0)
        minutes = int(matched.group(2) or 0)
        return (hours * 60) + minutes
