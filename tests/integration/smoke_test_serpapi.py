import asyncio
import json
import os
from src.destination_inference import InferenceParams, DestinationInferenceEngine
from src.provider_factory import get_provider

async def main():
    print("Starting smoke test for SerpApi Provider (Phase 3)...")
    
    # Check if key is available, if not we will just see what happens
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        print("SerpApi credentials detected: no")
        print("Skipping Live-Smoke-Test because API key is missing.")
        return
    else:
        print("SerpApi credentials detected: yes")
    
    # We test the "auto" logic
    provider = get_provider("auto")
    engine = DestinationInferenceEngine(provider)
    
    # The routes
    destinations = ["Prag", "Amsterdam"]
    
    # Hinflug ungefähr 06:00 Uhr
    params_a = InferenceParams(
        origin_airport="FRA",
        outbound_date="2026-08-07",
        return_date="2026-08-09",
        visible_destinations=destinations,
        target_outbound_time="06:00",
        target_return_time="08:50" # Assuming a return time for PRG, but it will pick closest
    )
    
    print("\n--- Running Inference Engine (Scenario A: 06:00) ---")
    results_a = await engine.infer_destinations(params_a)
    print("\n--- Results (Scenario A) ---")
    for r in results_a:
        print(json.dumps(r.to_dict(), indent=2))
        
    # Hinflug ungefähr 14:20 Uhr
    params_b = InferenceParams(
        origin_airport="FRA",
        outbound_date="2026-08-07",
        return_date="2026-08-09",
        visible_destinations=destinations,
        target_outbound_time="14:20",
        target_return_time="16:00"
    )
    
    print("\n--- Running Inference Engine (Scenario B: 14:20) ---")
    results_b = await engine.infer_destinations(params_b)
    print("\n--- Results (Scenario B) ---")
    for r in results_b:
        print(json.dumps(r.to_dict(), indent=2))
        
    # Dump raw flights to artifacts
    print("\nSaving raw extracted flights to artifacts/inference/serpapi_smoke_flights.json...")
    cache_data = {}
    if hasattr(provider, "cache"):
        for key, res in provider.cache.items():
            k_str = f"{key[0]}-{key[1]}_{key[2]}"
            meta = res.metadata.copy() if res.metadata else {}
            meta["flights"] = [f.__dict__ for f in res.flights]
            meta["status"] = res.status.value
            cache_data[k_str] = meta
            
    os.makedirs("artifacts/inference", exist_ok=True)
    with open("artifacts/inference/serpapi_smoke_flights.json", "w") as f:
        json.dump(cache_data, f, indent=2)
        
    print("\nSmoke test complete.")

if __name__ == "__main__":
    asyncio.run(main())
