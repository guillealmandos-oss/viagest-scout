from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime
from time import perf_counter
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import UserFacingError
from app.core.i18n import AppLocale, render_message_items, t
from app.models.analytics import FeedbackEvent
from app.models.search import ItineraryRecord, SearchRecord, StrategyResultRecord
from app.models.user import LoyaltyProfile, TravelerProfile, User
from app.schemas.analytics import AnalyticsSummary
from app.schemas.common import ItineraryOption, RiskFlag, SearchCreateRequest, SearchResponse, StrategyCard
from app.schemas.searches import SearchListResponse, SearchSummaryItem
from app.services.explainer import StrategyExplainer
from app.services.migration_rules import MigrationRulesEngine
from app.services.normalizer import FlightOfferNormalizer
from app.services.offer_deduper import OfferDeduper
from app.services.offer_quality import filter_test_inventory, is_implausible_itinerary, uses_test_flight_inventory
from app.services.provider_health import ProviderHealthService
from app.services.providers.base import BaseFlightProvider
from app.services.providers.factory import get_flight_providers
from app.services.scoring import ScoringEngine
from app.services.stopover import StopoverAdvisor
from app.services.strategies import StrategyGenerator


class SearchOrchestrator:
    def __init__(self) -> None:
        self.providers = get_flight_providers()
        self.normalizer = FlightOfferNormalizer()
        self.deduper = OfferDeduper()
        self.provider_health = ProviderHealthService()
        self.migration_engine = MigrationRulesEngine()
        self.stopover_advisor = StopoverAdvisor()
        self.scoring_engine = ScoringEngine()
        self.strategy_generator = StrategyGenerator()
        self.explainer = StrategyExplainer()

    async def execute_search(self, db: Session, payload: SearchCreateRequest, locale: AppLocale) -> SearchResponse:
        user = self._get_or_create_user(db, payload)
        traveler_record = self._create_traveler_profile(db, user.id, payload)
        self._replace_loyalty_profiles(db, user.id, payload)

        fetch_result = await self._fetch_offers(payload)
        if not fetch_result["offers"]:
            db.rollback()
            self.provider_health.record_results(
                db,
                search_id=None,
                provider_reports=fetch_result["provider_reports"],
            )
            db.commit()
            raise UserFacingError("error.providers_unavailable", status_code=502)

        itineraries = self.normalizer.normalize(fetch_result["offers"], locale)
        itineraries = self.deduper.dedupe(
            itineraries,
            provider_priority=fetch_result["providers_attempted"],
        )
        assumptions: list[dict] = list(fetch_result["assumptions"])
        if uses_test_flight_inventory():
            assumptions.append(
                {
                    "scope": "provider",
                    "rule": "test inventory",
                    "rule_key": "provider.assumption.test_inventory.rule",
                    "confidence": "high",
                    "note": "sandbox",
                    "note_key": "provider.assumption.test_inventory.note",
                }
            )
            itineraries, removed_implausible = filter_test_inventory(itineraries)
            if removed_implausible:
                assumptions.append(
                    {
                        "scope": "provider",
                        "rule": "filtered synthetic offers",
                        "rule_key": "provider.assumption.test_inventory.rule",
                        "confidence": "medium",
                        "note": f"Se descartaron {removed_implausible} ofertas con itinerario no vendible (directo imposible o precio incoherente).",
                        "note_key": "provider.assumption.test_inventory.note",
                    }
                )
        if not itineraries:
            self.provider_health.record_results(
                db,
                search_id=None,
                provider_reports=fetch_result["provider_reports"],
            )
            db.commit()
            raise UserFacingError("error.no_itineraries_found", status_code=502)

        cheapest_price = min(item.total_price for item in itineraries)
        for itinerary in itineraries:
            if uses_test_flight_inventory() and is_implausible_itinerary(itinerary):
                itinerary.risk_flags.append(
                    RiskFlag(
                        code="synthetic_inventory",
                        severity="high",
                        message_key="risk.synthetic_inventory",
                    )
                )
            migration = self.migration_engine.assess(itinerary, payload.traveler_profile)
            itinerary.risk_flags.extend(migration.risk_flags)
            itinerary.raw_payload["migration_note_items"] = migration.migration_note_items
            itinerary.migration_notes = render_message_items(
                locale,
                migration.migration_note_items,
                fallback=migration.migration_notes,
            )
            opportunity_items = self.stopover_advisor.annotate(itinerary, cheapest_price)
            itinerary.raw_payload["opportunity_note_items"] = opportunity_items
            itinerary.opportunity_notes = render_message_items(locale, opportunity_items)
            assumptions.extend(migration.assumptions)

        self.scoring_engine.score_itineraries(
            itineraries,
            payload.search,
            payload.traveler_profile,
            payload.loyalty_profiles,
        )
        for itinerary in itineraries:
            for flag in itinerary.risk_flags:
                if flag.message_key:
                    flag.message = t(locale, flag.message_key, **flag.message_params)

        strategies_raw = self.strategy_generator.generate(itineraries, payload.search)
        strategies: list[StrategyCard] = []
        for strategy in strategies_raw:
            title = t(locale, strategy["title_key"])
            recommendation_badge = t(locale, strategy["recommendation_badge_key"])
            tradeoffs = render_message_items(locale, strategy["tradeoffs"])
            opportunity_notes = render_message_items(
                locale,
                strategy["opportunity_notes"],
                fallback=strategy["itinerary"].opportunity_notes,
            )
            explanation = await self.explainer.explain_strategy(
                locale=locale,
                strategy_type=strategy["strategy_type"],
                itinerary=strategy["itinerary"],
                tradeoffs=strategy["tradeoffs"],
                opportunity_notes=strategy["opportunity_notes"],
            )
            strategies.append(
                StrategyCard(
                    strategy_type=strategy["strategy_type"],
                    title=title,
                    recommendation_badge=recommendation_badge,
                    total_score=strategy["total_score"],
                    explanation=explanation,
                    tradeoffs=tradeoffs,
                    opportunity_notes=opportunity_notes,
                    score_breakdown=strategy["score_breakdown"],
                    itinerary=strategy["itinerary"],
                    is_recommended=strategy["is_recommended"],
                )
            )

        summary = await self.explainer.build_summary(locale, strategies)
        deduped_assumptions = self._dedupe_assumptions(assumptions)
        search_record = self._persist_search(
            db=db,
            payload=payload,
            locale=locale,
            user_id=user.id,
            provider_name=", ".join(fetch_result["providers_succeeded"]),
            summary=summary,
            assumptions=deduped_assumptions,
            itineraries=itineraries,
            strategy_payloads=strategies_raw,
            strategies=strategies,
        )
        self.provider_health.record_results(
            db,
            search_id=search_record.id,
            provider_reports=fetch_result["provider_reports"],
        )
        self._record_event(
            db,
            event_name="search_created",
            search_id=search_record.id,
            payload={
                "origin": payload.search.origin,
                "destination": payload.search.destination,
                "providers": fetch_result["providers_succeeded"],
                "traveler_profile_id": traveler_record.id,
                "locale": locale,
            },
        )
        db.commit()
        db.refresh(search_record)
        return self._to_response(search_record, locale)

    def list_searches(self, db: Session, locale: AppLocale) -> SearchListResponse:
        records = db.scalars(
            select(SearchRecord)
            .order_by(SearchRecord.created_at.desc())
            .limit(20)
            .options(
                selectinload(SearchRecord.itineraries),
                selectinload(SearchRecord.strategies).selectinload(StrategyResultRecord.itinerary),
            )
        ).all()
        items = [
            SearchSummaryItem(
                search_id=record.id,
                origin=record.origin,
                destination=record.destination,
                provider_name=record.provider_name,
                created_at=record.created_at,
                summary=self._to_response(record, locale).summary,
            )
            for record in records
        ]
        return SearchListResponse(items=items)

    def get_search(self, db: Session, search_id: str, locale: AppLocale) -> SearchResponse | None:
        statement = (
            select(SearchRecord)
            .where(SearchRecord.id == search_id)
            .options(
                selectinload(SearchRecord.itineraries),
                selectinload(SearchRecord.strategies).selectinload(StrategyResultRecord.itinerary),
            )
        )
        record = db.scalar(statement)
        if record is None:
            return None
        return self._to_response(record, locale)

    def record_event(
        self,
        db: Session,
        *,
        event_name: str,
        actor: str,
        strategy_type: str | None,
        search_id: str | None,
        payload: dict,
        free_text: str | None,
    ) -> None:
        self._record_event(
            db,
            event_name=event_name,
            actor=actor,
            strategy_type=strategy_type,
            search_id=search_id,
            payload=payload,
            free_text=free_text,
        )
        db.commit()

    def get_analytics_summary(self, db: Session) -> AnalyticsSummary:
        total_searches = db.scalar(select(func.count()).select_from(SearchRecord)) or 0
        total_events = db.scalar(select(func.count()).select_from(FeedbackEvent)) or 0
        saved_recommendations = db.scalar(
            select(func.count()).select_from(FeedbackEvent).where(FeedbackEvent.event_name == "recommendation_saved")
        ) or 0
        feedback_submissions = db.scalar(
            select(func.count()).select_from(FeedbackEvent).where(FeedbackEvent.event_name == "feedback_submitted")
        ) or 0
        strategy_open_events = db.scalar(
            select(func.count()).select_from(FeedbackEvent).where(FeedbackEvent.event_name == "strategy_opened")
        ) or 0

        recent_feedback_records = db.scalars(
            select(FeedbackEvent)
            .where(
                FeedbackEvent.event_name == "feedback_submitted",
                FeedbackEvent.free_text.is_not(None),
            )
            .order_by(FeedbackEvent.created_at.desc())
            .limit(5)
        ).all()

        recent_provider_issue_records = db.scalars(
            select(FeedbackEvent)
            .where(
                FeedbackEvent.event_name == "provider_search_result",
                FeedbackEvent.free_text.is_not(None),
            )
            .order_by(FeedbackEvent.created_at.desc())
            .limit(3)
        ).all()

        return AnalyticsSummary(
            total_searches=total_searches,
            total_events=total_events,
            saved_recommendations=saved_recommendations,
            feedback_submissions=feedback_submissions,
            strategy_open_events=strategy_open_events,
            recent_feedback=[
                {
                    "event_name": record.event_name,
                    "search_id": record.search_id,
                    "text": record.free_text,
                    "created_at": record.created_at.isoformat(),
                }
                for record in recent_feedback_records
            ],
            recent_provider_issues=[
                {
                    "event_name": record.event_name,
                    "search_id": record.search_id,
                    "text": record.free_text,
                    "created_at": record.created_at.isoformat(),
                }
                for record in recent_provider_issue_records
            ],
        )

    def get_provider_health_summary(self, db: Session):
        return self.provider_health.get_summary(db)

    async def _fetch_offers(self, payload: SearchCreateRequest) -> dict:
        provider_tasks = [self._fetch_from_provider(provider, payload) for provider in self.providers]
        results = await asyncio.gather(*provider_tasks, return_exceptions=True)

        successful_offers: list[dict] = []
        successful_provider_names: list[str] = []
        failed_provider_messages: list[str] = []
        assumptions: list[dict] = []
        provider_reports: list[dict] = []

        for result in results:
            if isinstance(result, Exception):
                continue

            provider_name = result["provider_name"]
            offers = result["offers"]
            provider_reports.append(result["report"])

            if result["report"]["success"]:
                successful_provider_names.append(provider_name)
                successful_offers.extend(offers)
                assumptions.append(
                    {
                        "scope": "provider",
                        "rule": f"{provider_name} source active",
                        "rule_key": "provider.assumption.active.rule",
                        "rule_params": {"provider": provider_name.title()},
                        "confidence": "high",
                        "note": f"{provider_name.title()} devolvio {len(offers)} ofertas para esta busqueda.",
                        "note_key": "provider.assumption.active.note",
                        "note_params": {
                            "provider": provider_name.title(),
                            "offer_count": len(offers),
                        },
                    }
                )
            else:
                failed_provider_messages.append(result["report"]["error_message"])
                assumptions.append(
                    {
                        "scope": "provider",
                        "rule": "provider partial failure",
                        "rule_key": "provider.assumption.partial_failure.rule",
                        "confidence": "medium",
                        "note": result["report"]["error_message"],
                        "note_key": "provider.assumption.partial_failure.note",
                    }
                )

        return {
            "offers": successful_offers,
            "assumptions": assumptions,
            "providers_attempted": [provider.provider_name for provider in self.providers],
            "providers_succeeded": successful_provider_names,
            "provider_reports": provider_reports,
            "failed_provider_messages": failed_provider_messages,
        }

    async def _fetch_from_provider(self, provider: BaseFlightProvider, payload: SearchCreateRequest) -> dict:
        started_at = perf_counter()
        try:
            offers = await provider.search_offers(payload.search)
            latency_ms = round((perf_counter() - started_at) * 1000, 2)
            metadata = provider.get_last_request_metadata()
            return {
                "provider_name": provider.provider_name,
                "offers": offers,
                "report": {
                    "provider_name": provider.provider_name,
                    "success": True,
                    "latency_ms": latency_ms,
                    "offer_count": len(offers),
                    "error_message": None,
                    "external_request_id": metadata.get("external_request_id"),
                    "external_correlation_id": metadata.get("external_correlation_id"),
                },
            }
        except Exception as exc:
            latency_ms = round((perf_counter() - started_at) * 1000, 2)
            error_message = f"{provider.provider_name.title()} search failed: {exc}"
            metadata = provider.get_last_request_metadata()
            return {
                "provider_name": provider.provider_name,
                "offers": [],
                "report": {
                    "provider_name": provider.provider_name,
                    "success": False,
                    "latency_ms": latency_ms,
                    "offer_count": 0,
                    "error_message": error_message,
                    "external_request_id": metadata.get("external_request_id"),
                    "external_correlation_id": metadata.get("external_correlation_id"),
                },
            }

    def _get_or_create_user(self, db: Session, payload: SearchCreateRequest) -> User:
        if payload.user.email:
            existing = db.scalar(select(User).where(User.email == payload.user.email))
            if existing:
                existing.display_name = payload.user.display_name or existing.display_name
                existing.is_demo = False
                db.flush()
                return existing

        user = User(
            email=payload.user.email,
            display_name=payload.user.display_name,
            is_demo=payload.user.email is None,
        )
        db.add(user)
        db.flush()
        return user

    def _create_traveler_profile(self, db: Session, user_id: str, payload: SearchCreateRequest) -> TravelerProfile:
        traveler = TravelerProfile(
            user_id=user_id,
            nationality=payload.traveler_profile.nationality,
            residence_country=payload.traveler_profile.residence_country,
            checked_bag_required=payload.traveler_profile.checked_bag_required,
            max_stops=payload.traveler_profile.max_stops,
            travel_priority=payload.traveler_profile.travel_priority,
            stopover_interest=payload.traveler_profile.stopover_interest,
            risk_tolerance=payload.traveler_profile.risk_tolerance,
            valid_visas_csv=",".join(payload.traveler_profile.valid_visas),
        )
        db.add(traveler)
        db.flush()
        return traveler

    def _replace_loyalty_profiles(self, db: Session, user_id: str, payload: SearchCreateRequest) -> None:
        for profile in db.scalars(select(LoyaltyProfile).where(LoyaltyProfile.user_id == user_id)).all():
            db.delete(profile)
        db.flush()
        for profile in payload.loyalty_profiles:
            db.add(
                LoyaltyProfile(
                    user_id=user_id,
                    program_name=profile.program_name,
                    balance=profile.balance,
                    bank_name=profile.bank_name,
                    transfer_partners_csv=",".join(profile.transfer_partners),
                )
            )
        db.flush()

    def _persist_search(
        self,
        *,
        db: Session,
        payload: SearchCreateRequest,
        locale: AppLocale,
        user_id: str,
        provider_name: str,
        summary: str,
        assumptions: list[dict],
        itineraries,
        strategy_payloads: list[dict],
        strategies: list[StrategyCard],
    ) -> SearchRecord:
        search_record = SearchRecord(
            user_id=user_id,
            origin=payload.search.origin,
            destination=payload.search.destination,
            departure_date=payload.search.departure_date.isoformat(),
            return_date=payload.search.return_date.isoformat() if payload.search.return_date else None,
            flexible_days=payload.search.flexible_days,
            budget_usd=payload.search.budget_usd,
            passengers=payload.search.passengers,
            cabin_class=payload.search.cabin_class,
            checked_bag_required=payload.search.checked_bag_required,
            stopover_interest=payload.search.stopover_interest,
            travel_priority=payload.search.preferred_strategy,
            provider_name=provider_name,
            content_locale=locale,
            status="completed",
            summary_text=summary,
            assumptions_json=assumptions,
        )
        db.add(search_record)
        db.flush()

        itinerary_map: dict[str, ItineraryRecord] = {}
        for itinerary in itineraries:
            itinerary_record = ItineraryRecord(
                search_id=search_record.id,
                provider_offer_id=itinerary.provider_offer_id,
                itinerary_type=itinerary.title,
                total_price=itinerary.total_price,
                currency=itinerary.currency,
                total_duration_minutes=itinerary.total_duration_minutes,
                stops_count=itinerary.stops_count,
                baggage_included=itinerary.baggage_included,
                airlines_csv=",".join(itinerary.airlines),
                route_summary=itinerary.route_summary,
                raw_json=itinerary.raw_payload,
                normalized_json=itinerary.model_dump(mode="json"),
                dimension_scores_json=itinerary.score_breakdown,
                risk_flags_json=[flag.model_dump() for flag in itinerary.risk_flags],
            )
            db.add(itinerary_record)
            db.flush()
            itinerary_map[itinerary.id] = itinerary_record

        for strategy, strategy_payload in zip(strategies, strategy_payloads, strict=False):
            itinerary_record = itinerary_map[strategy.itinerary.id]
            db.add(
                StrategyResultRecord(
                    search_id=search_record.id,
                    itinerary_id=itinerary_record.id,
                    strategy_type=strategy.strategy_type,
                    title=strategy_payload["title_key"],
                    recommendation_badge=strategy_payload["recommendation_badge_key"],
                    total_score=strategy.total_score,
                    explanation_text=strategy.explanation,
                    tradeoffs_json=strategy_payload["tradeoffs"],
                    opportunity_notes_json=strategy_payload["opportunity_notes"],
                    score_breakdown_json=strategy.score_breakdown,
                    is_recommended=strategy.is_recommended,
                )
            )
        db.flush()
        return search_record

    def _to_response(self, record: SearchRecord, locale: AppLocale) -> SearchResponse:
        strategies: list[StrategyCard] = []
        for strategy_record in sorted(record.strategies, key=lambda item: item.strategy_type):
            itinerary_payload = self._localized_itinerary(strategy_record.itinerary, locale)
            tradeoffs = self._localized_tradeoffs(locale, strategy_record.tradeoffs_json)
            opportunity_notes = self._localized_opportunity_notes(
                locale,
                strategy_record.opportunity_notes_json,
                fallback=itinerary_payload.opportunity_notes,
            )
            title = self._localized_strategy_label(
                locale,
                strategy_record.title,
                strategy_record.strategy_type,
                label_kind="title",
            )
            recommendation_badge = self._localized_strategy_label(
                locale,
                strategy_record.recommendation_badge,
                strategy_record.strategy_type,
                label_kind="badge",
            )
            explanation = self.explainer.render_persisted_explanation(
                locale=locale,
                strategy_type=strategy_record.strategy_type,
                itinerary=itinerary_payload,
                tradeoffs=tradeoffs,
                opportunity_notes=opportunity_notes or itinerary_payload.opportunity_notes,
                stored_explanation=strategy_record.explanation_text,
                stored_locale=record.content_locale,
            )
            strategies.append(
                StrategyCard(
                    strategy_type=strategy_record.strategy_type,
                    title=title,
                    recommendation_badge=recommendation_badge,
                    total_score=strategy_record.total_score,
                    explanation=explanation,
                    tradeoffs=tradeoffs,
                    opportunity_notes=opportunity_notes,
                    score_breakdown=strategy_record.score_breakdown_json,
                    itinerary=itinerary_payload,
                    is_recommended=strategy_record.is_recommended,
                )
            )
        created_at = record.created_at.isoformat() if record.created_at else datetime.utcnow().isoformat()
        return SearchResponse(
            search_id=record.id,
            provider_name=record.provider_name,
            summary=self.explainer.render_persisted_summary(
                locale,
                strategies,
                stored_summary=record.summary_text,
                stored_locale=record.content_locale,
            ),
            assumptions=[self._localized_assumption(locale, assumption) for assumption in record.assumptions_json],
            strategies=strategies,
            created_at=created_at,
        )

    def _localized_assumption(self, locale: AppLocale, assumption: dict) -> dict:
        localized = dict(assumption)
        if not assumption.get("rule_key") or not assumption.get("note_key"):
            localized.update(self._backfill_assumption_metadata(assumption))
        rule_key = localized.get("rule_key")
        note_key = localized.get("note_key")
        if rule_key:
            localized["rule"] = t(locale, rule_key, **(localized.get("rule_params") or {}))
        if note_key:
            localized["note"] = t(locale, note_key, **(localized.get("note_params") or {}))
        return localized

    def _localized_itinerary(self, itinerary_record: ItineraryRecord, locale: AppLocale) -> ItineraryOption:
        payload = dict(itinerary_record.normalized_json)
        raw_payload = payload.get("raw_payload") or itinerary_record.raw_json or {}

        title_key = raw_payload.get("title_key")
        if title_key:
            payload["title"] = t(locale, title_key, **raw_payload.get("title_params", {}))

        flexibility_code = raw_payload.get("flexibility_code") or self._backfill_flexibility_code(
            raw_payload.get("flexibility_label") or payload.get("flexibility_label", ""),
            itinerary_record,
        )
        flexibility_key = raw_payload.get("flexibility_label_key")
        if flexibility_code:
            payload["flexibility_label"] = t(locale, f"provider.flexibility.{flexibility_code}")
        elif flexibility_key:
            payload["flexibility_label"] = t(locale, flexibility_key, **raw_payload.get("flexibility_label_params", {}))

        risk_flags_source = itinerary_record.risk_flags_json or payload.get("risk_flags", [])
        localized_flags: list[RiskFlag] = []
        for risk_flag in risk_flags_source:
            message_key = risk_flag.get("message_key")
            message_params = risk_flag.get("message_params") or {}
            if not message_key:
                message_key, message_params = self._backfill_risk_flag_metadata(risk_flag)
            localized_flags.append(
                RiskFlag(
                    code=risk_flag["code"],
                    severity=risk_flag["severity"],
                    message=t(locale, message_key, **message_params) if message_key else risk_flag["message"],
                    message_key=message_key,
                    message_params=message_params,
                )
            )
        payload["risk_flags"] = [flag.model_dump() for flag in localized_flags]

        payload["migration_notes"] = render_message_items(
            locale,
            raw_payload.get("migration_note_items", self._backfill_migration_note_items(payload.get("migration_notes", []))),
            fallback=payload.get("migration_notes", []),
        )
        payload["opportunity_notes"] = render_message_items(
            locale,
            raw_payload.get(
                "opportunity_note_items",
                self._backfill_opportunity_items(payload.get("opportunity_notes", [])),
            ),
            fallback=payload.get("opportunity_notes", []),
        )

        return ItineraryOption.model_validate(payload)

    def _localized_strategy_label(
        self,
        locale: AppLocale,
        stored_value: str,
        strategy_type: str,
        *,
        label_kind: Literal["title", "badge"],
    ) -> str:
        expected_prefix = f"strategy.{label_kind}."
        if stored_value.startswith(expected_prefix):
            return t(locale, stored_value)
        return t(locale, f"strategy.{label_kind}.{strategy_type}")

    def _localized_tradeoffs(self, locale: AppLocale, values: list) -> list[str]:
        return render_message_items(locale, self._backfill_tradeoff_items(values), fallback=values if isinstance(values, list) else [])

    def _localized_opportunity_notes(self, locale: AppLocale, values: list, fallback: list[str]) -> list[str]:
        return render_message_items(locale, self._backfill_opportunity_items(values), fallback=fallback)

    def _backfill_assumption_metadata(self, assumption: dict) -> dict:
        metadata: dict[str, dict | str] = {}
        rule = assumption.get("rule")
        note = assumption.get("note", "")
        if rule == "US sterile transit":
            metadata["rule_key"] = "migration.assumption.us.rule"
            metadata["note_key"] = "migration.assumption.us.note"
        elif rule == "Canada transit":
            metadata["rule_key"] = "migration.assumption.canada.rule"
            metadata["note_key"] = "migration.assumption.canada.note"
        elif rule == "UK airside transit":
            metadata["rule_key"] = "migration.assumption.uk.rule"
            metadata["note_key"] = "migration.assumption.uk.note"
        elif rule == "provider partial failure":
            metadata["rule_key"] = "provider.assumption.partial_failure.rule"
            metadata["note_key"] = "provider.assumption.partial_failure.note"
        elif isinstance(rule, str) and rule.endswith("source active"):
            provider_match = re.match(r"(?P<provider>[a-zA-Z]+) source active", rule)
            note_match = re.match(r"(?P<provider>[A-Za-z]+) devolvio (?P<count>\d+) ofertas", note)
            if provider_match:
                provider_name = provider_match.group("provider").title()
                metadata["rule_key"] = "provider.assumption.active.rule"
                metadata["rule_params"] = {"provider": provider_name}
                metadata["note_key"] = "provider.assumption.active.note"
                metadata["note_params"] = {
                    "provider": provider_name,
                    "offer_count": int(note_match.group("count")) if note_match else 0,
                }
        return metadata

    def _backfill_flexibility_code(self, label: str, itinerary_record: ItineraryRecord) -> str | None:
        normalized = label.lower()
        if itinerary_record.raw_json.get("provider_name") == "amadeus" and "reglas" in normalized:
            return None
        if "total" in normalized or "premium" in normalized or "fully" in normalized:
            return "total"
        if "semi" in normalized:
            return "semi"
        if "reembolsable" in normalized or "refund" in normalized:
            return "partial_refund"
        if "basic" in normalized or "basica" in normalized:
            return "basic"
        return None

    def _backfill_risk_flag_metadata(self, risk_flag: dict) -> tuple[str | None, dict]:
        code = risk_flag.get("code")
        message = risk_flag.get("message", "")
        if code == "self_transfer":
            return "risk.self_transfer", {}
        if code == "missing_baggage":
            return "risk.missing_baggage", {}
        if code == "tight_connection":
            matched = re.search(r"en (?P<airport>[A-Z]{3}).*?\((?P<minutes>\d+) min\)", message)
            if matched:
                return "risk.tight_connection", {
                    "airport": matched.group("airport"),
                    "minutes": int(matched.group("minutes")),
                }
        if code == "us_transit_authorization":
            return "migration.flag.us_transit_authorization", {}
        if code == "canada_transit_review":
            return "migration.flag.canada_transit_review", {}
        if code == "uk_transit_review":
            return "migration.flag.uk_transit_review", {}
        return None, {}

    def _backfill_tradeoff_items(self, values: list) -> list:
        if any(isinstance(value, dict) and value.get("key") for value in values):
            return values

        items: list[dict] = []
        for value in values:
            if not isinstance(value, str):
                continue
            premium_match = re.search(r"USD (?P<delta>\d+)", value)
            if premium_match and "premium" in value.lower():
                items.append({"key": "tradeoff.price_premium", "params": {"delta": int(premium_match.group("delta"))}})
            elif "mas escalas" in value.lower():
                items.append({"key": "tradeoff.multiple_stops", "params": {}})
            elif "equipaje" in value.lower():
                items.append({"key": "tradeoff.no_checked_baggage", "params": {}})
            elif "riesgo alto" in value.lower():
                items.append({"key": "tradeoff.high_risk", "params": {}})
            elif "puerta a puerta" in value.lower():
                items.append({"key": "tradeoff.long_duration", "params": {}})
            elif "good overall balance" in value.lower() or "buen equilibrio general" in value.lower():
                items.append({"key": "tradeoff.balanced_default", "params": {}})
        return items or values

    def _backfill_opportunity_items(self, values: list) -> list:
        if any(isinstance(value, dict) and value.get("key") for value in values):
            return values

        items: list[dict] = []
        for value in values:
            if not isinstance(value, str):
                continue
            low_delta_match = re.search(
                r"Agregar (?P<airport>[A-Z]{3}).*?USD (?P<delta>\d+)|Adding (?P<airport_en>[A-Z]{3}).*?USD (?P<delta_en>\d+)",
                value,
            )
            if low_delta_match:
                airport = low_delta_match.group("airport") or low_delta_match.group("airport_en")
                delta = low_delta_match.group("delta") or low_delta_match.group("delta_en")
                items.append({"key": "stopover.low_delta", "params": {"airport": airport, "delta": int(delta)}})
                continue

            experience_match = re.search(r"^(?P<airport>[A-Z]{3}) .*stopover", value)
            if experience_match:
                items.append({"key": "stopover.experience", "params": {"airport": experience_match.group("airport")}})
        return items or values

    def _backfill_migration_note_items(self, values: list[str]) -> list:
        items: list[dict] = []
        for value in values:
            normalized = value.lower()
            if "ee.uu" in normalized or "esta" in normalized:
                items.append({"key": "migration.note.us_avoid", "params": {}})
            elif "canada" in normalized:
                items.append({"key": "migration.note.canada_review", "params": {}})
            elif "reino unido" in normalized or "uk" in normalized:
                items.append({"key": "migration.note.uk_review", "params": {}})
        return items or values

    def _record_event(
        self,
        db: Session,
        *,
        event_name: str,
        search_id: str | None = None,
        actor: str = "anonymous",
        strategy_type: str | None = None,
        payload: dict | None = None,
        free_text: str | None = None,
    ) -> None:
        db.add(
            FeedbackEvent(
                search_id=search_id,
                event_name=event_name,
                actor=actor,
                strategy_type=strategy_type,
                payload_json=payload or {},
                free_text=free_text,
            )
        )
        db.flush()

    def _dedupe_assumptions(self, assumptions: list[dict]) -> list[dict]:
        seen: set[str] = set()
        unique: list[dict] = []
        for assumption in assumptions:
            key = json.dumps(assumption, sort_keys=True, ensure_ascii=False)
            if key in seen:
                continue
            seen.add(key)
            unique.append(assumption)
        return unique
