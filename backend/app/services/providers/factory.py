from app.core.config import get_settings
from app.services.providers.base import BaseFlightProvider
from app.services.providers.registry import build_provider


def get_flight_provider(provider_name: str | None = None) -> BaseFlightProvider:
    settings = get_settings()
    return build_provider(provider_name or settings.flight_provider)


def get_flight_providers() -> list[BaseFlightProvider]:
    settings = get_settings()
    configured_names = settings.flight_providers or [settings.flight_provider]
    ordered_unique_names: list[str] = []
    for provider_name in configured_names:
        normalized_name = provider_name.lower().strip()
        if normalized_name and normalized_name not in ordered_unique_names:
            ordered_unique_names.append(normalized_name)
    return [build_provider(provider_name) for provider_name in ordered_unique_names]
