import { ReactNode } from "react";

interface SectionCardProps {
  title: string;
  eyebrow?: string;
  subtitle?: string;
  children: ReactNode;
}

export function SectionCard({ title, eyebrow, subtitle, children }: SectionCardProps) {
  return (
    <section className="card p-6">
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      <div className="mt-2 space-y-1">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">{title}</h2>
        {subtitle ? (
          <p className="text-sm leading-6 text-[var(--color-text-muted)]">{subtitle}</p>
        ) : null}
      </div>
      <div className="mt-6">{children}</div>
    </section>
  );
}
