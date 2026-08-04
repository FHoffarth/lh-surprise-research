import json

with open("artifacts/inference/full_flex_pool_analysis.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Found IATAs in pool analysis:")
for item in data:
    print(f" - {item.get('iata')} (Outbound count: {item.get('outbound_count')}, Return count: {item.get('return_count')})")
