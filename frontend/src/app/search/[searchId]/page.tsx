import { redirect } from "next/navigation";

import { DEFAULT_LOCALE } from "@/i18n/config";

export const dynamic = "force-dynamic";

export default async function SearchResultPage({
  params,
}: {
  params: Promise<{ searchId: string }>;
}) {
  const { searchId } = await params;
  redirect(`/${DEFAULT_LOCALE}/search/${searchId}`);
}
