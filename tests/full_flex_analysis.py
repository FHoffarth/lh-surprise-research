import asyncio
import json
import os
from datetime import datetime
from src.serpapi_provider import SerpApiFlightScheduleProvider

city_to_iata = {
    "Florenz": "FLR",
    "Prag": "PRG",
    "Warschau": "WAW",
    "Breslau": "WRO",
    "Helsinki": "HEL",
    "Bologna": "BLQ",
    "Krakau": "KRK",
    "Basel": "BSL",
    "Sarajevo": "SJJ",
    "Mailand": "MIL",
    "Pula": "PUY"
}

def parse_time(t_str):
    try:
        # Expected format: "2026-08-07 10:00"
        return datetime.strptime(t_str, "%Y-%m-%d %H:%M").time()
    except:
        return None

def score_weekend_suitability(outbound_flights, return_flights):
    # Score based on how many hours you get at the destination
    # Best: early Friday (but not extremely early like 5am, let's say >= 07:00) and late Sunday
    # For a simple ranking, let's calculate the "best possible duration" in hours between arrival and return departure
    # We also want to favor multiple options.
    
    if not outbound_flights or not return_flights:
        return 0, "no_match"
        
    valid_outbounds = [f for f in outbound_flights if "Lufthansa" in (f.operating_carrier or f.marketing_carrier) or "Air Dolomiti" in (f.operating_carrier or f.marketing_carrier) or "LH" in (f.operating_carrier or f.marketing_carrier)]
    valid_returns = [f for f in return_flights if "Lufthansa" in (f.operating_carrier or f.marketing_carrier) or "Air Dolomiti" in (f.operating_carrier or f.marketing_carrier) or "LH" in (f.operating_carrier or f.marketing_carrier)]
    
    if not valid_outbounds and outbound_flights:
        valid_outbounds = outbound_flights # fallback if no LH flights found
    if not valid_returns and return_flights:
        valid_returns = return_flights
        
    if not valid_outbounds or not valid_returns:
        return 0, "fragile"
        
    combos = len(valid_outbounds) * len(valid_returns)
    if combos >= 4:
        classification = "strong_fit"
    elif combos >= 2:
        classification = "possible"
    else:
        classification = "fragile"
        
    # Find the earliest outbound (preferably after 06:00)
    best_outbound = None
    for f in sorted(valid_outbounds, key=lambda x: x.departure_time):
        t = parse_time(f.departure_time)
        if t and t.hour >= 6:
            best_outbound = f
            break
    if not best_outbound:
        best_outbound = valid_outbounds[0]
        
    # Find the latest return (preferably before 22:00)
    best_return = None
    for f in sorted(valid_returns, key=lambda x: x.departure_time, reverse=True):
        t = parse_time(f.departure_time)
        if t and t.hour <= 22:
            best_return = f
            break
    if not best_return:
        best_return = valid_returns[0]
        
    # Rough score: number of combinations + (late return bonus) + (good outbound bonus)
    score = combos * 10
    rt = parse_time(best_return.departure_time)
    if rt and rt.hour >= 16:
        score += 20
    elif rt and rt.hour >= 12:
        score += 10
        
    ot = parse_time(best_outbound.departure_time)
    if ot and 7 <= ot.hour <= 11:
        score += 20
        
    return score, classification

async def main():
    api_key = os.environ.get("SERPAPI_API_KEY")
    provider = SerpApiFlightScheduleProvider(api_key)
    
    origin = "FRA"
    outbound_date = "2026-08-07"
    return_date = "2026-08-09"
    
    results = []
    
    for city, iata in city_to_iata.items():
        print(f"Fetching {city} ({iata})...")
        outbound_res = await provider.get_flights(origin, iata, outbound_date, direct_only=True)
        return_res = await provider.get_flights(iata, origin, return_date, direct_only=True)
        
        outbound_flights = outbound_res.flights if outbound_res.status.value == "success" else []
        return_flights = return_res.flights if return_res.status.value == "success" else []
        
        score, classification = score_weekend_suitability(outbound_flights, return_flights)
        
        # Prepare for JSON
        def serialize_flights(flights):
            return [{
                "flight_number": f.flight_number,
                "airline": f.airline,
                "marketing_carrier": f.marketing_carrier,
                "operating_carrier": f.operating_carrier,
                "departure_time": f.departure_time,
                "arrival_time": f.arrival_time,
                "duration": f.duration
            } for f in flights]
            
        results.append({
            "destination": city,
            "iata": iata,
            "classification": classification,
            "score": score,
            "outbound_count": len(outbound_flights),
            "return_count": len(return_flights),
            "outbound_flights": serialize_flights(outbound_flights),
            "return_flights": serialize_flights(return_flights)
        })
        
    results.sort(key=lambda x: x["score"], reverse=True)
    
    os.makedirs("artifacts/inference", exist_ok=True)
    
    with open("artifacts/inference/full_flex_pool_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    # Generate Markdown
    md = "# Full-Flex-Restmengenanalyse (Live)\n\n"
    md += "**Parameter:** FRA, 07.08.2026 - 09.08.2026, Volle Flexibilität\n\n"
    
    for r in results:
        md += f"## {r['destination']} ({r['iata']}) - {r['classification'].upper()}\n"
        md += f"- **Ranking-Score:** {r['score']}\n"
        md += f"- **Hinflüge (FRA -> {r['iata']}):** {r['outbound_count']} direkt verfügbar\n"
        for f in r['outbound_flights']:
            op = f['operating_carrier'] or f['airline']
            md += f"  - {f['flight_number']} ({op}): {f['departure_time']} -> {f['arrival_time']}\n"
            
        md += f"- **Rückflüge ({r['iata']} -> FRA):** {r['return_count']} direkt verfügbar\n"
        for f in r['return_flights']:
            op = f['operating_carrier'] or f['airline']
            md += f"  - {f['flight_number']} ({op}): {f['departure_time']} -> {f['arrival_time']}\n"
        md += "\n"
        
    with open("artifacts/inference/full_flex_recommendation.md", "w", encoding="utf-8") as f:
        f.write(md)
        
    print("Analysis complete.")

if __name__ == "__main__":
    asyncio.run(main())
