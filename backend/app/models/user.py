from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UuidMixin


class User(UuidMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True)

    traveler_profiles = relationship("TravelerProfile", back_populates="user", cascade="all, delete-orphan")
    loyalty_profiles = relationship("LoyaltyProfile", back_populates="user", cascade="all, delete-orphan")
    searches = relationship("SearchRecord", back_populates="user", cascade="all, delete-orphan")


class TravelerProfile(UuidMixin, TimestampMixin, Base):
    __tablename__ = "traveler_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    nationality: Mapped[str] = mapped_column(String(2))
    residence_country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    checked_bag_required: Mapped[bool] = mapped_column(Boolean, default=False)
    max_stops: Mapped[int] = mapped_column(Integer, default=2)
    travel_priority: Mapped[str] = mapped_column(String(32), default="balanced")
    stopover_interest: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_tolerance: Mapped[str] = mapped_column(String(16), default="medium")
    valid_visas_csv: Mapped[str] = mapped_column(String(255), default="")

    user = relationship("User", back_populates="traveler_profiles")


class LoyaltyProfile(UuidMixin, TimestampMixin, Base):
    __tablename__ = "loyalty_profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    program_name: Mapped[str] = mapped_column(String(120))
    balance: Mapped[int] = mapped_column(Integer, default=0)
    bank_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    transfer_partners_csv: Mapped[str] = mapped_column(String(255), default="")

    user = relationship("User", back_populates="loyalty_profiles")
