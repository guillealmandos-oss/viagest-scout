from __future__ import annotations

from typing import Any

from app.core.i18n import AppLocale, message_item, render_message_item


def provider_error_item(provider_name: str, source: BaseException | str | None) -> dict[str, Any] | None:
    if source is None:
        return None

    raw = str(source).strip()
    if not raw:
        return None

    lowered = raw.lower()
    provider = provider_name.lower()

    if "token is missing" in lowered or "credentials are missing" in lowered:
        if provider == "duffel":
            return message_item("provider.error.duffel.missing_token")
        if provider == "amadeus":
            return message_item("provider.error.amadeus.missing_credentials")
        return message_item("provider.error.missing_credentials", provider=provider_name)

    if "401" in lowered or "unauthorized" in lowered:
        if provider == "duffel":
            return message_item("provider.error.duffel.unauthorized")
        return message_item("provider.error.unauthorized", provider=provider_name)

    if "403" in lowered or "forbidden" in lowered:
        return message_item("provider.error.forbidden", provider=provider_name)

    if "timeout" in lowered or "timed out" in lowered:
        return message_item("provider.error.timeout", provider=provider_name)

    if "429" in lowered or "rate limit" in lowered:
        return message_item("provider.error.rate_limited", provider=provider_name)

    if "connection" in lowered or "network" in lowered:
        return message_item("provider.error.network", provider=provider_name)

    return message_item("provider.error.generic", provider=provider_name)


def explain_provider_error(
    locale: AppLocale,
    provider_name: str,
    source: BaseException | str | dict[str, Any] | None,
) -> str | None:
    if isinstance(source, dict):
        item = source
    else:
        item = provider_error_item(provider_name, source)

    if not item:
        return None

    fallback = str(source) if source is not None and not isinstance(source, dict) else None
    return render_message_item(locale, item, fallback=fallback)
