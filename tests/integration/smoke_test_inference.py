import asyncio
import json
import logging
import os
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

from src.destination_inference import InferenceParams, DestinationInferenceEngine
from src.lufthansa_public_provider import PublicLufthansaTimetableProvider

async def run_smoke_test():
    print("Starting smoke test for Destination Inference (Phase 2)...")
    
    os.makedirs("artifacts/inference", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        provider = PublicLufthansaTimetableProvider(page)
        engine = DestinationInferenceEngine(provider)
        
        # Test PRG and AMS
        engine.city_to_iata["Prague"] = "PRG"
        engine.city_to_iata["Amsterdam"] = "AMS"
        
        print("\n--- Running Inference Engine (Scenario A: 06:00) ---")
        params_a = InferenceParams(
            origin_airport="FRA",
            outbound_date="2026-08-07",
            return_date="2026-08-09",
            visible_destinations=["Prague", "Amsterdam"],
            target_outbound_time="06:00",
            target_return_time="20:00"
        )
        results_a = await engine.infer_destinations(params_a)
        
        print("\n--- Results (Scenario A) ---")
        for res in results_a:
            print(json.dumps(res.to_dict(), indent=2))
            
        print("\n--- Running Inference Engine (Scenario B: 14:20) ---")
        params_b = InferenceParams(
            origin_airport="FRA",
            outbound_date="2026-08-07",
            return_date="2026-08-09",
            visible_destinations=["Prague", "Amsterdam"],
            target_outbound_time="14:20",
            target_return_time="20:00"
        )
        results_b = await engine.infer_destinations(params_b)
        
        print("\n--- Results (Scenario B) ---")
        for res in results_b:
            print(json.dumps(res.to_dict(), indent=2))
            
        # Save smoke_flights.json
        print("\nSaving raw extracted flights to artifacts/inference/smoke_flights.json...")
        cache_data = {}
        for key, res in provider.cache.items():
            k_str = f"{key[0]}-{key[1]}_{key[2]}"
            meta = res.metadata.copy() if res.metadata else {}
            meta["flights"] = [f.__dict__ for f in res.flights]
            meta["status"] = res.status.value
            cache_data[k_str] = meta
            
        with open("artifacts/inference/smoke_flights.json", "w") as f:
            json.dump({
                "consent_method": provider.consent_method,
                "flights": cache_data
            }, f, indent=2)
            
        await browser.close()
        print("\nSmoke test complete.")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
