import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from enum import Enum


class FlightScheduleStatus(str, Enum):
    SUCCESS = "success"
    NO_SCHEDULE_FOUND = "no_schedule_found"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"
    PARSE_FAILED = "parse_failed"
    PARAMETER_MISMATCH = "parameter_mismatch"
    REDIRECTED_TO_HOME = "redirected_to_home"
    UNVERIFIED_RESPONSE = "unverified_response"
    CAPTCHA_DETECTED = "captcha_detected"
    UNKNOWN = "unknown"

@dataclass
class ProviderResult:
    flights: List['Flight']
    status: FlightScheduleStatus
    message: str = ""
    metadata: Dict = None


@dataclass
class Flight:
    flight_number: str
    airline: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    direct: bool = True
    marketing_carrier: str = ""
    operating_carrier: str = ""
    ticket_also_sold_by: str = ""
    duration: str = ""
    stops: int = 0
    source_type: str = "unknown"
    price: str = ""
    extraction_time: str = "" # Format: "HH:MM"
    is_direct: bool = True


@dataclass
class FlightMatchInfo:
    flight: str
    scheduled_departure: str
    displayed_departure: Optional[str] = None
    difference_minutes: Optional[int] = None
    
    def to_dict(self) -> Dict:
        res = {
            "flight": self.flight,
            "scheduled_departure": self.scheduled_departure
        }
        if self.displayed_departure is not None:
            res["displayed_departure"] = self.displayed_departure
        if self.difference_minutes is not None:
            res["difference_minutes"] = self.difference_minutes
        return res


@dataclass
class InferenceResult:
    destination: str
    airport: str
    score_breakdown: Dict = field(default_factory=dict)
    score: int = 0
    confidence: str = "low" # "low", "medium", "high"
    outbound_match: Optional[FlightMatchInfo] = None
    return_match: Optional[FlightMatchInfo] = None
    reasons: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        res = {
            "destination": self.destination,
            "airport": self.airport,
            "score_breakdown": self.score_breakdown,
            "score": self.score,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "uncertainties": self.uncertainties
        }
        if self.outbound_match:
            res["outbound_match"] = self.outbound_match.to_dict()
        if self.return_match:
            res["return_match"] = self.return_match.to_dict()
        return res


@dataclass
class InferenceParams:
    origin_airport: str
    outbound_date: str  # "YYYY-MM-DD"
    return_date: str  # "YYYY-MM-DD"
    visible_destinations: List[str] = field(default_factory=list)
    target_outbound_time: Optional[str] = None
    target_return_time: Optional[str] = None
    outbound_time_window: Optional[str] = None  # e.g. "06:00" or "06:00-12:00" (Not fully parsed in mock)
    return_time_window: Optional[str] = None
    direct_flights_only: bool = True
    cabin_class: str = "Economy"
    destination_pool: Optional[List[str]] = None

    def __post_init__(self):
        if self.destination_pool is not None and not self.visible_destinations:
            self.visible_destinations = self.destination_pool
        if not self.target_outbound_time and self.outbound_time_window:
            self.target_outbound_time = self.outbound_time_window
        if not self.target_return_time and self.return_time_window:
            self.target_return_time = self.return_time_window


class FlightScheduleProvider:
    """Abstract interface for flight schedule retrieval."""
    
    async def get_flights(self, origin: str, destination: str, date: str, direct_only: bool = True, airline: str = "LH") -> ProviderResult:
        raise NotImplementedError


class MockScheduleProvider(FlightScheduleProvider):
    """
    Mock provider returning hardcoded flight data for testing.
    In a real scenario, this would query a flight database or API.
    """
    
    def __init__(self):
        # We store some dummy flights. Keys are (origin, destination).
        # We don't strictly check date in the mock, just origin/dest to simulate schedule.
        self.mock_db = {
            ("FRA", "PRG"): [
                Flight("LH1392", "LH", "FRA", "PRG", "06:05", "07:05"),
                Flight("LH1396", "LH", "FRA", "PRG", "12:15", "13:15"),
            ],
            ("PRG", "FRA"): [
                Flight("LH1393", "LH", "PRG", "FRA", "07:45", "08:50"),
                Flight("LH1401", "LH", "PRG", "FRA", "20:10", "21:20"),
            ],
            ("FRA", "DUB"): [
                Flight("LH976", "LH", "FRA", "DUB", "10:10", "11:15"),
            ],
            ("DUB", "FRA"): [
                Flight("LH977", "LH", "DUB", "FRA", "12:05", "15:05"),
            ],
            ("FRA", "VCE"): [
                Flight("LH324", "LH", "FRA", "VCE", "08:20", "09:35"),
                Flight("LH326", "LH", "FRA", "VCE", "16:40", "17:55"),
            ],
            ("VCE", "FRA"): [
                Flight("LH325", "LH", "VCE", "FRA", "10:20", "11:45"),
                Flight("LH327", "LH", "VCE", "FRA", "18:40", "20:05"),
            ],
        }

    async def get_flights(self, origin: str, destination: str, date: str, direct_only: bool = True, airline: str = "LH") -> ProviderResult:
        flights = self.mock_db.get((origin, destination), [])
        if flights:
            return ProviderResult(flights=flights, status=FlightScheduleStatus.SUCCESS, metadata={"parameters_verified": True})
        return ProviderResult(flights=[], status=FlightScheduleStatus.NO_SCHEDULE_FOUND, metadata={"parameters_verified": True})


