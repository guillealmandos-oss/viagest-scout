import { AppDictionary } from "@/i18n/dictionary";

export function DevelopmentBanner({ dictionary }: { dictionary: AppDictionary }) {
  const copy = dictionary.developmentBanner;

  return (
    <div
      className="mb-6 rounded-2xl border border-[var(--color-gold-border)] bg-[rgba(201,168,76,0.08)] px-4 py-3 text-sm leading-6 text-[var(--color-text-body)]"
      role="status"
    >
      <p className="font-semibold text-[var(--color-gold)]">{copy.title}</p>
      <p className="mt-1 text-[var(--color-text-muted)]">{copy.body}</p>
    </div>
  );
}
