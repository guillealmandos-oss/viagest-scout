export type TravelPriority = "savings" | "balanced" | "comfort" | "experience" | "miles";
export type StrategyType = "savings" | "experience" | "miles";

export interface SearchPayload {
  user: {
    email?: string;
    display_name?: string;
  };
  traveler_profile: {
    nationality: string;
    residence_country?: string;
    checked_bag_required: boolean;
    max_stops: number;
    travel_priority: TravelPriority;
    stopover_interest: boolean;
    risk_tolerance: "low" | "medium" | "high";
    valid_visas: string[];
  };
  loyalty_profiles: Array<{
    program_name: string;
    balance: number;
    bank_name?: string;
    transfer_partners: string[];
  }>;
  search: {
    origin: string;
    destination: string;
    departure_date: string;
    return_date?: string;
    flexible_days: number;
    budget_usd?: number;
    passengers: number;
    cabin_class: "ECONOMY" | "PREMIUM_ECONOMY" | "BUSINESS" | "FIRST";
    checked_bag_required: boolean;
    stopover_interest: boolean;
    preferred_strategy: TravelPriority;
    notes?: string;
  };
}

export interface AnalyticsSummary {
  total_searches: number;
  total_events: number;
  saved_recommendations: number;
  feedback_submissions: number;
  strategy_open_events: number;
  recent_feedback: Array<{
    event_name: string;
    search_id: string;
    text: string;
    created_at: string;
  }>;
}

export interface ProviderHealthSummary {
  items: ProviderHealthItem[];
}

export interface ProviderHealthItem {
  provider_name: string;
  total_attempts: number;
  successful_attempts: number;
  failed_attempts: number;
  success_rate: number;
  avg_latency_ms: number;
  avg_offer_count: number;
  last_status: string;
  last_error?: string | null;
  last_external_request_id?: string | null;
  last_external_correlation_id?: string | null;
}

export interface SearchResponse {
  search_id: string;
  provider_name: string;
  summary: string;
  assumptions: Array<{
    scope: string;
    rule: string;
    confidence: string;
    note: string;
  }>;
  strategies: Strategy[];
  created_at: string;
}

export interface Strategy {
  strategy_type: StrategyType;
  title: string;
  recommendation_badge: string;
  total_score: number;
  explanation: string;
  tradeoffs: string[];
  opportunity_notes: string[];
  score_breakdown: Record<string, number>;
  itinerary: Itinerary;
  is_recommended: boolean;
}

export interface Itinerary {
  id: string;
  provider_offer_id: string;
  provider_name: string;
  title: string;
  total_price: number;
  currency: string;
  total_duration_minutes: number;
  stops_count: number;
  baggage_included: boolean;
  flexibility_label: string;
  route_summary: string;
  airlines: string[];
  segments: Segment[];
  layovers: Layover[];
  slices?: FlightSlice[];
  risk_flags: RiskFlag[];
  migration_notes: string[];
  opportunity_notes: string[];
  score_breakdown: Record<string, number>;
}

export interface Segment {
  origin: string;
  destination: string;
  departure_at: string;
  arrival_at: string;
  airline: string;
  airline_name?: string | null;
  flight_number: string;
  cabin_class: string;
  duration_minutes: number;
}

export interface Layover {
  airport: string;
  duration_minutes: number;
  stopover_candidate: boolean;
}

export interface FlightSlice {
  segments: Segment[];
  layovers: Layover[];
}

export interface RiskFlag {
  code: string;
  severity: "low" | "medium" | "high";
  message: string;
}