class DestinationInferenceEngine:
    def __init__(self, provider: FlightScheduleProvider):
        self.provider = provider
        
        # Extended mapping for the full pool
        self.city_to_iata = {
            "Prague": "PRG",
            "Prag": "PRG",
            "Dublin": "DUB",
            "Venice": "VCE",
            "Venedig": "VCE",
            "Amsterdam": "AMS",
            "Paris": "CDG", # CDG or ORY, assume CDG for LH
            "London": "LHR",
            "Rom": "FCO",
            "Rome": "FCO",
            "Wien": "VIE",
            "Vienna": "VIE",
            "Madrid": "MAD",
            "Barcelona": "BCN",
            "Budapest": "BUD"
        }

    async def infer_destinations(self, params: InferenceParams) -> List[InferenceResult]:
        results = []
        pool_size = len(params.visible_destinations)
        checked_destinations = 0
        
        for city in params.visible_destinations:
            airport_code = self.city_to_iata.get(city)
            if not airport_code:
                results.append(self._create_empty_result(city, "???", "No airport code mapping found"))
                continue
                
            outbound_res = await self.provider.get_flights(
                origin=params.origin_airport, 
                destination=airport_code, 
                date=params.outbound_date,
                direct_only=params.direct_flights_only
            )
            
            verified = False
            if outbound_res.metadata and outbound_res.metadata.get("parameters_verified") is True:
                verified = True
            
            if outbound_res.status == FlightScheduleStatus.SUCCESS and verified:
                outbound_flights = outbound_res.flights
            else:
                outbound_flights = []
            
            return_res = await self.provider.get_flights(
                origin=airport_code, 
                destination=params.origin_airport, 
                date=params.return_date,
                direct_only=params.direct_flights_only
            )
            
            verified_ret = False
            if return_res.metadata and return_res.metadata.get("parameters_verified") is True:
                verified_ret = True
                
            if return_res.status == FlightScheduleStatus.SUCCESS and verified_ret:
                return_flights = return_res.flights
            else:
                return_flights = []

            # Handle blocked or unknown statuses
            if (outbound_res.status not in (FlightScheduleStatus.SUCCESS, FlightScheduleStatus.NO_SCHEDULE_FOUND) or not verified) or \
               (return_res.status not in (FlightScheduleStatus.SUCCESS, FlightScheduleStatus.NO_SCHEDULE_FOUND) or not verified_ret):
                results.append(self._create_empty_result(
                    city, 
                    airport_code, 
                    f"Provider returned status Outbound:{outbound_res.status.value}, Return:{return_res.status.value}"
                ))
                continue
            
            checked_destinations += 1
            
            if not outbound_flights or not return_flights:
                results.append(self._create_empty_result(city, airport_code, "No valid LH flights found on these dates"))
                continue
                
            # We have flights! Let's score them.
            nonstop_score = 40
            outbound_time_score = 0
            return_time_score = 0
            carrier_score = 0
            ambiguity_penalty = 0
            
            reasons = ["Nonstop service operates on both dates"]
            uncertainties = []
            
            outbound_match = None
            return_match = None
            
            # Outbound flight matching
            best_outbound = outbound_flights[0]
            if params.target_outbound_time:
                best_outbound, diff = self._find_closest_flight(outbound_flights, params.target_outbound_time)
                outbound_time_score = max(0, 30 - diff)
                reasons.append("outbound schedule match")
                outbound_match = FlightMatchInfo(
                    flight=best_outbound.flight_number,
                    scheduled_departure=best_outbound.departure_time,
                    displayed_departure=params.target_outbound_time,
                    difference_minutes=diff
                )
            else:
                outbound_match = FlightMatchInfo(flight=best_outbound.flight_number, scheduled_departure=best_outbound.departure_time)
                ambiguity_penalty -= 5
                uncertainties.append("Missing target outbound time")
                
            # Return flight matching
            best_return = return_flights[-1]
            if params.target_return_time:
                best_return, diff = self._find_closest_flight(return_flights, params.target_return_time)
                return_time_score = max(0, 30 - diff)
                reasons.append("return schedule match")
                return_match = FlightMatchInfo(
                    flight=best_return.flight_number,
                    scheduled_departure=best_return.departure_time,
                    displayed_departure=params.target_return_time,
                    difference_minutes=diff
                )
            else:
                return_match = FlightMatchInfo(flight=best_return.flight_number, scheduled_departure=best_return.departure_time)
                ambiguity_penalty -= 5
                uncertainties.append("Missing target return time")
                
            # Carrier scoring
            outbound_carrier = best_outbound.operating_carrier or best_outbound.marketing_carrier or best_outbound.airline
            return_carrier = best_return.operating_carrier or best_return.marketing_carrier or best_return.airline
            
            if "Lufthansa" in outbound_carrier or "LH" in outbound_carrier:
                carrier_score += 5
            elif best_outbound.ticket_also_sold_by and "Lufthansa" in best_outbound.ticket_also_sold_by:
                carrier_score += 5
            else:
                carrier_score -= 5
                
            if "Lufthansa" in return_carrier or "LH" in return_carrier:
                carrier_score += 5
            elif best_return.ticket_also_sold_by and "Lufthansa" in best_return.ticket_also_sold_by:
                carrier_score += 5
            else:
                carrier_score -= 5

            if carrier_score <= 10:
                ambiguity_penalty -= 10
                uncertainties.append("Operating carrier is not explicitly Lufthansa")

            final_score = nonstop_score + outbound_time_score + return_time_score + carrier_score + ambiguity_penalty
            final_score = min(100, max(0, final_score))
            
            score_breakdown = {
                "outbound_time_score": outbound_time_score,
                "return_time_score": return_time_score,
                "nonstop_score": nonstop_score,
                "carrier_score": carrier_score,
                "ambiguity_penalty": ambiguity_penalty,
                "final_score": final_score
            }
            
            confidence = "low"
            if final_score > 80:
                confidence = "high"
            elif final_score > 50:
                confidence = "medium"
            
            uncertainties.append("Lufthansa Surprise inventory cannot be confirmed")
            results.append(InferenceResult(
                destination=city,
                airport=airport_code,
                score_breakdown=score_breakdown,
                score=final_score,
                confidence=confidence,
                outbound_match=outbound_match,
                return_match=return_match,
                reasons=reasons,
                uncertainties=uncertainties
            ))
            
        # Sort results by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Apply Confidence Penalties
        # 1. Pool check
        pool_penalty = checked_destinations < pool_size
        
        # 2. Close top candidates check
        close_candidates_penalty = False
        if len(results) > 1:
            if abs(results[0].score - results[1].score) <= 10:
                close_candidates_penalty = True
        
        for r in results:
            if pool_penalty:
                r.uncertainties.append("Not all destinations in the pool were verified successfully")
                self._downgrade_confidence(r)
            if close_candidates_penalty and r.score >= results[0].score - 10:
                r.uncertainties.append("Multiple destinations have equally strong flight schedules")
                self._downgrade_confidence(r)
            if not params.target_return_time:
                self._downgrade_confidence(r)

        return results
        
    def _downgrade_confidence(self, r: InferenceResult):
        if r.confidence == "high":
            r.confidence = "medium"
        elif r.confidence == "medium":
            r.confidence = "low"

    def _create_empty_result(self, city: str, airport: str, reason: str) -> InferenceResult:
        return InferenceResult(
            destination=city,
            airport=airport,
            score_breakdown={
                "outbound_time_score": 0,
                "return_time_score": 0,
                "nonstop_score": 0,
                "carrier_score": 0,
                "ambiguity_penalty": 0,
                "final_score": 0
            },
            score=0,
            confidence="low",
            reasons=[],
            uncertainties=[
                reason,
                "Lufthansa Surprise inventory cannot be confirmed"
            ]
        )
        
    def _find_closest_flight(self, flights: List[Flight], target_time_str: str) -> tuple[Flight, int]:
        try:
            h, m = map(int, target_time_str.split(":"))
            target_mins = h * 60 + m
        except Exception:
            return flights[0], 0
            
        best_flight = flights[0]
        min_diff = 9999
        
        for f in flights:
            try:
                time_str = f.departure_time.split()[-1]
                fh, fm = map(int, time_str.split(":"))
                fmins = fh * 60 + fm
                diff = abs(fmins - target_mins)
                if diff < min_diff:
                    min_diff = diff
                    best_flight = f
            except Exception:
                continue
                
        return best_flight, min_diff
