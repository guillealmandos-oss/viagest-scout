import ianaByIata from "@/data/iata-to-iana.json";

import type { AppLocale } from "@/i18n/config";

import { formatFlightDatetimeUtc } from "@/lib/api";

type IataMap = Record<string, string>;

const TZ_BY_IATA = ianaByIata as IataMap;

export function timezoneForAirport(iataCode: string | undefined): string | undefined {
  if (!iataCode || iataCode === "N/A") {
    return undefined;
  }
  return TZ_BY_IATA[iataCode.toUpperCase()];
}

function formatInZone(iso: string, locale: AppLocale, timeZone: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) {
    return iso;
  }
  const tag = locale === "es" ? "es-UY" : "en-US";
  return new Intl.DateTimeFormat(tag, {
    timeZone,
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: locale === "en",
    timeZoneName: "short",
  }).format(d);
}

/** departure_at → hora local en aeropuerto de origen; arrival_at → en aeropuerto de destino */
export function formatScheduleLines(
  iso: string,
  locale: AppLocale,
  airportCode: string,
): { localText: string | null; utcText: string } {
  const utcText = formatFlightDatetimeUtc(iso, locale);
  const tz = timezoneForAirport(airportCode);
  if (!tz) {
    return { localText: null, utcText };
  }
  try {
    return { localText: formatInZone(iso, locale, tz), utcText };
  } catch {
    return { localText: null, utcText };
  }
}
