import asyncio
import json
import os
import re
import datetime
import traceback
from playwright.async_api import async_playwright

ALL_TARGETS = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]
SCREENSHOTS_DIR = "artifacts/screenshots/puy_diff_test"

async def run_single_puy_check(browser, test_id, description, active_targets):
    print(f"\n==================================================")
    print(f"RUNNING TEST [{test_id}]: {description}")
    print(f"Active targets: {active_targets}")
    print(f"==================================================")
    
    context = await browser.new_context(viewport={"width": 1280, "height": 900})
    page = await context.new_page()
    
    intercepted_requests = []
    page.on("request", lambda request: intercepted_requests.append({
        "url": request.url,
        "method": request.method,
        "post_data": request.post_data
    }))
    
    timestamp_start = datetime.datetime.now().isoformat()
    
    try:
        url = "https://www.lufthansa-surprise.com/"
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        
        # Cookies
        try:
            accept = page.locator("button:has-text('Einverstanden'), button:has-text('Alle akzeptieren')")
            if await accept.count() > 0:
                await accept.first.click()
                await asyncio.sleep(1.5)
        except Exception:
            pass

        # Frankfurt/Main
        await page.locator("text='Frankfurt/Main'").first.click()
        await asyncio.sleep(2)
        
        # Theme
        await page.locator("text='Kunst und Kultur'").first.click()
        await asyncio.sleep(1.5)
        
        ok_btn = page.locator("button:has-text('OK')")
        if await ok_btn.count() > 0:
            await ok_btn.first.click()
            await asyncio.sleep(2)
            
        # Reisedaten
        await page.locator("text='Reisedaten eingeben'").first.click()
        await asyncio.sleep(3)
        
        # Date Clicks
        await page.locator("#earliestOut").click()
        await asyncio.sleep(1.5)
        day7 = page.locator(".react-datepicker__day[aria-label*='7. August 2026']")
        if await day7.count() == 0:
            day7 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="7")
        await day7.first.click()
        await asyncio.sleep(1.5)
        
        await page.locator("#latestRet").click()
        await asyncio.sleep(1.5)
        day9 = page.locator(".react-datepicker__day[aria-label*='9. August 2026']")
        if await day9.count() == 0:
            day9 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="9")
        await day9.first.click()
        await asyncio.sleep(1.5)
        
        # Close modal
        close_btn = page.locator(".datepicker-modal button.close, button.closeButton")
        if await close_btn.count() > 0 and await close_btn.is_visible():
            await close_btn.first.click()
        else:
            await page.keyboard.press("Escape")
        await asyncio.sleep(2)
        
        # Toggle checkboxes
        desired_state = {t: (t in active_targets) for t in ALL_TARGETS}
        for t in ALL_TARGETS:
            cb = page.locator(f"#pool_destion_{t}")
            if await cb.count() > 0:
                is_checked = await cb.is_checked()
                if is_checked != desired_state[t]:
                    await page.evaluate(f"document.getElementById('pool_destion_{t}').click()")
                    await asyncio.sleep(0.3)
                    
        await asyncio.sleep(2)
        
        # Confirm Checkboxes
        mismatches = []
        actual_cb_state = {}
        for t in ALL_TARGETS:
            cb = page.locator(f"#pool_destion_{t}")
            if await cb.count() > 0:
                actual = await cb.is_checked()
                actual_cb_state[t] = actual
                if actual != desired_state[t]:
                    mismatches.append(f"{t}: expected {desired_state[t]}, got {actual}")
            else:
                mismatches.append(f"{t} not found")
                
        cb_verified = len(mismatches) == 0
        
        before_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_before.png")
        await page.screenshot(path=before_screenshot, full_page=True)
        
        if not cb_verified:
            print(f"[{test_id}] Checkbox state verification failed! Mismatches: {mismatches}")
            await page.close()
            await context.close()
            return {
                "test_id": test_id,
                "description": description,
                "status": "validation_failed",
                "error": f"Checkbox mismatch: {mismatches}",
                "cb_verified": False
            }
            
        # Click Weiter
        weiter = page.locator("button:has-text('Weiter')")
        await weiter.first.click()
        print(f"[{test_id}] Clicked Weiter. Waiting for response...")
        await asyncio.sleep(7)
        
        after_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_after.png")
        await page.screenshot(path=after_screenshot, full_page=True)
        
        page_text = await page.evaluate("document.body.innerText")
        
        if "Security check" in page_text or "Sicherheitscheck" in page_text or "resembles that of a bot" in page_text:
            status = "blocked"
            price = None
            details = "Bot security check triggered"
        elif (
            "Leider sind für die von Ihnen gewählten" in page_text or
            "keine verfügbaren flüge" in page_text.lower() or
            "für ihre auswahl leider keine flüge" in page_text.lower() or
            "nicht verfügbar" in page_text.lower()
        ):
            status = "unavailable"
            price = None
            details = "Explicit no-availability on UI"
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
            details = "Offer page loaded"
            
        await page.close()
        await context.close()
        
        # Analyze intercepted requests
        json_reqs = [r for r in intercepted_requests if "jsonapi" in r["url"]]
        
        return {
            "test_id": test_id,
            "description": description,
            "timestamp_start": timestamp_start,
            "timestamp_end": datetime.datetime.now().isoformat(),
            "active_targets": active_targets,
            "status": status,
            "price": price,
            "details": details,
            "cb_verified": True,
            "json_requests": json_reqs
        }
    except Exception as e:
        traceback.print_exc()
        await page.close()
        await context.close()
        return {
            "test_id": test_id,
            "description": description,
            "status": "error",
            "error": str(e)
        }

