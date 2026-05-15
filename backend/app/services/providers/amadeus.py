from __future__ import annotations

import re
from datetime import datetime

import httpx

from app.schemas.common import SearchRequestInput
from app.services.providers.base import BaseFlightProvider


class AmadeusFlightProvider(BaseFlightProvider):
    provider_name = "amadeus"

    async def search_offers(self, search_input: SearchRequestInput) -> list[dict]:
        self.reset_last_request_metadata()
        if not self.settings.amadeus_api_key or not self.settings.amadeus_api_secret:
            raise RuntimeError("Amadeus credentials are missing. Set AMADEUS_API_KEY and AMADEUS_API_SECRET.")

        async with httpx.AsyncClient(
            base_url=self.settings.amadeus_base_url,
            timeout=self.get_timeout_seconds(),
        ) as client:
            token = await self._get_access_token(client)
            response = await client.get(
                "/v2/shopping/flight-offers",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "originLocationCode": search_input.origin,
                    "destinationLocationCode": search_input.destination,
                    "departureDate": search_input.departure_date.isoformat(),
                    "returnDate": search_input.return_date.isoformat() if search_input.return_date else None,
                    "adults": search_input.passengers,
                    "travelClass": search_input.cabin_class,
                    "currencyCode": self.settings.default_currency,
                    "max": 12,
                },
            )
            self.capture_response_metadata(response)
            response.raise_for_status()
            payload = response.json()
        return [self._map_offer(offer) for offer in payload.get("data", [])]

    async def _get_access_token(self, client: httpx.AsyncClient) -> str:
        response = await client.post(
            "/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.settings.amadeus_api_key,
                "client_secret": self.settings.amadeus_api_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.capture_response_metadata(response)
        response.raise_for_status()
        return response.json()["access_token"]

    def _map_offer(self, offer: dict) -> dict:
        segments_by_slice: list[list[dict]] = []
        segments: list[dict] = []
        for itinerary in offer.get("itineraries", []):
            slice_segments: list[dict] = []
            for segment in itinerary.get("segments", []):
                mapped = {
                    "origin": segment["departure"]["iataCode"],
                    "destination": segment["arrival"]["iataCode"],
                    "departure_at": segment["departure"]["at"],
                    "arrival_at": segment["arrival"]["at"],
                    "airline": segment["carrierCode"],
                    "flight_number": segment["number"],
                    "cabin_class": self._extract_cabin_class(offer, segment["id"]),
                    "duration_minutes": self._parse_iso_duration(segment["duration"]),
                }
                slice_segments.append(mapped)
                segments.append(mapped)
            segments_by_slice.append(slice_segments)

        baggage_included = self._extract_baggage_flag(offer)
        airline_codes = sorted({segment["airline"] for segment in segments})
        first_origin = segments[0]["origin"] if segments else "N/A"
        last_destination = segments[-1]["destination"] if segments else "N/A"

        return {
            "id": offer["id"],
            "offer_code": offer["id"],
            "provider_name": self.provider_name,
            "title": f"Amadeus {first_origin}-{last_destination}",
            "title_key": "provider.amadeus.option_title",
            "title_params": {"route_label": f"{first_origin}-{last_destination}"},
            "total_price": float(offer["price"]["grandTotal"]),
            "currency": offer["price"]["currency"],
            "baggage_included": baggage_included,
            "flexibility_label": "Revisar reglas tarifarias",
            "flexibility_label_key": "provider.amadeus.flexibility.review",
            "self_transfer": False,
            "segments_by_slice": segments_by_slice,
            "segments": segments,
            "cash_miles_hint": f"Revisar si {', '.join(airline_codes)} permite mejor valor en tramos largos.",
            "cash_miles_hint_key": "provider.amadeus.miles_hint",
            "cash_miles_hint_params": {"airlines": ", ".join(airline_codes)},
        }

    def _extract_cabin_class(self, offer: dict, segment_id: str) -> str:
        for pricing in offer.get("travelerPricings", []):
            for fare_detail in pricing.get("fareDetailsBySegment", []):
                if fare_detail.get("segmentId") == segment_id:
                    return fare_detail.get("cabin", "ECONOMY")
        return "ECONOMY"

    def _extract_baggage_flag(self, offer: dict) -> bool:
        for pricing in offer.get("travelerPricings", []):
            for fare_detail in pricing.get("fareDetailsBySegment", []):
                included = fare_detail.get("includedCheckedBags", {})
                if included.get("quantity", 0) > 0 or included.get("weight", 0) > 0:
                    return True
        return False

    def _parse_iso_duration(self, value: str) -> int:
        matched = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", value)
        if not matched:
            return 0
        hours = int(matched.group(1) or 0)
        minutes = int(matched.group(2) or 0)
        return (hours * 60) + minutes
