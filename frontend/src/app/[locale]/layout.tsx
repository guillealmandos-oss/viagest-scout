import type { Metadata } from "next";

import { LanguageSwitcher } from "@/components/language-switcher";
import { getLocaleDictionary } from "@/i18n/server";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale: rawLocale } = await params;
  const { dictionary } = getLocaleDictionary(rawLocale);

  return {
    title: "Viagest Scout",
    description: dictionary.header.description,
  };
}

export default async function LocaleLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}>) {
  const { locale: rawLocale } = await params;
  const { locale, dictionary } = getLocaleDictionary(rawLocale);

  return (
    <div className="mx-auto flex min-h-full w-full max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
      <header className="card-raised mb-8 flex flex-col gap-4 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div
            className="flex shrink-0 items-center justify-center"
            style={{
              width: 38,
              height: 38,
              background: "var(--color-gold)",
              borderRadius: "var(--radius-md)",
            }}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--color-gold-text)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden
            >
              <circle cx="12" cy="12" r="10" />
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
            </svg>
          </div>
          <div>
            <p className="eyebrow" style={{ marginBottom: 2 }}>
              {dictionary.header.eyebrow}
            </p>
            <h1
              className="text-[1.1rem] font-medium tracking-tight text-[var(--color-text-primary)]"
              style={{ margin: 0, letterSpacing: "-0.3px" }}
            >
              Viagest <span style={{ color: "var(--color-gold)" }}>Scout</span>
            </h1>
          </div>
        </div>

        <p className="hidden max-w-sm text-sm leading-relaxed text-[var(--color-text-muted)] md:block">
          {dictionary.header.description}
        </p>

        <LanguageSwitcher
          currentLocale={locale}
          label={dictionary.header.languageLabel}
          localeNames={dictionary.header.localeNames}
        />
      </header>

      <main className="flex-1">{children}</main>

      <footer className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-[var(--color-border)] pt-6">
        <p className="text-[0.72rem] text-[var(--color-text-faint)]">
          © {new Date().getFullYear()} Viagest · Scout decide. Flow te acompaña.
        </p>
        <p className="text-[0.72rem] text-[var(--color-text-faint)]">
          Datos de vuelos provistos por Duffel · Precios orientativos
        </p>
      </footer>
    </div>
  );
}
