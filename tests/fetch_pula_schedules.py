import asyncio
import os
import json
from src.serpapi_provider import SerpApiFlightScheduleProvider

async def main():
    api_key = os.environ.get("SERPAPI_API_KEY")
    provider = SerpApiFlightScheduleProvider(api_key)
    
    dates = ["2026-08-07", "2026-08-08", "2026-08-09"]
    pula_data = {}
    
    for d in dates:
        print(f"Fetching FRA-PUY on {d}...")
        res_out = await provider.get_flights("FRA", "PUY", d)
        print(f"Fetching PUY-FRA on {d}...")
        res_ret = await provider.get_flights("PUY", "FRA", d)
        
        pula_data[d] = {
            "outbound": [f.__dict__ for f in res_out.flights],
            "return": [f.__dict__ for f in res_ret.flights]
        }
        
    os.makedirs("artifacts/schedule_risk", exist_ok=True)
    with open("artifacts/schedule_risk/pula_schedule_dates.json", "w", encoding="utf-8") as f:
        json.dump(pula_data, f, indent=2, ensure_ascii=False)
        
    print("Done. Saved Pula flights to artifacts/schedule_risk/pula_schedule_dates.json")

if __name__ == "__main__":
    asyncio.run(main())
