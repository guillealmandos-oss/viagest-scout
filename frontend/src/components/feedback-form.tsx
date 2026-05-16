"use client";

import { useState } from "react";

import { AppDictionary } from "@/i18n/dictionary";
import { AppLocale } from "@/i18n/config";
import { postAnalyticsEvent } from "@/lib/api";

import { SectionCard } from "./section-card";

export function FeedbackForm({
  searchId,
  locale,
  dictionary,
}: {
  searchId: string;
  locale: AppLocale;
  dictionary: AppDictionary;
}) {
  const copy = dictionary.feedback;
  const [feedback, setFeedback] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "sent">("idle");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!feedback.trim()) {
      return;
    }

    setStatus("submitting");
    await postAnalyticsEvent({
      event_name: "feedback_submitted",
      search_id: searchId,
      actor: "beta-user",
      free_text: feedback.trim(),
      payload: { source: "search_result" },
    }, locale).catch(() => null);
    setStatus("sent");
    setFeedback("");
  }

  return (
    <SectionCard
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={copy.subtitle}
    >
      <form className="grid gap-4" onSubmit={handleSubmit}>
        <textarea
          className="field-textarea"
          onChange={(event) => setFeedback(event.target.value)}
          placeholder={copy.placeholder}
          value={feedback}
        />
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-[var(--color-text-muted)]">{copy.footer}</p>
          <button
            className="btn-primary px-5 py-3 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={status === "submitting"}
            type="submit"
          >
            {status === "submitting" ? copy.submitLoading : status === "sent" ? copy.submitSuccess : copy.submitIdle}
          </button>
        </div>
      </form>
    </SectionCard>
  );
}
