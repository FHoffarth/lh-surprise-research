import pytest
from src.models import ObservedOfferResult, DecisionRecommendation, SearchProfile, PoolConfiguration, ScheduleRiskResult
from src.pool_dependency_mapper import PoolDependencyMapper
from src.decision_engine import DecisionEngine

def test_data_origin_is_mandatory():
    # Attempting to create ObservedOfferResult without data_origin or with invalid ones
    with pytest.raises(TypeError):
        # Missing positional/keyword argument data_origin
        ObservedOfferResult(
            status="available",
            observed_at="2026-08-04T22:00:00Z",
            search_fingerprint="fp123",
            session_id="sess_abc"
        )
    
    with pytest.raises(ValueError, match="Invalid data_origin"):
        ObservedOfferResult(
            status="available",
            data_origin="invalid_origin_value",
            observed_at="2026-08-04T22:00:00Z",
            search_fingerprint="fp123",
            session_id="sess_abc"
        )

def test_synthetic_data_not_exported_as_live():
    # ObservedOfferResult with synthetic data
    res = ObservedOfferResult(
        status="available",
        data_origin="synthetic_test",
        observed_at="2026-08-04T22:00:00Z",
        search_fingerprint="fp123",
        session_id="sess_abc"
    )
    assert res.data_origin == "synthetic_test"
    # Ensure it's never treated as "live_browser_observation" or "live_network_observation"
    assert res.data_origin != "live_browser_observation"
    assert res.data_origin != "live_network_observation"

def test_unknown_inventory_leads_to_skip():
    profile = SearchProfile("FRA", "2026-08-07", "2026-08-09")
    pool_config = PoolConfiguration("Arts & Culture", ["FLR", "PRG", "WAW"], ["FLR", "PRG", "WAW"])
    engine = DecisionEngine(profile, pool_config)
    
    # We have unknown inventory status
    # Create mock ObservedOfferResult and ScheduleRiskResult
    obs_res = ObservedOfferResult(
        status="available",
        data_origin="synthetic_test",
        observed_at="2026-08-04T22:00:00Z",
        search_fingerprint="fp123",
        session_id="sess_abc"
    )
    
    # Let's say all targets have no safe schedules (unsafe)
    risk_results = [
        ScheduleRiskResult("Florence", "FLR", 10, 0, 0, 0, 10, "", "", None, "unsafe", "EXCLUDE", [], {}),
        ScheduleRiskResult("Prague", "PRG", 10, 0, 0, 0, 10, "", "", None, "unsafe", "EXCLUDE", [], {}),
        ScheduleRiskResult("Warsaw", "WAW", 10, 0, 0, 0, 10, "", "", None, "unsafe", "EXCLUDE", [], {})
    ]
    
    recommendation = engine.formulate_recommendation([obs_res], risk_results)
    assert recommendation.decision == "SKIP"
    assert recommendation.target_inventory_status == "unknown"

def test_unknown_allocation_probability_visible_in_report():
    profile = SearchProfile("FRA", "2026-08-07", "2026-08-09")
    pool_config = PoolConfiguration("Arts & Culture", ["FLR", "PRG", "WAW"], ["FLR", "PRG", "WAW"])
    engine = DecisionEngine(profile, pool_config)
    
    obs_res = ObservedOfferResult(
        status="available",
        data_origin="synthetic_test",
        observed_at="2026-08-04T22:00:00Z",
        search_fingerprint="fp123",
        session_id="sess_abc"
    )
    risk_results = [
        ScheduleRiskResult("Florence", "FLR", 10, 10, 0, 10, 0, "15:00", "15:00", None, "safe", "KEEP", [], {}),
        ScheduleRiskResult("Prague", "PRG", 10, 10, 0, 10, 0, "15:00", "15:00", None, "safe", "KEEP", [], {}),
        ScheduleRiskResult("Warsaw", "WAW", 10, 10, 0, 10, 0, "15:00", "15:00", None, "safe", "KEEP", [], {})
    ]
    
    recommendation = engine.formulate_recommendation([obs_res], risk_results)
    assert recommendation.allocation_probability == "unknown"
    assert recommendation.allocation_distribution == "unknown"

def test_nonlinear_pricing_rules():
    pool_config = PoolConfiguration("Arts & Culture", ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"], ["FLR", "PRG", "WAW"])
    mapper = PoolDependencyMapper(pool_config)
    
    # 11 active: 129.00
    p11 = mapper.calculate_price_premium(129.0, 11, ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"])
    assert p11 == 129.00
    
    # 10 active with LIN: 138.58
    p10_with_lin = mapper.calculate_price_premium(129.0, 10, ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN"])
    assert p10_with_lin == 138.58
    
    # 10 active without LIN: 140.32
    p10_no_lin = mapper.calculate_price_premium(129.0, 10, ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "PUY"])
    assert p10_no_lin == 140.32
    
    # 3 active FLR/PRG/WAW: 177.52
    p3_subset1 = mapper.calculate_price_premium(129.0, 3, ["FLR", "PRG", "WAW"])
    assert p3_subset1 == 177.52
    
    # 3 active HEL/BLQ/KRK: 204.89
    p3_subset2 = mapper.calculate_price_premium(129.0, 3, ["HEL", "BLQ", "KRK"])
    assert p3_subset2 == 204.89
