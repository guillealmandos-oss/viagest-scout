from pydantic import BaseModel, Field


class AnalyticsEventCreate(BaseModel):
    event_name: str = Field(min_length=2, max_length=64)
    actor: str = Field(default="anonymous", min_length=2, max_length=64)
    strategy_type: str | None = Field(default=None, max_length=32)
    search_id: str | None = Field(default=None, max_length=36)
    payload: dict = Field(default_factory=dict)
    free_text: str | None = Field(default=None, max_length=1000)


class AnalyticsSummary(BaseModel):
    total_searches: int
    total_events: int
    saved_recommendations: int
    feedback_submissions: int
    strategy_open_events: int
    recent_feedback: list[dict]


class ProviderHealthItem(BaseModel):
    provider_name: str
    total_attempts: int
    successful_attempts: int
    failed_attempts: int
    success_rate: float
    avg_latency_ms: float
    avg_offer_count: float
    last_status: str
    last_error: str | None = None
    last_external_request_id: str | None = None
    last_external_correlation_id: str | None = None


class ProviderHealthSummary(BaseModel):
    items: list[ProviderHealthItem]
