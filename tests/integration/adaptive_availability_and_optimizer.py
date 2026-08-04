import asyncio
import json
import os
import re
import datetime
import traceback
from playwright.async_api import async_playwright

ALL_TARGETS = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]
SCREENSHOTS_DIR = "artifacts/screenshots/adaptive_run"

async def navigate_and_set_parameters(page, test_id):
    url = "https://www.lufthansa-surprise.com/"
    print(f"[{test_id}] Navigating to {url}...")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(2)
    
    # Cookies
    try:
        accept = page.locator("button:has-text('Einverstanden'), button:has-text('Alle akzeptieren')")
        if await accept.count() > 0:
            await accept.first.click()
            await asyncio.sleep(1)
    except Exception:
        pass

    # Frankfurt/Main
    fra = page.locator("text='Frankfurt/Main'")
    if await fra.count() == 0:
        return False, "Origin FRA not found"
    await fra.first.click()
    await asyncio.sleep(2)
    
    # Kunst und Kultur
    arts = page.locator("text='Kunst und Kultur'")
    if await arts.count() == 0:
        return False, "Theme Kunst und Kultur not found"
    await arts.first.click()
    await asyncio.sleep(1)
    
    ok_btn = page.locator("button:has-text('OK')")
    if await ok_btn.count() > 0:
        await ok_btn.first.click()
        await asyncio.sleep(2)
        
    # Reisedaten eingeben
    reisedaten = page.locator("text='Reisedaten eingeben'")
    if await reisedaten.count() == 0:
        return False, "'Reisedaten eingeben' not found"
    await reisedaten.first.click()
    await asyncio.sleep(3)
    
    # Dates via React Datepicker clicks (Zero DOM injection)
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
    
    # Close datepicker modal
    close_btn = page.locator(".datepicker-modal button.close, button.closeButton")
    if await close_btn.count() > 0 and await close_btn.is_visible():
        await close_btn.first.click()
    else:
        await page.keyboard.press("Escape")
    await asyncio.sleep(1)
    
    # Verify parameters from DOM
    val_out = await page.locator("#earliestOut").input_value()
    val_ret = await page.locator("#latestRet").input_value()
    val_class = await page.locator("#travelClass").input_value() if await page.locator("#travelClass").count() > 0 else ""
    
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
            
    await asyncio.sleep(1)
    
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
    await asyncio.sleep(6)
    
    after_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_after.png")
    await page.screenshot(path=after_screenshot, full_page=True)
    
    page_text = await page.evaluate("document.body.innerText")
    
    if "Security check" in page_text or "Sicherheitscheck" in page_text or "resembles that of a bot" in page_text or "Access Denied" in page_text:
        return "blocked", None, "Security check or Bot protection triggered"
        
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

