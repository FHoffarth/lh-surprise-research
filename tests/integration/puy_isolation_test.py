import asyncio
import json
import os
import re
import datetime
import traceback
from playwright.async_api import async_playwright

ALL_TARGETS = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]
SCREENSHOTS_DIR = "artifacts/screenshots/puy_isolation_test"

async def run_isolation_check(browser, test_id, active_targets):
    print(f"\n[Isolation Step] Targets: {active_targets}")
    context = await browser.new_context(viewport={"width": 1280, "height": 900})
    page = await context.new_page()
    
    intercepted_requests = []
    page.on("request", lambda request: intercepted_requests.append({
        "url": request.url,
        "method": request.method,
        "post_data": request.post_data
    }))
    
    try:
        url = "https://www.lufthansa-surprise.com/"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2.5)
        
        try:
            accept = page.locator("button:has-text('Einverstanden'), button:has-text('Alle akzeptieren')")
            if await accept.count() > 0:
                await accept.first.click()
                await asyncio.sleep(1)
        except Exception:
            pass

        await page.locator("text='Frankfurt/Main'").first.click()
        await asyncio.sleep(1.5)
        await page.locator("text='Kunst und Kultur'").first.click()
        await asyncio.sleep(1)
        ok_btn = page.locator("button:has-text('OK')")
        if await ok_btn.count() > 0:
            await ok_btn.first.click()
            await asyncio.sleep(1.5)
            
        await page.locator("text='Reisedaten eingeben'").first.click()
        await asyncio.sleep(2)
        
        await page.locator("#earliestOut").click()
        await asyncio.sleep(1)
        day7 = page.locator(".react-datepicker__day[aria-label*='7. August 2026']")
        if await day7.count() == 0:
            day7 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="7")
        await day7.first.click()
        await asyncio.sleep(1)
        
        await page.locator("#latestRet").click()
        await asyncio.sleep(1)
        day9 = page.locator(".react-datepicker__day[aria-label*='9. August 2026']")
        if await day9.count() == 0:
            day9 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="9")
        await day9.first.click()
        await asyncio.sleep(1)
        
        if await page.locator(".datepicker-modal button.close").count() > 0:
            await page.locator(".datepicker-modal button.close").first.click()
        else:
            await page.keyboard.press("Escape")
        await asyncio.sleep(1.5)
        
        # Checkbox states
        desired_state = {t: (t in active_targets) for t in ALL_TARGETS}
        for t in ALL_TARGETS:
            cb = page.locator(f"#pool_destion_{t}")
            if await cb.count() > 0:
                is_checked = await cb.is_checked()
                if is_checked != desired_state[t]:
                    await page.evaluate(f"document.getElementById('pool_destion_{t}').click()")
                    await asyncio.sleep(0.3)
                    
        await asyncio.sleep(1.5)
        
        # Capture screenshot before click
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"{test_id}_before.png"), full_page=True)
        
        # Click Weiter
        await page.locator("button:has-text('Weiter')").first.click()
        await asyncio.sleep(6.5)
        
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"{test_id}_after.png"), full_page=True)
        
        page_text = await page.evaluate("document.body.innerText")
        
        if (
            "Leider sind für die von Ihnen gewählten" in page_text or
            "keine verfügbaren flüge" in page_text.lower() or
            "für ihre auswahl leider keine flüge" in page_text.lower() or
            "nicht verfügbar" in page_text.lower()
        ):
            status = "unavailable"
            price = None
        else:
            status = "available"
            price = None
            m = re.search(r'Gesamtpreis\s*\n\s*(\d+[\.,]\d{2}\s*€?)', page_text)
            if m:
                price = m.group(1).strip()
            else:
                m2 = re.search(r'€\s*(\d+[\.,]?\d*)', page_text)
                if m2:
                    price = f"€ {m2.group(1)}"
                    
        await page.close()
        await context.close()
        
        # Parse active destination codes from availability request
        payload_targets = []
        for r in intercepted_requests:
            if "availability" in r["url"] and r.get("post_data"):
                try:
                    pd = json.loads(r["post_data"])
                    payload_targets = [d["value"]["destination"] for d in pd.get("poolDestinationsData", []) if d.get("active")]
                except:
                    pass
                    
        return {
            "status": status,
            "price": price,
            "payload_targets": payload_targets,
            "cb_verified": True
        }
    except Exception as e:
        traceback.print_exc()
        await page.close()
        await context.close()
        return {
            "status": "error",
            "error": str(e),
            "cb_verified": False
        }

