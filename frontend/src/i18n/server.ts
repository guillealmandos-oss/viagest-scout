import { notFound } from "next/navigation";

import { AppDictionary, getDictionary } from "./dictionary";
import { AppLocale, isSupportedLocale } from "./config";

export function requireLocale(locale: string): AppLocale {
  if (!isSupportedLocale(locale)) {
    notFound();
  }
  return locale;
}

export function getLocaleDictionary(locale: string): { locale: AppLocale; dictionary: AppDictionary } {
  const normalizedLocale = requireLocale(locale);
  return {
    locale: normalizedLocale,
    dictionary: getDictionary(normalizedLocale),
  };
}
