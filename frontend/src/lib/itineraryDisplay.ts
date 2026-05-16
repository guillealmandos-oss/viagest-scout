import type { AppDictionary } from "@/i18n/dictionary";
import type { FlightSlice } from "@/types/travel";

import { formatMinutes } from "@/lib/api";
import type { AppLocale } from "@/i18n/config";

const LONG_CONNECTION_MINUTES = 4 * 60;

export function sliceDoorToDoorMinutes(slice: FlightSlice): number {
  const segments = slice.segments;
  if (!segments.length) {
    return 0;
  }
  const start = new Date(segments[0].departure_at);
  const end = new Date(segments[segments.length - 1].arrival_at);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    return segments.reduce((sum, segment) => sum + segment.duration_minutes, 0);
  }
  return Math.max(0, Math.round((end.getTime() - start.getTime()) / 60_000));
}

export function sliceStopAirports(slice: FlightSlice): string[] {
  const airports: string[] = [];
  for (const layover of slice.layovers) {
    if (layover.airport && !airports.includes(layover.airport)) {
      airports.push(layover.airport);
    }
  }
  for (const segment of slice.segments) {
    for (const stop of segment.technical_stops ?? []) {
      if (stop.airport && !airports.includes(stop.airport)) {
        airports.push(stop.airport);
      }
    }
  }
  return airports;
}

export function sliceConnectionCount(slice: FlightSlice): number {
  const technical = slice.segments.reduce((n, segment) => n + (segment.technical_stops?.length ?? 0), 0);
  return slice.layovers.length + technical;
}

export function formatSliceStopsSummary(
  slice: FlightSlice,
  locale: AppLocale,
  copy: AppDictionary["strategyCard"]["sections"],
): string {
  const duration = formatMinutes(sliceDoorToDoorMinutes(slice), locale);
  const stops = sliceConnectionCount(slice);
  const airports = sliceStopAirports(slice);

  if (stops === 0) {
    return copy.sliceSummaryDirect.replace("{duration}", duration);
  }

  const airportList = airports.length > 0 ? airports.join(", ") : "—";
  return copy.sliceSummaryWithStops
    .replace("{duration}", duration)
    .replace("{count}", String(stops))
    .replace("{airports}", airportList);
}

export function isLongConnection(durationMinutes: number): boolean {
  return durationMinutes >= LONG_CONNECTION_MINUTES;
}