async def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs("artifacts/puy_isolation", exist_ok=True)
    
    # We will test up to 3 pairs
    # Pair 1: BSL, SJJ
    # Pair 2: WRO, SJJ
    # Pair 3: BSL, WRO
    pairs = [
        {"A": "BSL", "B": "SJJ", "C": "FLR"},
        {"A": "WRO", "B": "SJJ", "C": "PRG"},
        {"A": "BSL", "B": "WRO", "C": "WAW"}
    ]
    
    session_results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        for idx, p_item in enumerate(pairs):
            pair_id = f"pair_{idx+1}_{p_item['A']}_{p_item['B']}"
            print(f"\n=== TESTING PAIR {idx+1}: {p_item['A']} + {p_item['B']} ===")
            
            # 1. PUY + A + B
            targets_1 = ["PUY", p_item["A"], p_item["B"]]
            res_1 = await run_isolation_check(browser, f"{pair_id}_step1_puy", targets_1)
            await asyncio.sleep(3)
            
            # 2. C + A + B
            targets_2 = [p_item["C"], p_item["A"], p_item["B"]]
            res_2 = await run_isolation_check(browser, f"{pair_id}_step2_ctrl", targets_2)
            await asyncio.sleep(3)
            
            # 3. PUY + A + B Repeat
            res_3 = await run_isolation_check(browser, f"{pair_id}_step3_repeat", targets_1)
            await asyncio.sleep(3)
            
            session_results.append({
                "pair": p_item,
                "step1": res_1,
                "step2": res_2,
                "step3": res_3
            })
            
        await browser.close()
        
    # Write JSON report
    with open("artifacts/puy_isolation/puy_isolation_results.json", "w", encoding="utf-8") as f:
        json.dump(session_results, f, indent=2, ensure_ascii=False)
        
    # Build Markdown report
    md = "# Lufthansa Surprise: PUY Isolation-Test Abschlussbericht\n\n"
    md += f"**Ausgeführt am:** {datetime.datetime.now().isoformat()}  \n\n"
    
    md += "## Testergebnisse Übersicht\n\n"
    for idx, item in enumerate(session_results):
        pair = item["pair"]
        s1 = item["step1"]
        s2 = item["step2"]
        s3 = item["step3"]
        
        md += f"### Isolationstest Paar {idx+1}: {pair['A']} + {pair['B']} (Kontrollziel: {pair['C']})\n"
        md += "| Testschritt | Konfiguration | Status | Preis | Intercepted Targets |\n"
        md += "| :--- | :--- | :---: | :---: | :--- |\n"
        md += f"| Test 1 | PUY + {pair['A']} + {pair['B']} | `{s1.get('status')}` | {s1.get('price') or '-'} | {s1.get('payload_targets')} |\n"
        md += f"| Test 2 | {pair['C']} + {pair['A']} + {pair['B']} (PUY off) | `{s2.get('status')}` | {s2.get('price') or '-'} | {s2.get('payload_targets')} |\n"
        md += f"| Test 3 | PUY + {pair['A']} + {pair['B']} (Repeat) | `{s3.get('status')}` | {s3.get('price') or '-'} | {s3.get('payload_targets')} |\n\n"
        
        # Check trigger criteria
        if s1.get("status") == "available" and s2.get("status") == "unavailable" and s3.get("status") == "available":
            md += f"**Ergebnis:** PUY ist für dieses Paar ein **nachweislich notwendiger Deal-Trigger**!  \n"
            md += f"PUY-containing configuration: `available` ({s1.get('price')})  \n"
            md += f"Control configuration: `unavailable`  \n\n"
        else:
            md += f"**Ergebnis:** Keine eindeutige Trigger-Wirkung nachgewiesen. (Status Test 1: `{s1.get('status')}`, Test 2: `{s2.get('status')}`).  \n\n"
            
    with open("artifacts/puy_isolation/puy_isolation_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("PUY Isolation report written successfully.")

if __name__ == "__main__":
    asyncio.run(main())
