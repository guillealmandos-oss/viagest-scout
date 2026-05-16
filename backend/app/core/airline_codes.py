"""Códigos IATA de prueba o genéricos que no deben mostrarse al usuario."""

PLACEHOLDER_AIRLINE_CODES = frozenset({"ZZ", "N/A", "XX", "??"})


def is_placeholder_airline_code(code: str | None) -> bool:
    if not code:
        return True
    return code.strip().upper() in PLACEHOLDER_AIRLINE_CODES


def filter_airline_codes(codes: list[str] | set[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in codes:
        code = str(raw).strip().upper()
        if is_placeholder_airline_code(code) or code in seen:
            continue
        seen.add(code)
        out.append(code)
    return sorted(out)
