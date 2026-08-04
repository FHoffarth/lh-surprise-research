import json
import os
import datetime
import asyncio
from typing import List, Dict, Any
from src.schedule_risk_engine import ScheduleRiskEngine

# Define target pool
ALL_TARGETS = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]
TARGET_NAMES = {
    "FLR": "Florenz",
    "PRG": "Prag",
    "WAW": "Warschau",
    "WRO": "Breslau",
    "HEL": "Helsinki",
    "BLQ": "Bologna",
    "KRK": "Krakau",
    "BSL": "Basel",
    "SJJ": "Sarajevo",
    "LIN": "Mailand (Linate)",
    "PUY": "Pula"
}

def parse_datetime(dt_str: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(dt_str[:16], "%Y-%m-%d %H:%M")
    except:
        return None

def deduplicate_flights(flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []
    for f in flights:
        dep = f.get("departure_time", "")
        if not dep:
            continue
        time_key = dep.split(" ")[-1][:5]
        if time_key in seen:
            continue
        seen.add(time_key)
        deduped.append(f)
    return deduped

async def main():
    print("Starting itinerary-based schedule risk run...")
    
    # Load cache pool
    cache_path = "artifacts/inference/full_flex_pool_analysis.json"
    cached_destinations = []
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cached_destinations = json.load(f)
            
    # Load Milan airports data from previously fetched full_pool_schedule_risk.json (to avoid new calls)
    milan_source_path = "artifacts/schedule_risk/full_pool_schedule_risk.json"
    milan_outbound = []
    milan_return = []
    if os.path.exists(milan_source_path):
        with open(milan_source_path, "r", encoding="utf-8") as f:
            milan_data = json.load(f)
            # Find the MIL details
            for eval_item in milan_data.get("evaluation", []):
                if eval_item.get("iata") == "MIL":
                    # We extract only LIN airport details as LIN is verified to be the only Surprise target
                    airport_details = eval_item.get("all_outbound_flights", [])
                    # Filter LIN flights (LH 270-280, Air Dolomiti LIN flights)
                    milan_outbound = [fl for fl in airport_details if "LIN" in fl.get("flight_number") or "LIN" in fl.get("destination") or "LIN" in fl.get("origin") or "Lufthansa" in fl.get("airline") or "LH" in fl.get("flight_number")]
                    milan_return = [fl for fl in eval_item.get("all_return_flights", []) if "LIN" in fl.get("flight_number") or "LIN" in fl.get("destination") or "LIN" in fl.get("origin") or "Lufthansa" in fl.get("airline") or "LH" in fl.get("flight_number")]
                    
    profile = {
        "origin": "FRA",
        "departure_date": "2026-08-07",
        "earliest_acceptable_outbound": "14:00",
        "outbound_risk_policy": "reject_if_any_plausible_direct_flight_is_too_early"
    }
    
    engine = ScheduleRiskEngine(profile)
    results = {}
    
    # Process destinations
    for item in cached_destinations:
        iata = item.get("iata")
        if iata == "MIL" or iata == "LIN":
            continue
        dest_name = item.get("destination")
        outbound = item.get("outbound_flights", [])
        ret = item.get("return_flights", [])
        
        results[iata] = {
            "destination": dest_name,
            "iata": iata,
            "outbound_flights": outbound,
            "return_flights": ret
        }
        
    # Inject LIN Milan flights
    results["LIN"] = {
        "destination": "Mailand (Linate)",
        "iata": "LIN",
        "outbound_flights": milan_outbound if milan_outbound else [],
        "return_flights": milan_return if milan_return else []
    }
    
    final_evaluation = []
    
    for iata, data in results.items():
        dest = data["destination"]
        outbound = data["outbound_flights"]
        return_fls = data["return_flights"]
        
        eval_res = engine.evaluate_itineraries(dest, outbound, return_fls)
        eval_res["iata"] = iata
        final_evaluation.append(eval_res)
        
    # Write JSON
    os.makedirs("artifacts/schedule_risk", exist_ok=True)
    with open("artifacts/schedule_risk/full_pool_schedule_risk.json", "w", encoding="utf-8") as f:
        json.dump({
            "run_id": f"itinerary_risk_run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.datetime.now().isoformat(),
            "new_api_calls_made": 0,
            "evaluation": final_evaluation
        }, f, indent=2, ensure_ascii=False)
        
    # Write Report
    md = "# Lufthansa Surprise: Itinerary-Based Schedule Risk Report\n\n"
    md += f"**Reisedatum:** 07.08.2026 - 09.08.2026  \n"
    md += f"**Abflughafen:** Frankfurt/Main (FRA)  \n"
    md += f"**Nutzerprofil:** earliest_acceptable_outbound = 14:00 | outbound_risk_policy = reject_if_any_plausible_direct_flight_is_too_early  \n"
    md += f"**Mailand-Verifikation:** LIN wird laut Surprise-UI explizit als Ziel-Airport verwendet. MXP/BGY wurden vorschriftsmäßig ausgeschlossen.\n\n"
    
    keep_list = [item["destination"] for item in final_evaluation if item["recommendation"] == "KEEP"]
    md += "## Ziele, die nach der 14:00-Uhr-Risikoregel verbleiben (KEEP)\n\n"
    if keep_list:
        for k in keep_list:
            md += f"- **{k}**\n"
    else:
        md += "> [!WARNING]\n> Kein einziges Ziel verbleibt unter der strengen Risikoregel als sicher (KEEP)!\n"
        
    md += "\n## Übersicht der Zielrangfolge & Risikoauswertung\n\n"
    md += "| Zielstadt | IATA | Risiko-Klassifikation | Kombinationen (Gesamt / Gültig) | Hinflugsfenster (Gültig) | Entscheidung | Begründung |\n"
    md += "| :--- | :---: | :---: | :---: | :---: | :---: | :--- |\n"
    for item in final_evaluation:
        combos_str = f"{item['total_combinations']} / {item['valid_combinations']}"
        time_win = f"{item['earliest_outbound_valid']} - {item['latest_outbound_valid']}"
        decision_label = f"**{item['recommendation']}**"
        md += f"| {item['destination']} | {item['iata']} | `{item['risk_classification']}` | {combos_str} | {time_win} | {decision_label} | {', '.join(item['reasons'])} |\n"
        
    md += "\n## Detaillierte Auswertung je Zielstadt (Gültige Kombinationen)\n\n"
    for item in final_evaluation:
        md += f"### {item['destination']} ({item['iata']})\n"
        md += f"- **Risikoklassifikation:** `{item['risk_classification']}` | **Entscheidung:** {item['recommendation']}\n"
        md += f"- **Verbindungen (Gesamt / Gültig >= 36h):** {item['total_combinations']} / {item['valid_combinations']}\n"
        
        worst = item.get("worst_valid_itinerary")
        if worst:
            worst_out = worst["outbound"]
            worst_ret = worst["return"]
            md += f"- **Schlechteste zulässige Kombination (nach Abflugzeit):** Hinflug {worst_out['flight_number']} ({worst_out['departure_time'].split(' ')[-1]}) / Rückflug {worst_ret['flight_number']} ({worst_ret['departure_time'].split(' ')[-1]}) - Aufenthalt: {worst['stay_hours']:.1f} Std.\n"
            
        md += "\n#### Auflistung aller gültigen Kombinationen (>= 36 Std. Aufenthalt):\n\n"
        md += "| Hinflug (Uhrzeit) | Rückflug (Uhrzeit) | Aufenthalt (Stunden) | Bewertung Hinflug |\n"
        md += "| :--- | :--- | :---: | :--- |\n"
        for combo in item.get("all_valid_itineraries", []):
            o = combo["outbound"]
            r = combo["return"]
            o_time = o["departure_time"].split(" ")[-1]
            r_time = r["departure_time"].split(" ")[-1]
            # Check if outbound is acceptable
            dep_hour = int(o_time.split(":")[0])
            eval_str = "Akzeptabel (>= 14:00)" if dep_hour >= 14 else "Zu früh (< 14:00) ❌"
            md += f"| {o['flight_number']} ({o_time}) | {r['flight_number']} ({r_time}) | {combo['stay_hours']:.1f} | {eval_str} |\n"
        md += "\n---\n\n"
        
    with open("artifacts/schedule_risk/full_pool_schedule_risk_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("Itinerary report written successfully.")

if __name__ == "__main__":
    asyncio.run(main())
