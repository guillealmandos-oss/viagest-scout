"""Heurísticas para detectar ofertas sintéticas o invendibles (p. ej. token Duffel test)."""

from __future__ import annotations

from app.core.config import Settings, get_settings
from app.core.flight_providers_config import uses_test_flight_inventory
from app.schemas.common import FlightSlice, ItineraryOption

# Vuelos comerciales no operan más de ~18 h sin escala.
MAX_PLAUSIBLE_NONSTOP_MINUTES = 18 * 60

SOUTH_AMERICA_AIRPORTS = frozenset(
    {"MVD", "EZE", "AEP", "GRU", "CGH", "GIG", "SCL", "LIM", "BOG", "UIO", "ASU", "VVI", "LPB"}
)
EAST_ASIA_AIRPORTS = frozenset({"NRT", "HND", "ICN", "GMP", "PEK", "PKX", "PVG", "SHA", "HKG", "TPE", "KIX", "NGO"})
OCEANIA_AIRPORTS = frozenset({"SYD", "MEL", "BNE", "AKL", "PER"})

# Referencia orientativa MVD ↔ Tokio ida y vuelta (mercado ~USD 2k+ en economy).
LONG_HAUL_RT_PRICE_FLOOR_USD = 1_750.0


def _slice_is_claimed_nonstop(slice_model: FlightSlice) -> bool:
    if len(slice_model.segments) != 1:
        return False
    segment = slice_model.segments[0]
    if slice_model.layovers:
        return False
    if segment.technical_stops:
        return False
    return True


def _slice_door_to_door_minutes(slice_model: FlightSlice) -> int:
    segments = slice_model.segments
    if not segments:
        return 0
    from datetime import datetime

    start = datetime.fromisoformat(segments[0].departure_at.replace("Z", "+00:00"))
    end = datetime.fromisoformat(segments[-1].arrival_at.replace("Z", "+00:00"))
    if start.tzinfo is None or end.tzinfo is None:
        return sum(segment.duration_minutes for segment in segments)
    return max(0, int((end - start).total_seconds() // 60))


def _is_sa_asia_or_oceania_route(origin: str, destination: str) -> bool:
    o = origin.upper()
    d = destination.upper()
    sa_to_far = o in SOUTH_AMERICA_AIRPORTS and (d in EAST_ASIA_AIRPORTS or d in OCEANIA_AIRPORTS)
    far_to_sa = d in SOUTH_AMERICA_AIRPORTS and (o in EAST_ASIA_AIRPORTS or o in OCEANIA_AIRPORTS)
    return sa_to_far or far_to_sa


def itinerary_quality_issues(itinerary: ItineraryOption) -> list[str]:
    issues: list[str] = []
    slices = itinerary.slices or []
    if not slices:
        flat_segments = itinerary.segments
        if flat_segments:
            slices = [FlightSlice(segments=flat_segments, layovers=itinerary.layovers or [])]

    flight_numbers: set[str] = set()
    for slice_model in slices:
        for segment in slice_model.segments:
            if segment.flight_number and segment.flight_number != "N/A":
                flight_numbers.add(segment.flight_number)

        if not slice_model.segments:
            continue

        origin = slice_model.segments[0].origin
        destination = slice_model.segments[-1].destination

        if _slice_is_claimed_nonstop(slice_model):
            minutes = _slice_door_to_door_minutes(slice_model)
            if minutes > MAX_PLAUSIBLE_NONSTOP_MINUTES:
                issues.append("implausible_nonstop_duration")
            if _is_sa_asia_or_oceania_route(origin, destination):
                issues.append("implausible_nonstop_route")

    if len(flight_numbers) == 1 and len(slices) > 1:
        issues.append("duplicate_flight_number_roundtrip")

    if (
        itinerary.stops_count == 0
        and itinerary.total_price < LONG_HAUL_RT_PRICE_FLOOR_USD
        and slices
        and _is_sa_asia_or_oceania_route(slices[0].segments[0].origin, slices[0].segments[-1].destination)
        and len(slices) > 1
    ):
        issues.append("suspicious_low_price")

    return issues


def is_implausible_itinerary(itinerary: ItineraryOption) -> bool:
    return bool(itinerary_quality_issues(itinerary))


def filter_test_inventory(itineraries: list[ItineraryOption]) -> tuple[list[ItineraryOption], int]:
    """Descarta ofertas claramente sintéticas cuando hay alternativas mejores."""
    if not itineraries:
        return itineraries, 0
    plausible = [item for item in itineraries if not is_implausible_itinerary(item)]
    removed = len(itineraries) - len(plausible)
    if plausible:
        return plausible, removed
    return itineraries, 0
