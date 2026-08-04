import json
import os
from src.schedule_risk_engine import ScheduleRiskEngine

def main():
    print("Running Schedule Risk Engine Live-Test...")
    
    # Define user profile
    profile = {
        "origin": "FRA",
        "departure_date": "2026-08-07",
        "earliest_acceptable_outbound": "14:00",
        "outbound_risk_policy": "reject_if_any_plausible_direct_flight_is_too_early"
    }
    
    engine = ScheduleRiskEngine(profile)
    
    # Load flights from full_flex_pool_analysis.json
    cache_path = "artifacts/inference/full_flex_pool_analysis.json"
    if not os.path.exists(cache_path):
        print(f"Error: {cache_path} not found.")
        return
        
    with open(cache_path, "r", encoding="utf-8") as f:
        pool_data = json.load(f)
        
    target_iatas = ["WRO", "PRG", "WAW"]
    results = {}
    
    for item in pool_data:
        iata = item.get("iata")
        dest = item.get("destination")
        if iata in target_iatas:
            # Prepare flights for the engine
            flights = []
            for f in item.get("outbound_flights", []):
                flights.append({
                    "flight_number": f.get("flight_number"),
                    "airline": f.get("airline"),
                    "marketing_carrier": f.get("marketing_carrier"),
                    "operating_carrier": f.get("operating_carrier"),
                    "departure_time": f.get("departure_time"),
                    "arrival_time": f.get("arrival_time")
                })
            
            res = engine.evaluate_destination_risk(dest, flights)
            # Add iata code to result
            res["iata"] = iata
            results[iata] = res

    # Write JSON results
    os.makedirs("artifacts/schedule_risk", exist_ok=True)
    with open("artifacts/schedule_risk/schedule_risk_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Saved results to artifacts/schedule_risk/schedule_risk_results.json")
    
    # Write Markdown report
    md = "# Lufthansa Surprise: Schedule Risk Engine Report\n\n"
    md += f"**Reisedatum:** Freitag, 07.08.2026  \n"
    md += f"**Abflughafen:** Frankfurt/Main (FRA)  \n"
    md += f"**Früheste akzeptable Abflugzeit:** {profile['earliest_acceptable_outbound']} Uhr  \n"
    md += f"**Risikopolitik:** `reject_if_any_plausible_direct_flight_is_too_early` (Ausschließen, wenn ein möglicher Direktflug vor der akzeptablen Zeit liegt)  \n\n"
    
    md += "## Übersicht der Ergebnisse\n\n"
    md += "| Zielstadt | IATA | Risiko-Klassifikation | Entscheidung | Gründe |\n"
    md += "| :--- | :---: | :---: | :---: | :--- |\n"
    for iata in target_iatas:
        res = results.get(iata)
        if not res:
            continue
        decision_label = "**KEEP**" if res["recommendation"] == "KEEP" else f"**{res['recommendation']}**"
        md += f"| {res['destination']} | {iata} | `{res['risk_classification']}` | {decision_label} | {', '.join(res['reasons'])} |\n"
        
    md += "\n## Detaillierte Flugplanauswertung\n\n"
    for iata in target_iatas:
        res = results.get(iata)
        if not res:
            continue
        md += f"### {res['destination']} ({iata}) - Risikoklassifikation: `{res['risk_classification']}`\n\n"
        md += f"- **Entscheidung:** {res['recommendation']}\n"
        if res['uncertainty_notes']:
            md += f"- **Unsicherheitshinweis:** {res['uncertainty_notes']}\n"
            
        md += "\n#### Gefundene Flüge (Dedupliziert):\n\n"
        md += "| Flugnummer | Abflugzeit | Ankunftszeit | Bewertung |\n"
        md += "| :--- | :---: | :---: | :---: |\n"
        
        acc_nums = [f["flight_number"] for f in res["acceptable_outbound_flights"]]
        for f in res["all_outbound_flights"]:
            is_acc = "Akzeptabel (>= 14:00)" if f["flight_number"] in acc_nums else "Zwei-Früh (< 14:00) ❌"
            md += f"| {f['flight_number']} | {f['departure_time'].split(' ')[-1]} | {f['arrival_time'].split(' ')[-1]} | {is_acc} |\n"
        md += "\n"
        
    with open("artifacts/schedule_risk/schedule_risk_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("Saved report to artifacts/schedule_risk/schedule_risk_report.md")

if __name__ == "__main__":
    main()
