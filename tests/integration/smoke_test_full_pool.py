import asyncio
import json
import os
from src.destination_inference import InferenceParams, DestinationInferenceEngine
from src.provider_factory import get_provider

async def main():
    print("Starting full pool smoke test for SerpApi Provider (Validation Pass)...")
    
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        print("SerpApi credentials detected: no")
        print("Skipping Live-Smoke-Test because API key is missing.")
        return
    else:
        print("SerpApi credentials detected: yes")
    
    provider = get_provider("auto")
    engine = DestinationInferenceEngine(provider)
    
    # Arts & Sights typical pool (Go West or similar)
    destinations = [
        "Prag", "Amsterdam", "Paris", "London", "Rom", 
        "Venedig", "Wien", "Madrid", "Barcelona", "Budapest"
    ]
    
    params = InferenceParams(
        origin_airport="FRA",
        outbound_date="2026-08-07",
        return_date="2026-08-09",
        visible_destinations=destinations,
        target_outbound_time="10:00",
        target_return_time="15:00" 
    )
    
    print("\n--- Running Inference Engine (Full Pool) ---")
    results = await engine.infer_destinations(params)
    
    print("\n--- Results Summary ---")
    for r in results:
        print(f"[{r.confidence.upper():<6}] {r.destination:<12} | Score: {r.score} | Breakdown: {r.score_breakdown}")
        
    print("\nSaving raw inference results to artifacts/inference/full_pool_ranking.json...")
    
    os.makedirs("artifacts/inference", exist_ok=True)
    with open("artifacts/inference/full_pool_ranking.json", "w") as f:
        json.dump([r.to_dict() for r in results], f, indent=2)
        
    print("\nSmoke test complete.")

if __name__ == "__main__":
    asyncio.run(main())
