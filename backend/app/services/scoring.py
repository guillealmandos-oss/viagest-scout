from __future__ import annotations

from app.schemas.common import ItineraryOption, LoyaltyProfileInput, RiskFlag, SearchRequestInput, TravelerProfileInput


class ScoringEngine:
    def score_itineraries(
        self,
        itineraries: list[ItineraryOption],
        search_input: SearchRequestInput,
        traveler: TravelerProfileInput,
        loyalty_profiles: list[LoyaltyProfileInput],
    ) -> list[ItineraryOption]:
        if not itineraries:
            return []

        cheapest_price = min(item.total_price for item in itineraries)
        max_price = max(item.total_price for item in itineraries)
        fastest_duration = min(item.total_duration_minutes for item in itineraries)
        slowest_duration = max(item.total_duration_minutes for item in itineraries)
        highest_loyalty_balance = max((profile.balance for profile in loyalty_profiles), default=0)

        for itinerary in itineraries:
            risk_flags = list(itinerary.risk_flags)
            if itinerary.raw_payload.get("self_transfer"):
                risk_flags.append(
                    RiskFlag(
                        code="self_transfer",
                        severity="high",
                        message="Incluye self-transfer, con riesgo de re-check y perdida de proteccion entre boletos.",
                        message_key="risk.self_transfer",
                    )
                )

            for layover in itinerary.layovers:
                if layover.duration_minutes < 90:
                    risk_flags.append(
                        RiskFlag(
                            code="tight_connection",
                            severity="medium",
                            message=f"La conexion en {layover.airport} es ajustada ({layover.duration_minutes} min).",
                            message_key="risk.tight_connection",
                            message_params={"airport": layover.airport, "minutes": layover.duration_minutes},
                        )
                    )

            if search_input.checked_bag_required and not itinerary.baggage_included:
                risk_flags.append(
                    RiskFlag(
                        code="missing_baggage",
                        severity="medium",
                        message="No incluye equipaje despachado aunque el viajero lo necesita.",
                        message_key="risk.missing_baggage",
                    )
                )

            itinerary.risk_flags = risk_flags
            itinerary.score_breakdown = {
                "price": self._inverse_score(itinerary.total_price, cheapest_price, max_price),
                "duration": self._inverse_score(
                    itinerary.total_duration_minutes,
                    fastest_duration,
                    slowest_duration,
                ),
                "convenience": self._convenience_score(itinerary, traveler),
                "flexibility": self._flexibility_score(itinerary.flexibility_label),
                "experience": self._experience_score(itinerary, traveler),
                "miles": self._miles_score(itinerary, highest_loyalty_balance),
                "migration": self._migration_score(itinerary),
                "risk": self._risk_score(risk_flags, traveler),
            }
        return itineraries

    def _inverse_score(self, value: float, best: float, worst: float) -> float:
        if best == worst:
            return 100.0
        normalized = (value - best) / (worst - best)
        return round(max(10.0, 100.0 - (normalized * 90.0)), 2)

    def _convenience_score(self, itinerary: ItineraryOption, traveler: TravelerProfileInput) -> float:
        bag_component = 100.0 if itinerary.baggage_included or not traveler.checked_bag_required else 35.0
        stop_component = max(20.0, 100.0 - (itinerary.stops_count * 22.0))
        return round((bag_component * 0.5) + (stop_component * 0.5), 2)

    def _flexibility_score(self, label: str) -> float:
        normalized = label.lower()
        if "total" in normalized:
            return 100.0
        if "premium" in normalized or "flexible" in normalized:
            return 85.0
        if "semi" in normalized:
            return 65.0
        return 40.0

    def _experience_score(self, itinerary: ItineraryOption, traveler: TravelerProfileInput) -> float:
        stopover_bonus = 28.0 if any(layover.stopover_candidate for layover in itinerary.layovers) else 0.0
        interest_bonus = 10.0 if traveler.stopover_interest and stopover_bonus else 0.0
        airline_bonus = 12.0 if len(itinerary.airlines) == 1 else 4.0
        return round(min(100.0, 45.0 + stopover_bonus + interest_bonus + airline_bonus), 2)

    def _miles_score(self, itinerary: ItineraryOption, highest_loyalty_balance: int) -> float:
        premium_segment_bonus = 20.0 * sum(1 for segment in itinerary.segments if segment.cabin_class == "BUSINESS")
        loyalty_bonus = 15.0 if highest_loyalty_balance >= 25000 else 5.0 if highest_loyalty_balance else 0.0
        price_signal = 12.0 if itinerary.total_price >= 1100 else 0.0
        return round(min(100.0, 38.0 + premium_segment_bonus + loyalty_bonus + price_signal), 2)

    def _migration_score(self, itinerary: ItineraryOption) -> float:
        penalties = 15.0 * len(itinerary.migration_notes)
        return round(max(25.0, 100.0 - penalties), 2)

    def _risk_score(self, risk_flags: list[RiskFlag], traveler: TravelerProfileInput) -> float:
        severity_penalties = {"low": 6.0, "medium": 16.0, "high": 28.0}
        penalty = sum(severity_penalties[flag.severity] for flag in risk_flags)
        tolerance_bonus = {"low": 0.0, "medium": 5.0, "high": 10.0}[traveler.risk_tolerance]
        return round(max(15.0, min(100.0, 100.0 - penalty + tolerance_bonus)), 2)
