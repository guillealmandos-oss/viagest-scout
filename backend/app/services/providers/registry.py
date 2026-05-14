from app.services.providers.amadeus import AmadeusFlightProvider
from app.services.providers.base import BaseFlightProvider
from app.services.providers.demo import DemoFlightProvider
from app.services.providers.duffel import DuffelFlightProvider


PROVIDER_BUILDERS: dict[str, type[BaseFlightProvider]] = {
    "duffel": DuffelFlightProvider,
    "amadeus": AmadeusFlightProvider,
    "demo": DemoFlightProvider,
}


def build_provider(provider_name: str) -> BaseFlightProvider:
    normalized_name = provider_name.lower().strip()
    try:
        return PROVIDER_BUILDERS[normalized_name]()
    except KeyError as exc:
        supported = ", ".join(sorted(PROVIDER_BUILDERS))
        raise ValueError(
            f"Unsupported flight provider '{provider_name}'. Use one of: {supported}."
        ) from exc
