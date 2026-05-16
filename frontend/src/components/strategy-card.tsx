"use client";

import { Fragment, useMemo, useState } from "react";

import { AppDictionary } from "@/i18n/dictionary";
import { AppLocale } from "@/i18n/config";
import { formatAirlineWithCode } from "@/lib/airlines";
import { formatMinutes, postAnalyticsEvent } from "@/lib/api";
import { googleFlightsSearchUrl, tripSearchParamsFromItinerary } from "@/lib/externalFlightSearch";
import { formatScheduleLines } from "@/lib/flightTimes";
import { formatSliceStopsSummary, isLongConnection } from "@/lib/itineraryDisplay";
import { strategyTheme } from "@/lib/strategyTheme";
import { Strategy } from "@/types/travel";

interface StrategyCardProps {
  searchId: string;
  strategy: Strategy;
  locale: AppLocale;
  dictionary: AppDictionary;
}

export function StrategyCard({ searchId, strategy, locale, dictionary }: StrategyCardProps) {
  const copy = dictionary.strategyCard;
  const theme = strategyTheme[strategy.strategy_type];
  const [isExpanded, setIsExpanded] = useState(strategy.is_recommended);
  const [hasTrackedOpen, setHasTrackedOpen] = useState(strategy.is_recommended);
  const [saveState, setSaveState] = useState<"idle" | "saved">("idle");

  const slices = useMemo(() => {
    const it = strategy.itinerary;
    if (it.slices && it.slices.length > 0) {
      return it.slices;
    }
    return [{ segments: it.segments, layovers: it.layovers ?? [] }];
  }, [strategy.itinerary]);

  const googleFlightsUrl = useMemo(() => {
    const p = tripSearchParamsFromItinerary(strategy.itinerary);
    return p ? googleFlightsSearchUrl(p, locale) : null;
  }, [strategy.itinerary, locale]);

  function sliceHeading(sliceIndex: number, sliceCount: number): string {
    if (sliceCount === 1) {
      return "";
    }
    if (sliceIndex === 0) {
      return copy.sections.sliceOutbound;
    }
    if (sliceIndex === 1 && sliceCount === 2) {
      return copy.sections.sliceInbound;
    }
    return copy.sections.sliceOther.replace("{n}", String(sliceIndex + 1));
  }

  const topScores = useMemo(
    () =>
      Object.entries(strategy.score_breakdown)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3),
    [strategy.score_breakdown],
  );

  async function toggleExpanded() {
    const nextValue = !isExpanded;
    setIsExpanded(nextValue);
    if (nextValue && !hasTrackedOpen) {
      setHasTrackedOpen(true);
      await postAnalyticsEvent(
        {
          event_name: "strategy_opened",
          strategy_type: strategy.strategy_type,
          search_id: searchId,
          payload: { total_score: strategy.total_score },
        },
        locale,
      ).catch(() => null);
    }
  }

  async function saveRecommendation() {
    const key = `travel-strategy:${searchId}:${strategy.strategy_type}`;
    localStorage.setItem(
      key,
      JSON.stringify({
        searchId,
        strategyType: strategy.strategy_type,
        savedAt: new Date().toISOString(),
      }),
    );
    setSaveState("saved");
    await postAnalyticsEvent(
      {
        event_name: "recommendation_saved",
        strategy_type: strategy.strategy_type,
        search_id: searchId,
        payload: { route: strategy.itinerary.route_summary },
      },
      locale,
    ).catch(() => null);
  }

  return (
    <article
      className={`card relative overflow-hidden transition-shadow hover:shadow-md ${theme.borderClass}`}
    >
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-32 opacity-80"
        style={{ background: theme.muted }}
      />

      <div className="relative p-6 md:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex-1 space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-bold uppercase tracking-widest ${theme.badgeClass}`}
              >
                {strategy.title}
              </span>
              {strategy.is_recommended ? (
                <span className="inline-flex items-center rounded-full bg-[var(--color-ink)] px-3 py-1 text-xs font-bold uppercase tracking-widest text-white">
                  {copy.recommended}
                </span>
              ) : null}
            </div>

            <div>
              <h2 className="text-xl font-bold tracking-tight text-[var(--color-text-primary)] md:text-2xl">
                {strategy.recommendation_badge}
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-7 text-[var(--color-text-muted)]">
                {strategy.explanation}
              </p>
            </div>
          </div>

          <div className="shrink-0 lg:min-w-56 xl:min-w-64">
            <div
              className="rounded-2xl border p-5"
              style={{ borderColor: theme.border, background: theme.muted }}
            >
              <p className="text-xs font-semibold uppercase tracking-widest text-[var(--color-text-faint)]">
                {copy.metrics.price}
              </p>
              <p
                className="mt-1 text-4xl font-black tracking-tight"
                style={{ color: theme.accent }}
              >
                {strategy.itinerary.currency} {strategy.itinerary.total_price.toFixed(0)}
              </p>
              <div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 border-t border-[var(--color-border)]/60 pt-4">
                <Metric
                  label={copy.metrics.duration}
                  value={formatMinutes(strategy.itinerary.total_duration_minutes, locale)}
                />
                <Metric label={copy.metrics.stops} value={String(strategy.itinerary.stops_count)} />
                <Metric label={copy.metrics.flexibility} value={strategy.itinerary.flexibility_label} />
                <Metric
                  label={copy.metrics.score}
                  value={String(strategy.total_score)}
                  highlight
                  accent={theme.accent}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {topScores.map(([label, score]) => (
            <ScoreBlock
              key={label}
              label={copy.scoreLabels[label] ?? label}
              score={score}
              accent={theme.accent}
            />
          ))}
          <div className="panel-muted px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-[var(--color-text-faint)]">
              {copy.metrics.route}
            </p>
            <p className="mt-2 text-xs font-medium leading-5 text-[var(--color-text-body)]">
              {strategy.itinerary.route_summary}
            </p>
          </div>
        </div>

        <div className="mt-6 flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <button className="btn-secondary" onClick={toggleExpanded} type="button">
              {isExpanded ? copy.actions.hideDetails : copy.actions.showDetails}
            </button>
            <button
              className="btn-primary"
              onClick={saveRecommendation}
              type="button"
              style={
                saveState === "saved" ? { background: "var(--color-success)" } : undefined
              }
            >
              {saveState === "saved" ? copy.actions.saved : copy.actions.save}
            </button>
            {googleFlightsUrl ? (
              <a
                className={`inline-flex items-center rounded-full border px-5 py-2.5 text-sm font-semibold transition hover:opacity-90 ${theme.badgeClass}`}
                href={googleFlightsUrl}
                onClick={() => {
                  void postAnalyticsEvent(
                    {
                      event_name: "external_flight_search_opened",
                      strategy_type: strategy.strategy_type,
                      search_id: searchId,
                      payload: { provider: "google_flights" },
                    },
                    locale,
                  ).catch(() => null);
                }}
                rel="noopener noreferrer"
                target="_blank"
              >
                {copy.externalSearch.openGoogleFlights}
              </a>
            ) : null}
          </div>
          {googleFlightsUrl ? (
            <p className="max-w-2xl text-xs leading-relaxed text-[var(--color-text-faint)]">
              {copy.externalSearch.disclaimer}
            </p>
          ) : null}
        </div>

        {isExpanded ? (
          <div className="mt-8 border-t border-[var(--color-border)] pt-8">
            <div className="grid gap-6 xl:grid-cols-2">
              <div className="space-y-4">
                <DetailBlock
                  title={copy.sections.tradeoffs}
                  items={strategy.tradeoffs}
                  emptyLabel={copy.sections.tradeoffsEmpty}
                />
                <DetailBlock
                  title={copy.sections.opportunities}
                  items={
                    strategy.opportunity_notes.length > 0
                      ? strategy.opportunity_notes
                      : strategy.itinerary.opportunity_notes
                  }
                  emptyLabel={copy.sections.opportunitiesEmpty}
                />
                <DetailBlock
                  title={copy.sections.migration}
                  items={strategy.itinerary.migration_notes}
                  emptyLabel={copy.sections.migrationEmpty}
                />
              </div>

              <div className="space-y-4">
                <DetailBlock
                  title={copy.sections.operationalRisk}
                  items={strategy.itinerary.risk_flags.map(
                    (flag) => `${copy.severityLabels[flag.severity]}: ${flag.message}`,
                  )}
                  emptyLabel={copy.sections.operationalRiskEmpty}
                />
                <div className="panel-muted p-5">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-[var(--color-text-muted)]">
                    {copy.sections.segments}
                  </h3>
                  <div className="mt-4 grid gap-6">
                    {slices.map((slice, sliceIndex) => (
                      <div key={`slice-${sliceIndex}`} className="grid gap-3">
                        {slices.length > 1 ? (
                          <h4 className="text-xs font-semibold uppercase tracking-widest text-[var(--color-text-faint)]">
                            {sliceHeading(sliceIndex, slices.length)}
                          </h4>
                        ) : null}
                        <p className="text-sm font-medium text-[var(--color-text-body)]">
                          {formatSliceStopsSummary(slice, locale, copy.sections)}
                        </p>
                        {slice.segments.map((segment, segIdx) => (
                          <Fragment
                            key={`${segment.airline}-${segment.flight_number}-${segment.departure_at}-${sliceIndex}-${segIdx}`}
                          >
                            <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3">
                              <div className="flex items-center justify-between gap-3">
                                <p className="text-sm font-bold text-[var(--color-text-primary)]">
                                  {segment.origin} → {segment.destination}
                                </p>
                                <span className="text-xs text-[var(--color-text-faint)]">
                                  {formatMinutes(segment.duration_minutes, locale)}
                                </span>
                              </div>
                              <p className="mt-1 text-xs text-[var(--color-text-muted)]">
                                {formatAirlineWithCode(segment)} {segment.flight_number} ·{" "}
                                {segment.cabin_class}
                              </p>
                              {segment.operating_carrier_name ? (
                                <p className="mt-1 text-xs text-[var(--color-text-muted)]">
                                  {copy.sections.operatedBy.replace(
                                    "{carrier}",
                                    segment.operating_carrier_name,
                                  )}
                                </p>
                              ) : null}
                              <p className="mt-2 space-y-0.5 text-xs leading-5 text-[var(--color-text-muted)]">
                                <SegmentTimesBlock
                                  copy={copy.segmentSchedule}
                                  iso={segment.departure_at}
                                  locale={locale}
                                  airportCode={segment.origin}
                                  variant="departure"
                                />
                                <SegmentTimesBlock
                                  copy={copy.segmentSchedule}
                                  iso={segment.arrival_at}
                                  locale={locale}
                                  airportCode={segment.destination}
                                  variant="arrival"
                                />
                              </p>
                              {segment.technical_stops && segment.technical_stops.length > 0 ? (
                                <ul className="mt-2 space-y-1 border-t border-[var(--color-border)] pt-2 text-xs text-[var(--color-text-body)]">
                                  {segment.technical_stops.map((stop) => (
                                    <li key={`${segment.departure_at}-${stop.airport}`}>
                                      <span className="font-medium text-[var(--color-text-body)]">
                                        {copy.sections.technicalStopPrefix}
                                      </span>
                                      {" · "}
                                      {stop.airport}
                                      {stop.duration_minutes > 0 ? (
                                        <>
                                          {" · "}
                                          {formatMinutes(stop.duration_minutes, locale)}
                                        </>
                                      ) : null}
                                    </li>
                                  ))}
                                </ul>
                              ) : null}
                            </div>
                            {segIdx < slice.layovers.length ? (
                              <LayoverRow
                                airport={slice.layovers[segIdx].airport}
                                copy={copy}
                                durationMinutes={slice.layovers[segIdx].duration_minutes}
                                isTechnical={
                                  segment.flight_number !== "N/A" &&
                                  slice.segments[segIdx + 1]?.flight_number === segment.flight_number
                                }
                                locale={locale}
                                themeBorder={theme.border}
                              />
                            ) : null}
                          </Fragment>
                        ))}
                      </div>
                    ))}
                  </div>
                  <p className="mt-4 text-xs leading-relaxed text-[var(--color-text-faint)]">
                    {copy.segmentSchedule.utcFootnote}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </article>
  );
}

function SegmentTimesBlock({
  copy,
  iso,
  locale,
  airportCode,
  variant,
}: {
  copy: AppDictionary["strategyCard"]["segmentSchedule"];
  iso: string;
  locale: AppLocale;
  airportCode: string;
  variant: "departure" | "arrival";
}) {
  const { localText, utcText } = formatScheduleLines(iso, locale, airportCode);
  const localLabel =
    variant === "departure"
      ? copy.departLocalLabel.replace("{code}", airportCode)
      : copy.arriveLocalLabel.replace("{code}", airportCode);
  const utcOnlyLabel = variant === "departure" ? copy.departUtc : copy.arriveUtc;

  return (
    <>
      <span className="block">
        {localText ? (
          <>
            <span className="font-medium text-[var(--color-text-body)]">{localLabel}:</span>{" "}
            {localText}
          </>
        ) : (
          <>
            <span className="font-medium text-[var(--color-text-body)]">{utcOnlyLabel}:</span>{" "}
            {utcText}
          </>
        )}
      </span>
      {localText ? (
        <span className="block text-[var(--color-text-faint)]">
          <span className="font-medium">{copy.utcReferenceLabel}:</span> {utcText}
        </span>
      ) : null}
    </>
  );
}

function Metric({
  label,
  value,
  highlight = false,
  accent,
}: {
  label: string;
  value: string;
  highlight?: boolean;
  accent?: string;
}) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-widest text-[var(--color-text-faint)]">
        {label}
      </p>
      <p
        className="mt-0.5 text-sm font-bold"
        style={highlight && accent ? { color: accent } : { color: "var(--color-text-primary)" }}
      >
        {value}
      </p>
    </div>
  );
}

