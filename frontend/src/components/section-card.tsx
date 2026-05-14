import { ReactNode } from "react";

interface SectionCardProps {
  title: string;
  eyebrow?: string;
  subtitle?: string;
  children: ReactNode;
}

export function SectionCard({ title, eyebrow, subtitle, children }: SectionCardProps) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/50">
      {eyebrow ? <p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-600">{eyebrow}</p> : null}
      <div className="mt-2 space-y-1">
        <h2 className="text-xl font-semibold text-slate-950">{title}</h2>
        {subtitle ? <p className="text-sm leading-6 text-slate-600">{subtitle}</p> : null}
      </div>
      <div className="mt-6">{children}</div>
    </section>
  );
}
