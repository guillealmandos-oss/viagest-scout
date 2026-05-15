"use client";

import { Fragment, useMemo, useState } from "react";

import { AppDictionary } from "@/i18n/dictionary";
import { AppLocale } from "@/i18n/config";
import { formatMinutes, postAnalyticsEvent } from "@/lib/api";
import { Strategy } from "@/types/travel";

interface StrategyCardProps {
  searchId: string;
  strategy: Strategy;
  locale: AppLocale;
  dictionary: AppDictionary;
}

const accentClasses: Record<Strategy["strategy_type"], string> = {
  savings: "border-emerald-200 bg-emerald-50 text-emerald-700",
  experience: "border-sky-200 bg-sky-50 text-sky-700",
  miles: "border-violet-200 bg-violet-50 text-violet-700",
};

export function StrategyCard({ searchId, strategy, locale, dictionary }: StrategyCardProps) {
  const copy = dictionary.strategyCard;
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
      await postAnalyticsEvent({
        event_name: "strategy_opened",
        strategy_type: strategy.strategy_type,
        search_id: searchId,
        payload: { total_score: strategy.total_score },
      }, locale).catch(() => null);
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
    await postAnalyticsEvent({
      event_name: "recommendation_saved",
      strategy_type: strategy.strategy_type,
      search_id: searchId,
      payload: { route: strategy.itinerary.route_summary },
    }, locale).catch(() => null);
  }

  return (
    <article className="rounded-[1.75rem] border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/50">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <span className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${accentClasses[strategy.strategy_type]}`}>
              {strategy.title}
            </span>
            {strategy.is_recommended ? (
              <span className="rounded-full bg-slate-950 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-white">
                {copy.recommended}
              </span>
            ) : null}
          </div>
          <div>
            <h2 className="text-2xl font-semibold text-slate-950">{strategy.recommendation_badge}</h2>
            <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-600">{strategy.explanation}</p>
          </div>
        </div>

        <div className="grid min-w-64 gap-3 rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{copy.metrics.price}</p>
            <p className="mt-1 text-2xl font-semibold text-slate-950">
              {strategy.itinerary.currency} {strategy.itinerary.total_price.toFixed(0)}
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Metric label={copy.metrics.duration} value={formatMinutes(strategy.itinerary.total_duration_minutes, locale)} />
            <Metric label={copy.metrics.stops} value={String(strategy.itinerary.stops_count)} />
            <Metric label={copy.metrics.flexibility} value={strategy.itinerary.flexibility_label} />
            <Metric label={copy.metrics.score} value={String(strategy.total_score)} />
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {topScores.map(([label, score]) => (
          <div key={label} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
              {copy.scoreLabels[label] ?? label}
            </p>
            <p className="mt-2 text-xl font-semibold text-slate-950">{score}</p>
          </div>
        ))}
        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{copy.metrics.route}</p>
          <p className="mt-2 text-sm font-medium text-slate-900">{strategy.itinerary.route_summary}</p>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-950 hover:text-slate-950"
          onClick={toggleExpanded}
          type="button"
        >
          {isExpanded ? copy.actions.hideDetails : copy.actions.showDetails}
        </button>
        <button
          className="rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
          onClick={saveRecommendation}
          type="button"
        >
          {saveState === "saved" ? copy.actions.saved : copy.actions.save}
        </button>
      </div>

      {isExpanded ? (
        <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_0.9fr]">
          <div className="space-y-5">
            <DetailBlock title={copy.sections.tradeoffs} items={strategy.tradeoffs} emptyLabel={copy.sections.tradeoffsEmpty} />
            <DetailBlock
              title={copy.sections.opportunities}
              items={strategy.opportunity_notes.length > 0 ? strategy.opportunity_notes : strategy.itinerary.opportunity_notes}
              emptyLabel={copy.sections.opportunitiesEmpty}
            />
            <DetailBlock
              title={copy.sections.migration}
              items={strategy.itinerary.migration_notes}
              emptyLabel={copy.sections.migrationEmpty}
            />
          </div>

          <div className="space-y-5">
            <DetailBlock
              title={copy.sections.operationalRisk}
              items={strategy.itinerary.risk_flags.map(
                (flag) => `${copy.severityLabels[flag.severity]}: ${flag.message}`,
              )}
              emptyLabel={copy.sections.operationalRiskEmpty}
            />
            <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
              <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">{copy.sections.segments}</h3>
              <div className="mt-4 grid gap-6">
                {slices.map((slice, sliceIndex) => (
                  <div key={`slice-${sliceIndex}`} className="grid gap-3">
                    {slices.length > 1 ? (
                      <h4 className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        {sliceHeading(sliceIndex, slices.length)}
                      </h4>
                    ) : null}
                    {slice.segments.map((segment, segIdx) => (
                      <Fragment key={`${segment.airline}-${segment.flight_number}-${segment.departure_at}-${sliceIndex}-${segIdx}`}>
                        <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3">
                          <p className="text-sm font-semibold text-slate-950">
                            {segment.origin} {"->"} {segment.destination}
                          </p>
                          <p className="mt-1 text-sm text-slate-600">
                            {segment.airline} {segment.flight_number} · {segment.cabin_class} ·{" "}
                            {formatMinutes(segment.duration_minutes, locale)}
                          </p>
                        </div>
                        {segIdx < slice.layovers.length ? (
                          <div className="ml-3 border-l-2 border-sky-200 pl-4 text-sm text-slate-600">
                            <span className="font-medium text-slate-700">{copy.sections.connectionPrefix}</span>
                            {" · "}
                            {slice.layovers[segIdx].airport}
                            {" · "}
                            {formatMinutes(slice.layovers[segIdx].duration_minutes, locale)}
                          </div>
                        ) : null}
                      </Fragment>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{label}</p>
      <p className="mt-1 text-sm font-semibold text-slate-900">{value}</p>
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
    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
      <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">{title}</h3>
      <ul className="mt-4 grid gap-3">
        {items.length > 0 ? (
          items.map((item) => (
            <li key={item} className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-700">
              {item}
            </li>
          ))
        ) : (
          <li className="rounded-2xl border border-dashed border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-500">
            {emptyLabel}
          </li>
        )}
      </ul>
    </div>
  );
}
