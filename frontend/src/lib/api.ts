import { AppLocale, DEFAULT_LOCALE } from "@/i18n/config";
import { AnalyticsSummary, ProviderHealthSummary, SearchPayload, SearchResponse } from "@/types/travel";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

interface RequestOptions extends RequestInit {
  locale?: AppLocale;
}

async function request<T>(path: string, init?: RequestOptions): Promise<T> {
  const locale = init?.locale ?? DEFAULT_LOCALE;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "Accept-Language": locale,
      "X-Locale": locale,
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const fallbackMessage = `Request failed with status ${response.status}`;
    let detail = fallbackMessage;

    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? fallbackMessage;
    } catch {
      detail = fallbackMessage;
    }

    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export function createSearch(payload: SearchPayload, locale: AppLocale): Promise<SearchResponse> {
  return request<SearchResponse>("/api/v1/searches", {
    method: "POST",
    body: JSON.stringify(payload),
    locale,
  });
}

export function getSearch(searchId: string, locale: AppLocale): Promise<SearchResponse> {
  return request<SearchResponse>(`/api/v1/searches/${searchId}`, { locale });
}

export function getAnalyticsSummary(locale: AppLocale): Promise<AnalyticsSummary> {
  return request<AnalyticsSummary>("/api/v1/analytics/summary", { locale });
}

export function getProviderHealthSummary(locale: AppLocale): Promise<ProviderHealthSummary> {
  return request<ProviderHealthSummary>("/api/v1/analytics/provider-health", { locale });
}

export function postAnalyticsEvent(payload: {
  event_name: string;
  actor?: string;
  strategy_type?: string;
  search_id?: string;
  payload?: Record<string, unknown>;
  free_text?: string;
}, locale: AppLocale): Promise<{ status: string }> {
  return request<{ status: string }>("/api/v1/analytics/events", {
    method: "POST",
    body: JSON.stringify(payload),
    locale,
  });
}

export function formatMinutes(totalMinutes: number, locale: AppLocale): string {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return locale === "es" ? `${hours}h ${minutes}m` : `${hours}h ${minutes}m`;
}

/** UTC formatted timestamps — typical shape from Duffel / Amadeus ISO strings. */
export function formatFlightDatetimeUtc(iso: string, locale: AppLocale): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) {
    return iso;
  }
  const tag = locale === "es" ? "es-UY" : "en-US";
  return new Intl.DateTimeFormat(tag, {
    timeZone: "UTC",
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: locale === "en",
  }).format(d);
}
