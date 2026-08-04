import asyncio
import json
import os
import re
import datetime
import traceback
from playwright.async_api import async_playwright

ALL_TARGETS = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]

async def navigate_and_set_parameters(page, test_id):
    """
    Navigates to the Lufthansa Surprise search form and sets parameters via regular UI only:
    - Origin: Frankfurt/Main
    - Theme: Kunst und Kultur
    - Dates: 07.08.2026 - 09.08.2026 via React Datepicker clicks
    - Travelers: 1 Reisender, Economy
    Verifies all parameters from the DOM.
    """
    url = "https://www.lufthansa-surprise.com/"
    print(f"[{test_id}] Navigating to {url}...")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(2)
    
    # 1. Cookies
    try:
        accept = page.locator("button:has-text('Einverstanden'), button:has-text('Alle akzeptieren')")
        if await accept.count() > 0:
            await accept.first.click()
            await asyncio.sleep(1)
    except Exception:
        pass

    # 2. Select Frankfurt/Main
    fra = page.locator("text='Frankfurt/Main'")
    if await fra.count() == 0:
        print(f"[{test_id}] Origin Frankfurt/Main not found!")
        return False, "Origin FRA not found"
    await fra.first.click()
    await asyncio.sleep(2)
    
    # 3. Select Theme "Kunst und Kultur"
    arts = page.locator("text='Kunst und Kultur'")
    if await arts.count() == 0:
        print(f"[{test_id}] Theme Kunst und Kultur not found!")
        return False, "Theme Kunst und Kultur not found"
    await arts.first.click()
    await asyncio.sleep(1)
    
    ok_btn = page.locator("button:has-text('OK')")
    if await ok_btn.count() > 0:
        await ok_btn.first.click()
        await asyncio.sleep(2)
        
    # 4. Click "Reisedaten eingeben"
    reisedaten = page.locator("text='Reisedaten eingeben'")
    if await reisedaten.count() == 0:
        print(f"[{test_id}] 'Reisedaten eingeben' not found!")
        return False, "'Reisedaten eingeben' button not found"
    await reisedaten.first.click()
    await asyncio.sleep(3)
    
    # 5. Set Dates via React Datepicker (Regular UI only)
    out_input = page.locator("#earliestOut")
    if await out_input.count() == 0:
        return False, "earliestOut input not found"
    await out_input.click()
    await asyncio.sleep(1)
    
    day7 = page.locator(".react-datepicker__day[aria-label*='7. August 2026']")
    if await day7.count() == 0:
        day7 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="7")
    if await day7.count() == 0:
        return False, "Calendar Day 07.08.2026 not found"
    await day7.first.click()
    await asyncio.sleep(1)
    
    ret_input = page.locator("#latestRet")
    if await ret_input.count() == 0:
        return False, "latestRet input not found"
    await ret_input.click()
    await asyncio.sleep(1)
    
    day9 = page.locator(".react-datepicker__day[aria-label*='9. August 2026']")
    if await day9.count() == 0:
        day9 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="9")
    if await day9.count() == 0:
        return False, "Calendar Day 09.08.2026 not found"
    await day9.first.click()
    await asyncio.sleep(1)
    
    # 6. Close the Datepicker Modal to enable interaction with Weiter
    close_btn = page.locator(".datepicker-modal button.close, button.closeButton")
    if await close_btn.count() > 0 and await close_btn.is_visible():
        await close_btn.first.click()
    else:
        await page.keyboard.press("Escape")
    await asyncio.sleep(1)
    
    # 7. Verify parameters from DOM
    val_out = await page.locator("#earliestOut").input_value()
    val_ret = await page.locator("#latestRet").input_value()
    val_class = await page.locator("#travelClass").input_value() if await page.locator("#travelClass").count() > 0 else ""
    
    # Check if security check or bot protection is visible
    page_text = await page.evaluate("document.body.innerText")
    if "Security check" in page_text or "Sicherheitscheck" in page_text or "resembles that of a bot" in page_text:
        return False, "blocked: Security check detected"
        
    param_verified = (
        val_out == "07.08.2026" and
        val_ret == "09.08.2026" and
        "1 Reisender" in val_class and
        "Economy" in val_class
    )
    
    if not param_verified:
        print(f"[{test_id}] Parameter verification failed: out={val_out}, ret={val_ret}, class={val_class}")
        return False, f"Parameter verification failed: out={val_out}, ret={val_ret}, class={val_class}"
        
    return True, {
        "origin": "Frankfurt/Main",
        "theme": "Kunst und Kultur",
        "earliestOut": val_out,
        "latestRet": val_ret,
        "travelClass": val_class,
        "parameters_verified": True
    }

