from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UuidMixin


class FeedbackEvent(UuidMixin, TimestampMixin, Base):
    __tablename__ = "feedback_events"

    search_id: Mapped[str | None] = mapped_column(ForeignKey("searches.id", ondelete="SET NULL"), nullable=True)
    event_name: Mapped[str] = mapped_column(String(64))
    actor: Mapped[str] = mapped_column(String(64), default="anonymous")
    strategy_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    free_text: Mapped[str | None] = mapped_column(Text, nullable=True)
