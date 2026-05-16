"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { getDictionary } from "@/i18n/dictionary";
import { DEFAULT_LOCALE, getLocaleFromPathname } from "@/i18n/config";

export default function NotFound() {
  const pathname = usePathname();
  const locale = getLocaleFromPathname(pathname) ?? DEFAULT_LOCALE;
  const copy = getDictionary(locale).notFound;

  return (
    <div className="flex min-h-[50vh] items-center justify-center">
      <div className="card max-w-xl p-10 text-center">
        <p className="eyebrow">{copy.eyebrow}</p>
        <h2 className="mt-3 text-3xl font-semibold text-[var(--color-text-primary)]">{copy.title}</h2>
        <p className="mt-4 text-sm leading-7 text-[var(--color-text-muted)]">{copy.description}</p>
        <Link className="btn-primary mt-6 px-5 py-3" href={`/${locale}`}>
          {copy.cta}
        </Link>
      </div>
    </div>
  );
}
