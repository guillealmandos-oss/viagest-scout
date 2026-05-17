import { AnalyticsPanel } from "@/components/analytics-panel";
import { Hero } from "@/components/hero";
import { SearchForm } from "@/components/search-form";
import { SectionCard } from "@/components/section-card";
import { getLocaleDictionary } from "@/i18n/server";
import { showInternalUi } from "@/lib/appEnv";

export const dynamic = "force-dynamic";

export default async function LocalizedHome({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale: rawLocale } = await params;
  const { locale, dictionary } = getLocaleDictionary(rawLocale);
  const internalUi = showInternalUi();
  const sideCopy = internalUi ? dictionary.home.mvp : dictionary.home.highlights;

  return (
    <div className="space-y-8">
      <Hero dictionary={dictionary} />

      <div className="grid gap-8 xl:grid-cols-[1.2fr_0.8fr]">
        <SearchForm dictionary={dictionary} locale={locale} />
        <SectionCard eyebrow={sideCopy.eyebrow} title={sideCopy.title} subtitle={sideCopy.subtitle}>
          <ul className="grid gap-3 text-sm leading-6 text-[var(--color-text-body)]">
            {sideCopy.items.map((item) => (
              <li key={item} className="stat-tile-inner px-4 py-3">
                {item}
              </li>
            ))}
          </ul>
        </SectionCard>
      </div>

      <AnalyticsPanel dictionary={dictionary} locale={locale} />
    </div>
  );
}
