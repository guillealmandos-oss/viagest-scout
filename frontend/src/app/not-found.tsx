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
      <div className="max-w-xl rounded-[2rem] border border-slate-200 bg-white p-10 text-center shadow-sm shadow-slate-200/50">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-600">{copy.eyebrow}</p>
        <h2 className="mt-3 text-3xl font-semibold text-slate-950">{copy.title}</h2>
        <p className="mt-4 text-sm leading-7 text-slate-600">{copy.description}</p>
        <Link
          className="mt-6 inline-flex rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          href={`/${locale}`}
        >
          {copy.cta}
        </Link>
      </div>
    </div>
  );
}
