from __future__ import annotations

from datetime import datetime

from app.core.i18n import AppLocale, t
from app.schemas.common import FlightSegment, ItineraryOption, LayoverInfo


class FlightOfferNormalizer:
    def normalize(self, raw_offers: list[dict], locale: AppLocale) -> list[ItineraryOption]:
        normalized: list[ItineraryOption] = []
        for raw_offer in raw_offers:
            segments = [self._build_segment(segment) for segment in raw_offer.get("segments", [])]
            layovers = self._build_layovers(segments)
            route_summary = self._build_route_summary(segments, locale)
            normalized.append(
                ItineraryOption(
                    id=raw_offer["id"],
                    provider_offer_id=raw_offer["offer_code"],
                    provider_name=raw_offer["provider_name"],
                    title=self._build_title(raw_offer, locale),
                    total_price=float(raw_offer["total_price"]),
                    currency=raw_offer.get("currency", "USD"),
                    total_duration_minutes=self._get_total_duration_minutes(segments),
                    stops_count=max(len(layovers), 0),
                    baggage_included=bool(raw_offer.get("baggage_included", False)),
                    flexibility_label=self._build_flexibility_label(raw_offer, locale),
                    route_summary=route_summary,
                    airlines=sorted({segment.airline for segment in segments}),
                    segments=segments,
                    layovers=layovers,
                    raw_payload=raw_offer,
                )
            )
        return normalized

    def _build_segment(self, raw_segment: dict) -> FlightSegment:
        return FlightSegment(
            origin=raw_segment["origin"],
            destination=raw_segment["destination"],
            departure_at=raw_segment["departure_at"],
            arrival_at=raw_segment["arrival_at"],
            airline=raw_segment["airline"],
            flight_number=raw_segment["flight_number"],
            cabin_class=raw_segment["cabin_class"],
            duration_minutes=int(raw_segment["duration_minutes"]),
        )

    def _build_layovers(self, segments: list[FlightSegment]) -> list[LayoverInfo]:
        layovers: list[LayoverInfo] = []
        for previous, current in zip(segments, segments[1:]):
            previous_arrival = datetime.fromisoformat(previous.arrival_at)
            current_departure = datetime.fromisoformat(current.departure_at)
            duration_minutes = int((current_departure - previous_arrival).total_seconds() // 60)
            layovers.append(
                LayoverInfo(
                    airport=previous.destination,
                    duration_minutes=max(duration_minutes, 0),
                    stopover_candidate=18 * 60 <= duration_minutes <= 120 * 60,
                )
            )
        return layovers

    def _get_total_duration_minutes(self, segments: list[FlightSegment]) -> int:
        if not segments:
            return 0
        start = datetime.fromisoformat(segments[0].departure_at)
        end = datetime.fromisoformat(segments[-1].arrival_at)
        return int((end - start).total_seconds() // 60)

    def _build_route_summary(self, segments: list[FlightSegment], locale: AppLocale) -> str:
        if not segments:
            return t(locale, "normalizer.route_unavailable")
        codes = [segments[0].origin]
        codes.extend(segment.destination for segment in segments)
        return " -> ".join(codes)

    def _build_title(self, raw_offer: dict, locale: AppLocale) -> str:
        title_key = raw_offer.get("title_key")
        title_params = raw_offer.get("title_params", {})
        if title_key:
            return t(locale, title_key, **title_params)
        return raw_offer["title"]

    def _build_flexibility_label(self, raw_offer: dict, locale: AppLocale) -> str:
        flexibility_code = raw_offer.get("flexibility_code")
        if flexibility_code:
            return t(locale, f"provider.flexibility.{flexibility_code}")
        flexibility_key = raw_offer.get("flexibility_label_key")
        if flexibility_key:
            return t(locale, flexibility_key, **raw_offer.get("flexibility_label_params", {}))
        return raw_offer.get("flexibility_label", t(locale, "normalizer.review_conditions"))
