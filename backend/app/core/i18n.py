from __future__ import annotations

from typing import Any, Literal

from fastapi import Header

AppLocale = Literal["es", "en"]

DEFAULT_LOCALE: AppLocale = "es"
SUPPORTED_LOCALES = {"es", "en"}

MESSAGES: dict[AppLocale, dict[str, str]] = {
    "es": {
        "error.internal_server_error": "Algo salió mal en el servidor. Revisá los logs del backend o probá de nuevo más tarde.",
        "error.search_not_found": "Búsqueda no encontrada.",
        "error.providers_unavailable": "No pudimos obtener opciones de vuelos en este momento. Inténtalo de nuevo en unos minutos.",
        "error.providers_live_required":
            "No hay proveedor con vuelos reales configurado. Usá Amadeus producción (api.amadeus.com) o un token Duffel live; el token duffel_test_ no se usa.",
        "error.no_itineraries_found": "No encontramos itinerarios utilizables para esa búsqueda.",
        "strategy.title.savings": "Estrategia ahorro",
        "strategy.title.experience": "Estrategia experiencia",
        "strategy.title.miles": "Estrategia millas",
        "strategy.badge.savings": "Menor costo total con fricción controlada",
        "strategy.badge.experience": "Más valor de viaje sin disparar complejidad",
        "strategy.badge.miles": "Guardar cash y reservar millas para tramos inteligentes",
        "tradeoff.price_premium": "Pagas un premium de USD {delta:.0f} frente a la opción más barata.",
        "tradeoff.multiple_stops": "Tiene más escalas que otras alternativas del set.",
        "tradeoff.no_checked_baggage": "El equipaje despachado no está incluido.",
        "tradeoff.high_risk": "Incluye al menos un factor operativo de riesgo alto.",
        "tradeoff.long_duration": "El tiempo puerta a puerta es elevado respecto al promedio.",
        "tradeoff.balanced_default": "No es la alternativa más extrema, pero mantiene buen equilibrio general.",
        "provider.assumption.active.rule": "Proveedor activo",
        "provider.assumption.active.note": "{provider} devolvió {offer_count} ofertas para esta búsqueda.",
        "provider.assumption.partial_failure.rule": "Falla parcial de proveedor",
        "provider.assumption.partial_failure.note": "Uno de los proveedores configurados no devolvió resultados para esta búsqueda.",
        "provider.assumption.test_inventory.rule": "Inventario de prueba",
        "provider.assumption.test_inventory.note":
            "El backend usa credenciales de sandbox (Duffel test o Amadeus test). Precios e itinerarios pueden ser ficticios y no comparables con Skyscanner ni con la venta real.",
        "risk.synthetic_inventory":
            "Itinerario o precio poco creíble para esta ruta (típico del modo prueba). Usá el enlace externo o conectá proveedor live antes de decidir.",
        "provider.flexibility.total": "Flexible total",
        "provider.flexibility.semi": "Semi flexible",
        "provider.flexibility.partial_refund": "Reembolsable parcial",
        "provider.flexibility.basic": "Básica",
        "normalizer.review_conditions": "Revisar condiciones",
        "normalizer.route_unavailable": "Ruta no disponible",
        "normalizer.route_round_trip_summary": "Ida: {outbound} | Vuelta: {inbound}",
        "provider.duffel.route_fallback": "Ruta Duffel",
        "provider.duffel.option_title": "Opción Duffel {owner_name} {route_label}",
        "provider.duffel.miles_hint.airlines": "Revisar si {airlines} o {owner} ofrece mejor valor de millas en tramos largos.",
        "provider.duffel.miles_hint.owner": "Revisar si {owner} tiene buen canje o acumulación para esta ruta.",
        "provider.amadeus.option_title": "Opción Amadeus {route_label}",
        "provider.amadeus.miles_hint": "Revisar si {airlines} permite mejor valor en tramos largos.",
        "provider.amadeus.flexibility.review": "Revisar reglas tarifarias",
        "provider.demo.title.save_madrid": "Ahorro vía Madrid",
        "provider.demo.title.stopover_lisbon": "Experiencia con stopover en Lisboa",
        "provider.demo.title.miles_istanbul": "Maximizar millas en el tramo largo",
        "provider.demo.title.risk_toronto": "Precio bajo pero con conexión riesgosa",
        "provider.demo.title.comfort_direct": "Comodidad y menor fricción",
        "provider.demo.hint.save_madrid": "Guardar millas para un tramo largo da mejor valor.",
        "provider.demo.hint.stopover_lisbon": "El stopover agrega valor por un delta de costo bajo.",
        "provider.demo.hint.miles_istanbul": "Tiene mejor valor por punto si canjeas solo la cabina premium.",
        "provider.demo.hint.risk_toronto": "Solo conviene si aceptas visa y self-transfer.",
        "provider.demo.hint.comfort_direct": "Conviene si priorizas tiempo total y cambios simples.",
        "risk.self_transfer": "Incluye self-transfer, con riesgo de re-check y pérdida de protección entre boletos.",
        "risk.tight_connection": "La conexión en {airport} es ajustada ({minutes} min).",
        "risk.missing_baggage": "No incluye equipaje despachado aunque el viajero lo necesita.",
        "migration.assumption.us.rule": "Tránsito por EE.UU.",
        "migration.assumption.us.note": "Los tránsitos por EE.UU. suelen requerir autorización de entrada completa.",
        "migration.flag.us_transit_authorization": "La conexión vía EE.UU. puede requerir visa o ESTA incluso en tránsito.",
        "migration.note.us_avoid": "Evitar vía EE.UU. si no tienes visa o ESTA confirmado.",
        "migration.assumption.canada.rule": "Tránsito por Canadá",
        "migration.assumption.canada.note": "Canadá puede requerir eTA o visa según nacionalidad y documentos vigentes.",
        "migration.flag.canada_transit_review": "La conexión vía Canadá requiere revisar eTA o visa antes de emitir.",
        "migration.note.canada_review": "Conexión vía Canadá: validar eTA o visa antes de avanzar.",
        "migration.assumption.uk.rule": "Tránsito por Reino Unido",
        "migration.assumption.uk.note": "El Reino Unido tiene reglas variables por nacionalidad, destino y documentos.",
        "migration.flag.uk_transit_review": "La conexión vía Reino Unido necesita validación de visa de tránsito.",
        "migration.note.uk_review": "Vía Reino Unido: revisar si aplica visa de tránsito airside/landside.",
        "stopover.low_delta": "Agregar {airport} como stopover cuesta solo USD {delta:.0f} más que la opción más barata.",
        "stopover.experience": "{airport} aparece como stopover posible si priorizas experiencia sobre precio.",
        "explainer.summary": "Encontramos {count} estrategias accionables. La mejor recomendación actual es {recommended_title} vía {recommended_route}. La opción más barata cuesta {currency} {cheapest_price:.0f} y la alternativa de experiencia destaca {experience_note}.",
        "explainer.summary.experience_default": "por sumar valor sin disparar complejidad",
        "explainer.headline.savings": "Esta opción prioriza costo total y mantiene la complejidad en un nivel razonable.",
        "explainer.headline.experience": "Esta opción busca sumar valor al viaje sin convertirlo en una operación complicada.",
        "explainer.headline.miles": "Esta opción reserva el mayor valor para tramos donde las millas pueden rendir mejor.",
        "explainer.risk_inline": "Riesgo principal: {risk}.",
        "explainer.risk_none": "No aparece un riesgo operativo dominante en esta opción.",
        "explainer.tradeoff_default": "No domina en todas las variables a la vez.",
        "explainer.body": "{headline} {opportunity} {risk_note} El tradeoff principal es: {tradeoff}",
    },
    "en": {
        "error.internal_server_error": "Something went wrong on the server. Check backend logs or try again later.",
        "error.search_not_found": "Search not found.",
        "error.providers_unavailable": "We couldn't fetch flight options right now. Please try again in a few minutes.",
        "error.providers_live_required":
            "No live flight provider is configured. Use Amadeus production (api.amadeus.com) or a Duffel live token; duffel_test_ tokens are disabled.",
        "error.no_itineraries_found": "We couldn't find usable itineraries for that search.",
        "strategy.title.savings": "Savings strategy",
        "strategy.title.experience": "Experience strategy",
        "strategy.title.miles": "Miles strategy",
        "strategy.badge.savings": "Lowest total cost with controlled friction",
        "strategy.badge.experience": "More travel value without spiking complexity",
        "strategy.badge.miles": "Save cash and reserve miles for smarter long-haul use",
        "tradeoff.price_premium": "You are paying a USD {delta:.0f} premium versus the cheapest option.",
        "tradeoff.multiple_stops": "It has more stops than other alternatives in the set.",
        "tradeoff.no_checked_baggage": "Checked baggage is not included.",
        "tradeoff.high_risk": "It includes at least one high-risk operational factor.",
        "tradeoff.long_duration": "Door-to-door travel time is high versus the average.",
        "tradeoff.balanced_default": "It is not the most extreme option, but it keeps a strong overall balance.",
        "provider.assumption.active.rule": "Provider active",
        "provider.assumption.active.note": "{provider} returned {offer_count} offers for this search.",
        "provider.assumption.partial_failure.rule": "Partial provider failure",
        "provider.assumption.partial_failure.note": "One of the configured providers did not return results for this search.",
        "provider.assumption.test_inventory.rule": "Test inventory",
        "provider.assumption.test_inventory.note":
            "The backend is using sandbox credentials (Duffel test or Amadeus test). Fares and itineraries may be fictional and are not comparable to Skyscanner or real booking.",
        "risk.synthetic_inventory":
            "Itinerary or price is unlikely for this route (common in test mode). Use the external link or connect a live provider before deciding.",
        "provider.flexibility.total": "Fully flexible",
        "provider.flexibility.semi": "Semi flexible",
        "provider.flexibility.partial_refund": "Partially refundable",
        "provider.flexibility.basic": "Basic",
        "normalizer.review_conditions": "Review conditions",
        "normalizer.route_unavailable": "Route unavailable",
        "normalizer.route_round_trip_summary": "Outbound: {outbound} | Return: {inbound}",
        "provider.duffel.route_fallback": "Duffel route",
        "provider.duffel.option_title": "Duffel option {owner_name} {route_label}",
        "provider.duffel.miles_hint.airlines": "Check whether {airlines} or {owner} offers better mileage value on long-haul segments.",
        "provider.duffel.miles_hint.owner": "Check whether {owner} offers strong redemption or accrual value for this route.",
        "provider.amadeus.option_title": "Amadeus option {route_label}",
        "provider.amadeus.miles_hint": "Check whether {airlines} offers better value on long-haul segments.",
        "provider.amadeus.flexibility.review": "Review fare rules",
        "provider.demo.title.save_madrid": "Savings via Madrid",
        "provider.demo.title.stopover_lisbon": "Experience with a Lisbon stopover",
        "provider.demo.title.miles_istanbul": "Maximize miles on the long-haul leg",
        "provider.demo.title.risk_toronto": "Low price with a risky connection",
        "provider.demo.title.comfort_direct": "Comfort and lower friction",
        "provider.demo.hint.save_madrid": "Saving miles for a long-haul segment gives better value.",
        "provider.demo.hint.stopover_lisbon": "The stopover adds value for a low marginal cost.",
        "provider.demo.hint.miles_istanbul": "It delivers better point value if you redeem only the premium cabin.",
        "provider.demo.hint.risk_toronto": "It only makes sense if you accept the visa and self-transfer tradeoff.",
        "provider.demo.hint.comfort_direct": "It works well if you prioritize total travel time and simple changes.",
        "risk.self_transfer": "It includes self-transfer, with re-check risk and loss of ticket protection.",
        "risk.tight_connection": "The connection in {airport} is tight ({minutes} min).",
        "risk.missing_baggage": "Checked baggage is not included even though the traveler needs it.",
        "migration.assumption.us.rule": "US transit",
        "migration.assumption.us.note": "US transits often require full entry authorization.",
        "migration.flag.us_transit_authorization": "A connection via the US may require a visa or ESTA even for transit.",
        "migration.note.us_avoid": "Avoid routing via the US unless you have a confirmed visa or ESTA.",
        "migration.assumption.canada.rule": "Canada transit",
        "migration.assumption.canada.note": "Canada may require an eTA or visa depending on nationality and current documents.",
        "migration.flag.canada_transit_review": "A connection via Canada requires checking eTA or visa requirements before ticketing.",
        "migration.note.canada_review": "Connection via Canada: validate eTA or visa before moving forward.",
        "migration.assumption.uk.rule": "UK transit",
        "migration.assumption.uk.note": "The UK has variable rules depending on nationality, destination, and documents.",
        "migration.flag.uk_transit_review": "A connection via the UK needs transit visa validation.",
        "migration.note.uk_review": "Via the UK: review whether an airside or landside transit visa applies.",
        "stopover.low_delta": "Adding {airport} as a stopover costs only USD {delta:.0f} more than the cheapest option.",
        "stopover.experience": "{airport} appears as a possible stopover if you prioritize experience over price.",
        "explainer.summary": "We found {count} actionable strategies. The current best recommendation is {recommended_title} via {recommended_route}. The cheapest option costs {currency} {cheapest_price:.0f}, and the experience alternative stands out {experience_note}.",
        "explainer.summary.experience_default": "for adding value without increasing complexity too much",
        "explainer.headline.savings": "This option prioritizes total cost while keeping complexity at a reasonable level.",
        "explainer.headline.experience": "This option aims to add value to the trip without turning it into a complicated operation.",
        "explainer.headline.miles": "This option preserves the strongest value for segments where miles can perform better.",
        "explainer.risk_inline": "Main risk: {risk}.",
        "explainer.risk_none": "There is no dominant operational risk in this option.",
        "explainer.tradeoff_default": "It does not dominate every variable at once.",
        "explainer.body": "{headline} {opportunity} {risk_note} The main tradeoff is: {tradeoff}",
    },
}


