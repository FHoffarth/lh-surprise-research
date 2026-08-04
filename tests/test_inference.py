import pytest
from src.destination_inference import (
    Flight, 
    FlightMatchInfo, 
    InferenceResult, 
    InferenceParams,
    MockScheduleProvider, 
    DestinationInferenceEngine
)


@pytest.mark.asyncio
async def test_inference_with_mock_provider():
    provider = MockScheduleProvider()
    engine = DestinationInferenceEngine(provider)
    
    # Prg and Dub have flights. Vce has multiple. Paris has none.
    params = InferenceParams(
        origin_airport="FRA",
        outbound_date="2026-08-07",
        return_date="2026-08-09",
        destination_pool=["Prague", "Dublin", "Venice", "Paris"],
        outbound_time_window="06:00",
        return_time_window="20:00"
    )
    
    results = await engine.infer_destinations(params)
    
    assert len(results) == 4
    
    # Prague should be high score because LH1392 departs at 06:05 (diff 5) and LH1401 returns 20:10 (diff 10)
    # Total score should be 40 + (30-5) + (30-10) = 40 + 25 + 20 = 85
    prague = next((r for r in results if r.destination == "Prague"), None)
    assert prague is not None
    assert prague.airport == "PRG"
    assert prague.score == 85
    # Should be high if it's the only one > 80.
    
    # Dublin: LH976 at 10:10 (diff 4 h 10 min = 250 min -> score base 40 + 0 (max 0, 30-250))
    # Return LH977 at 12:05 (diff 7 h 55 min = 475 min -> score base 40 + 0)
    # Total score = 40
    dublin = next((r for r in results if r.destination == "Dublin"), None)
    assert dublin is not None
    assert dublin.airport == "DUB"
    assert dublin.score == 40
    assert dublin.confidence == "low"
    
    # Venice: LH324 at 08:20 (diff 140 min), LH325 at 10:20 (diff 580 min)
    # Score = 40
    venice = next((r for r in results if r.destination == "Venice"), None)
    assert venice is not None
    assert venice.airport == "VCE"
    assert venice.score == 40
    
    # Paris: No mapping or no flights
    paris = next((r for r in results if r.destination == "Paris"), None)
    assert paris is not None
    assert paris.score == 0
    
    
@pytest.mark.asyncio
async def test_confidence_normalization():
    provider = MockScheduleProvider()
    engine = DestinationInferenceEngine(provider)
    
    # We will simulate high scores by putting time windows that perfectly match Dublin and Venice as well,
    # or we just test the logic directly by modifying the provider.
    
    # Add fake flights to mock that match perfectly for multiple destinations
    provider.mock_db[("FRA", "DUB")] = [Flight("LH999", "LH", "FRA", "DUB", "06:00", "07:00")]
    provider.mock_db[("DUB", "FRA")] = [Flight("LH998", "LH", "DUB", "FRA", "20:00", "21:00")]
    
    provider.mock_db[("FRA", "VCE")] = [Flight("LH888", "LH", "FRA", "VCE", "06:00", "07:00")]
    provider.mock_db[("VCE", "FRA")] = [Flight("LH887", "LH", "VCE", "FRA", "20:00", "21:00")]
    
    params = InferenceParams(
        origin_airport="FRA",
        outbound_date="2026-08-07",
        return_date="2026-08-09",
        destination_pool=["Dublin", "Venice"],
        outbound_time_window="06:00",
        return_time_window="20:00"
    )
    
    results = await engine.infer_destinations(params)
    
    assert len(results) == 2
    for r in results:
        assert r.score == 100
        # They should be downgraded to medium
        assert r.confidence == "medium"
        assert "Multiple destinations have equally strong flight schedules" in r.uncertainties
