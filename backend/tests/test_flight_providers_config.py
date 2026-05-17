from app.core.config import Settings
from app.core.flight_providers_config import resolve_active_flight_provider_names


def test_blocks_duffel_test_token_by_default():
    settings = Settings(
        flight_providers=["duffel"],
        duffel_api_token="duffel_test_abc",
        allow_duffel_test=False,
        allow_demo_fallback=False,
    )
    active, skips = resolve_active_flight_provider_names(settings)
    assert active == []
    assert skips[0].reason == "test_token_blocked"


def test_allows_amadeus_production():
    settings = Settings(
        flight_providers=["amadeus"],
        amadeus_api_key="key",
        amadeus_api_secret="secret",
        amadeus_base_url="https://api.amadeus.com",
        allow_duffel_test=False,
    )
    active, skips = resolve_active_flight_provider_names(settings)
    assert active == ["amadeus"]
    assert skips == []


def test_blocks_amadeus_test_host_when_sandbox_disallowed():
    settings = Settings(
        flight_providers=["amadeus"],
        amadeus_api_key="key",
        amadeus_api_secret="secret",
        amadeus_base_url="https://test.api.amadeus.com",
        allow_duffel_test=False,
        allow_demo_fallback=False,
    )
    active, skips = resolve_active_flight_provider_names(settings)
    assert active == []
    assert skips[0].reason == "test_host_blocked"
