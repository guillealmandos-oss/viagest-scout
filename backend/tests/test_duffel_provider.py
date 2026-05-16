from datetime import date

import httpx
import pytest

from app.core.config import get_settings
from app.schemas.common import SearchRequestInput
from app.services.providers.duffel import DuffelFlightProvider
from app.services.providers.factory import get_flight_provider, get_flight_providers


def sample_duffel_offer() -> dict:
    return {
        "id": "off_123",
        "total_amount": "954.20",
        "total_currency": "USD",
        "cabin_class": "economy",
        "owner": {"name": "Duffel Airways", "iata_code": "ZZ"},
        "conditions": {
            "change_before_departure": {"allowed": True},
            "refund_before_departure": {"allowed": False},
        },
        "slices": [
            {
                "segments": [
                    {
                        "origin": {"iata_code": "MVD"},
                        "destination": {"iata_code": "LIS"},
                        "departing_at": "2026-06-18T08:10:00+00:00",
                        "arriving_at": "2026-06-18T17:10:00+00:00",
                        "marketing_carrier": {"iata_code": "TP"},
                        "operating_carrier": {"iata_code": "TP"},
                        "marketing_carrier_flight_number": "117",
                        "duration": "PT9H00M",
                    },
                    {
                        "origin": {"iata_code": "LIS"},
                        "destination": {"iata_code": "NRT"},
                        "departing_at": "2026-06-19T12:10:00+00:00",
                        "arriving_at": "2026-06-20T02:20:00+00:00",
                        "marketing_carrier": {"iata_code": "TP"},
                        "operating_carrier": {"iata_code": "TP"},
                        "marketing_carrier_flight_number": "321",
                        "duration": "PT14H10M",
                    },
                ]
            }
        ],
    }


def test_duffel_provider_requires_token(monkeypatch):
    monkeypatch.setenv("DUFFEL_API_TOKEN", "")
    get_settings.cache_clear()
    provider = DuffelFlightProvider()
    search = SearchRequestInput(
        origin="MVD",
        destination="NRT",
        departure_date=date(2026, 6, 18),
        passengers=1,
        cabin_class="ECONOMY",
    )

    with pytest.raises(RuntimeError):
        import asyncio

        asyncio.run(provider.search_offers(search))


def test_duffel_provider_expands_technical_stops_into_legs():
    offer = sample_duffel_offer()
    offer["slices"][0]["segments"] = [
        {
            "origin": {"iata_code": "MVD"},
            "destination": {"iata_code": "NRT"},
            "departing_at": "2026-07-20T17:42:00+00:00",
            "arriving_at": "2026-07-22T06:58:00+00:00",
            "marketing_carrier": {"iata_code": "IB", "name": "Iberia"},
            "operating_carrier": {"iata_code": "IB", "name": "Iberia"},
            "marketing_carrier_flight_number": "3167",
            "duration": "PT37H16M",
            "stops": [
                {
                    "airport": {"iata_code": "MAD"},
                    "arriving_at": "2026-07-21T08:00:00+00:00",
                    "departing_at": "2026-07-21T10:30:00+00:00",
                    "duration": "PT2H30M",
                }
            ],
        }
    ]

    mapped = DuffelFlightProvider()._map_offer(offer)
    legs = mapped["segments_by_slice"][0]

    assert len(legs) == 2
    assert legs[0]["origin"] == "MVD"
    assert legs[0]["destination"] == "MAD"
    assert legs[1]["origin"] == "MAD"
    assert legs[1]["destination"] == "NRT"
    assert legs[0]["flight_number"] == "3167"
    assert legs[1]["flight_number"] == "3167"


def test_duffel_provider_maps_offer_to_internal_shape():
    provider = DuffelFlightProvider()

    mapped = provider._map_offer(sample_duffel_offer())

    assert mapped["provider_name"] == "duffel"
    assert mapped["offer_code"] == "off_123"
    assert mapped["total_price"] == 954.20
    assert mapped["currency"] == "USD"
    assert mapped["flexibility_label"] == "Semi flexible"
    assert mapped["title_key"] == "provider.duffel.option_title"
    assert mapped["flexibility_code"] == "semi"
    assert len(mapped["segments"]) == 2
    assert mapped["segments"][0]["origin"] == "MVD"
    assert mapped["segments"][1]["destination"] == "NRT"
    assert len(mapped["segments_by_slice"]) == 1
    assert len(mapped["segments_by_slice"][0]) == 2


def test_factory_returns_duffel_provider_when_selected(monkeypatch):
    monkeypatch.setenv("FLIGHT_PROVIDER", "duffel")
    monkeypatch.delenv("FLIGHT_PROVIDERS", raising=False)
    monkeypatch.setenv("DUFFEL_API_TOKEN", "duffel_test_123")
    get_settings.cache_clear()

    provider = get_flight_provider()

    assert isinstance(provider, DuffelFlightProvider)


def test_factory_returns_multiple_providers_from_configured_list(monkeypatch):
    monkeypatch.setenv("FLIGHT_PROVIDER", "duffel")
    monkeypatch.setenv("FLIGHT_PROVIDERS", "duffel,amadeus,duffel")
    monkeypatch.setenv("DUFFEL_API_TOKEN", "duffel_test_123")
    get_settings.cache_clear()

    providers = get_flight_providers()

    assert [provider.provider_name for provider in providers] == ["duffel", "amadeus"]


def test_provider_timeout_config_is_parsed_from_env(monkeypatch):
    monkeypatch.setenv("PROVIDER_TIMEOUTS", "duffel:45,amadeus:18")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.provider_timeouts == {"duffel": 45.0, "amadeus": 18.0}


def test_duffel_provider_uses_timeout_from_settings(monkeypatch):
    monkeypatch.setenv("PROVIDER_TIMEOUTS", "duffel:41")
    monkeypatch.setenv("DUFFEL_API_TOKEN", "duffel_test_123")
    get_settings.cache_clear()

    provider = DuffelFlightProvider()

    assert provider.get_timeout_seconds() == 41.0


def test_duffel_provider_captures_external_request_ids():
    provider = DuffelFlightProvider()
    response = httpx.Response(
        200,
        headers={
            "x-request-id": "req_123",
            "x-client-correlation-id": "corr_456",
        },
    )

    provider.capture_response_metadata(response)

    assert provider.get_last_request_metadata() == {
        "external_request_id": "req_123",
        "external_correlation_id": "corr_456",
    }
