import re

with open('artifacts/calendar_popover.html', encoding='utf-8') as f:
    html = f.read()

modal = re.findall(r'<div[^>]*class="[^"]*datepicker-modal[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
print("Found modals:", len(modal))
if modal:
    buttons = re.findall(r'<button[^>]*>(.*?)</button>', modal[0], re.DOTALL)
    print("Buttons inside modal:")
    for b in buttons:
        print(" -", b.strip())

# Look for any button with class or text related to close / apply / ok / save
all_buttons = re.findall(r'<button[^>]*class="([^"]*)"[^>]*>(.*?)</button>', html, re.DOTALL)
for c, txt in all_buttons:
    print(f"Button: class='{c}' text='{txt.strip()}'")
