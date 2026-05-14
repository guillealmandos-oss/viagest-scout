export const SUPPORTED_LOCALES = ["es", "en"] as const;

export type AppLocale = (typeof SUPPORTED_LOCALES)[number];

export const DEFAULT_LOCALE: AppLocale = "es";
export const LOCALE_COOKIE_NAME = "viagest-locale";

export function isSupportedLocale(value: string): value is AppLocale {
  return SUPPORTED_LOCALES.includes(value as AppLocale);
}

export function normalizeLocale(value?: string | null): AppLocale {
  if (!value) {
    return DEFAULT_LOCALE;
  }

  const normalized = value.toLowerCase();
  if (normalized.startsWith("en")) {
    return "en";
  }
  if (normalized.startsWith("es")) {
    return "es";
  }
  return DEFAULT_LOCALE;
}

export function getLocaleFromPathname(pathname: string): AppLocale | null {
  const [, maybeLocale] = pathname.split("/");
  return maybeLocale && isSupportedLocale(maybeLocale) ? maybeLocale : null;
}
