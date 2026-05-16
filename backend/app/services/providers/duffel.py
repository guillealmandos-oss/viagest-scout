from __future__ import annotations

import re
from datetime import datetime

import httpx

from app.core.airline_codes import filter_airline_codes, is_placeholder_airline_code
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
                "max_connections": 2,
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
        segments_by_slice: list[list[dict]] = []
        segments: list[dict] = []
        airlines: set[str] = set()

        for slice_payload in offer.get("slices", []):
            slice_segments: list[dict] = []
            for segment in slice_payload.get("segments", []):
                marketing = segment.get("marketing_carrier") or {}
                operating = segment.get("operating_carrier") or {}
                owner_carrier = offer.get("owner") or {}
                airline_code = (
                    marketing.get("iata_code")
                    or operating.get("iata_code")
                    or owner_carrier.get("iata_code")
                    or "ZZ"
                )
                if is_placeholder_airline_code(airline_code):
                    airline_code = owner_carrier.get("iata_code") or airline_code
                airline_name_raw = (
                    marketing.get("name") or operating.get("name") or owner_carrier.get("name") or ""
                ).strip()
                airline_name = airline_name_raw or None
                if not is_placeholder_airline_code(airline_code):
                    airlines.add(airline_code)
                mapped = {
                    "origin": self._airport_code(segment.get("origin")),
                    "destination": self._airport_code(segment.get("destination")),
                    "departure_at": segment.get("departing_at"),
                    "arrival_at": segment.get("arriving_at"),
                    "airline": airline_code,
                    "airline_name": airline_name,
                    "flight_number": segment.get("marketing_carrier_flight_number")
                    or segment.get("operating_carrier_flight_number")
                    or segment.get("flight_number")
                    or "N/A",
                    "cabin_class": self._extract_cabin_class(offer),
                    "duration_minutes": self._duration_minutes(segment),
                }
                slice_segments.append(mapped)
                segments.append(mapped)
            segments_by_slice.append(slice_segments)

        route_label = "Duffel"
        if segments_by_slice and segments_by_slice[0]:
            first_slice = segments_by_slice[0]
            route_label = f"{first_slice[0]['origin']}-{first_slice[-1]['destination']}"
            if len(segments_by_slice) > 1 and segments_by_slice[1]:
                rt = segments_by_slice[1]
                route_label = f"{route_label}_{rt[0]['origin']}-{rt[-1]['destination']}"
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
            "segments_by_slice": segments_by_slice,
            "segments": segments,
            "cash_miles_hint": self._build_miles_hint(filter_airline_codes(airlines), offer),
            "cash_miles_hint_key": self._build_miles_hint_key(filter_airline_codes(airlines)),
            "cash_miles_hint_params": self._build_miles_hint_params(filter_airline_codes(airlines), offer),
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
        owner = offer.get("owner", {}).get("name", "la aerolínea")
        if airlines:
            return {
                "airlines": ", ".join(airlines),
                "owner": owner,
            }
        return {"owner": owner}

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
