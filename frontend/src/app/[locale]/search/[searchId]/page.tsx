import Link from "next/link";
import { notFound } from "next/navigation";

import { FeedbackForm } from "@/components/feedback-form";
import { SearchTelemetry } from "@/components/search-telemetry";
import { SectionCard } from "@/components/section-card";
import { StrategyCard } from "@/components/strategy-card";
import { getLocaleDictionary } from "@/i18n/server";
import { getSearch } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function LocalizedSearchResultPage({
  params,
}: {
  params: Promise<{ locale: string; searchId: string }>;
}) {
  const { locale: rawLocale, searchId } = await params;
  const { locale, dictionary } = getLocaleDictionary(rawLocale);
  const copy = dictionary.searchResult;
  const result = await getSearch(searchId, locale).catch(() => null);

  if (!result) {
    notFound();
  }

  const showTestInventoryBanner = result.assumptions.some(
    (assumption) =>
      assumption.rule_key === "provider.assumption.test_inventory.rule" ||
      assumption.rule?.toLowerCase().includes("inventario de prueba") ||
      assumption.rule?.toLowerCase().includes("test inventory"),
  );

  return (
    <div className="space-y-8">
      <SearchTelemetry locale={locale} searchId={searchId} />

      {showTestInventoryBanner ? (
        <div className="alert-warning px-5 py-4 text-sm leading-6">
          {copy.testInventoryBanner}
        </div>
      ) : null}

      <SectionCard
        eyebrow={`${copy.eyebrowPrefix} ${result.provider_name}`}
        title={copy.title}
        subtitle={copy.subtitle}
      >
        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-4">
            <p className="text-base leading-8 text-slate-700">{result.summary}</p>
            <div className="flex flex-wrap gap-3">
              <Link className="btn-primary px-5 py-3" href={`/${locale}`}>
                {copy.newSearch}
              </Link>
              <Link className="btn-secondary px-5 py-3" href={`/${locale}`}>
                {copy.adjustContext}
              </Link>
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
            <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
              {copy.assumptionsTitle}
            </h2>
            <div className="mt-4 grid gap-3">
              {result.assumptions.length > 0 ? (
                result.assumptions.map((assumption) => (
                  <article
                    key={`${assumption.scope}-${assumption.rule}`}
                    className="rounded-2xl border border-slate-200 bg-white px-4 py-3"
                  >
                    <p className="text-sm font-semibold text-slate-900">{assumption.rule}</p>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{assumption.note}</p>
                    <p className="mt-2 text-xs uppercase tracking-[0.2em] text-slate-400">
                      {copy.scopeLabels[assumption.scope] ?? assumption.scope} · {copy.confidenceLabel}{" "}
                      {copy.confidenceValues[assumption.confidence as keyof typeof copy.confidenceValues] ??
                        assumption.confidence}
                    </p>
                  </article>
                ))
              ) : (
                <p className="rounded-2xl border border-dashed border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
                  {copy.assumptionsEmpty}
                </p>
              )}
            </div>
          </div>
        </div>
      </SectionCard>

      <section className="grid gap-6">
        {result.strategies.map((strategy) => (
          <StrategyCard
            key={`${result.search_id}-${strategy.strategy_type}`}
            dictionary={dictionary}
            locale={locale}
            searchId={result.search_id}
            strategy={strategy}
          />
        ))}
      </section>

      <FeedbackForm dictionary={dictionary} locale={locale} searchId={result.search_id} />
    </div>
  );
}
