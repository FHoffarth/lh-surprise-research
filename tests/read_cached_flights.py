import json

with open("artifacts/inference/full_flex_pool_analysis.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    dest = item.get("destination")
    iata = item.get("iata")
    if iata in ["WRO", "PRG", "WAW"] or dest in ["Breslau", "Prag", "Warschau"]:
        print(f"=== {dest} ({iata}) ===")
        print("Outbound flights:")
        for f in item.get("outbound_flights", []):
            print(f" - {f.get('flight_number')}: {f.get('departure_time')} -> {f.get('arrival_time')} (Carrier: {f.get('marketing_carrier')}/{f.get('operating_carrier')})")
