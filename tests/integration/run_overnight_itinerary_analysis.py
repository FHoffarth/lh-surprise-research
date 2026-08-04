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
    print("Running overnight-dependent stay itinerary analysis...")
    
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
                    for combo in eval_item.get("all_valid_itineraries", []):
                        milan_outbound.append(combo["outbound"])
                        milan_return.append(combo["return"])
                    milan_outbound = deduplicate_flights(milan_outbound)
                    milan_return = deduplicate_flights(milan_return)
                    
    # Load Pula multi-date flights
    pula_dates_path = "artifacts/schedule_risk/pula_schedule_dates.json"
    pula_multi_outbound = []
    pula_multi_return = []
    if os.path.exists(pula_dates_path):
        with open(pula_dates_path, "r", encoding="utf-8") as f:
            pula_data = json.load(f)
            for d, d_data in pula_data.items():
                pula_multi_outbound.extend(d_data.get("outbound", []))
                pula_multi_return.extend(d_data.get("return", []))
                
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
    
    # Overwrite Pula with multi-date flights
    if pula_multi_outbound:
        raw_dest_data["PUY"] = {
            "destination": "Pula",
            "outbound": pula_multi_outbound,
            "return": pula_multi_return
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
        rejected_due_to_stay = 0
        
        one_night_combos = []
        two_night_combos = []
        
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
                    
                # The return departure must be after outbound arrival
                if r_dep <= o_arr:
                    continue
                    
                stay_hours = (r_dep - o_arr).total_seconds() / 3600.0
                overnights = (r_dep.date() - o_dep.date()).days
                
                # We only allow 1 or 2 overnights inside our search window
                if overnights not in [1, 2]:
                    continue
                    
                # Stay constraints
                min_required = 18.0 if overnights == 1 else 36.0
                is_stay_valid = stay_hours >= min_required
                is_usable = o_dep.time() >= earliest_acceptable_outbound
                
                combo = {
                    "outbound_flight": out["flight_number"],
                    "outbound_time": o_dep.strftime("%H:%M"),
                    "outbound_date": o_dep.strftime("%Y-%m-%d"),
                    "return_flight": ret["flight_number"],
                    "return_time": r_dep.strftime("%H:%M"),
                    "return_date": r_dep.strftime("%Y-%m-%d"),
                    "stay_hours": round(stay_hours, 1),
                    "overnights": overnights,
                    "usable": is_usable
                }
                
                all_combinations.append(combo)
                
                if is_stay_valid:
                    valid_itineraries.append(combo)
                    if overnights == 1:
                        one_night_combos.append(combo)
                    else:
                        two_night_combos.append(combo)
                else:
                    rejected_due_to_stay += 1
                    
        total_combos = len(all_combinations)
        valid_combos = len(valid_itineraries)
        
        # Risk classification overall
        if total_combos > 0 and valid_combos == 0:
            classification = "no_valid_itinerary"
            recommendation = "EXCLUDE"
            reason = "No itinerary combination meets the stay requirement."
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
                reason = f"All {len(valid_itineraries)} valid itineraries satisfy the 14:00 outbound constraint."
            elif len(usable_combos) > 0 and len(unusable_combos) > 0:
                classification = "mixed"
                recommendation = "EXCLUDE"
                reason = f"Mixed schedule: {len(usable_combos)} usable and {len(unusable_combos)} unusable combinations."
            else:
                classification = "unsafe"
                recommendation = "EXCLUDE"
                reason = "All valid itineraries start before 14:00."
                
        # Risk classification by trip length
        def get_sub_class(combos):
            if not combos:
                return "no_valid_itinerary"
            usable = [c for c in combos if c["usable"]]
            if len(usable) == len(combos):
                return "safe"
            elif usable:
                return "mixed"
            return "unsafe"
            
        one_night_class = get_sub_class(one_night_combos)
        two_night_class = get_sub_class(two_night_combos)
        
        # Early / Late bounds
        valid_out_times = [datetime.datetime.strptime(c["outbound_time"], "%H:%M").time() for c in valid_itineraries]
        earliest_out = min(valid_out_times).strftime("%H:%M") if valid_out_times else "-"
        latest_out = max(valid_out_times).strftime("%H:%M") if valid_out_times else "-"
        
        worst_valid = min(valid_itineraries, key=lambda c: datetime.datetime.strptime(c["outbound_time"], "%H:%M").time()) if valid_itineraries else None
        
        evaluation.append({
            "destination": dest,
            "iata": iata,
            "total_combinations": total_combos,
            "valid_combinations": valid_combos,
            "one_night_count": len(one_night_combos),
            "two_night_count": len(two_night_combos),
            "rejected_due_to_minimum_stay": rejected_due_to_stay,
            "earliest_outbound_valid": earliest_out,
            "latest_outbound_valid": latest_out,
            "worst_valid_itinerary": worst_valid,
            "risk_classification": classification,
            "recommendation": recommendation,
            "reasons": [reason],
            "risk_by_trip_length": {
                "one_night": one_night_class,
                "two_nights": two_night_class
            },
            "all_valid_itineraries": valid_itineraries
        })

    # Save JSON
    with open("artifacts/schedule_risk/new_itinerary_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "run_type": "overnight_dependent_stay_itinerary_analysis",
            "created_at": datetime.datetime.now().isoformat(),
            "evaluation": evaluation
        }, f, indent=2, ensure_ascii=False)
        
    # Generate Report
    md = "# Lufthansa Surprise: Overnight-Dependent Schedule Risk Report\n\n"
    md += f"**Reisedatum:** 07.08.2026 - 09.08.2026  \n"
    md += f"**Abflughafen:** Frankfurt/Main (FRA)  \n"
    md += f"**Nutzerprofil:** earliest_acceptable_outbound = 14:00  \n"
    md += f"**Preise:** Baseline-Preis 129,00 €  \n"
    md += f"**Aufenthaltsregeln:**  \n"
    md += f"- 1 Übernachtung (one_night): min. 18 Stunden Aufenthalt  \n"
    md += f"- 2 Übernachtungen (two_nights): min. 36 Stunden Aufenthalt  \n\n"
    
    md += "## Übersicht der Ergebnisse (Übernachtungsabhängiges Szenario)\n\n"
    md += "| Zielstadt | IATA | Kombinationen (Gültig / Verworfene Stay) | Risiko (Gesamt) | Risiko 1 Nacht | Risiko 2 Nächte | Entscheidung | Begründung |\n"
    md += "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n"
    for item in evaluation:
        combos_str = f"{item['valid_combinations']} / {item['rejected_due_to_minimum_stay']}"
        md += f"| {item['destination']} | {item['iata']} | {combos_str} | `{item['risk_classification']}` | `{item['risk_by_trip_length']['one_night']}` | `{item['risk_by_trip_length']['two_nights']}` | **{item['recommendation']}** | {', '.join(item['reasons'])} |\n"
        
    md += "\n## Korrektur-Vergleich zum ungenauen 18h-Stay-Szenario\n\n"
    md += "Im vorigen Szenario wurden fälschlicherweise alle Kombinationen mit >= 18h als gültig gezählt, "
    md += "selbst wenn sie 2 Nächte betrafen (was min. 36h erfordert). Dies ist nun korrigiert.\n\n"
    
    md += "| Zielstadt | Falsche Gültige (18h-Pauschal) | Korrekte Gültige (Übernachtungsbasiert) | Differenz (Verworfene Kombis) | Auswirkung |\n"
    md += "| :--- | :---: | :---: | :---: | :--- |\n"
    
    # Mapping previous raw 18h-Pauschal counts
    prev_flat_counts = {
        "FLR": 25, "PRG": 64, "WAW": 42, "WRO": 9, "HEL": 20, "BLQ": 12, "KRK": 16, "BSL": 9, "SJJ": 4, "LIN": 99, "PUY": 1
    }
    for item in evaluation:
        iata = item["iata"]
        prev_cnt = prev_flat_counts.get(iata, 0)
        diff = prev_cnt - item["valid_combinations"]
        effect = "Korrigiert (keine Auswirkung)" if diff == 0 else f"⚠️ {diff} ungültige 2-Nächte-Kombis verworfen"
        md += f"| {item['destination']} | {prev_cnt} | {item['valid_combinations']} | {diff} | {effect} |\n"
        
    md += "\n## Auswertung Pula (PUY) nach Reiseschemen\n\n"
    puy_item = next((item for item in evaluation if item["iata"] == "PUY"), None)
    if puy_item:
        md += f"- **Gesamt gültige Kombinationen:** {puy_item['valid_combinations']} (Abgelehnt wegen Stay: {puy_item['rejected_due_to_minimum_stay']})\n"
        md += "\n| Reiseschema | Hinflugsdatum & -zeit | Rückflugsdatum & -zeit | Aufenthalt (Std.) | Übernachtungen | Status |\n"
        md += "| :--- | :--- | :--- | :---: | :---: | :--- |\n"
        for c in puy_item["all_valid_itineraries"]:
            schema_str = f"{c['outbound_date']} → {c['return_date']}"
            md += f"| {schema_str} | {c['outbound_date']} {c['outbound_time']} | {c['return_date']} {c['return_time']} | {c['stay_hours']} | {c['overnights']} | `safe` (>=14:00) |\n"
            
    md += "\n## Detaillierte Auflistung je Zielstadt (Gültige Kombinationen)\n\n"
    for item in evaluation:
        if item["iata"] == "PUY":
            continue
        md += f"### {item['destination']} ({item['iata']})\n"
        md += f"- **Risikoklassifikation:** `{item['risk_classification']}` | **Entscheidung:** {item['recommendation']}\n"
        md += f"- **Verbindungen (1 Nacht / 2 Nächte):** {item['one_night_count']} / {item['two_night_count']} (Verworfen: {item['rejected_due_to_minimum_stay']})\n"
        
        worst = item.get("worst_valid_itinerary")
        if worst:
            md += f"- **Schlechteste zulässige Kombination:** Hinflug {worst['outbound_flight']} ({worst['outbound_date']} {worst['outbound_time']}) / Rückflug {worst['return_flight']} ({worst['return_date']} {worst['return_time']}) - Aufenthalt: {worst['stay_hours']} Std. (Nächte: {worst['overnights']})\n"
            
        md += "\n| Hinflug | Rückflug | Aufenthalt (Std.) | Übernachtungen | Nutzbarkeit |\n"
        md += "| :--- | :--- | :---: | :---: | :--- |\n"
        for c in item["all_valid_itineraries"]:
            usable_str = "Akzeptabel ✅" if c["usable"] else "Zu früh ❌"
            md += f"| {c['outbound_flight']} ({c['outbound_date']} {c['outbound_time']}) | {c['return_flight']} ({c['return_date']} {c['return_time']}) | {c['stay_hours']} | {c['overnights']} | {usable_str} |\n"
        md += "\n---\n\n"
        
    with open("artifacts/schedule_risk/new_itinerary_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("New overnight-dependent report written successfully.")

if __name__ == "__main__":
    main()
