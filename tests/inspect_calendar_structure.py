import re

with open('artifacts/calendar_popover.html', encoding='utf-8') as f:
    html = f.read()

# Let's find react-datepicker elements
print("Datepicker classes found:")
classes = set(re.findall(r'class="([^"]*react-datepicker[^"]*)"', html))
for c in sorted(classes):
    print(" -", c)

# Check for navigation buttons (next month, prev month)
buttons = re.findall(r'<button[^>]*class="[^"]*react-datepicker[^"]*"[^>]*>.*?</button>', html, re.DOTALL)
print("\nButtons:", len(buttons))
for b in buttons:
    print(b)

# Check for days in August
days = re.findall(r'<div[^>]*class="[^"]*react-datepicker__day[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
print("\nDay elements count:", len(days))
sample_days = re.findall(r'<div[^>]*class="[^"]*react-datepicker__day[^"]*"[^>]*aria-label="([^"]*)"[^>]*>', html)
for sd in sample_days[:15]:
    print(" - Day aria-label:", sd)
