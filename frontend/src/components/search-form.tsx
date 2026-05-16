"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { createSearch } from "@/lib/api";
import { AppDictionary } from "@/i18n/dictionary";
import { AppLocale } from "@/i18n/config";
import { SearchPayload, TravelPriority } from "@/types/travel";

import { SectionCard } from "./section-card";

const today = new Date().toISOString().slice(0, 10);
const nextWeek = new Date(Date.now() + 1000 * 60 * 60 * 24 * 10).toISOString().slice(0, 10);

interface FormState {
  origin: string;
  destination: string;
  departureDate: string;
  returnDate: string;
  flexibleDays: string;
  budgetUsd: string;
  passengers: string;
  cabinClass: SearchPayload["search"]["cabin_class"];
  checkedBagRequired: boolean;
  stopoverInterest: boolean;
  preferredStrategy: TravelPriority;
  notes: string;
  email: string;
  displayName: string;
  nationality: string;
  residenceCountry: string;
  maxStops: string;
  riskTolerance: "low" | "medium" | "high";
  validVisas: string;
  loyaltyProgram: string;
  loyaltyBalance: string;
  loyaltyBank: string;
  transferPartners: string;
}

function buildInitialState(locale: AppLocale): FormState {
  return {
    origin: "MVD",
    destination: "NRT",
    departureDate: today,
    returnDate: nextWeek,
    flexibleDays: "2",
    budgetUsd: "1200",
    passengers: "1",
    cabinClass: "ECONOMY",
    checkedBagRequired: true,
    stopoverInterest: true,
    preferredStrategy: "experience",
    notes:
      locale === "es"
        ? "Quiero evitar conexiones que compliquen visa y si se puede sumar una ciudad, mejor."
        : "I want to avoid connections that create visa issues, and if we can add a city, even better.",
    email: "",
    displayName: "",
    nationality: "UY",
    residenceCountry: "UY",
    maxStops: "2",
    riskTolerance: "medium",
    validVisas: "",
    loyaltyProgram: "Smiles",
    loyaltyBalance: "28000",
    loyaltyBank: "Santander",
    transferPartners: "Gol, Air France",
  };
}

