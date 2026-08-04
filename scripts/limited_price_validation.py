import asyncio
import os
import re
import datetime
from playwright.async_api import async_playwright

ALL_TARGETS = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]
SCREENSHOTS_DIR = "artifacts/screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

async def run_single_test(test_id: str, active_targets: list) -> dict:
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{test_id}] Starting run with active targets: {active_targets}")
    
    async with async_playwright() as p:
        # Launch headful to match previous verification test practices
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale="de-DE")
        page = await context.new_page()
        
        url = "https://www.lufthansa-surprise.com/"
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # Accept Cookies
        try:
            accept = page.locator("button:has-text('Einverstanden')")
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
            await asyncio.sleep(2)
            
        # Reisedaten
        await page.locator("text='Reisedaten eingeben'").first.click()
        await asyncio.sleep(3)
        
        # Date Clicks (7. August 2026 - 9. August 2026)
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
        
        # Toggle checkboxes to match active_targets
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
                
        before_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_before.png")
        await page.screenshot(path=before_screenshot, full_page=True)
        
        if len(mismatches) > 0:
            print(f"[{test_id}] Checkbox state verification failed! Mismatches: {mismatches}")
            await browser.close()
            return {
                "test_id": test_id,
                "status": "validation_failed",
                "error": f"Checkbox mismatch: {mismatches}",
                "timestamp": timestamp
            }
            
        # Click Weiter
        weiter = page.locator("button:has-text('Weiter')")
        await weiter.first.click()
        print(f"[{test_id}] Clicked Weiter. Waiting for response...")
        await asyncio.sleep(7)
        
        after_screenshot = os.path.join(SCREENSHOTS_DIR, f"{test_id}_after.png")
        await page.screenshot(path=after_screenshot, full_page=True)
        
        page_text = await page.evaluate("document.body.innerText")
        
        status = "unknown"
        price = None
        details = ""
        
        if "Security check" in page_text or "Sicherheitscheck" in page_text or "resembles that of a bot" in page_text:
            status = "blocked"
            details = "Bot security check triggered"
        elif (
            "Leider sind für die von Ihnen gewählten" in page_text or
            "keine verfügbaren flüge" in page_text.lower() or
            "für ihre auswahl leider keine flüge" in page_text.lower() or
            "nicht verfügbar" in page_text.lower()
        ):
            status = "unavailable"
            details = "Explicit no-availability on UI"
        else:
            status = "available"
            m = re.search(r'Gesamtpreis\s*\n\s*(\d+[\.,]\d{2}\s*€?)', page_text)
            if m:
                price = m.group(1).strip()
            else:
                m2 = re.search(r'€\s*(\d+[\.,]?\d*)', page_text)
                if m2:
                    price = f"€ {m2.group(1)}"
            details = "Offer page loaded"
            
        await browser.close()
        
        print(f"[{test_id}] Result: status={status}, price={price}, details={details}")
        return {
            "test_id": test_id,
            "status": status,
            "price": price,
            "details": details,
            "timestamp": timestamp,
            "active_targets": active_targets
        }

async def main():
    results = []
    
    # 1. Baseline 1 (All 11 targets active)
    res_b1 = await run_single_test("baseline_1", ALL_TARGETS)
    results.append(res_b1)
    await asyncio.sleep(5) # Stable cooldown
    
    # 2. Test k=2 (9 active, FLR and PRG deactivated)
    k2_targets = [t for t in ALL_TARGETS if t not in ["FLR", "PRG"]]
    res_k2 = await run_single_test("k2_test", k2_targets)
    results.append(res_k2)
    await asyncio.sleep(5)
    
    # 3. Test k=3 (8 active, FLR, PRG, WAW deactivated)
    k3_targets = [t for t in ALL_TARGETS if t not in ["FLR", "PRG", "WAW"]]
    res_k3 = await run_single_test("k3_test", k3_targets)
    results.append(res_k3)
    await asyncio.sleep(5)
    
    # 4. Baseline 2 (All 11 targets active)
    res_b2 = await run_single_test("baseline_2", ALL_TARGETS)
    results.append(res_b2)
    
    # Document results into a markdown artifact
    report_content = f"""# Limited Price Validation Report (v0.1 Repair Run)

Executed on: {datetime.datetime.now().isoformat()}

## Summary of Results

| Run ID | k | Active Targets | Status | Price | Details | Timestamp |
|---|---|---|---|---|---|---|
"""
    for r in results:
        active_str = ", ".join(r.get("active_targets", []))
        report_content += f"| {r['test_id']} | {11 - len(r.get('active_targets', []))} | {active_str} | {r['status']} | {r.get('price')} | {r.get('details')} | {r['timestamp']} |\n"
        
    report_content += """
## Interpretation & Findings
- **Baseline stability:** Check if baseline_1 matches baseline_2 (usually 129,00 €).
- **Price comparison:** Compare baseline (129,00 €) with k=2 and k=3. 
- **Linearity vs Composition:** Helps confirm if prices scale additively for small k or if composition effects dominate.
"""
    
    os.makedirs("artifacts/price_validation", exist_ok=True)
    with open("artifacts/price_validation/repaired_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print("Price validation completed. Report written to artifacts/price_validation/repaired_validation_report.md")

if __name__ == "__main__":
    asyncio.run(main())
