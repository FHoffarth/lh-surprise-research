from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class SearchProfile:
    origin: str
    earliest_outbound_date: str
    latest_return_date: str
    passenger_count: int = 1
    travel_class: str = "ECONOMY"
    earliest_acceptable_outbound: str = "14:00"
    outbound_risk_policy: str = "reject_if_any_plausible_direct_flight_is_too_early"
    usage_mode: str = "target_roundtrip"  # target_roundtrip, flexible_destination_good_times, target_outbound_only

    def __getitem__(self, item):
        return getattr(self, item)

@dataclass
class PoolConfiguration:
    pool_name: str
    targets: List[str]
    active_targets: List[str]
    min_active_count: int = 3

    def __getitem__(self, item):
        return getattr(self, item)

@dataclass
class ObservedOfferResult:
    status: str  # available, unavailable, blocked, error
    data_origin: str  # live_browser_observation, live_network_observation, recorded_fixture, synthetic_test
    observed_at: str
    search_fingerprint: str
    session_id: str
    run_id: str = ""
    price: Optional[float] = None
    currency: str = "EUR"
    details: str = ""
    active_targets: List[str] = field(default_factory=list)

    def __post_init__(self):
        allowed_origins = {
            "live_browser_observation",
            "live_network_observation",
            "recorded_fixture",
            "synthetic_test"
        }
        if not self.data_origin:
            raise ValueError("data_origin is mandatory")
        if self.data_origin not in allowed_origins:
            raise ValueError(f"Invalid data_origin: {self.data_origin}")
        if not self.observed_at:
            raise ValueError("observed_at is mandatory")
        if not self.search_fingerprint:
            raise ValueError("search_fingerprint is mandatory")
        if not self.session_id and not self.run_id:
            raise ValueError("Either session_id or run_id must be populated")

    def __getitem__(self, item):
        return getattr(self, item)

@dataclass
class ScheduleRiskResult:
    destination: str
    iata: str
    total_combinations: int
    valid_combinations: int
    one_night_count: int
    two_night_count: int
    rejected_due_to_minimum_stay: int
    earliest_outbound_valid: str
    latest_outbound_valid: str
    worst_valid_itinerary: Optional[Dict[str, Any]]
    risk_classification: str  # safe, mixed, unsafe, no_valid_itinerary, unknown
    recommendation: str  # KEEP, EXCLUDE
    reasons: List[str]
    risk_by_trip_length: Dict[str, str]  # {"one_night": "...", "two_nights": "..."}
    all_valid_itineraries: List[Dict[str, Any]] = field(default_factory=list)

    def __getitem__(self, item):
        return getattr(self, item)

@dataclass
class DecisionRecommendation:
    decision: str  # KEEP_POOL, REDUCE_POOL, SKIP
    recommended_active_targets: List[str]
    final_price: Optional[float]
    reasoning: str
    schedule_compatibility: str  # safe, mixed, unsafe, unknown (refers ONLY to flight plan compatibility, not booking safety)
    observed_pool_availability: str  # e.g., available, unavailable, blocked
    target_inventory_status: str  # e.g., unknown, confirmed_available, confirmed_unavailable
    allocation_probability: str  # e.g., unknown, high, low
    confidence: str  # low, medium, high
    confidence_justification: str
    allocation_distribution: str = "unknown"
    details: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, item):
        return getattr(self, item)
