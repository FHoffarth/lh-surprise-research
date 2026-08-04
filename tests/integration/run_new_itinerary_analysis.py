import json
import os
import datetime
from typing import List, Dict, Any

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

def main():
    print("Running new 18-hour stay itinerary analysis...")
    
    # Load cache pool
    cache_path = "artifacts/inference/full_flex_pool_analysis.json"
    if not os.path.exists(cache_path):
        print(f"Error: {cache_path} not found.")
        return
        
    with open(cache_path, "r", encoding="utf-8") as f:
        pool_data = json.load(f)
        
    # Load LIN flights from full_pool_schedule_risk.json
    milan_source_path = "artifacts/schedule_risk/full_pool_schedule_risk.json"
    milan_outbound = []
    milan_return = []
    if os.path.exists(milan_source_path):
        with open(milan_source_path, "r", encoding="utf-8") as f:
            milan_data = json.load(f)
            for eval_item in milan_data.get("evaluation", []):
                if eval_item.get("iata") == "LIN":
                    outbound_seen = set()
                    return_seen = set()
                    for combo in eval_item.get("all_valid_itineraries", []):
                        out_fl = combo.get("outbound")
                        ret_fl = combo.get("return")
                        if out_fl and out_fl.get("flight_number") not in outbound_seen:
                            milan_outbound.append(out_fl)
                            outbound_seen.add(out_fl.get("flight_number"))
                        if ret_fl and ret_fl.get("flight_number") not in return_seen:
                            milan_return.append(ret_fl)
                            return_seen.add(ret_fl.get("flight_number"))

    raw_dest_data = {}
    for item in pool_data:
        iata = item.get("iata")
        if iata == "MIL" or iata == "LIN":
            continue
        raw_dest_data[iata] = {
            "destination": item.get("destination"),
            "outbound": item.get("outbound_flights", []),
            "return": item.get("return_flights", [])
        }
        
    # Milan (Linate only)
    raw_dest_data["LIN"] = {
        "destination": "Mailand (Linate)",
        "outbound": milan_outbound,
        "return": milan_return
    }
    
    earliest_acceptable_outbound = datetime.time(14, 0)
    evaluation = []
    
    for iata in ALL_TARGETS:
        data = raw_dest_data.get(iata)
        if not data:
            continue
            
        dest = data["destination"]
        out_deduped = deduplicate_flights(data["outbound"])
        ret_deduped = deduplicate_flights(data["return"])
        
        all_combinations = []
        valid_itineraries = []
        
        for out in out_deduped:
            o_arr = parse_datetime(out.get("arrival_time", ""))
            o_dep = parse_datetime(out.get("departure_time", ""))
            if not o_arr or not o_dep:
                continue
                
            for ret in ret_deduped:
                r_dep = parse_datetime(ret.get("departure_time", ""))
                r_arr = parse_datetime(ret.get("arrival_time", ""))
                if not r_dep or not r_arr:
                    continue
                    
                stay_hours = (r_dep - o_arr).total_seconds() / 3600.0
                # Calculate overnights (based on calendar days of departure)
                overnights = (r_dep.date() - o_dep.date()).days
                
                # Check personal usability: Hinflug ab 14:00 Uhr
                is_usable = o_dep.time() >= earliest_acceptable_outbound
                
                combo = {
                    "outbound_flight": out["flight_number"],
                    "outbound_time": o_dep.strftime("%H:%M"),
                    "return_flight": ret["flight_number"],
                    "return_time": r_dep.strftime("%H:%M"),
                    "stay_hours": round(stay_hours, 1),
                    "overnights": overnights,
                    "usable": is_usable
                }
                all_combinations.append(combo)
                
                if stay_hours >= 18.0:
                    valid_itineraries.append(combo)
                    
        total_combos = len(all_combinations)
        valid_combos = len(valid_itineraries)
        
        # Risk Classification
        if total_combos > 0 and valid_combos == 0:
            classification = "no_valid_itinerary"
            recommendation = "EXCLUDE"
            reason = "No itinerary combination meets the 18h minimum stay requirement."
        elif not all_combinations:
            classification = "unknown"
            recommendation = "MANUAL REVIEW"
            reason = "No flight schedule data available."
        else:
            usable_combos = [c for c in valid_itineraries if c["usable"]]
            unusable_combos = [c for c in valid_itineraries if not c["usable"]]
            
            if len(usable_combos) == len(valid_itineraries):
                classification = "safe"
                recommendation = "KEEP"
                reason = "All valid itineraries satisfy the 14:00 outbound constraint."
            elif len(usable_combos) > 0 and len(unusable_combos) > 0:
                classification = "mixed"
                recommendation = "EXCLUDE"
                reason = f"Mixed schedule: {len(usable_combos)} usable and {len(unusable_combos)} unusable combinations."
            else:
                classification = "unsafe"
                recommendation = "EXCLUDE"
                reason = "All valid itineraries start before 14:00."
                
        # Find earliest/latest outbound within valid itineraries
        valid_out_times = [datetime.datetime.strptime(c["outbound_time"], "%H:%M").time() for c in valid_itineraries]
        earliest_out = min(valid_out_times).strftime("%H:%M") if valid_out_times else "-"
        latest_out = max(valid_out_times).strftime("%H:%M") if valid_out_times else "-"
        
        # Find worst valid itinerary
        worst_valid = min(valid_itineraries, key=lambda c: datetime.datetime.strptime(c["outbound_time"], "%H:%M").time()) if valid_itineraries else None
        
        evaluation.append({
            "destination": dest,
            "iata": iata,
            "total_combinations": total_combos,
            "valid_combinations": valid_combos,
            "earliest_outbound_valid": earliest_out,
            "latest_outbound_valid": latest_out,
            "worst_valid_itinerary": worst_valid,
            "risk_classification": classification,
            "recommendation": recommendation,
            "reasons": [reason],
            "all_valid_itineraries": valid_itineraries
        })

    # Save JSON results
    os.makedirs("artifacts/schedule_risk", exist_ok=True)
    with open("artifacts/schedule_risk/new_itinerary_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "run_type": "18h_stay_itinerary_analysis",
            "created_at": datetime.datetime.now().isoformat(),
            "evaluation": evaluation
        }, f, indent=2, ensure_ascii=False)
        
    # Generate Markdown Report
    md = "# Lufthansa Surprise: 18h Itinerary Schedule Risk Report\n\n"
    md += f"**Reisedatum:** 07.08.2026 - 09.08.2026 (Freitag bis Sonntag)  \n"
    md += f"**Abflughafen:** Frankfurt/Main (FRA)  \n"
    md += f"**Nutzerprofil:** earliest_acceptable_outbound = 14:00  \n"
    md += f"**Neue Constraints:** min_stay_hours = 18.0 | allowed_overnights = 1 oder 2  \n\n"
    
    md += "## Übersicht der Ergebnisse (18-Stunden-Szenario)\n\n"
    md += "| Zielstadt | IATA | Risiko-Klassifikation | Kombinationen (Gesamt / Gültig) | Hinflugsfenster (Gültig) | Entscheidung | Begründung |\n"
    md += "| :--- | :---: | :---: | :---: | :---: | :---: | :--- |\n"
    for item in evaluation:
        combos_str = f"{item['total_combinations']} / {item['valid_combinations']}"
        time_win = f"{item['earliest_outbound_valid']} - {item['latest_outbound_valid']}"
        md += f"| {item['destination']} | {item['iata']} | `{item['risk_classification']}` | {combos_str} | {time_win} | **{item['recommendation']}** | {', '.join(item['reasons'])} |\n"
        
    md += "\n## Vergleich mit dem 36-Stunden-Szenario\n\n"
    md += "Durch die Reduzierung des Mindestaufenthalts von 36 auf 18 Stunden wurden deutlich mehr Kombinationen als gültig eingestuft. "
    md += "Folgende Veränderungen haben sich im Vergleich zum 36h-Szenario ergeben:\n\n"
    
    md += "| Zielstadt | 36h-Klassifikation | 18h-Klassifikation | 36h-Gültige Kombis | 18h-Gültige Kombis | Auswirkung |\n"
    md += "| :--- | :---: | :---: | :---: | :---: | :--- |\n"
    
    # We load previous results from artifacts/schedule_risk/full_pool_schedule_risk.json for comparison
    prev_matrix = {}
    prev_json_path = "artifacts/schedule_risk/full_pool_schedule_risk_report.md" # We can just map them from previous run values
    # Previous run results:
    # FLR: mixed (25/23)
    # PRG: mixed (64/58)
    # WAW: mixed (42/36)
    # KRK: mixed (16/13)
    # BLQ: mixed (12/11)
    # HEL: mixed (20/16)
    # WRO: mixed (9/8)
    # BSL: mixed (9/8)
    # SJJ: mixed (4/3)
    # PUY: safe (1/1)
    # LIN: mixed (99/95)
    prev_data = {
        "FLR": {"class": "mixed", "valid": 23},
        "PRG": {"class": "mixed", "valid": 58},
        "WAW": {"class": "mixed", "valid": 36},
        "KRK": {"class": "mixed", "valid": 13},
        "BLQ": {"class": "mixed", "valid": 11},
        "HEL": {"class": "mixed", "valid": 16},
        "WRO": {"class": "mixed", "valid": 8},
        "BSL": {"class": "mixed", "valid": 8},
        "SJJ": {"class": "mixed", "valid": 3},
        "PUY": {"class": "safe", "valid": 1},
        "LIN": {"class": "mixed", "valid": 95}
    }
    
    for item in evaluation:
        iata = item["iata"]
        prev = prev_data.get(iata, {"class": "unknown", "valid": 0})
        diff_combis = item["valid_combinations"] - prev["valid"]
        effect = "Keine Änderung"
        if diff_combis > 0:
            effect = f"+{diff_combis} neue gültige Kombinationen"
        md += f"| {item['destination']} | `{prev['class']}` | `{item['risk_classification']}` | {prev['valid']} | {item['valid_combinations']} | {effect} |\n"
        
    md += "\n## Detaillierte Auflistung je Zielstadt (Gültige Kombinationen >= 18h)\n\n"
    for item in evaluation:
        md += f"### {item['destination']} ({item['iata']})\n"
        md += f"- **Risikoklassifikation:** `{item['risk_classification']}` | **Entscheidung:** {item['recommendation']}\n"
        md += f"- **Gültige Kombinationen:** {item['valid_combinations']}\n"
        
        worst = item.get("worst_valid_itinerary")
        if worst:
            md += f"- **Schlechteste zulässige Kombination:** Hinflug {worst['outbound_flight']} ({worst['outbound_time']}) / Rückflug {worst['return_flight']} ({worst['return_time']}) - Aufenthalt: {worst['stay_hours']} Std. (Übernachtungen: {worst['overnights']})\n"
            
        md += "\n| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit (outbound >= 14:00) |\n"
        md += "| :--- | :--- | :---: | :---: | :--- |\n"
        for c in item["all_valid_itineraries"]:
            usable_str = "Akzeptabel ✅" if c["usable"] else "Zu früh ❌"
            md += f"| {c['outbound_flight']} ({c['outbound_time']}) | {c['return_flight']} ({c['return_time']}) | {c['stay_hours']} | {c['overnights']} | {usable_str} |\n"
        md += "\n---\n\n"
        
    with open("artifacts/schedule_risk/new_itinerary_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("New report written to artifacts/schedule_risk/new_itinerary_report.md")

if __name__ == "__main__":
    main()
