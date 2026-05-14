from app.models.analytics import FeedbackEvent
from app.services.provider_health import ProviderHealthService


def build_event(
    *,
    provider_name: str,
    success: bool,
    latency_ms: float,
    offer_count: int,
    error_message: str | None = None,
    external_request_id: str | None = None,
    external_correlation_id: str | None = None,
):
    return FeedbackEvent(
        search_id=None,
        event_name=ProviderHealthService.EVENT_NAME,
        actor="system",
        strategy_type=None,
        payload_json={
            "provider_name": provider_name,
            "success": success,
            "latency_ms": latency_ms,
            "offer_count": offer_count,
            "error_message": error_message,
            "external_request_id": external_request_id,
            "external_correlation_id": external_correlation_id,
        },
        free_text=error_message,
    )


def test_provider_health_summary_aggregates_success_and_failures():
    service = ProviderHealthService()
    summary = service.summarize_events(
        [
            build_event(provider_name="duffel", success=False, latency_ms=1200, offer_count=0, error_message="timeout"),
            build_event(provider_name="duffel", success=True, latency_ms=800, offer_count=4),
            build_event(provider_name="amadeus", success=True, latency_ms=1500, offer_count=6),
        ]
    )

    assert len(summary.items) == 2
    duffel = next(item for item in summary.items if item.provider_name == "duffel")
    assert duffel.total_attempts == 2
    assert duffel.successful_attempts == 1
    assert duffel.failed_attempts == 1
    assert duffel.success_rate == 50.0
    assert duffel.last_status == "failed"
    assert duffel.last_error == "timeout"


def test_provider_health_summary_calculates_averages():
    service = ProviderHealthService()
    summary = service.summarize_events(
        [
            build_event(provider_name="duffel", success=True, latency_ms=1000, offer_count=2),
            build_event(provider_name="duffel", success=True, latency_ms=500, offer_count=4),
        ]
    )

    duffel = summary.items[0]
    assert duffel.avg_latency_ms == 750.0
    assert duffel.avg_offer_count == 3.0


def test_provider_health_summary_keeps_latest_external_ids():
    service = ProviderHealthService()
    summary = service.summarize_events(
        [
            build_event(
                provider_name="duffel",
                success=False,
                latency_ms=950,
                offer_count=0,
                error_message="bad gateway",
                external_request_id="req_latest",
                external_correlation_id="corr_latest",
            ),
            build_event(
                provider_name="duffel",
                success=True,
                latency_ms=700,
                offer_count=3,
                external_request_id="req_old",
                external_correlation_id="corr_old",
            ),
        ]
    )

    duffel = summary.items[0]
    assert duffel.last_external_request_id == "req_latest"
    assert duffel.last_external_correlation_id == "corr_latest"