function splitCommaSeparated(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function buildPayload(state: FormState): SearchPayload {
  return {
    user: {
      email: state.email || undefined,
      display_name: state.displayName || undefined,
    },
    traveler_profile: {
      nationality: state.nationality.toUpperCase(),
      residence_country: state.residenceCountry.toUpperCase() || undefined,
      checked_bag_required: state.checkedBagRequired,
      max_stops: Number(state.maxStops),
      travel_priority: state.preferredStrategy,
      stopover_interest: state.stopoverInterest,
      risk_tolerance: state.riskTolerance,
      valid_visas: splitCommaSeparated(state.validVisas).map((visa) => visa.toUpperCase()),
    },
    loyalty_profiles: state.loyaltyProgram
      ? [
          {
            program_name: state.loyaltyProgram,
            balance: Number(state.loyaltyBalance || 0),
            bank_name: state.loyaltyBank || undefined,
            transfer_partners: splitCommaSeparated(state.transferPartners),
          },
        ]
      : [],
    search: {
      origin: state.origin.toUpperCase(),
      destination: state.destination.toUpperCase(),
      departure_date: state.departureDate,
      return_date: state.returnDate || undefined,
      flexible_days: Number(state.flexibleDays),
      budget_usd: state.budgetUsd ? Number(state.budgetUsd) : undefined,
      passengers: Number(state.passengers),
      cabin_class: state.cabinClass,
      checked_bag_required: state.checkedBagRequired,
      stopover_interest: state.stopoverInterest,
      preferred_strategy: state.preferredStrategy,
      notes: state.notes || undefined,
    },
  };
}

export function SearchForm({
  locale,
  dictionary,
}: {
  locale: AppLocale;
  dictionary: AppDictionary;
}) {
  const router = useRouter();
  const copy = dictionary.searchForm;
  const [formState, setFormState] = useState<FormState>(() => buildInitialState(locale));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fieldClassName = "field-input mt-2";

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setFormState((current) => ({ ...current, [key]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const payload = buildPayload(formState);
      const response = await createSearch(payload, locale);
      router.push(`/${locale}/search/${response.search_id}`);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : copy.errorFallback);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <SectionCard
      eyebrow={copy.eyebrow}
      title={copy.title}
      subtitle={copy.subtitle}
    >
      <form className="grid gap-6" onSubmit={handleSubmit}>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="field-label">
            {copy.fields.origin}
            <input className={fieldClassName} value={formState.origin} onChange={(event) => update("origin", event.target.value)} maxLength={3} />
          </label>
          <label className="field-label">
            {copy.fields.destination}
            <input className={fieldClassName} value={formState.destination} onChange={(event) => update("destination", event.target.value)} maxLength={3} />
          </label>
          <label className="field-label">
            {copy.fields.departureDate}
            <input className={fieldClassName} type="date" value={formState.departureDate} onChange={(event) => update("departureDate", event.target.value)} />
          </label>
          <label className="field-label">
            {copy.fields.returnDate}
            <input className={fieldClassName} type="date" value={formState.returnDate} onChange={(event) => update("returnDate", event.target.value)} />
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="field-label">
            {copy.fields.flexibleDays}
            <input className={fieldClassName} type="number" min={0} max={14} value={formState.flexibleDays} onChange={(event) => update("flexibleDays", event.target.value)} />
          </label>
          <label className="field-label">
            {copy.fields.budgetUsd}
            <input className={fieldClassName} type="number" min={0} value={formState.budgetUsd} onChange={(event) => update("budgetUsd", event.target.value)} />
          </label>
          <label className="field-label">
            {copy.fields.passengers}
            <input className={fieldClassName} type="number" min={1} max={9} value={formState.passengers} onChange={(event) => update("passengers", event.target.value)} />
          </label>
          <label className="field-label">
            {copy.fields.cabinClass}
            <select className={fieldClassName} value={formState.cabinClass} onChange={(event) => update("cabinClass", event.target.value as FormState["cabinClass"])}>
              <option value="ECONOMY">{copy.options.cabinClass.ECONOMY}</option>
              <option value="PREMIUM_ECONOMY">{copy.options.cabinClass.PREMIUM_ECONOMY}</option>
              <option value="BUSINESS">{copy.options.cabinClass.BUSINESS}</option>
              <option value="FIRST">{copy.options.cabinClass.FIRST}</option>
            </select>
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="field-label">
            {copy.fields.nationality}
            <input className={fieldClassName} value={formState.nationality} onChange={(event) => update("nationality", event.target.value)} maxLength={2} />
          </label>
          <label className="field-label">
            {copy.fields.residenceCountry}
            <input className={fieldClassName} value={formState.residenceCountry} onChange={(event) => update("residenceCountry", event.target.value)} maxLength={2} />
          </label>
          <label className="field-label">
            {copy.fields.riskTolerance}
            <select className={fieldClassName} value={formState.riskTolerance} onChange={(event) => update("riskTolerance", event.target.value as FormState["riskTolerance"])}>
              <option value="low">{copy.options.riskTolerance.low}</option>
              <option value="medium">{copy.options.riskTolerance.medium}</option>
              <option value="high">{copy.options.riskTolerance.high}</option>
            </select>
          </label>
          <label className="field-label">
            {copy.fields.preferredStrategy}
            <select className={fieldClassName} value={formState.preferredStrategy} onChange={(event) => update("preferredStrategy", event.target.value as TravelPriority)}>
              <option value="savings">{copy.options.preferredStrategy.savings}</option>
              <option value="balanced">{copy.options.preferredStrategy.balanced}</option>
              <option value="comfort">{copy.options.preferredStrategy.comfort}</option>
              <option value="experience">{copy.options.preferredStrategy.experience}</option>
              <option value="miles">{copy.options.preferredStrategy.miles}</option>
            </select>
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="field-label">
            {copy.fields.validVisas}
            <input className={fieldClassName} value={formState.validVisas} onChange={(event) => update("validVisas", event.target.value)} placeholder={copy.placeholders.validVisas} />
          </label>
          <label className="field-label">
            {copy.fields.maxStops}
            <input className={fieldClassName} type="number" min={0} max={4} value={formState.maxStops} onChange={(event) => update("maxStops", event.target.value)} />
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="field-label">
            {copy.fields.loyaltyProgram}
            <input className={fieldClassName} value={formState.loyaltyProgram} onChange={(event) => update("loyaltyProgram", event.target.value)} placeholder={copy.placeholders.loyaltyProgram} />
          </label>
          <label className="field-label">
            {copy.fields.loyaltyBalance}
            <input className={fieldClassName} type="number" min={0} value={formState.loyaltyBalance} onChange={(event) => update("loyaltyBalance", event.target.value)} />
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="field-label">
            {copy.fields.loyaltyBank}
            <input className={fieldClassName} value={formState.loyaltyBank} onChange={(event) => update("loyaltyBank", event.target.value)} placeholder={copy.placeholders.loyaltyBank} />
          </label>
          <label className="field-label">
            {copy.fields.transferPartners}
            <input className={fieldClassName} value={formState.transferPartners} onChange={(event) => update("transferPartners", event.target.value)} placeholder={copy.placeholders.transferPartners} />
          </label>
        </div>

        <label className="field-label">
          {copy.fields.notes}
          <textarea
            className={`${fieldClassName} min-h-28 resize-y`}
            value={formState.notes}
            onChange={(event) => update("notes", event.target.value)}
            placeholder={copy.placeholders.notes}
          />
        </label>

        <div className="panel-muted grid gap-3 p-4 md:grid-cols-2">
          <label className="flex items-start gap-3 text-sm text-slate-700">
            <input
              className="mt-1 size-4 rounded border-slate-300"
              type="checkbox"
              checked={formState.checkedBagRequired}
              onChange={(event) => update("checkedBagRequired", event.target.checked)}
            />
            {copy.toggles.checkedBagRequired}
          </label>
          <label className="flex items-start gap-3 text-sm text-slate-700">
            <input
              className="mt-1 size-4 rounded border-slate-300"
              type="checkbox"
              checked={formState.stopoverInterest}
              onChange={(event) => update("stopoverInterest", event.target.checked)}
            />
            {copy.toggles.stopoverInterest}
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="field-label">
            {copy.fields.email}
            <input className={fieldClassName} type="email" value={formState.email} onChange={(event) => update("email", event.target.value)} />
          </label>
          <label className="field-label">
            {copy.fields.displayName}
            <input className={fieldClassName} value={formState.displayName} onChange={(event) => update("displayName", event.target.value)} />
          </label>
        </div>

        {error ? <p className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="max-w-2xl text-sm leading-6 text-slate-600">
            {copy.footer}
          </p>
          <button
            className="btn-brand px-6 py-3 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? copy.submitLoading : copy.submitIdle}
          </button>
        </div>
      </form>
    </SectionCard>
  );
}
