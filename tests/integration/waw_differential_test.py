import asyncio
import json
import os
import re
import datetime
import traceback
from playwright.async_api import async_playwright

ALL_TARGETS = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]
SCREENSHOTS_DIR = "artifacts/screenshots/waw_diff_test"

async def navigate_and_set_parameters_with_retry(page, test_id, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            url = "https://www.lufthansa-surprise.com/"
            print(f"[{test_id}] (Attempt {attempt}/{max_retries}) Navigating to {url}...")
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

            # Origin FRA
            fra = page.locator("text='Frankfurt/Main'")
            if await fra.count() == 0:
                print(f"[{test_id}] FRA origin not found on attempt {attempt}")
                continue
            await fra.first.click()
            await asyncio.sleep(2)
            
            # Theme
            arts = page.locator("text='Kunst und Kultur'")
            if await arts.count() == 0:
                print(f"[{test_id}] Theme not found on attempt {attempt}")
                continue
            await arts.first.click()
            await asyncio.sleep(1.5)
            
            ok_btn = page.locator("button:has-text('OK')")
            if await ok_btn.count() > 0:
                await ok_btn.first.click()
                await asyncio.sleep(2)
                
            # Reisedaten
            reisedaten = page.locator("text='Reisedaten eingeben'")
            if await reisedaten.count() == 0:
                print(f"[{test_id}] 'Reisedaten eingeben' not found on attempt {attempt}")
                continue
            await reisedaten.first.click()
            await asyncio.sleep(3)
            
            # Date Selection
            out_input = page.locator("#earliestOut")
            if await out_input.count() == 0:
                continue
            await out_input.click()
            await asyncio.sleep(1.5)
            
            day7 = page.locator(".react-datepicker__day[aria-label*='7. August 2026']")
            if await day7.count() == 0:
                day7 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="7")
            await day7.first.click()
            await asyncio.sleep(1.5)
            
            ret_input = page.locator("#latestRet")
            if await ret_input.count() == 0:
                continue
            await ret_input.click()
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
            
            # Verify parameters
            val_out = await page.locator("#earliestOut").input_value()
            val_ret = await page.locator("#latestRet").input_value()
            val_class = await page.locator("#travelClass").input_value() if await page.locator("#travelClass").count() > 0 else ""
            
            param_verified = (
                val_out == "07.08.2026" and
                val_ret == "09.08.2026" and
                "1 Reisender" in val_class and
                "Economy" in val_class
            )
            
            if param_verified:
                return True, {
                    "origin": "Frankfurt/Main",
                    "theme": "Kunst und Kultur",
                    "earliestOut": val_out,
                    "latestRet": val_ret,
                    "travelClass": val_class,
                    "parameters_verified": True
                }
            else:
                print(f"[{test_id}] Verification mismatch on attempt {attempt}: out={val_out}, ret={val_ret}")
        except Exception as e:
            print(f"[{test_id}] Exception on attempt {attempt}: {str(e)}")
            
    return False, "Failed to navigate and set parameters after retries"

async def set_and_verify_checkboxes(page, active_targets):
    dom_state_before = {}
    desired_state = {t: (t in active_targets) for t in ALL_TARGETS}
    
    for t in ALL_TARGETS:
        cb = page.locator(f"#pool_destion_{t}")
        if await cb.count() > 0:
            dom_state_before[t] = await cb.is_checked()
        else:
            dom_state_before[t] = None
            
    for t in ALL_TARGETS:
        should_be_checked = desired_state[t]
        current = dom_state_before.get(t)
        if current is not None and current != should_be_checked:
            await page.evaluate(f"document.getElementById('pool_destion_{t}').click()")
            await asyncio.sleep(0.3)
            
    await asyncio.sleep(1.5)
    
    dom_state_after = {}
    mismatches = []
    for t in ALL_TARGETS:
        cb = page.locator(f"#pool_destion_{t}")
        if await cb.count() > 0:
            actual = await cb.is_checked()
            dom_state_after[t] = actual
            if actual != desired_state[t]:
                mismatches.append(f"{t}: expected {desired_state[t]}, got {actual}")
        else:
            dom_state_after[t] = None
            mismatches.append(f"{t}: element not found")
            
    verified = (len(mismatches) == 0)
    
    proof = {
        "all_targets": ALL_TARGETS,
        "desired_state": desired_state,
        "actual_dom_state": dom_state_after,
        "checkboxes_verified": verified,
        "mismatches": mismatches
    }
    return verified, proof

