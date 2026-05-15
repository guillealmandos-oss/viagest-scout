from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UuidMixin


class SearchRecord(UuidMixin, TimestampMixin, Base):
    __tablename__ = "searches"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    origin: Mapped[str] = mapped_column(String(3))
    destination: Mapped[str] = mapped_column(String(3))
    departure_date: Mapped[str] = mapped_column(String(10))
    return_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    flexible_days: Mapped[int] = mapped_column(Integer, default=0)
    budget_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    passengers: Mapped[int] = mapped_column(Integer, default=1)
    cabin_class: Mapped[str] = mapped_column(String(24), default="ECONOMY")
    checked_bag_required: Mapped[bool] = mapped_column(Boolean, default=False)
    stopover_interest: Mapped[bool] = mapped_column(Boolean, default=False)
    travel_priority: Mapped[str] = mapped_column(String(32), default="balanced")
    provider_name: Mapped[str] = mapped_column(String(32))
    content_locale: Mapped[str] = mapped_column(String(8), default="es")
    status: Mapped[str] = mapped_column(String(24), default="completed")
    summary_text: Mapped[str] = mapped_column(Text)
    assumptions_json: Mapped[list[dict]] = mapped_column(JSON, default=list)

    user = relationship("User", back_populates="searches")
    itineraries = relationship("ItineraryRecord", back_populates="search", cascade="all, delete-orphan")
    strategies = relationship("StrategyResultRecord", back_populates="search", cascade="all, delete-orphan")


class ItineraryRecord(UuidMixin, TimestampMixin, Base):
    __tablename__ = "itineraries"

    search_id: Mapped[str] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"))
    provider_offer_id: Mapped[str] = mapped_column(String(64))
    itinerary_type: Mapped[str] = mapped_column(String(512))
    total_price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3))
    total_duration_minutes: Mapped[int] = mapped_column(Integer)
    stops_count: Mapped[int] = mapped_column(Integer)
    baggage_included: Mapped[bool] = mapped_column(Boolean, default=False)
    airlines_csv: Mapped[str] = mapped_column(String(255))
    route_summary: Mapped[str] = mapped_column(String(255))
    raw_json: Mapped[dict] = mapped_column(JSON)
    normalized_json: Mapped[dict] = mapped_column(JSON)
    dimension_scores_json: Mapped[dict] = mapped_column(JSON)
    risk_flags_json: Mapped[list[dict]] = mapped_column(JSON, default=list)

    search = relationship("SearchRecord", back_populates="itineraries")
    strategy_results = relationship("StrategyResultRecord", back_populates="itinerary")


class StrategyResultRecord(UuidMixin, TimestampMixin, Base):
    __tablename__ = "strategy_results"

    search_id: Mapped[str] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"))
    itinerary_id: Mapped[str] = mapped_column(ForeignKey("itineraries.id", ondelete="CASCADE"))
    strategy_type: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(120))
    recommendation_badge: Mapped[str] = mapped_column(String(120))
    total_score: Mapped[float] = mapped_column(Float)
    explanation_text: Mapped[str] = mapped_column(Text)
    tradeoffs_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunity_notes_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    score_breakdown_json: Mapped[dict] = mapped_column(JSON)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False)

    search = relationship("SearchRecord", back_populates="strategies")
    itinerary = relationship("ItineraryRecord", back_populates="strategy_results")
