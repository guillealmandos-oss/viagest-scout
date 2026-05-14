import { AnalyticsPanel } from "@/components/analytics-panel";
import { Hero } from "@/components/hero";
import { SearchForm } from "@/components/search-form";
import { SectionCard } from "@/components/section-card";
import { getLocaleDictionary } from "@/i18n/server";

export const dynamic = "force-dynamic";

export default async function LocalizedHome({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale: rawLocale } = await params;
  const { locale, dictionary } = getLocaleDictionary(rawLocale);
  const copy = dictionary.home.mvp;

  return (
    <div className="space-y-8">
      <Hero dictionary={dictionary} />

      <div className="grid gap-8 xl:grid-cols-[1.2fr_0.8fr]">
        <SearchForm dictionary={dictionary} locale={locale} />
        <SectionCard eyebrow={copy.eyebrow} title={copy.title} subtitle={copy.subtitle}>
          <ul className="grid gap-3 text-sm leading-6 text-slate-700">
            {copy.items.map((item) => (
              <li key={item} className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
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
