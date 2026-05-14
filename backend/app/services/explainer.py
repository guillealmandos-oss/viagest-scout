from __future__ import annotations

import httpx

from app.core.config import get_settings
from app.core.i18n import AppLocale, render_message_items, t
from app.schemas.common import ItineraryOption, StrategyCard


class StrategyExplainer:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def explain_strategy(
        self,
        *,
        locale: AppLocale,
        strategy_type: str,
        itinerary: ItineraryOption,
        tradeoffs: list[dict] | list[str],
        opportunity_notes: list[dict] | list[str],
    ) -> str:
        if not self.settings.openai_api_key:
            return self._fallback_explanation(locale, strategy_type, itinerary, tradeoffs, opportunity_notes)
        try:
            return await self._openai_explanation(locale, strategy_type, itinerary, tradeoffs, opportunity_notes)
        except Exception:
            return self._fallback_explanation(locale, strategy_type, itinerary, tradeoffs, opportunity_notes)

    async def build_summary(
        self,
        locale: AppLocale,
        strategies: list[StrategyCard],
        *,
        stored_summary: str | None = None,
        stored_locale: str | None = None,
    ) -> str:
        if stored_summary and stored_locale == locale:
            return stored_summary

        recommended = next((strategy for strategy in strategies if strategy.is_recommended), strategies[0])
        cheapest = min(strategies, key=lambda strategy: strategy.itinerary.total_price)
        experience = next(
            (strategy for strategy in strategies if strategy.strategy_type == "experience"),
            strategies[0],
        )
        experience_note = (
            experience.opportunity_notes[0].lower()
            if experience.opportunity_notes
            else t(locale, "explainer.summary.experience_default")
        )
        return t(
            locale,
            "explainer.summary",
            count=len(strategies),
            recommended_title=recommended.title.lower(),
            recommended_route=recommended.itinerary.route_summary,
            currency=cheapest.itinerary.currency,
            cheapest_price=cheapest.itinerary.total_price,
            experience_note=experience_note,
        )

    def render_persisted_summary(
        self,
        locale: AppLocale,
        strategies: list[StrategyCard],
        *,
        stored_summary: str | None = None,
        stored_locale: str | None = None,
    ) -> str:
        if stored_summary and stored_locale == locale:
            return stored_summary

        recommended = next((strategy for strategy in strategies if strategy.is_recommended), strategies[0])
        cheapest = min(strategies, key=lambda strategy: strategy.itinerary.total_price)
        experience = next(
            (strategy for strategy in strategies if strategy.strategy_type == "experience"),
            strategies[0],
        )
        experience_note = (
            experience.opportunity_notes[0].lower()
            if experience.opportunity_notes
            else t(locale, "explainer.summary.experience_default")
        )
        return t(
            locale,
            "explainer.summary",
            count=len(strategies),
            recommended_title=recommended.title.lower(),
            recommended_route=recommended.itinerary.route_summary,
            currency=cheapest.itinerary.currency,
            cheapest_price=cheapest.itinerary.total_price,
            experience_note=experience_note,
        )

    async def _openai_explanation(
        self,
        locale: AppLocale,
        strategy_type: str,
        itinerary: ItineraryOption,
        tradeoffs: list[dict] | list[str],
        opportunity_notes: list[dict] | list[str],
    ) -> str:
        localized_tradeoffs = render_message_items(locale, list(tradeoffs), fallback=list(tradeoffs))
        localized_opportunities = render_message_items(locale, list(opportunity_notes), fallback=list(opportunity_notes))
        localized_risks = [self._localize_risk_flag(locale, flag) for flag in itinerary.risk_flags]
        prompt_language = "Spanish" if locale == "es" else "English"
        prompt = (
            f"Act as a senior travel strategist and answer in {prompt_language}. "
            "Explain in 3 to 4 sentences why this strategy is valuable, mention one key tradeoff, "
            "and avoid inventing new migration rules.\n"
            f"Estrategia: {strategy_type}\n"
            f"Ruta: {itinerary.route_summary}\n"
            f"Precio: {itinerary.currency} {itinerary.total_price}\n"
            f"Duracion: {self._format_minutes(itinerary.total_duration_minutes)}\n"
            f"Riesgos: {localized_risks}\n"
            f"Tradeoffs: {localized_tradeoffs}\n"
            f"Oportunidades: {localized_opportunities}\n"
        )

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.settings.openai_model,
                    "temperature": 0.4,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You explain flight strategy recommendations clearly and conservatively.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    def _fallback_explanation(
        self,
        locale: AppLocale,
        strategy_type: str,
        itinerary: ItineraryOption,
        tradeoffs: list[dict] | list[str],
        opportunity_notes: list[dict] | list[str],
    ) -> str:
        headline = t(locale, f"explainer.headline.{strategy_type}")
        localized_tradeoffs = render_message_items(locale, list(tradeoffs), fallback=list(tradeoffs))
        localized_opportunities = render_message_items(locale, list(opportunity_notes), fallback=list(opportunity_notes))
        risk_note = (
            t(locale, "explainer.risk_watch", risk=self._localize_risk_flag(locale, itinerary.risk_flags[0]).lower())
            if itinerary.risk_flags
            else t(locale, "explainer.risk_none")
        )
        opportunity = localized_opportunities[0] if localized_opportunities else self._localize_cash_hint(locale, itinerary)
        tradeoff = localized_tradeoffs[0] if localized_tradeoffs else t(locale, "explainer.tradeoff_default")
        return t(
            locale,
            "explainer.body",
            headline=headline,
            opportunity=opportunity,
            risk_note=risk_note,
            tradeoff=tradeoff,
        )

    def render_persisted_explanation(
        self,
        *,
        locale: AppLocale,
        strategy_type: str,
        itinerary: ItineraryOption,
        tradeoffs: list[str],
        opportunity_notes: list[str],
        stored_explanation: str | None = None,
        stored_locale: str | None = None,
    ) -> str:
        if stored_explanation and stored_locale == locale:
            return stored_explanation
        return self._fallback_explanation(
            locale,
            strategy_type,
            itinerary,
            tradeoffs,
            opportunity_notes,
        )

    def _format_minutes(self, minutes: int) -> str:
        hours, remaining_minutes = divmod(minutes, 60)
        return f"{hours}h {remaining_minutes}m"

    def _localize_cash_hint(self, locale: AppLocale, itinerary: ItineraryOption) -> str:
        hint_key = itinerary.raw_payload.get("cash_miles_hint_key")
        if hint_key:
            return t(locale, hint_key, **itinerary.raw_payload.get("cash_miles_hint_params", {}))
        return itinerary.raw_payload.get("cash_miles_hint", "")

    def _localize_risk_flag(self, locale: AppLocale, flag) -> str:
        message_key = getattr(flag, "message_key", None)
        message_params = getattr(flag, "message_params", {}) or {}
        if message_key:
            return t(locale, message_key, **message_params)
        return flag.message
