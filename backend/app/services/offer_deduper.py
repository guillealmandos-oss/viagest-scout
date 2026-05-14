from __future__ import annotations

from app.schemas.common import ItineraryOption


class OfferDeduper:
    def dedupe(
        self,
        itineraries: list[ItineraryOption],
        *,
        provider_priority: list[str],
    ) -> list[ItineraryOption]:
        if len(itineraries) <= 1:
            return itineraries

        priority_index = {name: index for index, name in enumerate(provider_priority)}
        grouped: dict[tuple, ItineraryOption] = {}

        for itinerary in itineraries:
            signature = self._signature(itinerary)
            current = grouped.get(signature)
            if current is None or self._is_better_candidate(itinerary, current, priority_index):
                grouped[signature] = itinerary

        return sorted(grouped.values(), key=lambda item: (item.total_price, item.total_duration_minutes))

    def _signature(self, itinerary: ItineraryOption) -> tuple:
        first_segment = itinerary.segments[0] if itinerary.segments else None
        last_segment = itinerary.segments[-1] if itinerary.segments else None
        airline_signature = tuple(sorted(itinerary.airlines))
        return (
            itinerary.route_summary,
            itinerary.stops_count,
            round(itinerary.total_duration_minutes / 30),
            first_segment.departure_at if first_segment else "",
            last_segment.arrival_at if last_segment else "",
            airline_signature,
        )

    def _is_better_candidate(
        self,
        candidate: ItineraryOption,
        current: ItineraryOption,
        priority_index: dict[str, int],
    ) -> bool:
        if candidate.total_price != current.total_price:
            return candidate.total_price < current.total_price
        if candidate.total_duration_minutes != current.total_duration_minutes:
            return candidate.total_duration_minutes < current.total_duration_minutes
        return priority_index.get(candidate.provider_name, 999) < priority_index.get(current.provider_name, 999)
