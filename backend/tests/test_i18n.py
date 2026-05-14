from fastapi.testclient import TestClient

from app.core.i18n import normalize_locale
from app.main import app
from app.services.normalizer import FlightOfferNormalizer


def test_normalize_locale_supports_browser_values():
    assert normalize_locale("en-US,en;q=0.9") == "en"
    assert normalize_locale("es-419,es;q=0.8") == "es"
    assert normalize_locale(None) == "es"


def test_search_not_found_is_localized_to_english():
    client = TestClient(app)

    response = client.get("/api/v1/searches/missing-id", headers={"X-Locale": "en"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Search not found."


def test_normalizer_localizes_provider_copy_to_english():
    normalizer = FlightOfferNormalizer()
    itineraries = normalizer.normalize(
        [
            {
                "id": "offer_1",
                "offer_code": "offer_1",
                "provider_name": "duffel",
                "title": "Opcion Duffel Demo MVD-NRT",
                "title_key": "provider.duffel.option_title",
                "title_params": {"owner_name": "Demo Air", "route_label": "MVD-NRT"},
                "total_price": 950,
                "currency": "USD",
                "baggage_included": True,
                "flexibility_label": "Semi flexible",
                "flexibility_code": "semi",
                "segments": [
                    {
                        "origin": "MVD",
                        "destination": "NRT",
                        "departure_at": "2026-06-18T08:10:00+00:00",
                        "arrival_at": "2026-06-18T22:10:00+00:00",
                        "airline": "TP",
                        "flight_number": "117",
                        "cabin_class": "ECONOMY",
                        "duration_minutes": 840,
                    }
                ],
                "cash_miles_hint": "placeholder",
            }
        ],
        "en",
    )

    itinerary = itineraries[0]
    assert itinerary.title == "Duffel option Demo Air MVD-NRT"
    assert itinerary.flexibility_label == "Semi flexible"
