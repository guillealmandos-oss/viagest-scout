import { NextRequest, NextResponse } from "next/server";

import {
  DEFAULT_LOCALE,
  LOCALE_COOKIE_NAME,
  getLocaleFromPathname,
  normalizeLocale,
} from "@/i18n/config";

function getPreferredLocale(request: NextRequest) {
  const cookieLocale = request.cookies.get(LOCALE_COOKIE_NAME)?.value;
  if (cookieLocale) {
    return normalizeLocale(cookieLocale);
  }

  const acceptLanguage = request.headers.get("accept-language");
  return normalizeLocale(acceptLanguage ?? DEFAULT_LOCALE);
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/_next") || pathname.startsWith("/api") || pathname.includes(".")) {
    return NextResponse.next();
  }

  const localeFromPath = getLocaleFromPathname(pathname);
  if (localeFromPath) {
    const response = NextResponse.next();
    response.cookies.set(LOCALE_COOKIE_NAME, localeFromPath, { path: "/" });
    return response;
  }

  const locale = getPreferredLocale(request);
  const redirectUrl = request.nextUrl.clone();
  redirectUrl.pathname = `/${locale}${pathname === "/" ? "" : pathname}`;

  const response = NextResponse.redirect(redirectUrl);
  response.cookies.set(LOCALE_COOKIE_NAME, locale, { path: "/" });
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
