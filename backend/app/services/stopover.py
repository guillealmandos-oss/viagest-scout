from app.core.i18n import message_item
from app.schemas.common import ItineraryOption


class StopoverAdvisor:
    def annotate(self, itinerary: ItineraryOption, cheapest_price: float) -> list[dict]:
        notes: list[dict] = []
        delta = itinerary.total_price - cheapest_price
        for layover in itinerary.layovers:
            if not layover.stopover_candidate:
                continue
            if delta <= 120:
                notes.append(message_item("stopover.low_delta", airport=layover.airport, delta=max(delta, 0)))
            else:
                notes.append(message_item("stopover.experience", airport=layover.airport))
        return notes
