from __future__ import annotations

from datetime import datetime

from app.core.i18n import AppLocale, t
from app.schemas.common import FlightSegment, FlightSlice, ItineraryOption, LayoverInfo


class FlightOfferNormalizer:
    def normalize(self, raw_offers: list[dict], locale: AppLocale) -> list[ItineraryOption]:
        normalized: list[ItineraryOption] = []
        for raw_offer in raw_offers:
            slice_groups_raw = raw_offer.get("segments_by_slice")
            if slice_groups_raw:
                slice_segment_models: list[list[FlightSegment]] = [
                    [self._build_segment(segment) for segment in slice_raw] for slice_raw in slice_groups_raw
                ]
            else:
                flat = [self._build_segment(segment) for segment in raw_offer.get("segments", [])]
                slice_segment_models = [flat] if flat else []

            layovers_merged: list[LayoverInfo] = []
            slice_models: list[FlightSlice] = []
            for slice_segs in slice_segment_models:
                slice_layovers = self._build_layovers(slice_segs)
                layovers_merged.extend(slice_layovers)
                slice_models.append(FlightSlice(segments=slice_segs, layovers=slice_layovers))

            all_segments = [segment for slice_segs in slice_segment_models for segment in slice_segs]
            route_summary = self._build_route_summary_slices(slice_segment_models, locale)
            total_duration = sum(self._get_total_duration_minutes(slice_segs) for slice_segs in slice_segment_models)
            stops_count = sum(max(len(slice_segs) - 1, 0) for slice_segs in slice_segment_models)

            normalized.append(
                ItineraryOption(
                    id=raw_offer["id"],
                    provider_offer_id=raw_offer["offer_code"],
                    provider_name=raw_offer["provider_name"],
                    title=self._build_title(raw_offer, locale),
                    total_price=float(raw_offer["total_price"]),
                    currency=raw_offer.get("currency", "USD"),
                    total_duration_minutes=total_duration,
                    stops_count=stops_count,
                    baggage_included=bool(raw_offer.get("baggage_included", False)),
                    flexibility_label=self._build_flexibility_label(raw_offer, locale),
                    route_summary=route_summary,
                    airlines=sorted({segment.airline for segment in all_segments}),
                    segments=all_segments,
                    layovers=layovers_merged,
                    slices=slice_models,
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
            airline_name=raw_segment.get("airline_name"),
            flight_number=raw_segment["flight_number"],
            cabin_class=raw_segment["cabin_class"],
            duration_minutes=int(raw_segment["duration_minutes"]),
        )

    def _build_layovers(self, segments: list[FlightSegment]) -> list[LayoverInfo]:
        layovers: list[LayoverInfo] = []
        for previous, current in zip(segments, segments[1:]):
            previous_arrival = datetime.fromisoformat(previous.arrival_at.replace("Z", "+00:00"))
            current_departure = datetime.fromisoformat(current.departure_at.replace("Z", "+00:00"))
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
        start = datetime.fromisoformat(segments[0].departure_at.replace("Z", "+00:00"))
        end = datetime.fromisoformat(segments[-1].arrival_at.replace("Z", "+00:00"))
        return max(0, int((end - start).total_seconds() // 60))

    def _slice_chain_text(self, segments: list[FlightSegment]) -> str:
        if not segments:
            return ""
        codes = [segments[0].origin]
        codes.extend(segment.destination for segment in segments)
        return " → ".join(codes)

    def _build_route_summary_slices(self, slices: list[list[FlightSegment]], locale: AppLocale) -> str:
        if not slices or not any(slices):
            return t(locale, "normalizer.route_unavailable")
        if len(slices) == 1:
            return self._slice_chain_text(slices[0])
        outbound = self._slice_chain_text(slices[0])
        inbound = self._slice_chain_text(slices[1])
        return t(locale, "normalizer.route_round_trip_summary", outbound=outbound, inbound=inbound)

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
