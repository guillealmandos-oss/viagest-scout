import { AppDictionary } from "@/i18n/dictionary";

export function Hero({ dictionary }: { dictionary: AppDictionary }) {
  const hero = dictionary.home.hero;

  return (
    <section className="card-raised grid gap-10 px-8 py-10 lg:grid-cols-[1.2fr_0.8fr] lg:px-12">
      <div className="space-y-6">
        <p className="eyebrow">{hero.eyebrow}</p>
        <div className="space-y-4">
          <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-balance text-[var(--color-text-primary)] sm:text-5xl">
            {hero.title}
          </h1>
          <p className="max-w-2xl text-base leading-7 text-[var(--color-text-muted)] sm:text-lg">
            {hero.description}
          </p>
        </div>
      </div>

      <div className="grid gap-4 rounded-[var(--radius-xl)] border border-[var(--color-border)] bg-[var(--color-surface-muted)] p-6">
        <div>
          <p className="text-sm font-medium text-[var(--color-text-muted)]">{hero.optimizeLabel}</p>
          <p className="mt-2 text-2xl font-semibold text-[var(--color-gold)]">{hero.optimizeValue}</p>
        </div>
        <ul className="grid gap-3 text-sm text-[var(--color-text-body)]">
          {hero.highlights.map((highlight) => (
            <li key={highlight} className="stat-tile-inner px-4 py-3">
              {highlight}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
