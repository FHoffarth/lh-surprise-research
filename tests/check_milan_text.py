with open("artifacts/step2_page_text.txt", encoding="utf-8") as f:
    text = f.read()

print("Mailand occurrences in step2_page_text.txt:")
for line in text.split("\n"):
    if "Mailand" in line or "LIN" in line or "MXP" in line:
        print(line)
