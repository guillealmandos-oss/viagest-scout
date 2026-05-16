from app.core.config import get_settings
from app.core.flight_providers_config import resolve_active_flight_provider_names
from app.services.providers.base import BaseFlightProvider
from app.services.providers.registry import build_provider


def get_flight_provider(provider_name: str | None = None) -> BaseFlightProvider:
    settings = get_settings()
    if provider_name:
        return build_provider(provider_name)
    active_names, _ = resolve_active_flight_provider_names(settings)
    resolved_name = active_names[0] if active_names else settings.flight_provider
    return build_provider(resolved_name)


def get_flight_providers() -> list[BaseFlightProvider]:
    active_names, _ = resolve_active_flight_provider_names()
    return [build_provider(provider_name) for provider_name in active_names]
