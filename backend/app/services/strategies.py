from __future__ import annotations

from app.core.i18n import message_item
from app.schemas.common import ItineraryOption, SearchRequestInput


class StrategyGenerator:
    WEIGHTS = {
        "savings": {
            "price": 0.32,
            "duration": 0.14,
            "convenience": 0.15,
            "flexibility": 0.08,
            "experience": 0.06,
            "miles": 0.05,
            "migration": 0.10,
            "risk": 0.10,
        },
        "experience": {
            "price": 0.12,
            "duration": 0.10,
            "convenience": 0.12,
            "flexibility": 0.08,
            "experience": 0.28,
            "miles": 0.05,
            "migration": 0.10,
            "risk": 0.15,
        },
        "miles": {
            "price": 0.10,
            "duration": 0.08,
            "convenience": 0.10,
            "flexibility": 0.10,
            "experience": 0.08,
            "miles": 0.34,
            "migration": 0.08,
            "risk": 0.12,
        },
    }

    def generate(self, itineraries: list[ItineraryOption], search_input: SearchRequestInput) -> list[dict]:
        if not itineraries:
            return []

        selected: list[dict] = []
        used_ids: set[str] = set()
        cheapest_price = min(option.total_price for option in itineraries)

        for strategy_type in ("savings", "experience", "miles"):
            ranked = sorted(
                itineraries,
                key=lambda option: self._weighted_score(option.score_breakdown, self.WEIGHTS[strategy_type]),
                reverse=True,
            )
            choice = next((option for option in ranked if option.id not in used_ids), ranked[0])
            used_ids.add(choice.id)
            total_score = self._weighted_score(choice.score_breakdown, self.WEIGHTS[strategy_type])
            selected.append(
                {
                    "strategy_type": strategy_type,
                    "title_key": f"strategy.title.{strategy_type}",
                    "recommendation_badge_key": f"strategy.badge.{strategy_type}",
                    "total_score": total_score,
                    "tradeoffs": self._build_tradeoffs(choice, cheapest_price),
                    "opportunity_notes": list(choice.raw_payload.get("opportunity_note_items", choice.opportunity_notes)),
                    "score_breakdown": choice.score_breakdown,
                    "itinerary": choice,
                    "is_recommended": strategy_type == search_input.preferred_strategy,
                }
            )

        if not any(strategy["is_recommended"] for strategy in selected):
            best_strategy = max(selected, key=lambda strategy: strategy["total_score"])
            best_strategy["is_recommended"] = True
        return selected

    def _weighted_score(self, score_breakdown: dict[str, float], weights: dict[str, float]) -> float:
        return round(sum(score_breakdown[key] * weight for key, weight in weights.items()), 2)

    def _build_tradeoffs(self, itinerary: ItineraryOption, cheapest_price: float) -> list[dict]:
        tradeoffs: list[dict] = []
        if itinerary.total_price - cheapest_price > 150:
            tradeoffs.append(message_item("tradeoff.price_premium", delta=itinerary.total_price - cheapest_price))
        if itinerary.stops_count >= 2:
            tradeoffs.append(message_item("tradeoff.multiple_stops"))
        if not itinerary.baggage_included:
            tradeoffs.append(message_item("tradeoff.no_checked_baggage"))
        if any(flag.severity == "high" for flag in itinerary.risk_flags):
            tradeoffs.append(message_item("tradeoff.high_risk"))
        if itinerary.total_duration_minutes > 2000:
            tradeoffs.append(message_item("tradeoff.long_duration"))
        if not tradeoffs:
            tradeoffs.append(message_item("tradeoff.balanced_default"))
        return tradeoffs
