import re
with open('artifacts/calendar_popover.html', encoding='utf-8') as f:
    html = f.read()

# Let's find month navigation buttons or month text
months = re.findall(r'<div[^>]*class="[^"]*month[^"]*"[^>]*>(.*?)</div>', html, re.IGNORECASE)
print("Months:", months[:10])

# Look for standard flatpickr or bootstrap datepicker
if 'flatpickr' in html.lower():
    print("Uses flatpickr")
if 'datepicker' in html.lower():
    print("Uses datepicker")
