import asyncio
import json
import os
import re
import datetime
import traceback
from playwright.async_api import async_playwright

ALL_TARGETS = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]
TARGET_NAMES = {
    "FLR": "Florenz",
    "PRG": "Prag",
    "WAW": "Warschau",
    "WRO": "Breslau",
    "HEL": "Helsinki",
    "BLQ": "Bologna",
    "KRK": "Krakau",
    "BSL": "Basel",
    "SJJ": "Sarajevo",
    "LIN": "Mailand (LIN)",
    "PUY": "Pula"
}
SCREENSHOTS_DIR = "artifacts/screenshots/adaptive_run_v2"

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
    if "Security check" in page_text or "Sicherheitscheck" in page_text or "resembles that of a bot" in page_text or "Access Denied" in page_text:
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

async def run_single_check(page, test_id, description, active_targets, run_id):
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
            "run_id": run_id,
            "test_id": test_id,
            "description": description,
            "timestamp_start": timestamp_start,
            "timestamp_end": datetime.datetime.now().isoformat(),
            "active_targets": active_targets,
            "status": "validation_failed" if "blocked" not in str(param_info) else "blocked",
            "price": None,
            "error": param_info,
            "parameters_verified": False,
            "checkboxes_verified": False,
            "evidence_screenshot": fail_screenshot
        }
        
    cb_ok, cb_proof = await set_and_verify_checkboxes(page, active_targets)
    
    before_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_before.png")
    await page.screenshot(path=before_screenshot, full_page=True)
    
    if not cb_ok:
        print(f"[{test_id}] Checkbox verification failed! Mismatches: {cb_proof['mismatches']}")
        return {
            "run_id": run_id,
            "test_id": test_id,
            "description": description,
            "timestamp_start": timestamp_start,
            "timestamp_end": datetime.datetime.now().isoformat(),
            "active_targets": active_targets,
            "parameters": param_info,
            "checkbox_proof": cb_proof,
            "status": "validation_failed",
            "price": None,
            "error": "Checkbox state verification failed",
            "parameters_verified": True,
            "checkboxes_verified": False,
            "evidence_screenshot": before_screenshot
        }
        
    await asyncio.sleep(2)
    status, price, details = await evaluate_availability(page, test_id)
    print(f"[{test_id}] Result: status={status}, price={price}, details={details}")
    
    timestamp_end = datetime.datetime.now().isoformat()
    after_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_after.png")
    
    return {
        "run_id": run_id,
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
        "checkboxes_verified": True,
        "evidence_screenshot": after_screenshot
    }

