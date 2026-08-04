import json
import datetime

def main():
    with open("artifacts/puy_differential/puy_diff_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    results = data["results"]
    res_a = results[0]
    res_b = results[1]
    res_c = results[2]
    
    status_a = res_a.get("status")
    status_b = res_b.get("status")
    status_c = res_c.get("status")
    price_a = res_a.get("price")
    price_b = res_b.get("price")
    price_c = res_c.get("price")
    
    interpretation = "unknown"
    if status_a == "available" and status_b == "unavailable" and status_c == "available":
        interpretation = "PUY_is_necessary_observed_deal_trigger"
    elif status_a == "available" and status_b == "available":
        interpretation = "PUY_not_necessary_for_offer"
    elif status_a != status_c or price_a != price_c:
        interpretation = "inventory_or_session_unstable"
        
    # Extract request params from Test A availability
    dates_found = "Not found"
    stay_found = "Not found"
    targets_found = "Not found"
    
    for r in res_a.get("json_requests", []):
        if "availability" in r["url"] and r.get("post_data"):
            try:
                pd = json.loads(r["post_data"])
                dates_found = f"{pd.get('earliestOut')} bis {pd.get('latestRet')}"
                stay_found = f"minStay: {pd.get('minStay')} | maxStay: {pd.get('maxStay')} | availableStayValues: {pd.get('availableStayValues')}"
                active_list = [d["label"] for d in pd.get("poolDestinationsData", []) if d.get("active")]
                targets_found = f"{len(active_list)} targets: {active_list}"
                break
            except:
                pass

    md = "# Lufthansa Surprise: PUY Differential-Test Abschlussbericht\n\n"
    md += f"**Ausgeführt am:** {data['timestamp']}  \n\n"
    
    md += "## Testergebnisse Übersicht\n\n"
    md += "| Test | Beschreibung | Status | Preis | Checkboxen bewiesen |\n"
    md += "| :--- | :--- | :---: | :---: | :---: |\n"
    md += f"| Test A | All 11 active (Baseline) | `{status_a}` | {price_a or '-'} | {'✅' if res_a.get('cb_verified') else '❌'} |\n"
    md += f"| Test B | PUY deactivated | `{status_b}` | {price_b or '-'} | {'✅' if res_b.get('cb_verified') else '❌'} |\n"
    md += f"| Test C | PUY re-activated (Repeat) | `{status_c}` | {price_c or '-'} | {'✅' if res_c.get('cb_verified') else '❌'} |\n\n"
    
    md += "## Interpretation & Abhängigkeitsbewertung\n\n"
    md += f"- **Ergebnis-Klassifikation:** `{interpretation}`\n"
    if interpretation == "PUY_is_necessary_observed_deal_trigger":
        md += "- **Aussage:** `PUY` ist in diesem frischen Lauf ein **notwendiger beobachteter Deal-Trigger**. Ohne PUY erzeugt das System kein Angebot.\n"
    elif interpretation == "PUY_not_necessary_for_offer":
        md += f"- **Aussage:** `PUY` ist nicht notwendig für das Zustandekommen eines Deals. Preisunterschied: {price_a} (mit PUY) vs. {price_b} (ohne PUY).\n"
    elif interpretation == "inventory_or_session_unstable":
        md += "- **Aussage:** `inventory_or_session_unstable`. Test A und Test C weisen unterschiedliche Preise/Status auf. Keine verlässliche Schlussfolgerung möglich.\n"
        
    md += f"\n## Request-Parametervalidierung (Test A)\n"
    md += f"- **Suchdaten:** `{dates_found}`  \n"
    md += f"- **Aufenthaltsdauer:** `{stay_found}`  \n"
    md += f"- **Übertragene Zielcodes:** `{targets_found}`  \n"
    
    with open("artifacts/puy_differential/puy_diff_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("Regenerated report successfully.")

if __name__ == "__main__":
    main()
