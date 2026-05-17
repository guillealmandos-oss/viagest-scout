import { AppDictionary } from "@/i18n/dictionary";
import { AppLocale } from "@/i18n/config";
import { getAnalyticsSummary, getProviderHealthSummary } from "@/lib/api";
import { formatProviderError } from "@/lib/providerErrors";

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
      <SectionCard eyebrow={copy.eyebrow} title={copy.title} subtitle={copy.subtitle}>
        <p className="rounded-2xl border border-dashed border-[var(--color-border-strong)] px-4 py-6 text-sm leading-6 text-[var(--color-text-faint)]">
          {copy.unavailable}
        </p>
      </SectionCard>
    );
  }

  return (
    <SectionCard eyebrow={copy.eyebrow} title={copy.title} subtitle={copy.subtitle}>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <Metric label={copy.metrics.searches} value={summary.total_searches} />
        <Metric label={copy.metrics.events} value={summary.total_events} />
        <Metric label={copy.metrics.strategiesOpened} value={summary.strategy_open_events} />
        <Metric label={copy.metrics.saves} value={summary.saved_recommendations} />
        <Metric label={copy.metrics.feedback} value={summary.feedback_submissions} />
      </div>

      <div className="mt-6 space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
          {copy.recentFeedbackTitle}
        </h3>
        <div className="grid gap-3">
          {summary.recent_feedback.length > 0 ? (
            summary.recent_feedback.map((item) => (
              <article
                key={`${item.search_id}-${item.created_at}`}
                className="stat-tile-inner px-4 py-3 text-sm text-[var(--color-text-body)]"
              >
                <p>{item.text}</p>
                <p className="mt-2 text-xs uppercase tracking-[0.2em] text-[var(--color-text-faint)]">
                  {item.event_name}
                </p>
              </article>
            ))
          ) : (
            <p className="rounded-2xl border border-dashed border-[var(--color-border-strong)] px-4 py-6 text-sm text-[var(--color-text-faint)]">
              {copy.recentFeedbackEmpty}
            </p>
          )}
        </div>
      </div>

      {summary.recent_provider_issues.length > 0 ? (
        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
            {copy.recentProviderIssuesTitle}
          </h3>
          <div className="grid gap-3">
            {summary.recent_provider_issues.map((item) => (
              <article
                key={`provider-${item.search_id}-${item.created_at}`}
                className="alert-warning px-4 py-3 text-sm leading-6"
              >
                <p>{formatProviderError(item.text, locale) ?? item.text}</p>
              </article>
            ))}
          </div>
        </div>
      ) : null}

      <div className="mt-6 space-y-3">
        <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">
          {copy.providerHealthTitle}
        </h3>
        <div className="grid gap-3 md:grid-cols-2">
          {providerHealth && providerHealth.items.length > 0 ? (
            providerHealth.items.map((item) => (
              <article key={item.provider_name} className="stat-tile px-4 py-4 text-sm text-[var(--color-text-body)]">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-base font-semibold text-[var(--color-text-primary)]">{item.provider_name}</p>
                    <p className="mt-1 text-xs uppercase tracking-[0.2em] text-[var(--color-text-faint)]">
                      {copy.lastStatusPrefix}{" "}
                      {copy.providerStatuses[item.last_status as keyof typeof copy.providerStatuses] ??
                        item.last_status}
                    </p>
                  </div>
                  <p className="badge badge-gold">{item.success_rate}{copy.successRateSuffix}</p>
                </div>
                <div className="mt-4 grid grid-cols-3 gap-3">
                  <MiniMetric label={copy.miniMetrics.attempts} value={item.total_attempts} />
                  <MiniMetric label={copy.miniMetrics.latencyMs} value={item.avg_latency_ms} />
                  <MiniMetric label={copy.miniMetrics.offers} value={item.avg_offer_count} />
                </div>
                {item.last_external_request_id || item.last_external_correlation_id ? (
                  <div className="stat-tile-inner mt-3 space-y-2 px-3 py-3 text-xs leading-5 text-[var(--color-text-body)]">
                    {item.last_external_request_id ? (
                      <p>
                        <span className="font-semibold text-[var(--color-text-primary)]">
                          {copy.externalIds.requestId}:
                        </span>{" "}
                        {item.last_external_request_id}
                      </p>
                    ) : null}
                    {item.last_external_correlation_id ? (
                      <p>
                        <span className="font-semibold text-[var(--color-text-primary)]">
                          {copy.externalIds.correlationId}:
                        </span>{" "}
                        {item.last_external_correlation_id}
                      </p>
                    ) : null}
                  </div>
                ) : null}
                {item.last_error ? (
                  <p className="alert-warning mt-3 px-3 py-2 text-xs leading-5">
                    {copy.lastErrorPrefix}{" "}
                    {formatProviderError(item.last_error, locale, item.provider_name) ?? item.last_error}
                  </p>
                ) : null}
              </article>
            ))
          ) : (
            <p className="rounded-2xl border border-dashed border-[var(--color-border-strong)] px-4 py-6 text-sm text-[var(--color-text-faint)]">
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
    <div className="stat-tile px-4 py-5">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--color-text-muted)]">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-[var(--color-gold)]">{value}</p>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="stat-tile-inner px-3 py-3">
      <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--color-text-faint)]">{label}</p>
      <p className="mt-2 text-lg font-semibold text-[var(--color-text-primary)]">{value}</p>
    </div>
  );
}