async def main():
    run_id = f"adaptive_run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
                active_targets=ALL_TARGETS,
                run_id=run_id
            )
            all_step_logs.append(baseline_init)
            
            if baseline_init["status"] != "available":
                print(f"CRITICAL: Baseline unavailable ({baseline_init['status']}). Aborting.")
                return
                
            # -------------------------------------------------------------
            # PHASE 1: Find Negative Control Group (Max 5 Candidate Triads)
            # -------------------------------------------------------------
            candidate_triads = [
                ["BSL", "SJJ", "PUY"],
                ["BSL", "PUY", "LIN"],
                ["SJJ", "PUY", "WRO"],
                ["BSL", "SJJ", "WRO"],
                ["HEL", "BSL", "PUY"]
            ]
            
            neg_controls = []
            confirmed_unavailable_triads = []
            
            for i, triad in enumerate(candidate_triads, start=1):
                await asyncio.sleep(2)
                res_triad_1 = await run_single_check(
                    page,
                    test_id=f"phase1_triad_{i}_pass1_{'_'.join(t.lower() for t in triad)}",
                    description=f"Phase 1 Triad {i} Pass 1 ({', '.join(triad)})",
                    active_targets=triad,
                    run_id=run_id
                )
                all_step_logs.append(res_triad_1)
                
                if res_triad_1["status"] == "unavailable":
                    print(f"Candidate Triad {triad} returned UNAVAILABLE on Pass 1. Running mandatory Pass 2 verification...")
                    await asyncio.sleep(2)
                    res_triad_2 = await run_single_check(
                        page,
                        test_id=f"phase1_triad_{i}_pass2_repeat_{'_'.join(t.lower() for t in triad)}",
                        description=f"Phase 1 Triad {i} Pass 2 Repeat ({', '.join(triad)})",
                        active_targets=triad,
                        run_id=run_id
                    )
                    all_step_logs.append(res_triad_2)
                    
                    if res_triad_2["status"] == "unavailable":
                        print(f"CONFIRMED: Triad {triad} verified UNAVAILABLE on both Pass 1 & Pass 2!")
                        confirmed_unavailable_triads.append(triad)
                        neg_controls = triad[:2] # Pick N1, N2
                        break
                    else:
                        print(f"WARNING: Triad {triad} returned conflicting results (Pass 1=unavailable, Pass 2={res_triad_2['status']}). Inventory unstable!")
                        # Abort if inventory unstable
                        print("Aborting due to conflicting control group repeat result.")
                        return
                elif res_triad_1["status"] == "available":
                    print(f"Triad {triad} is available (Price: {res_triad_1['price']}). Trying next candidate...")
                else:
                    print(f"Triad {triad} status: {res_triad_1['status']}")
                    
            if len(neg_controls) < 2:
                print("No negative control triad found among the 5 candidates. Controlled single-target tests cannot proceed without proven negative controls.")
                # Save no-control report
                no_ctrl_summary = {
                    "run_id": run_id,
                    "created_at": datetime.datetime.now().isoformat(),
                    "status": "no_negative_control_found",
                    "baseline_initial": baseline_init,
                    "all_candidates_tested": candidate_triads,
                    "message": "All tested triads produced available offers or ambiguous states; no 2x-confirmed negative control group was found."
                }
                with open("artifacts/availability/elimination_matrix.json", "w", encoding="utf-8") as f:
                    json.dump(no_ctrl_summary, f, indent=2, ensure_ascii=False)
                return
                
            n1, n2 = neg_controls[0], neg_controls[1]
            third_neg = [t for t in confirmed_unavailable_triads[0] if t not in (n1, n2)][0]
            print(f"\nUsing Proven Negative Controls: N1={n1}, N2={n2} (with 3rd proven unavailable: {third_neg})")
            
            # Baseline check after control group verification
            await asyncio.sleep(2)
            baseline_mid = await run_single_check(
                page,
                test_id="baseline_post_control_group",
                description="Baseline Check Post Control Group Verification",
                active_targets=ALL_TARGETS,
                run_id=run_id
            )
            all_step_logs.append(baseline_mid)
            if baseline_mid["status"] != "available":
                print("Baseline changed after control group test! Aborting.")
                return

            control_assumption_metadata = {
                "monotonicity_assumed": True,
                "repeated_negative_result": True,
                "baseline_before_available": (baseline_init["status"] == "available"),
                "baseline_after_available": (baseline_mid["status"] == "available"),
                "validated_for_current_run": True,
                "negative_controls": [n1, n2],
                "proven_negative_triad": confirmed_unavailable_triads[0]
            }

            # -------------------------------------------------------------
            # PHASE 2: Controlled Single Target Tests
            # -------------------------------------------------------------
            target_matrix = {}
            # Initialize 3 proven unavailable from triad
            for t in confirmed_unavailable_triads[0]:
                target_matrix[t] = {
                    "destination_code": t,
                    "destination_name": TARGET_NAMES.get(t, t),
                    "status": "confirmed_unavailable_for_run",
                    "tested_configuration": confirmed_unavailable_triads[0],
                    "negative_controls_used": [],
                    "observed_price": None,
                    "tested_at": datetime.datetime.now().isoformat(),
                    "repeat_confirmed": True,
                    "parameters_verified": True,
                    "checkboxes_verified": True,
                    "evidence_screenshot": os.path.join(SCREENSHOTS_DIR, f"phase1_triad_1_pass2_repeat_{'_'.join(t.lower() for t in confirmed_unavailable_triads[0])}_after.png"),
                    "run_id": run_id
                }
                
            targets_to_test = [t for t in ALL_TARGETS if t not in confirmed_unavailable_triads[0]]
            confirmed_unavailable_all = list(confirmed_unavailable_triads[0])
            
            for t in targets_to_test:
                # Disjointness requirement: t != n1, t != n2
                assert t != n1 and t != n2
                triad_test = [t, n1, n2]
                
                await asyncio.sleep(2)
                res_t = await run_single_check(
                    page,
                    test_id=f"phase2_single_{t.lower()}",
                    description=f"Phase 2 Test for {t} ({TARGET_NAMES.get(t, t)}) with Controls [{n1}, {n2}]",
                    active_targets=triad_test,
                    run_id=run_id
                )
                all_step_logs.append(res_t)
                
                repeat_confirmed = False
                final_status = "unknown"
                observed_price = None
                
                if res_t["status"] == "available":
                    final_status = "confirmed_available_for_run"
                    observed_price = res_t["price"]
                    repeat_confirmed = True
                elif res_t["status"] == "unavailable":
                    # Repeat confirmation for unavailable
                    print(f"Target {t} returned unavailable. Running repeat confirmation...")
                    await asyncio.sleep(2)
                    res_t_rep = await run_single_check(
                        page,
                        test_id=f"phase2_single_{t.lower()}_repeat",
                        description=f"Phase 2 Repeat for {t} with Controls [{n1}, {n2}]",
                        active_targets=triad_test,
                        run_id=run_id
                    )
                    all_step_logs.append(res_t_rep)
                    if res_t_rep["status"] == "unavailable":
                        final_status = "confirmed_unavailable_for_run"
                        repeat_confirmed = True
                        if t not in confirmed_unavailable_all:
                            confirmed_unavailable_all.append(t)
                    else:
                        final_status = "unknown"
                        repeat_confirmed = False
                else:
                    final_status = "unknown"
                    repeat_confirmed = False
                    
                target_matrix[t] = {
                    "destination_code": t,
                    "destination_name": TARGET_NAMES.get(t, t),
                    "status": final_status,
                    "tested_configuration": triad_test,
                    "negative_controls_used": [n1, n2],
                    "observed_price": observed_price,
                    "tested_at": res_t["timestamp_end"],
                    "repeat_confirmed": repeat_confirmed,
                    "parameters_verified": res_t.get("parameters_verified", False),
                    "checkboxes_verified": res_t.get("checkboxes_verified", False),
                    "evidence_screenshot": res_t.get("evidence_screenshot"),
                    "run_id": run_id
                }

            # -------------------------------------------------------------
            # PHASE 3: Availability Matrix
            # -------------------------------------------------------------
            matrix_summary = {
                "run_id": run_id,
                "created_at": datetime.datetime.now().isoformat(),
                "minimum_active_targets_required": 3,
                "control_group_assumption": control_assumption_metadata,
                "matrix": target_matrix,
                "total_targets": len(ALL_TARGETS),
                "confirmed_available_count": sum(1 for v in target_matrix.values() if v["status"] == "confirmed_available_for_run"),
                "confirmed_unavailable_count": sum(1 for v in target_matrix.values() if v["status"] == "confirmed_unavailable_for_run"),
                "unknown_count": sum(1 for v in target_matrix.values() if v["status"] == "unknown")
            }
            
            with open("artifacts/availability/elimination_matrix.json", "w", encoding="utf-8") as f:
                json.dump(matrix_summary, f, indent=2, ensure_ascii=False)
                
            md_matrix = "# Lufthansa Surprise: Availability Elimination Matrix\n\n"
            md_matrix += f"**Run ID:** `{run_id}`  \n"
            md_matrix += f"**Timestamp:** {matrix_summary['created_at']}  \n"
            md_matrix += f"**UI Mindestlimit:** 3 aktive Ziel-Checkboxen  \n"
            md_matrix += f"**Verwendete negative Kontrollgruppe:** `{control_assumption_metadata['negative_controls']}`  \n\n"
            md_matrix += "## Monotonie- & Kontrollgruppen-Validierung\n\n"
            md_matrix += f"- **Monotonie angenommen:** `{control_assumption_metadata['monotonicity_assumed']}`\n"
            md_matrix += f"- **Wiederholter Negativtest (2x bestätigt):** `{control_assumption_metadata['repeated_negative_result']}`\n"
            md_matrix += f"- **Baseline vor Kontrolltest verfügbar:** `{control_assumption_metadata['baseline_before_available']}`\n"
            md_matrix += f"- **Baseline nach Kontrolltest verfügbar:** `{control_assumption_metadata['baseline_after_available']}`\n\n"
            
            md_matrix += "## Ziel-Verfügbarkeitsstatus & Provenienz\n\n"
            md_matrix += "| Zielcode | Stadt | Status | Getestete Konfiguration | Beobachteter Preis | 2x Bestätigt | Checkboxen bewiesen |\n"
            md_matrix += "| :--- | :--- | :--- | :--- | :---: | :---: | :---: |\n"
            for t in ALL_TARGETS:
                data = target_matrix.get(t, {})
                rep_str = "✅" if data.get("repeat_confirmed") else "❌"
                cb_str = "✅" if data.get("checkboxes_verified") else "❌"
                cfg_str = ", ".join(data.get("tested_configuration", []))
                md_matrix += f"| **{t}** | {data.get('destination_name', t)} | `{data.get('status')}` | `{cfg_str}` | {data.get('observed_price') or '-'} | {rep_str} | {cb_str} |\n"
                
            with open("artifacts/availability/elimination_matrix.md", "w", encoding="utf-8") as f:
                f.write(md_matrix)

            # -------------------------------------------------------------
            # PHASE 4: Target Fare Optimizer for PRG
            # -------------------------------------------------------------
            target_dest = "PRG"
            confirmed_avail = [k for k, v in target_matrix.items() if v["status"] == "confirmed_available_for_run"]
            competitors_excluded = [k for k in confirmed_avail if k != target_dest]
            unknown_excluded = [k for k, v in target_matrix.items() if v["status"] == "unknown"]
            
            opt_runs = []
            
            # Variant A: Target + 2 negative controls (exakt 3 active)
            var_a_targets = [target_dest, n1, n2]
            await asyncio.sleep(2)
            res_a = await run_single_check(
                page,
                test_id="phase4_opt_variant_a_triad",
                description=f"Optimizer Variant A: {target_dest} + 2 controls [{n1}, {n2}] (3 targets)",
                active_targets=var_a_targets,
                run_id=run_id
            )
            all_step_logs.append(res_a)
            opt_runs.append({"variant": "A_triad_3_targets", "targets": var_a_targets, "result": res_a})
            
            # Variant B: Target + ALL confirmed unavailable
            var_b_targets = list(set([target_dest] + confirmed_unavailable_all))
            if len(var_b_targets) >= 3 and set(var_b_targets) != set(var_a_targets):
                await asyncio.sleep(2)
                res_b = await run_single_check(
                    page,
                    test_id="phase4_opt_variant_b_all_unavail",
                    description=f"Optimizer Variant B: {target_dest} + all {len(confirmed_unavailable_all)} unavailable targets ({len(var_b_targets)} targets)",
                    active_targets=var_b_targets,
                    run_id=run_id
                )
                all_step_logs.append(res_b)
                opt_runs.append({"variant": "B_all_unavailable", "targets": var_b_targets, "result": res_b})
                
            # Variant C: Intermediate subset (if >= 4 unavailable targets)
            if len(confirmed_unavailable_all) >= 4:
                var_c_targets = [target_dest] + confirmed_unavailable_all[:3] # 4 targets total
                await asyncio.sleep(2)
                res_c = await run_single_check(
                    page,
                    test_id="phase4_opt_variant_c_intermediate",
                    description=f"Optimizer Variant C: {target_dest} + 3 unavailable targets (4 targets)",
                    active_targets=var_c_targets,
                    run_id=run_id
                )
                all_step_logs.append(res_c)
                opt_runs.append({"variant": "C_intermediate", "targets": var_c_targets, "result": res_c})
                
            # Select Best Empirical Configuration (Lowest price with available status)
            valid_opt_runs = [r for r in opt_runs if r["result"]["status"] == "available" and r["result"].get("price")]
            
            def parse_price(p_str):
                if not p_str: return 999999.0
                m = re.search(r'(\d+[\.,]?\d*)', p_str)
                return float(m.group(1).replace(",", ".")) if m else 999999.0

            best_variant = min(valid_opt_runs, key=lambda x: parse_price(x["result"]["price"]), default=None)
            
            # -------------------------------------------------------------
            # PHASE 4.1: Final Verification Run (Re-Check All Key States)
            # -------------------------------------------------------------
            print("\n--- RUNNING FINAL VERIFICATION PASS ---")
            
            # 1. Final Baseline Re-check
            await asyncio.sleep(2)
            baseline_final = await run_single_check(
                page,
                test_id="final_verification_baseline",
                description="Final Verification: Baseline (All 11 Targets)",
                active_targets=ALL_TARGETS,
                run_id=run_id
            )
            all_step_logs.append(baseline_final)
            
            # 2. Final Negative Control Re-check
            await asyncio.sleep(2)
            neg_ctrl_final = await run_single_check(
                page,
                test_id="final_verification_negative_control",
                description=f"Final Verification: Negative Control Triad ({', '.join(confirmed_unavailable_triads[0])})",
                active_targets=confirmed_unavailable_triads[0],
                run_id=run_id
            )
            all_step_logs.append(neg_ctrl_final)
            
            # 3. Final Target Best Configuration Re-check
            best_cfg_final = None
            if best_variant:
                await asyncio.sleep(2)
                best_cfg_final = await run_single_check(
                    page,
                    test_id="final_verification_best_target_config",
                    description=f"Final Verification: Best Configuration for {target_dest}",
                    active_targets=best_variant["targets"],
                    run_id=run_id
                )
                all_step_logs.append(best_cfg_final)
                
            inventory_stable = (
                baseline_init["status"] == baseline_final["status"] == "available" and
                baseline_init["price"] == baseline_final["price"] and
                neg_ctrl_final["status"] == "unavailable"
            )
            
            final_verification = (
                inventory_stable and
                best_cfg_final is not None and
                best_cfg_final["status"] == "available" and
                best_cfg_final["price"] == best_variant["result"]["price"]
            )
            
            triad_opt = next((r for r in opt_runs if r["variant"] == "A_triad_3_targets"), None)
            price_3_targets = triad_opt["result"]["price"] if triad_opt and triad_opt["result"].get("price") else "-"
            opt_price = best_variant["result"]["price"] if best_variant else "-"
            
            opt_report_data = {
                "run_id": run_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "target_destination": target_dest,
                "target_name": TARGET_NAMES.get(target_dest, target_dest),
                "minimum_active_targets": 3,
                "negative_controls_used": [n1, n2],
                "all_confirmed_unavailable_used": confirmed_unavailable_all,
                "baseline_initial_price": baseline_init["price"],
                "baseline_final_price": baseline_final["price"],
                "inventory_stable": inventory_stable,
                "final_verification": final_verification,
                "active_targets_in_recommended_config": best_variant["targets"] if best_variant else [],
                "passive_unavailable_targets_retained": [t for t in (best_variant["targets"] if best_variant else []) if t != target_dest],
                "competitors_excluded": competitors_excluded,
                "unknown_targets_excluded": unknown_excluded,
                "price_with_3_targets": price_3_targets,
                "optimized_price": opt_price,
                "best_variant_name": best_variant["variant"] if best_variant else None,
                "disclaimer": "Unter den in diesem Lauf einzeln kontrollierten Zielen war in der empfohlenen Konfiguration nur das Wunschziel als verfügbar bestätigt. Lufthansa-Inventar und Preise können sich jederzeit ändern; die endgültige Zuteilung erfolgt erst nach der Buchung."
            }
            
            with open("artifacts/optimizer/target_fare_recommendation.json", "w", encoding="utf-8") as f:
                json.dump(opt_report_data, f, indent=2, ensure_ascii=False)
                
            md_opt = "# Lufthansa Surprise: Target Fare Optimizer Abschlussbericht\n\n"
            md_opt += f"**Run ID:** `{run_id}`  \n"
            md_opt += f"**Timestamp:** {opt_report_data['timestamp']}  \n"
            md_opt += f"**Wunschziel:** `{target_dest}` ({TARGET_NAMES.get(target_dest, target_dest)})  \n"
            md_opt += f"**UI-Mindestlimit:** 3 aktive Zielcheckboxen  \n"
            md_opt += f"**Verwendete negative Kontrollgruppe:** `{opt_report_data['negative_controls_used']}`  \n"
            md_opt += f"**Inventar unverändert & stabil:** `{'Ja' if inventory_stable else 'NEIN (Inventory Changed!)'}`  \n"
            md_opt += f"**Final Verification:** `{'true' if final_verification else 'false'}`  \n\n"
            
            md_opt += "## Preisübersicht & Optimierung\n\n"
            md_opt += f"- **Baseline-Preis (alle 11 Ziele aktiv):** `{baseline_init['price']}`\n"
            md_opt += f"- **Preis mit exakt 3 Zielen (Prag + 2 Kontrollziele):** `{price_3_targets}`\n"
            md_opt += f"- **Optimierter Preis (Prag + alle nicht verfügbaren Puffer):** `{opt_price}`\n\n"
            
            md_opt += "## Empfohlene Checkbox-Konfiguration\n\n"
            md_opt += f"- **Aktiv zu lassendes Wunschziel:** `['{target_dest}']`\n"
            md_opt += f"- **Aktiv zu lassende passive Puffer-Ziele (im aktuellen Lauf nicht verfügbar):** `{opt_report_data['passive_unavailable_targets_retained']}`\n"
            md_opt += f"- **Auszuschließende tatsächlich verfügbare Konkurrenzziele:** `{competitors_excluded}`\n"
            md_opt += f"- **Auszuschließende uneindeutige / Unknown-Ziele:** `{unknown_excluded}`\n\n"
            
            md_opt += "## Verbindlicher Hinweis\n\n"
            md_opt += f"> [!IMPORTANT]\n> {opt_report_data['disclaimer']}\n\n"
            md_opt += "> Keine Buchung, keine Zahlung und keine Garantie der endgültigen Zuteilung durch Lufthansa Surprise.\n"
            
            with open("artifacts/optimizer/target_fare_recommendation.md", "w", encoding="utf-8") as f:
                f.write(md_opt)
                
            print("\nExecution completely finished. All artifacts written successfully.")
            
        except Exception as e:
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
