"""Resuelve qué proveedores de vuelos están activos (solo inventario real por defecto)."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class ProviderSkip:
    provider: str
    reason: str


def duffel_token_is_test(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    token = (settings.duffel_api_token or "").strip().lower()
    return token.startswith("duffel_test_")


def amadeus_uses_test_host(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    return "test.api.amadeus" in (settings.amadeus_base_url or "").lower()


def resolve_active_flight_provider_names(
    settings: Settings | None = None,
) -> tuple[list[str], list[ProviderSkip]]:
    """Devuelve proveedores habilitados y motivos de exclusión (p. ej. token Duffel test)."""
    settings = settings or get_settings()
    configured = settings.flight_providers or [settings.flight_provider]

    ordered_unique: list[str] = []
    for raw_name in configured:
        normalized = raw_name.lower().strip()
        if normalized and normalized not in ordered_unique:
            ordered_unique.append(normalized)

    active: list[str] = []
    skips: list[ProviderSkip] = []
    production = settings.app_env.lower() == "production"

    for name in ordered_unique:
        if name == "demo":
            sandbox_dev = not production and settings.allow_duffel_test
            if settings.allow_demo_provider or sandbox_dev:
                active.append(name)
            else:
                skips.append(ProviderSkip(name, "demo_not_allowed"))
            continue

        if name == "duffel":
            token = (settings.duffel_api_token or "").strip()
            if not token:
                skips.append(ProviderSkip(name, "missing_token"))
                continue
            if duffel_token_is_test(settings) and not settings.allow_duffel_test:
                skips.append(ProviderSkip(name, "test_token_blocked"))
                continue
            active.append(name)
            continue

        if name == "amadeus":
            if not settings.amadeus_api_key or not settings.amadeus_api_secret:
                skips.append(ProviderSkip(name, "missing_credentials"))
                continue
            if amadeus_uses_test_host(settings) and not settings.allow_duffel_test:
                # Mismo flag: ALLOW_DUFFEL_TEST habilita también sandbox Amadeus en dev.
                skips.append(ProviderSkip(name, "test_host_blocked"))
                continue
            active.append(name)
            continue

        skips.append(ProviderSkip(name, "unsupported"))

    return active, skips


def uses_test_flight_inventory(settings: Settings | None = None) -> bool:
    """True si algún proveedor activo usa sandbox (Duffel test o Amadeus test host)."""
    settings = settings or get_settings()
    active, _ = resolve_active_flight_provider_names(settings)
    if "duffel" in active and duffel_token_is_test(settings):
        return True
    if "amadeus" in active and amadeus_uses_test_host(settings):
        return True
    if "demo" in active:
        return True
    return False


def flight_inventory_status(settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    active, skips = resolve_active_flight_provider_names(settings)
    return {
        "active_providers": active,
        "skipped_providers": [{"provider": s.provider, "reason": s.reason} for s in skips],
        "uses_test_inventory": uses_test_flight_inventory(settings),
        "duffel_test_token_blocked": any(s.reason == "test_token_blocked" for s in skips),
        "allow_sandbox": settings.allow_duffel_test,
        "allow_demo_provider": settings.allow_demo_provider,
    }