def normalize_locale(value: str | None) -> AppLocale:
    if not value:
        return DEFAULT_LOCALE

    normalized = value.lower()
    if normalized.startswith("en"):
        return "en"
    if normalized.startswith("es"):
        return "es"
    return DEFAULT_LOCALE


def get_request_locale(
    x_locale: str | None = Header(default=None, alias="X-Locale"),
    accept_language: str | None = Header(default=None, alias="Accept-Language"),
) -> AppLocale:
    return normalize_locale(x_locale or accept_language)


def t(locale: AppLocale, key: str, **params: Any) -> str:
    template = MESSAGES.get(locale, MESSAGES[DEFAULT_LOCALE]).get(key)
    if template is None:
        template = MESSAGES[DEFAULT_LOCALE].get(key, key)
    return template.format(**params)


def message_item(key: str, **params: Any) -> dict[str, Any]:
    return {"key": key, "params": params}


def render_message_item(locale: AppLocale, value: Any, fallback: str | None = None) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        key = value.get("key")
        if key:
            return t(locale, str(key), **(value.get("params") or {}))
    return fallback or ""


def render_message_items(locale: AppLocale, values: list[Any], fallback: list[str] | None = None) -> list[str]:
    rendered = [render_message_item(locale, value).strip() for value in values]
    cleaned = [value for value in rendered if value]
    if cleaned:
        return cleaned
    return fallback or []
