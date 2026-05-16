from app.schemas.common import FlightSegment
from app.services.normalizer import FlightOfferNormalizer


def test_normalizer_counts_technical_stops_in_stops_count():
    normalizer = FlightOfferNormalizer()
    itineraries = normalizer.normalize(
        [
            {
                "id": "offer_1",
                "offer_code": "offer_1",
                "provider_name": "duffel",
                "title": "Test",
                "total_price": 1000,
                "currency": "USD",
                "baggage_included": True,
                "flexibility_label": "Basic",
                "segments_by_slice": [
                    [
                        {
                            "origin": "MVD",
                            "destination": "NRT",
                            "departure_at": "2026-07-20T17:42:00+00:00",
                            "arrival_at": "2026-07-22T06:58:00+00:00",
                            "airline": "IB",
                            "flight_number": "3167",
                            "cabin_class": "ECONOMY",
                            "duration_minutes": 2236,
                            "technical_stops": [{"airport": "MAD", "duration_minutes": 150}],
                        }
                    ]
                ],
            }
        ],
        "es",
    )

    assert itineraries[0].stops_count == 1
    assert itineraries[0].segments[0].technical_stops[0].airport == "MAD"
