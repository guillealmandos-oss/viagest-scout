from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytics import AnalyticsEventCreate, AnalyticsSummary, ProviderHealthSummary
from app.services.orchestrator import SearchOrchestrator


router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
service = SearchOrchestrator()


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)) -> AnalyticsSummary:
    return service.get_analytics_summary(db)


@router.get("/provider-health", response_model=ProviderHealthSummary)
def get_provider_health_summary(db: Session = Depends(get_db)) -> ProviderHealthSummary:
    return service.get_provider_health_summary(db)


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
def create_analytics_event(payload: AnalyticsEventCreate, db: Session = Depends(get_db)) -> dict:
    service.record_event(
        db,
        event_name=payload.event_name,
        actor=payload.actor,
        strategy_type=payload.strategy_type,
        search_id=payload.search_id,
        payload=payload.payload,
        free_text=payload.free_text,
    )
    return {"status": "accepted"}