async def run_single_check(page, test_id, description, active_targets):
    print(f"\n==================================================")
    print(f"RUNNING TEST [{test_id}]: {description}")
    print(f"Active targets ({len(active_targets)}): {active_targets}")
    print(f"==================================================")
    
    timestamp_start = datetime.datetime.now().isoformat()
    
    ok, param_info = await navigate_and_set_parameters(page, test_id)
    if not ok:
        fail_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_param_failed.png")
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
        
    cb_ok, cb_proof = await set_and_verify_checkboxes(page, active_targets)
    
    before_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_before.png")
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
        
    await asyncio.sleep(2)
    status, price, details = await evaluate_availability(page, test_id)
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
    os.makedirs("artifacts/optimizer", exist_ok=True)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    all_step_logs = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        
        try:
            # -------------------------------------------------------------
            # STEP 0: Initial Baseline Test (All 11 targets)
            # -------------------------------------------------------------
            baseline_init = await run_single_check(
                page, 
                test_id="baseline_initial", 
                description="Initial Baseline (All 11 Targets)", 
                active_targets=ALL_TARGETS
            )
            all_step_logs.append(baseline_init)
            
            if baseline_init["status"] != "available":
                print(f"CRITICAL: Baseline unavailable ({baseline_init['status']}). Aborting.")
                return
                
            # -------------------------------------------------------------
            # PHASE 1: Find Negative Control Group (3 targets)
            # -------------------------------------------------------------
            candidate_triads = [
                ["BSL", "SJJ", "PUY"],
                ["BSL", "PUY", "LIN"],
                ["SJJ", "PUY", "WRO"],
                ["BSL", "SJJ", "WRO"],
                ["HEL", "BSL", "PUY"]
            ]
            
            neg_controls = []
            confirmed_unavailable = []
            
            for i, triad in enumerate(candidate_triads, start=1):
                await asyncio.sleep(2)
                res_triad = await run_single_check(
                    page,
                    test_id=f"phase1_triad_{i}_{'_'.join(t.lower() for t in triad)}",
                    description=f"Phase 1 Triad {i} ({', '.join(triad)})",
                    active_targets=triad
                )
                all_step_logs.append(res_triad)
                
                if res_triad["status"] == "unavailable":
                    print(f"SUCCESS: Found confirmed unavailable triad: {triad}")
                    confirmed_unavailable.extend(triad)
                    confirmed_unavailable = list(set(confirmed_unavailable))
                    neg_controls = triad[:2] # Pick first 2 as negative controls N1, N2
                    break
                elif res_triad["status"] == "available":
                    print(f"Triad {triad} is available (Price: {res_triad['price']}). Trying next candidate...")
                else:
                    print(f"Triad {triad} status: {res_triad['status']}")
                    
            if len(neg_controls) < 2:
                print("Could not find a purely unavailable triad among candidates. Using best available strategy.")
                # If no triad was purely unavailable, all candidate triads returned available ->
                # The user will see that virtually all tested destinations have available seats!
            
            # -------------------------------------------------------------
            # PHASE 2: Controlled Single Target Tests
            # -------------------------------------------------------------
            target_matrix = {}
            for t in ALL_TARGETS:
                if t in confirmed_unavailable:
                    target_matrix[t] = {
                        "status": "confirmed_unavailable",
                        "price": None,
                        "method": "proven_via_negative_triad"
                    }
                else:
                    target_matrix[t] = {
                        "status": "pending",
                        "price": None,
                        "method": None
                    }
                    
            if len(neg_controls) >= 2:
                n1, n2 = neg_controls[0], neg_controls[1]
                print(f"\nUsing Negative Control Targets: N1={n1}, N2={n2}")
                
                targets_to_test = [t for t in ALL_TARGETS if t not in confirmed_unavailable]
                
                for t in targets_to_test:
                    await asyncio.sleep(2)
                    triad_test = [t, n1, n2]
                    res_t = await run_single_check(
                        page,
                        test_id=f"phase2_single_{t.lower()}",
                        description=f"Phase 2 Test for {t} with Controls [{n1}, {n2}]",
                        active_targets=triad_test
                    )
                    all_step_logs.append(res_t)
                    
                    if res_t["status"] == "available":
                        target_matrix[t] = {
                            "status": "available",
                            "price": res_t["price"],
                            "method": f"tested_with_controls_[{n1},{n2}]"
                        }
                    elif res_t["status"] == "unavailable":
                        target_matrix[t] = {
                            "status": "confirmed_unavailable",
                            "price": None,
                            "method": f"tested_with_controls_[{n1},{n2}]"
                        }
                        if t not in confirmed_unavailable:
                            confirmed_unavailable.append(t)
                    else:
                        target_matrix[t] = {
                            "status": "unknown",
                            "price": None,
                            "method": res_t["status"]
                        }
            
            # -------------------------------------------------------------
            # PHASE 3: Availability Matrix Output
            # -------------------------------------------------------------
            matrix_summary = {
                "created_at": datetime.datetime.now().isoformat(),
                "minimum_active_targets_required": 3,
                "negative_controls_used": neg_controls,
                "matrix": target_matrix,
                "total_targets": len(ALL_TARGETS),
                "confirmed_available_count": sum(1 for v in target_matrix.values() if v["status"] == "available"),
                "confirmed_unavailable_count": sum(1 for v in target_matrix.values() if v["status"] == "confirmed_unavailable"),
                "unknown_count": sum(1 for v in target_matrix.values() if v["status"] == "unknown")
            }
            
            with open("artifacts/availability/elimination_matrix.json", "w", encoding="utf-8") as f:
                json.dump(matrix_summary, f, indent=2, ensure_ascii=False)
                
            md_matrix = "# Lufthansa Surprise: Availability Elimination Matrix\n\n"
            md_matrix += f"**Timestamp:** {matrix_summary['created_at']}  \n"
            md_matrix += f"**UI Mindestlimit:** 3 aktive Ziel-Checkboxen  \n"
            md_matrix += f"**Verwendete negative Kontrollziele:** `{neg_controls}`  \n\n"
            md_matrix += "## Ziel-Verfügbarkeitsstatus\n\n"
            md_matrix += "| Zielcode | Stadt | Status | Triad-Preis | Nachweismethode |\n"
            md_matrix += "| :--- | :--- | :--- | :--- | :--- |\n"
            for t, data in target_matrix.items():
                p_str = data["price"] or "-"
                md_matrix += f"| **{t}** | {t} | `{data['status']}` | {p_str} | {data['method']} |\n"
            with open("artifacts/availability/elimination_matrix.md", "w", encoding="utf-8") as f:
                f.write(md_matrix)
                
            # -------------------------------------------------------------
            # PHASE 4: Target Fare Optimizer for PRG
            # -------------------------------------------------------------
            target_dest = "PRG"
            confirmed_avail = [k for k, v in target_matrix.items() if v["status"] == "available"]
            other_avail = [k for k in confirmed_avail if k != target_dest]
            
            opt_runs = []
            
            # Variant 1: Target + ALL confirmed_unavailable
            var1_targets = list(set([target_dest] + confirmed_unavailable))
            if len(var1_targets) >= 3:
                await asyncio.sleep(2)
                res_v1 = await run_single_check(
                    page,
                    test_id="phase4_opt_variant_1_all_unavail",
                    description=f"Optimizer Variant 1: {target_dest} + all confirmed unavailable ({len(var1_targets)} targets)",
                    active_targets=var1_targets
                )
                all_step_logs.append(res_v1)
                opt_runs.append(res_v1)
                
            # Variant 2: Target + 2 negative controls (exakt 3 targets)
            if len(neg_controls) >= 2:
                var2_targets = [target_dest, neg_controls[0], neg_controls[1]]
                await asyncio.sleep(2)
                res_v2 = await run_single_check(
                    page,
                    test_id="phase4_opt_variant_2_triad",
                    description=f"Optimizer Variant 2: {target_dest} + controls [{neg_controls[0]}, {neg_controls[1]}] (exakt 3 targets)",
                    active_targets=var2_targets
                )
                all_step_logs.append(res_v2)
                opt_runs.append(res_v2)
                
            # Final Baseline Consistency Check
            await asyncio.sleep(2)
            baseline_final = await run_single_check(
                page,
                test_id="baseline_final_consistency",
                description="Final Baseline Consistency Check (All 11 Targets)",
                active_targets=ALL_TARGETS
            )
            all_step_logs.append(baseline_final)
            
            inventory_changed = (
                baseline_init["status"] != baseline_final["status"] or
                baseline_init["price"] != baseline_final["price"]
            )
            
            # -------------------------------------------------------------
            # Build Final Optimizer Report
            # -------------------------------------------------------------
            best_opt = min([r for r in opt_runs if r["status"] == "available"], key=lambda x: float(re.search(r'\d+[\.,]?\d*', x.get("price","9999")).group(0).replace(",", ".")) if x.get("price") else 9999, default=None)
            
            price_3_targets = res_v2["price"] if 'res_v2' in locals() and res_v2.get("price") else "-"
            opt_price = best_opt["price"] if best_opt else "-"
            
            opt_summary = {
                "target_destination": target_dest,
                "minimum_active_targets": 3,
                "negative_controls": neg_controls,
                "baseline_initial_price": baseline_init["price"],
                "baseline_final_price": baseline_final["price"],
                "inventory_changed": inventory_changed,
                "final_verification": not inventory_changed and best_opt is not None,
                "competitor_destinations_excluded": other_avail,
                "passive_destinations_retained": [t for t in (best_opt["active_targets"] if best_opt else []) if t != target_dest],
                "price_with_3_targets": price_3_targets,
                "optimized_price": opt_price,
                "observed_savings": "Optimiert vs Einzelausschluss",
                "optimizer_runs": opt_runs
            }
            
            with open("artifacts/optimizer/target_fare_recommendation.json", "w", encoding="utf-8") as f:
                json.dump(opt_summary, f, indent=2, ensure_ascii=False)
                
            md_opt = "# Lufthansa Surprise: Target Fare Optimizer Report\n\n"
            md_opt += f"**Wunschziel:** `{target_dest}` (Prag)  \n"
            md_opt += f"**UI-Mindestlimit:** 3 aktive Zielcheckboxen  \n"
            md_opt += f"**Verwendete Kontrollziele:** `{neg_controls}`  \n"
            md_opt += f"**Inventar unverändert:** `{'Ja' if not inventory_changed else 'NEIN (Inventory Changed!)'}`  \n"
            md_opt += f"**Final Verification:** `{'true' if opt_summary['final_verification'] else 'false'}`  \n\n"
            
            md_opt += "## Preisübersicht & Optimierung\n\n"
            md_opt += f"- **Baseline-Preis (11 Ziele aktiv):** `{baseline_init['price']}`\n"
            md_opt += f"- **Preis mit exakt 3 Zielen (Prag + 2 Kontrollziele):** `{price_3_targets}`\n"
            md_opt += f"- **Optimierter Preis (Prag + alle nicht verfügbaren Puffer):** `{opt_price}`\n\n"
            
            md_opt += "## Empfohlene Checkbox-Konfiguration\n\n"
            md_opt += f"- **Aktiv zu lassendes Wunschziel:** `['{target_dest}']`\n"
            md_opt += f"- **Aktiv zu lassende passive Puffer-Ziele (nicht verfügbar):** `{opt_summary['passive_destinations_retained']}`\n"
            md_opt += f"- **Auszuschließende tatsächlich verfügbare Konkurrenzziele:** `{other_avail}`\n\n"
            
            md_opt += "## Hinweis\n"
            md_opt += "> [!IMPORTANT]\n> Keine Buchung, keine Zahlung und keine Garantie der endgültigen Zuteilung durch Lufthansa Surprise.\n"
            
            with open("artifacts/optimizer/target_fare_recommendation.md", "w", encoding="utf-8") as f:
                f.write(md_opt)
                
            print("\nAdaptive Availability & Optimizer Run Complete!")
            
        except Exception as e:
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
