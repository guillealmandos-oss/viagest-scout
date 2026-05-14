import { AppDictionary } from "@/i18n/dictionary";

export function Hero({ dictionary }: { dictionary: AppDictionary }) {
  const hero = dictionary.home.hero;

  return (
    <section className="grid gap-10 rounded-[2rem] border border-slate-200 bg-slate-950 px-8 py-10 text-white shadow-2xl shadow-slate-300/40 lg:grid-cols-[1.2fr_0.8fr] lg:px-12">
      <div className="space-y-6">
        <p className="text-sm font-semibold uppercase tracking-[0.32em] text-sky-300">{hero.eyebrow}</p>
        <div className="space-y-4">
          <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-balance sm:text-5xl">
            {hero.title}
          </h1>
          <p className="max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">
            {hero.description}
          </p>
        </div>
      </div>

      <div className="grid gap-4 rounded-[1.75rem] border border-white/10 bg-white/5 p-6 backdrop-blur">
        <div>
          <p className="text-sm font-medium text-slate-300">{hero.optimizeLabel}</p>
          <p className="mt-2 text-2xl font-semibold">{hero.optimizeValue}</p>
        </div>
        <ul className="grid gap-3 text-sm text-slate-200">
          {hero.highlights.map((highlight) => (
            <li key={highlight} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
              {highlight}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