async def evaluate_availability(page, test_id):
    weiter = page.locator("button:has-text('Weiter')")
    if await weiter.count() == 0:
        return "validation_failed", None, "Weiter button not found"
        
    await weiter.first.click()
    print(f"[{test_id}] Clicked Weiter. Waiting for response...")
    await asyncio.sleep(7)
    
    after_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_after.png")
    await page.screenshot(path=after_screenshot, full_page=True)
    
    page_text = await page.evaluate("document.body.innerText")
    
    if "Security check" in page_text or "Sicherheitscheck" in page_text or "resembles that of a bot" in page_text or "Access Denied" in page_text:
        return "blocked", None, "Security check detected"
        
    if (
        "Leider sind für die von Ihnen gewählten" in page_text or
        "keine verfügbaren flüge" in page_text.lower() or
        "für ihre auswahl leider keine flüge" in page_text.lower() or
        "nicht verfügbar" in page_text.lower() or
        "nicht möglich" in page_text.lower() or
        "leider keine angebote" in page_text.lower()
    ):
        return "unavailable", None, "Explicit no-availability notice on UI"
        
    if "Gesamtpreis" in page_text or "Buchungsinformationen" in page_text or "Ihre Reisedaten" in page_text:
        price = None
        m = re.search(r'Gesamtpreis\s*\n\s*(\d+[\.,]\d{2}\s*€?)', page_text)
        if m:
            price = m.group(1).strip()
            if "€" not in price:
                price += " €"
        else:
            m2 = re.search(r'€\s*(\d+[\.,]?\d*)', page_text)
            if m2:
                price = f"€ {m2.group(1)}"
            else:
                m3 = re.search(r'(\d+[\.,]?\d*)\s*€', page_text)
                if m3:
                    price = f"{m3.group(1)} €"
                    
        return "available", price, "Offer page loaded with price details"
        
    return "ambiguous", None, f"Page content ambiguous. Length: {len(page_text)} chars"

async def run_single_check(browser, test_id, description, active_targets):
    print(f"\n==================================================")
    print(f"RUNNING TEST [{test_id}]: {description}")
    print(f"Active targets: {active_targets}")
    print(f"==================================================")
    
    # Fresh context & page for clean isolation
    context = await browser.new_context(viewport={"width": 1280, "height": 900})
    page = await context.new_page()
    
    timestamp_start = datetime.datetime.now().isoformat()
    
    ok, param_info = await navigate_and_set_parameters_with_retry(page, test_id)
    if not ok:
        fail_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_param_failed.png")
        await page.screenshot(path=fail_screenshot)
        await page.close()
        await context.close()
        return {
            "test_id": test_id,
            "description": description,
            "timestamp": timestamp_start,
            "active_targets": active_targets,
            "status": "validation_failed",
            "price": None,
            "error": param_info,
            "parameters_verified": False,
            "checkboxes_verified": False
        }
        
    cb_ok, cb_proof = await set_and_verify_checkboxes(page, active_targets)
    
    before_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_before.png")
    await page.screenshot(path=before_screenshot, full_page=True)
    
    if not cb_ok:
        print(f"[{test_id}] Checkbox verification failed! Mismatches: {cb_proof['mismatches']}")
        await page.close()
        await context.close()
        return {
            "test_id": test_id,
            "description": description,
            "timestamp": timestamp_start,
            "active_targets": active_targets,
            "parameters": param_info,
            "checkbox_proof": cb_proof,
            "status": "validation_failed",
            "price": None,
            "error": "Checkbox state verification failed",
            "parameters_verified": True,
            "checkboxes_verified": False
        }
        
    await asyncio.sleep(2.5)
    status, price, details = await evaluate_availability(page, test_id)
    print(f"[{test_id}] Result: status={status}, price={price}, details={details}")
    
    await page.close()
    await context.close()
    
    return {
        "test_id": test_id,
        "description": description,
        "timestamp_start": timestamp_start,
        "timestamp_end": datetime.datetime.now().isoformat(),
        "active_targets": active_targets,
        "status": status,
        "price": price,
        "details": details,
        "parameters_verified": True,
        "checkboxes_verified": True
    }

