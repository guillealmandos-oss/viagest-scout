from app.core.config import Settings
from app.core.flight_providers_config import (
    resolve_active_flight_provider_names,
    uses_test_flight_inventory,
)


def test_demo_allowed_in_production_when_flag_set():
    settings = Settings(
        app_env="production",
        flight_providers=["demo"],
        allow_demo_provider=True,
        allow_duffel_test=False,
    )
    active, skips = resolve_active_flight_provider_names(settings)
    assert active == ["demo"]
    assert skips == []
    assert uses_test_flight_inventory(settings) is True


def test_demo_blocked_in_production_without_flag():
    settings = Settings(
        app_env="production",
        flight_providers=["demo"],
        allow_demo_provider=False,
        allow_demo_fallback=False,
    )
    active, skips = resolve_active_flight_provider_names(settings)
    assert active == []
    assert skips[0].reason == "demo_not_allowed"


def test_auto_fallback_when_configured_providers_unavailable():
    settings = Settings(
        flight_providers=["duffel"],
        duffel_api_token="duffel_test_abc",
        allow_duffel_test=False,
        allow_demo_fallback=True,
    )
    active, skips = resolve_active_flight_provider_names(settings)
    assert active == ["demo"]
    assert any(skip.reason == "auto_fallback" for skip in skips)
    assert uses_test_flight_inventory(settings) is True