async def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs("artifacts/puy_differential", exist_ok=True)
    
    test_results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        try:
            # Test A: All 11 targets active
            res_a = await run_single_puy_check(
                browser,
                test_id="test_a_all_active",
                description="Test A: All 11 Targets Active",
                active_targets=ALL_TARGETS
            )
            test_results.append(res_a)
            
            # Test B: PUY deactivated (10 active)
            await asyncio.sleep(4)
            puy_inactive = [t for t in ALL_TARGETS if t != "PUY"]
            res_b = await run_single_puy_check(
                browser,
                test_id="test_b_puy_inactive",
                description="Test B: PUY Deactivated (10 Active)",
                active_targets=puy_inactive
            )
            test_results.append(res_b)
            
            # Test C: PUY active again (Baseline repeat)
            await asyncio.sleep(4)
            res_c = await run_single_puy_check(
                browser,
                test_id="test_c_all_active_repeat",
                description="Test C: PUY Re-activated (Baseline Repeat)",
                active_targets=ALL_TARGETS
            )
            test_results.append(res_c)
            
        except Exception as e:
            traceback.print_exc()
        finally:
            await browser.close()
            
    # Save JSON report
    report_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "results": test_results
    }
    with open("artifacts/puy_differential/puy_diff_results.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
        
    # Analyze and build Markdown report
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
        
    md = "# Lufthansa Surprise: PUY Differential-Test Abschlussbericht\n\n"
    md += f"**Ausgeführt am:** {report_data['timestamp']}  \n\n"
    
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
        
    # Check request parameters
    req_a_details = "Nicht erfasst"
    if res_a.get("json_requests"):
        # Look for modelData
        for r in res_a["json_requests"]:
            if r.get("post_data") and "modelData" in r["post_data"]:
                try:
                    pd = json.loads(r["post_data"])
                    md_obj = pd.get("modelData", {})
                    req_a_details = f"Jahr/Dates: {md_obj.get('earliestOut')} bis {md_obj.get('latestRet')} | minStay/maxStay: {md_obj.get('minStay')}/{md_obj.get('maxStay')}"
                    break
                except:
                    pass
                    
    md += f"\n## Request-Parametervalidierung (Test A)\n"
    md += f"- **Backend-Request Details:** `{req_a_details}`\n"
    
    with open("artifacts/puy_differential/puy_diff_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("PUY Differential report written successfully.")

if __name__ == "__main__":
    asyncio.run(main())
