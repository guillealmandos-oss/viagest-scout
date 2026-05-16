const PLACEHOLDER_AIRLINE_CODES = new Set(["ZZ", "N/A", "XX", "??"]);

/** Etiqueta para UI: nombre comercial + código IATA cuando el backend lo envía. */
export function formatAirlineWithCode(segment: {
  airline: string;
  airline_name?: string | null;
}): string {
  const code = segment.airline?.trim().toUpperCase() || "";
  const rawName = segment.airline_name?.trim();
  const codeIsPlaceholder = !code || PLACEHOLDER_AIRLINE_CODES.has(code);

  if (rawName && codeIsPlaceholder) {
    return rawName;
  }
  if (rawName && rawName.toUpperCase() !== code) {
    return `${rawName} (${code})`;
  }
  return code || segment.airline;
}