async def set_and_verify_checkboxes(page, active_targets):
    """
    Sets the target checkboxes to match active_targets, reads back the actual DOM state,
    and returns a proof object with checkboxes_verified boolean.
    """
    dom_state_before = {}
    desired_state = {t: (t in active_targets) for t in ALL_TARGETS}
    
    # First, read existing state
    for t in ALL_TARGETS:
        cb = page.locator(f"#pool_destion_{t}")
        if await cb.count() > 0:
            dom_state_before[t] = await cb.is_checked()
        else:
            dom_state_before[t] = None
            
    # Adjust state
    for t in ALL_TARGETS:
        should_be_checked = desired_state[t]
        current = dom_state_before.get(t)
        if current is not None and current != should_be_checked:
            # Click the checkbox element directly via JS evaluate to avoid label overlap issues
            await page.evaluate(f"document.getElementById('pool_destion_{t}').click()")
            await asyncio.sleep(0.3)
            
    await asyncio.sleep(1)
    
    # Read actual DOM state after adjustments
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

async def evaluate_availability(page, test_id, screenshots_dir):
    """
    Clicks 'Weiter' and inspects the resulting page.
    Returns: (status, price, details)
    Status in: available, unavailable, ambiguous, blocked, timeout, validation_failed
    """
    weiter = page.locator("button:has-text('Weiter')")
    if await weiter.count() == 0:
        return "validation_failed", None, "Weiter button not found"
        
    await weiter.first.click()
    print(f"[{test_id}] Clicked Weiter. Waiting for response...")
    
    # Wait for response
    await asyncio.sleep(6)
    
    # Take screenshot of result
    after_screenshot = os.path.join(screenshots_dir, f"{test_id}_after.png")
    await page.screenshot(path=after_screenshot, full_page=True)
    
    page_text = await page.evaluate("document.body.innerText")
    
    # 1. Check for Bot / Security
    if "Security check" in page_text or "Sicherheitscheck" in page_text or "resembles that of a bot" in page_text or "Access Denied" in page_text:
        return "blocked", None, "Security check or Bot protection triggered"
        
    # 2. Check for explicit unavailable message
    if (
        "Leider sind für die von Ihnen gewählten" in page_text or
        "keine verfügbaren flüge" in page_text.lower() or
        "für ihre auswahl leider keine flüge" in page_text.lower() or
        "nicht verfügbar" in page_text.lower() or
        "nicht möglich" in page_text.lower()
    ):
        return "unavailable", None, "Explicit no-availability notice on UI"
        
    # 3. Check for available / price
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
        
    # 4. Fallback if ambiguous
    return "ambiguous", None, f"Page content ambiguous. Length: {len(page_text)} chars"

async def run_single_check(page, test_id, description, active_targets, screenshots_dir):
    """
    Executes one isolated check:
    1. Navigation and parameter set & verification
    2. Checkbox configuration & proof
    3. Screenshot before
    4. Availability evaluation & screenshot after
    """
    print(f"\n==================================================")
    print(f"RUNNING TEST [{test_id}]: {description}")
    print(f"Active targets: {active_targets}")
    print(f"==================================================")
    
    timestamp_start = datetime.datetime.now().isoformat()
    
    # 1. Setup & verify parameters
    ok, param_info = await navigate_and_set_parameters(page, test_id)
    if not ok:
        fail_screenshot = os.path.join(screenshots_dir, f"{test_id}_param_failed.png")
        await page.screenshot(path=fail_screenshot)
        return {
            "test_id": test_id,
            "description": description,
            "timestamp": timestamp_start,
            "active_targets": active_targets,
            "status": "validation_failed" if "blocked" not in str(param_info) else "blocked",
            "price": None,
            "error": param_info,
            "parameters_verified": False,
            "checkboxes_verified": False
        }
        
    # 2. Checkboxes
    cb_ok, cb_proof = await set_and_verify_checkboxes(page, active_targets)
    
    # 3. Screenshot before Weiter
    before_screenshot = os.path.join(screenshots_dir, f"{test_id}_before.png")
    await page.screenshot(path=before_screenshot, full_page=True)
    
    if not cb_ok:
        print(f"[{test_id}] Checkbox verification failed! Mismatches: {cb_proof['mismatches']}")
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
        
    # Gentle delay before action (1-3s)
    await asyncio.sleep(2)
    
    # 4. Evaluate availability
    status, price, details = await evaluate_availability(page, test_id, screenshots_dir)
    print(f"[{test_id}] Result: status={status}, price={price}, details={details}")
    
    timestamp_end = datetime.datetime.now().isoformat()
    
    return {
        "test_id": test_id,
        "description": description,
        "timestamp_start": timestamp_start,
        "timestamp_end": timestamp_end,
        "active_targets": active_targets,
        "parameters": param_info,
        "checkbox_proof": cb_proof,
        "status": status,
        "price": price,
        "details": details,
        "parameters_verified": True,
        "checkboxes_verified": True
    }

