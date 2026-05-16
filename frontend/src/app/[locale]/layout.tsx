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
      <header className="card mb-8 flex flex-col gap-4 px-6 py-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="eyebrow">{dictionary.header.eyebrow}</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-[var(--color-text-primary)]">
            {dictionary.header.title}
          </h1>
          <p className="mt-2 max-w-xl text-sm leading-6 text-[var(--color-text-muted)]">
            {dictionary.header.description}
          </p>
        </div>
        <LanguageSwitcher
          currentLocale={locale}
          label={dictionary.header.languageLabel}
          localeNames={dictionary.header.localeNames}
        />
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
