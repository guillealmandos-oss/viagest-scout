import type { Metadata } from "next";

import { DevelopmentBanner } from "@/components/development-banner";
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
        <div className="flex items-center gap-3.5">
          <div
            className="flex shrink-0 items-center justify-center"
            style={{
              width: 44,
              height: 44,
              background: "var(--color-gold)",
              borderRadius: "var(--radius-md)",
            }}
            aria-hidden
          >
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--color-gold-text)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
            </svg>
          </div>
          <p className="brand-wordmark">
            Viagest <span className="brand-wordmark-accent">Scout</span>
          </p>
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

      <DevelopmentBanner dictionary={dictionary} />

      <main className="flex-1">{children}</main>

      <footer className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-[var(--color-border)] pt-6">
        <p className="text-[0.72rem] text-[var(--color-text-faint)]">
          © {new Date().getFullYear()} Viagest · Scout decide. Flow te acompaña.
        </p>
        <p className="text-[0.72rem] text-[var(--color-text-faint)]">
          Demo en desarrollo · Los datos mostrados pueden no ser reales
        </p>
      </footer>
    </div>
  );
}
