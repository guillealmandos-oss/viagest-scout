from app.schemas.common import FlightSegment, FlightSlice, ItineraryOption
from app.services.offer_quality import is_implausible_itinerary


def _itinerary(**kwargs) -> ItineraryOption:
  defaults = {
      "id": "1",
      "provider_offer_id": "1",
      "provider_name": "duffel",
      "title": "Test",
      "total_price": 1300,
      "currency": "USD",
      "total_duration_minutes": 3000,
      "stops_count": 0,
      "baggage_included": False,
      "flexibility_label": "Basic",
      "route_summary": "MVD-NRT",
      "airlines": ["AA"],
      "segments": [],
      "layovers": [],
      "raw_payload": {},
  }
  defaults.update(kwargs)
  return ItineraryOption(**defaults)


def test_mvd_hnd_fake_direct_is_implausible():
    outbound = FlightSlice(
        segments=[
            FlightSegment(
                origin="MVD",
                destination="HND",
                departure_at="2026-06-01T03:00:00+00:00",
                arrival_at="2026-06-03T06:58:00+00:00",
                airline="AA",
                flight_number="10",
                cabin_class="ECONOMY",
                duration_minutes=37 * 60,
            )
        ],
        layovers=[],
    )
    inbound = FlightSlice(
        segments=[
            FlightSegment(
                origin="HND",
                destination="MVD",
                departure_at="2026-07-01T01:27:00+00:00",
                arrival_at="2026-07-01T14:48:00+00:00",
                airline="AA",
                flight_number="10",
                cabin_class="ECONOMY",
                duration_minutes=13 * 60,
            )
        ],
        layovers=[],
    )
    itinerary = _itinerary(slices=[outbound, inbound])

    assert is_implausible_itinerary(itinerary)
