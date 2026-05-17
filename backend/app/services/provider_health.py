from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.i18n import DEFAULT_LOCALE, AppLocale
from app.models.analytics import FeedbackEvent
from app.schemas.analytics import ProviderHealthItem, ProviderHealthSummary
from app.services.provider_errors import explain_provider_error


class ProviderHealthService:
    EVENT_NAME = "provider_search_result"

    def record_results(
        self,
        db: Session,
        *,
        search_id: str | None,
        provider_reports: list[dict],
    ) -> None:
        for report in provider_reports:
            db.add(
                FeedbackEvent(
                    search_id=search_id,
                    event_name=self.EVENT_NAME,
                    actor="system",
                    strategy_type=None,
                    payload_json=report,
                    free_text=report.get("error_message"),
                )
            )
        db.flush()

    def get_summary(self, db: Session, *, locale: AppLocale = DEFAULT_LOCALE) -> ProviderHealthSummary:
        events = db.scalars(
            select(FeedbackEvent)
            .where(FeedbackEvent.event_name == self.EVENT_NAME)
            .order_by(FeedbackEvent.created_at.desc())
        ).all()
        return self.summarize_events(events, locale=locale)

    def summarize_events(self, events: list[FeedbackEvent], *, locale: AppLocale = DEFAULT_LOCALE) -> ProviderHealthSummary:
        grouped: dict[str, list[FeedbackEvent]] = defaultdict(list)
        for event in events:
            provider_name = str(event.payload_json.get("provider_name", "unknown"))
            grouped[provider_name].append(event)

        items: list[ProviderHealthItem] = []
        for provider_name, provider_events in sorted(grouped.items()):
            total_attempts = len(provider_events)
            successful_attempts = sum(1 for event in provider_events if event.payload_json.get("success"))
            failed_attempts = total_attempts - successful_attempts
            total_latency = sum(float(event.payload_json.get("latency_ms", 0)) for event in provider_events)
            total_offer_count = sum(int(event.payload_json.get("offer_count", 0)) for event in provider_events)
            latest_event = provider_events[0]
            items.append(
                ProviderHealthItem(
                    provider_name=provider_name,
                    total_attempts=total_attempts,
                    successful_attempts=successful_attempts,
                    failed_attempts=failed_attempts,
                    success_rate=round((successful_attempts / total_attempts) * 100, 2) if total_attempts else 0.0,
                    avg_latency_ms=round(total_latency / total_attempts, 2) if total_attempts else 0.0,
                    avg_offer_count=round(total_offer_count / total_attempts, 2) if total_attempts else 0.0,
                    last_status="success" if latest_event.payload_json.get("success") else "failed",
                    last_error=self._render_last_error(locale, provider_name, latest_event),
                    last_external_request_id=latest_event.payload_json.get("external_request_id"),
                    last_external_correlation_id=latest_event.payload_json.get("external_correlation_id"),
                )
            )

        return ProviderHealthSummary(items=items)

    def _render_last_error(self, locale: AppLocale, provider_name: str, event: FeedbackEvent) -> str | None:
        payload = event.payload_json or {}
        error_detail = payload.get("error_detail")
        if error_detail:
            return explain_provider_error(locale, provider_name, error_detail)
        return explain_provider_error(locale, provider_name, payload.get("error_message") or event.free_text)
