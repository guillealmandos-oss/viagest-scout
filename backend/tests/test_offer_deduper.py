from app.schemas.common import FlightSegment, ItineraryOption
from app.services.offer_deduper import OfferDeduper


def build_itinerary(*, itinerary_id: str, provider_name: str, total_price: float) -> ItineraryOption:
    return ItineraryOption(
        id=itinerary_id,
        provider_offer_id=itinerary_id,
        provider_name=provider_name,
        title=f"Offer {itinerary_id}",
        total_price=total_price,
        currency="USD",
        total_duration_minutes=900,
        stops_count=1,
        baggage_included=True,
        flexibility_label="Semi flexible",
        route_summary="MVD -> MAD -> NRT",
        airlines=["IB"],
        segments=[
            FlightSegment(
                origin="MVD",
                destination="MAD",
                departure_at="2026-06-18T08:00:00+00:00",
                arrival_at="2026-06-18T20:00:00+00:00",
                airline="IB",
                flight_number="6040",
                cabin_class="ECONOMY",
                duration_minutes=720,
            ),
            FlightSegment(
                origin="MAD",
                destination="NRT",
                departure_at="2026-06-18T22:00:00+00:00",
                arrival_at="2026-06-19T11:00:00+00:00",
                airline="IB",
                flight_number="6217",
                cabin_class="ECONOMY",
                duration_minutes=780,
            ),
        ],
        layovers=[],
        raw_payload={"provider_name": provider_name},
    )


def test_offer_deduper_keeps_cheapest_duplicate():
    itineraries = [
        build_itinerary(itinerary_id="duffel-1", provider_name="duffel", total_price=980),
        build_itinerary(itinerary_id="amadeus-1", provider_name="amadeus", total_price=940),
    ]

    deduped = OfferDeduper().dedupe(itineraries, provider_priority=["duffel", "amadeus"])

    assert len(deduped) == 1
    assert deduped[0].id == "amadeus-1"


def test_offer_deduper_uses_provider_priority_when_price_matches():
    itineraries = [
        build_itinerary(itinerary_id="duffel-1", provider_name="duffel", total_price=980),
        build_itinerary(itinerary_id="amadeus-1", provider_name="amadeus", total_price=980),
    ]

    deduped = OfferDeduper().dedupe(itineraries, provider_priority=["duffel", "amadeus"])

    assert len(deduped) == 1
    assert deduped[0].id == "duffel-1"
