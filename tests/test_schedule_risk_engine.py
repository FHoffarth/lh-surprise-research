import pytest
from src.schedule_risk_engine import ScheduleRiskEngine

@pytest.fixture
def default_engine():
    profile = {
        "earliest_acceptable_outbound": "14:00",
        "outbound_risk_policy": "reject_if_any_plausible_direct_flight_is_too_early"
    }
    return ScheduleRiskEngine(profile)

def test_itinerary_safe(default_engine):
    outbound = [
        {"flight_number": "LH 100", "departure_time": "2026-08-07 15:00", "arrival_time": "2026-08-07 16:00"}
    ]
    returns = [
        {"flight_number": "LH 101", "departure_time": "2026-08-09 17:00", "arrival_time": "2026-08-09 18:00"}
    ]
    res = default_engine.evaluate_itineraries("XYZ", outbound, returns)
    assert res["risk_classification"] == "safe"
    assert res["recommendation"] == "KEEP"
    assert res["total_combinations"] == 1
    assert res["valid_combinations"] == 1

def test_itinerary_mixed(default_engine):
    outbound = [
        {"flight_number": "LH 100", "departure_time": "2026-08-07 10:00", "arrival_time": "2026-08-07 11:00"},
        {"flight_number": "LH 102", "departure_time": "2026-08-07 15:00", "arrival_time": "2026-08-07 16:00"}
    ]
    returns = [
        {"flight_number": "LH 101", "departure_time": "2026-08-09 17:00", "arrival_time": "2026-08-09 18:00"}
    ]
    res = default_engine.evaluate_itineraries("XYZ", outbound, returns)
    assert res["risk_classification"] == "mixed"
    assert res["recommendation"] == "EXCLUDE"
    assert res["valid_combinations"] == 2

def test_itinerary_invalid_stay(default_engine):
    outbound = [
        {"flight_number": "LH 100", "departure_time": "2026-08-07 22:00", "arrival_time": "2026-08-07 23:00"}
    ]
    returns = [
        {"flight_number": "LH 101", "departure_time": "2026-08-09 08:00", "arrival_time": "2026-08-09 09:00"}
    ]
    # Stay duration: Sunday 08:00 - Friday 23:00 = 33 hours (< 36 hours!)
    res = default_engine.evaluate_itineraries("XYZ", outbound, returns)
    assert res["risk_classification"] == "no_valid_itinerary"
    assert res["recommendation"] == "EXCLUDE"
    assert res["valid_combinations"] == 0