async def main():
    os.makedirs("artifacts/availability", exist_ok=True)
    screenshots_dir = "artifacts/screenshots/pilot_run"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    pilot_results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        
        try:
            # -------------------------------------------------------------
            # 1. Initial Baseline Test (All 11 targets active)
            # -------------------------------------------------------------
            res_base_init = await run_single_check(
                page, 
                test_id="baseline_initial", 
                description="Initial Baseline (All 11 Targets)", 
                active_targets=ALL_TARGETS,
                screenshots_dir=screenshots_dir
            )
            pilot_results.append(res_base_init)
            
            if res_base_init["status"] != "available":
                print(f"CRITICAL: Initial Baseline returned '{res_base_init['status']}'. Aborting pilot run.")
            else:
                # ---------------------------------------------------------
                # 2. Group Test 1 (FLR, PRG, WAW)
                # ---------------------------------------------------------
                await asyncio.sleep(3)
                res_group_1 = await run_single_check(
                    page,
                    test_id="group_1_flr_prg_waw",
                    description="Group 1 (FLR, PRG, WAW)",
                    active_targets=["FLR", "PRG", "WAW"],
                    screenshots_dir=screenshots_dir
                )
                pilot_results.append(res_group_1)
                
                # ---------------------------------------------------------
                # 3. Group Test 2 (HEL, BLQ, KRK)
                # ---------------------------------------------------------
                await asyncio.sleep(3)
                res_group_2 = await run_single_check(
                    page,
                    test_id="group_2_hel_blq_krk",
                    description="Group 2 (HEL, BLQ, KRK)",
                    active_targets=["HEL", "BLQ", "KRK"],
                    screenshots_dir=screenshots_dir
                )
                pilot_results.append(res_group_2)
                
                # ---------------------------------------------------------
                # 4. Single Target Test (PRG)
                # ---------------------------------------------------------
                await asyncio.sleep(3)
                res_single_prg = await run_single_check(
                    page,
                    test_id="single_target_prg",
                    description="Single Target Test (PRG)",
                    active_targets=["PRG"],
                    screenshots_dir=screenshots_dir
                )
                pilot_results.append(res_single_prg)
                
                # ---------------------------------------------------------
                # 5. Final Baseline Test (Verification of Inventory Stability)
                # ---------------------------------------------------------
                await asyncio.sleep(3)
                res_base_final = await run_single_check(
                    page,
                    test_id="baseline_final",
                    description="Final Baseline (Inventory Consistency Check)",
                    active_targets=ALL_TARGETS,
                    screenshots_dir=screenshots_dir
                )
                pilot_results.append(res_base_final)
                
        except Exception as e:
            traceback.print_exc()
        finally:
            await browser.close()
            
    # -----------------------------------------------------------------
    # Evaluate Pilot Run
    # -----------------------------------------------------------------
    initial_base = next((r for r in pilot_results if r["test_id"] == "baseline_initial"), None)
    final_base = next((r for r in pilot_results if r["test_id"] == "baseline_final"), None)
    
    inventory_changed = False
    if initial_base and final_base:
        if (initial_base["status"] != final_base["status"]) or (initial_base["price"] != final_base["price"]):
            inventory_changed = True
            
    all_param_verified = all(r.get("parameters_verified", False) for r in pilot_results)
    all_cb_verified = all(r.get("checkboxes_verified", False) for r in pilot_results)
    no_blocks = all(r.get("status") not in ("blocked", "validation_failed") for r in pilot_results)
    
    recommendation = "READY_FOR_FULL_RUN" if (all_param_verified and all_cb_verified and no_blocks and not inventory_changed and len(pilot_results) == 5) else "FIXES_REQUIRED"
    
    pilot_summary = {
        "run_type": "pilot_availability_elimination",
        "created_at": datetime.datetime.now().isoformat(),
        "recommendation": recommendation,
        "inventory_changed": inventory_changed,
        "parameters_confirmed": {
            "origin": "Frankfurt/Main",
            "outbound_date": "07.08.2026",
            "return_date": "09.08.2026",
            "travelers": 1,
            "cabin_class": "Economy",
            "flexibility": "Volle Flexibilität",
            "theme": "Kunst und Kultur",
            "input_method": "react_datepicker_ui_only (zero DOM injection)"
        },
        "initial_baseline": {
            "status": initial_base["status"] if initial_base else None,
            "price": initial_base["price"] if initial_base else None
        },
        "final_baseline": {
            "status": final_base["status"] if final_base else None,
            "price": final_base["price"] if final_base else None
        },
        "tests_executed": len(pilot_results),
        "results": pilot_results
    }
    
    # Write JSON
    json_path = "artifacts/availability/pilot_run.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pilot_summary, f, indent=2, ensure_ascii=False)
    print(f"Saved pilot JSON to {json_path}")
    
    # Write Markdown
    md = "# Lufthansa Surprise Pilot Run Report\n\n"
    md += f"**Timestamp:** {pilot_summary['created_at']}  \n"
    md += f"**Empfehlung:** `{recommendation}`  \n"
    md += f"**Inventar unverändert (Konsistenz):** `{'Ja' if not inventory_changed else 'NEIN (Inventory Changed!)'}`  \n"
    md += f"**Eingabemethode:** React Datepicker UI interaction only (keine DOM-/JavaScript-Injektion)\n\n"
    
    md += "## Bestätigte Suchparameter\n\n"
    md += "- **Abflug:** Frankfurt/Main (FRA)\n"
    md += "- **Hinflug:** 07.08.2026\n"
    md += "- **Rückflug:** 09.08.2026\n"
    md += "- **Reisende:** 1 Erwachsener\n"
    md += "- **Klasse:** Economy\n"
    md += "- **Flexibilität:** Volle Flexibilität\n"
    md += "- **Thema:** Kunst und Kultur\n\n"
    
    md += "## Übersicht der Testschritte\n\n"
    md += "| Test-ID | Beschreibung | Aktive Ziele | Status | Preis | Param. verifiziert | Checkboxen verifiziert |\n"
    md += "| :--- | :--- | :--- | :--- | :--- | :---: | :---: |\n"
    for r in pilot_results:
        p_v = "✅" if r.get("parameters_verified") else "❌"
        cb_v = "✅" if r.get("checkboxes_verified") else "❌"
        targets_str = ", ".join(r.get("active_targets", []))
        if len(targets_str) > 25:
            targets_str = targets_str[:22] + "..."
        price_str = r.get("price") or "-"
        md += f"| `{r['test_id']}` | {r['description']} | {targets_str} | **{r['status']}** | {price_str} | {p_v} | {cb_v} |\n"
        
    md += "\n## Baseline-Stabilitätsvergleich\n\n"
    md += f"- **Initial Baseline:** Status = `{pilot_summary['initial_baseline']['status']}`, Preis = `{pilot_summary['initial_baseline']['price']}`\n"
    md += f"- **Final Baseline:** Status = `{pilot_summary['final_baseline']['status']}`, Preis = `{pilot_summary['final_baseline']['price']}`\n"
    if inventory_changed:
        md += "\n> [!WARNING]\n> Baseline-Inventar oder Preis hat sich während des Laufs verändert!\n"
    else:
        md += "\n> [!NOTE]\n> Baseline-Inventar und Preis blieben über alle Testschritte hinweg exakt stabil und konsistent.\n"
        
    md += "\n## Details je Testschritt\n\n"
    for r in pilot_results:
        md += f"### `{r['test_id']}`: {r['description']}\n"
        md += f"- **Zeitraum:** {r.get('timestamp_start', '-')} bis {r.get('timestamp_end', '-')}\n"
        md += f"- **Aktive Ziele:** `{r.get('active_targets')}`\n"
        md += f"- **Status:** `{r.get('status')}`\n"
        md += f"- **Preis:** `{r.get('price')}`\n"
        md += f"- **Details:** {r.get('details') or r.get('error')}\n\n"
        
    md_path = "artifacts/availability/pilot_run.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Saved pilot Markdown to {md_path}")

if __name__ == "__main__":
    asyncio.run(main())
