"use client";

import { usePathname, useRouter } from "next/navigation";

import { AppLocale, LOCALE_COOKIE_NAME } from "@/i18n/config";

interface LanguageSwitcherProps {
  currentLocale: AppLocale;
  label: string;
  localeNames: Record<AppLocale, string>;
}

export function LanguageSwitcher({
  currentLocale,
  label,
  localeNames,
}: LanguageSwitcherProps) {
  const pathname = usePathname();
  const router = useRouter();

  function switchLocale(nextLocale: AppLocale) {
    const segments = pathname.split("/");
    if (segments.length > 1) {
      segments[1] = nextLocale;
    }

    document.cookie = `${LOCALE_COOKIE_NAME}=${nextLocale}; path=/; max-age=31536000`;
    router.push(segments.join("/") || `/${nextLocale}`);
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{label}</span>
      <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 p-1">
        {(["es", "en"] as const).map((locale) => (
          <button
            key={locale}
            className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
              locale === currentLocale
                ? "bg-slate-950 text-white"
                : "text-slate-600 hover:bg-white hover:text-slate-950"
            }`}
            onClick={() => switchLocale(locale)}
            type="button"
          >
            {localeNames[locale]}
          </button>
        ))}
      </div>
    </div>
  );
}
