import type { AppLocale } from "@/i18n/config";
import type { Itinerary } from "@/types/travel";

export interface TripSearchParams {
  origin: string;
  destination: string;
  departDate: string;
  returnDate?: string;
}

function isoDateOnly(iso: string): string | null {
  if (!iso || iso.length < 10) {
    return null;
  }
  const prefix = iso.slice(0, 10);
  if (/^\d{4}-\d{2}-\d{2}$/.test(prefix)) {
    return prefix;
  }
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) {
    return null;
  }
  return d.toISOString().slice(0, 10);
}

/** Origen/destino de la ida y fechas a partir del itinerario normalizado (incluye slices ida/vuelta). */
export function tripSearchParamsFromItinerary(itinerary: Itinerary): TripSearchParams | null {
  const slices =
    itinerary.slices && itinerary.slices.length > 0
      ? itinerary.slices
      : [{ segments: itinerary.segments, layovers: itinerary.layovers ?? [] }];

  const outbound = slices[0]?.segments;
  if (!outbound?.length) {
    return null;
  }

  const origin = outbound[0].origin?.trim().toUpperCase();
  const destination = outbound[outbound.length - 1].destination?.trim().toUpperCase();
  const departDate = isoDateOnly(outbound[0].departure_at);

  if (!origin || !destination || !departDate || origin === "N/A" || destination === "N/A") {
    return null;
  }

  let returnDate: string | undefined;
  if (slices.length > 1) {
    const inbound = slices[1]?.segments;
    const rd = inbound?.length ? isoDateOnly(inbound[0].departure_at) : null;
    if (rd) {
      returnDate = rd;
    }
  }

  return { origin, destination, departDate, returnDate };
}

/**
 * Búsqueda en Google Travel Flights vía parámetro `q` (no garantiza coincidencia con la tarifa del proveedor).
 * @see https://www.google.com/travel/flights
 */
export function googleFlightsSearchUrl(params: TripSearchParams, locale: AppLocale): string {
  const hl = locale === "es" ? "es" : "en-US";
  let q: string;
  if (locale === "es") {
    q = params.returnDate
      ? `Vuelos de ida y vuelta de ${params.origin} a ${params.destination}, salida ${params.departDate}, regreso ${params.returnDate}`
      : `Vuelos de ${params.origin} a ${params.destination} el ${params.departDate}`;
  } else {
    q = params.returnDate
      ? `Round-trip flights from ${params.origin} to ${params.destination} departing ${params.departDate} returning ${params.returnDate}`
      : `Flights from ${params.origin} to ${params.destination} on ${params.departDate}`;
  }

  const search = new URLSearchParams({ q, hl });
  return `https://www.google.com/travel/flights?${search.toString()}`;
}
