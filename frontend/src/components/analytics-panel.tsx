import { AppDictionary } from "@/i18n/dictionary";
import { AppLocale } from "@/i18n/config";
import { getAnalyticsSummary, getProviderHealthSummary } from "@/lib/api";

import { SectionCard } from "./section-card";

export async function AnalyticsPanel({
  locale,
  dictionary,
}: {
  locale: AppLocale;
  dictionary: AppDictionary;
}) {
  const copy = dictionary.analytics;
  const [summary, providerHealth] = await Promise.all([
    getAnalyticsSummary(locale).catch(() => null),
    getProviderHealthSummary(locale).catch(() => null),
  ]);

  if (!summary) {
    return (
      <SectionCard
        eyebrow={copy.eyebrow}
        title={copy.title}
        subtitle={copy.subtitle}
      >
        <p className="rounded-2xl border border-dashed border-slate-200 px-4 py-6 text-sm leading-6 text-slate-500">
          {copy.unavailable}
        </p>
      </SectionCard>
    );
  }

  return (
    <SectionCard
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={copy.subtitle}
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <Metric label={copy.metrics.searches} value={summary.total_searches} />
        <Metric label={copy.metrics.events} value={summary.total_events} />
        <Metric label={copy.metrics.strategiesOpened} value={summary.strategy_open_events} />
        <Metric label={copy.metrics.saves} value={summary.saved_recommendations} />
        <Metric label={copy.metrics.feedback} value={summary.feedback_submissions} />
      </div>

      <div className="mt-6 space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">{copy.recentFeedbackTitle}</h3>
        <div className="grid gap-3">
          {summary.recent_feedback.length > 0 ? (
            summary.recent_feedback.map((item) => (
              <article key={`${item.search_id}-${item.created_at}`} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <p>{item.text}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.2em] text-slate-400">{item.event_name}</p>
              </article>
            ))
          ) : (
            <p className="rounded-2xl border border-dashed border-slate-200 px-4 py-6 text-sm text-slate-500">
              {copy.recentFeedbackEmpty}
            </p>
          )}
        </div>
      </div>

      <div className="mt-6 space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">{copy.providerHealthTitle}</h3>
        <div className="grid gap-3 md:grid-cols-2">
          {providerHealth && providerHealth.items.length > 0 ? (
            providerHealth.items.map((item) => (
              <article key={item.provider_name} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-700">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-base font-semibold text-slate-950">{item.provider_name}</p>
                    <p className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-400">
                      {copy.lastStatusPrefix} {copy.providerStatuses[item.last_status as keyof typeof copy.providerStatuses] ?? item.last_status}
                    </p>
                  </div>
                  <p className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700">
                    {item.success_rate}{copy.successRateSuffix}
                  </p>
                </div>
                <div className="mt-4 grid grid-cols-3 gap-3">
                  <MiniMetric label={copy.miniMetrics.attempts} value={item.total_attempts} />
                  <MiniMetric label={copy.miniMetrics.latencyMs} value={item.avg_latency_ms} />
                  <MiniMetric label={copy.miniMetrics.offers} value={item.avg_offer_count} />
                </div>
                {item.last_external_request_id || item.last_external_correlation_id ? (
                  <div className="mt-3 space-y-2 rounded-2xl border border-slate-200 bg-white px-3 py-3 text-xs leading-5 text-slate-600">
                    {item.last_external_request_id ? (
                      <p>
                        <span className="font-semibold text-slate-900">{copy.externalIds.requestId}:</span> {item.last_external_request_id}
                      </p>
                    ) : null}
                    {item.last_external_correlation_id ? (
                      <p>
                        <span className="font-semibold text-slate-900">{copy.externalIds.correlationId}:</span> {item.last_external_correlation_id}
                      </p>
                    ) : null}
                  </div>
                ) : null}
                {item.last_error ? (
                  <p className="mt-3 rounded-2xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-800">
                    {copy.lastErrorPrefix} {item.last_error}
                  </p>
                ) : null}
              </article>
            ))
          ) : (
            <p className="rounded-2xl border border-dashed border-slate-200 px-4 py-6 text-sm text-slate-500">
              {copy.providerHealthEmpty}
            </p>
          )}
        </div>
      </div>
    </SectionCard>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-5">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-950">{value}</p>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white px-3 py-3">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 text-lg font-semibold text-slate-950">{value}</p>
    </div>
  );
}