function ScoreBlock({
  label,
  score,
  accent,
}: {
  label: string;
  score: number;
  accent: string;
}) {
  const pct = Math.min(100, Math.max(0, score));
  return (
    <div className="panel-muted px-4 py-3">
      <p className="text-xs font-semibold uppercase tracking-widest text-[var(--color-text-faint)]">
        {label}
      </p>
      <p className="mt-1 text-2xl font-black text-[var(--color-text-primary)]">{score}</p>
      <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-[var(--color-border)]">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, background: accent }}
        />
      </div>
    </div>
  );
}

function DetailBlock({
  title,
  items,
  emptyLabel,
}: {
  title: string;
  items: string[];
  emptyLabel: string;
}) {
  return (
    <div className="panel-muted p-5">
      <h3 className="text-xs font-bold uppercase tracking-widest text-[var(--color-text-muted)]">
        {title}
      </h3>
      <ul className="mt-3 space-y-2">
        {items.length > 0 ? (
          items.map((item) => (
            <li
              key={item}
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2.5 text-sm leading-6 text-[var(--color-text-body)]"
            >
              {item}
            </li>
          ))
        ) : (
          <li className="rounded-lg border border-dashed border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2.5 text-sm text-[var(--color-text-faint)]">
            {emptyLabel}
          </li>
        )}
      </ul>
    </div>
  );
}

function LayoverRow({
  airport,
  copy,
  durationMinutes,
  isTechnical,
  locale,
  themeBorder,
}: {
  airport: string;
  copy: AppDictionary["strategyCard"];
  durationMinutes: number;
  isTechnical: boolean;
  locale: AppLocale;
  themeBorder: string;
}) {
  return (
    <div
      className="ml-3 border-l-2 pl-4 text-sm text-[var(--color-text-body)]"
      style={{ borderColor: themeBorder }}
    >
      <span className="font-medium text-[var(--color-text-primary)]">
        {isTechnical ? copy.sections.technicalStopPrefix : copy.sections.connectionPrefix}
      </span>
      {" · "}
      {airport}
      {" · "}
      {formatMinutes(durationMinutes, locale)}
      {isLongConnection(durationMinutes) ? copy.sections.longConnectionNote : ""}
    </div>
  );
}