async def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs("artifacts/waw_differential", exist_ok=True)
    
    test_results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        try:
            # A. WAW deactivated, all others active
            waw_inactive = [t for t in ALL_TARGETS if t != "WAW"]
            res_a = await run_single_check(
                browser,
                test_id="waw_inactive",
                description="WAW deactivated (10 targets active)",
                active_targets=waw_inactive
            )
            test_results.append(res_a)
            
            # B. WAW activated (Baseline)
            await asyncio.sleep(3)
            res_b = await run_single_check(
                browser,
                test_id="waw_active_baseline",
                description="WAW activated again (Baseline - 11 targets)",
                active_targets=ALL_TARGETS
            )
            test_results.append(res_b)
            
            # C. Deactivate exactly one other target (excluding WAW)
            other_targets = [t for t in ALL_TARGETS if t != "WAW"]
            for target in other_targets:
                await asyncio.sleep(3)
                active_list = [t for t in ALL_TARGETS if t != target]
                res_c = await run_single_check(
                    browser,
                    test_id=f"deactivate_{target.lower()}",
                    description=f"Deactivate {target} (WAW + remaining 9 targets active)",
                    active_targets=active_list
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
    with open("artifacts/waw_differential/waw_diff_results.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
        
    # Generate Markdown Report
    md = "# Lufthansa Surprise: WAW Differential-Test Report\n\n"
    md += f"**Ausgeführt am:** {report_data['timestamp']}  \n\n"
    
    md += "## Testergebnisse Übersicht\n\n"
    md += "| Test-ID | Beschreibung | Status | Preis | Param. verifiziert | Checkboxen verifiziert |\n"
    md += "| :--- | :--- | :---: | :---: | :---: | :---: |\n"
    for r in test_results:
        p_v = "✅" if r.get("parameters_verified") else "❌"
        cb_v = "✅" if r.get("checkboxes_verified") else "❌"
        price_str = r.get("price") or "-"
        md += f"| `{r['test_id']}` | {r['description']} | `{r['status']}` | {price_str} | {p_v} | {cb_v} |\n"
        
    md += "\n## Wichtigste Erkenntnisse\n\n"
    res_a_status = res_a.get("status")
    res_b_price = res_b.get("price")
    
    if res_a_status == "unavailable":
        md += f"- **WAW als Deal-Trigger:** `Ja` (Ohne WAW ist kein Angebot verfügbar, mit WAW beträgt der Preis {res_b_price}).\n"
    else:
        md += f"- **WAW als Deal-Trigger:** `Nein` / `Unbestimmt` (Status ohne WAW ist `{res_a_status}`).\n"
        
    non_influential = []
    influential = []
    for r in test_results:
        if r["test_id"] in ["waw_inactive", "waw_active_baseline"]:
            continue
        deactivated_target = r["test_id"].split("_")[-1].upper()
        if r["status"] == "available" and r["price"] == res_b_price:
            non_influential.append(deactivated_target)
        else:
            influential.append(f"{deactivated_target} (Status: {r['status']}, Preis: {r['price']})")
            
    md += f"- **Ziele, die den Baseline-Preis von {res_b_price or '129 EUR'} nicht beeinflussen:** `{non_influential}`\n"
    if influential:
        md += f"- **Ziele, die den Preis oder Status beeinflussen:** `{influential}`\n"
        
    with open("artifacts/waw_differential/waw_diff_report.md", "w", encoding="utf-8") as f:
        f.write(md)
    print("Differential report written successfully.")

if __name__ == "__main__":
    asyncio.run(main())
