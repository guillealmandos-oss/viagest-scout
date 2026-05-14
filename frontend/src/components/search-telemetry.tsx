"use client";

import { useEffect } from "react";

import { AppLocale } from "@/i18n/config";
import { postAnalyticsEvent } from "@/lib/api";

export function SearchTelemetry({
  searchId,
  locale,
}: {
  searchId: string;
  locale: AppLocale;
}) {
  useEffect(() => {
    postAnalyticsEvent({
      event_name: "result_viewed",
      search_id: searchId,
      actor: "beta-user",
      payload: { source: "result_page" },
    }, locale).catch(() => null);
  }, [locale, searchId]);

  return null;
}
