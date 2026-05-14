from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


CabinClass = Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
TravelPriority = Literal["savings", "balanced", "comfort", "experience", "miles"]
RiskTolerance = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    email: str | None = None
    display_name: str | None = None


class TravelerProfileInput(BaseModel):
    nationality: str = Field(min_length=2, max_length=2)
    residence_country: str | None = Field(default=None, min_length=2, max_length=2)
    checked_bag_required: bool = False
    max_stops: int = Field(default=2, ge=0, le=4)
    travel_priority: TravelPriority = "balanced"
    stopover_interest: bool = False
    risk_tolerance: RiskTolerance = "medium"
    valid_visas: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_country_codes(self) -> "TravelerProfileInput":
        self.nationality = self.nationality.upper()
        if self.residence_country:
            self.residence_country = self.residence_country.upper()
        self.valid_visas = [visa.upper() for visa in self.valid_visas]
        return self


class LoyaltyProfileInput(BaseModel):
    program_name: str = Field(min_length=2, max_length=120)
    balance: int = Field(default=0, ge=0)
    bank_name: str | None = None
    transfer_partners: list[str] = Field(default_factory=list)


class SearchRequestInput(BaseModel):
    origin: str = Field(min_length=3, max_length=3)
    destination: str = Field(min_length=3, max_length=3)
    departure_date: date
    return_date: date | None = None
    flexible_days: int = Field(default=0, ge=0, le=14)
    budget_usd: float | None = Field(default=None, ge=0)
    passengers: int = Field(default=1, ge=1, le=9)
    cabin_class: CabinClass = "ECONOMY"
    checked_bag_required: bool = False
    stopover_interest: bool = False
    preferred_strategy: TravelPriority = "balanced"
    notes: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def normalize_airports(self) -> "SearchRequestInput":
        self.origin = self.origin.upper()
        self.destination = self.destination.upper()
        return self


class SearchCreateRequest(BaseModel):
    user: UserInput = Field(default_factory=UserInput)
    traveler_profile: TravelerProfileInput
    loyalty_profiles: list[LoyaltyProfileInput] = Field(default_factory=list)
    search: SearchRequestInput


class FlightSegment(BaseModel):
    origin: str
    destination: str
    departure_at: str
    arrival_at: str
    airline: str
    flight_number: str
    cabin_class: CabinClass
    duration_minutes: int


class LayoverInfo(BaseModel):
    airport: str
    duration_minutes: int
    stopover_candidate: bool = False


class RiskFlag(BaseModel):
    code: str
    severity: Literal["low", "medium", "high"]
    message: str
    message_key: str | None = None
    message_params: dict[str, str | int | float] = Field(default_factory=dict)


class ItineraryOption(BaseModel):
    id: str
    provider_offer_id: str
    provider_name: str
    title: str
    total_price: float
    currency: str
    total_duration_minutes: int
    stops_count: int
    baggage_included: bool
    flexibility_label: str
    route_summary: str
    airlines: list[str]
    segments: list[FlightSegment]
    layovers: list[LayoverInfo]
    raw_payload: dict
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    migration_notes: list[str] = Field(default_factory=list)
    opportunity_notes: list[str] = Field(default_factory=list)


class StrategyCard(BaseModel):
    strategy_type: Literal["savings", "experience", "miles"]
    title: str
    recommendation_badge: str
    total_score: float
    explanation: str
    tradeoffs: list[str]
    opportunity_notes: list[str]
    score_breakdown: dict[str, float]
    itinerary: ItineraryOption
    is_recommended: bool = False


class SearchResponse(BaseModel):
    search_id: str
    provider_name: str
    summary: str
    assumptions: list[dict]
    strategies: list[StrategyCard]
    created_at: str
