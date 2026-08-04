import asyncio
import json
import os
import traceback
from playwright.async_api import async_playwright

async def setup_page(page):
    url = "https://www.lufthansa-surprise.com/"
    # print(f"Setting up page...")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(2)
    
    # accept cookies if visible
    try:
        accept = page.locator("button:has-text('Einverstanden'), button:has-text('Alle akzeptieren')")
        if await accept.count() > 0:
            await accept.first.click()
            await asyncio.sleep(1)
    except:
        pass
        
    # Click Frankfurt
    fra = page.locator("text='Frankfurt/Main'")
    if await fra.count() > 0:
        await fra.first.click()
        await asyncio.sleep(2)
        
    # Click Kunst und Kultur
    arts = page.locator("text='Kunst und Kultur'")
    if await arts.count() > 0:
        await arts.first.click()
        await asyncio.sleep(1)
        
        ok_btn = page.locator("button:has-text('OK')")
        if await ok_btn.count() > 0:
            await ok_btn.first.click()
            await asyncio.sleep(2)
            
    # Click Reisedaten eingeben
    reisedaten = page.locator("text='Reisedaten eingeben'")
    if await reisedaten.count() > 0:
        await reisedaten.first.click()
        await asyncio.sleep(3)

    # Force dates
    await page.evaluate("""
        let out = document.getElementById('earliestOut');
        let ret = document.getElementById('latestRet');
        if(out && ret) {
            out.removeAttribute('readonly');
            ret.removeAttribute('readonly');
            out.value = '07.08.2026';
            ret.value = '09.08.2026';
            out.dispatchEvent(new Event('input', { bubbles: true }));
            out.dispatchEvent(new Event('change', { bubbles: true }));
            ret.dispatchEvent(new Event('input', { bubbles: true }));
            ret.dispatchEvent(new Event('change', { bubbles: true }));
        }
    """)
    await asyncio.sleep(1)

async def test_group(page, all_targets, active_targets):
    print(f"\nTesting group: {active_targets}")
    
    # Reload page to clean state
    await setup_page(page)
    
    # Set checkboxes
    for target in all_targets:
        checkbox = page.locator(f"id=pool_destion_{target}")
        if await checkbox.count() > 0:
            is_checked = await checkbox.is_checked()
            should_be_checked = target in active_targets
            
            if is_checked and not should_be_checked:
                await page.evaluate(f"document.getElementById('pool_destion_{target}').click()")
                await asyncio.sleep(0.5)
            elif not is_checked and should_be_checked:
                await page.evaluate(f"document.getElementById('pool_destion_{target}').click()")
                await asyncio.sleep(0.5)
                
    await asyncio.sleep(1)
    
    # Click Weiter
    weiter = page.locator("button:has-text('Weiter')")
    if await weiter.count() > 0:
        await weiter.first.click()
    else:
        print("Weiter button not found! Maybe block or CAPTCHA?")
        return "blocked", None
        
    await asyncio.sleep(5)
    
    text_content = await page.evaluate("document.body.innerText")
    
    status = "unknown"
    price = None
    
    if "Leider sind für die von Ihnen gewählten" in text_content or "keine verfügbaren" in text_content.lower() or "nicht verfügbar" in text_content.lower() or "nicht möglich" in text_content.lower():
        status = "unavailable"
    elif "Gesamtpreis" in text_content or "€" in text_content or "Buchungsinformationen" in text_content:
        status = "available"
        import re
        m = re.search(r'€\s*(\d+)', text_content)
        if m:
            price = f"€ {m.group(1)}"
        else:
            # Check other currency formats
            m2 = re.search(r'(\d+)\s*€', text_content)
            if m2:
                price = f"{m2.group(1)} €"
            else:
                price = "Preis gefunden, aber nicht parslar"
    elif "Access Denied" in text_content or "Security" in text_content or "CAPTCHA" in text_content:
        status = "blocked"
    else:
        status = "ambiguous"
        
    print(f"Result for {active_targets}: {status} (Price: {price})")
    return status, price

async def run_elimination(page, all_targets):
    results = {}
    
    print("Running baseline test...")
    status, base_price = await test_group(page, all_targets, all_targets)
    if status != "available":
        print(f"Baseline failed with status: {status}! Aborting elimination.")
        return results, base_price
        
    async def eliminate(targets):
        if len(targets) == 0:
            return
            
        if len(targets) == 1:
            t = targets[0]
            st, pr = await test_group(page, all_targets, [t])
            results[t] = {"status": st, "price": pr}
            return
            
        st, pr = await test_group(page, all_targets, targets)
        if st == "unavailable":
            for t in targets:
                results[t] = {"status": "unavailable", "price": None}
            return
        elif st == "blocked":
            print("Blocked during elimination! Aborting.")
            for t in targets:
                results[t] = {"status": "blocked", "price": None}
            return
            
        mid = len(targets) // 2
        left = targets[:mid]
        right = targets[mid:]
        
        await eliminate(left)
        await eliminate(right)
        
    await eliminate(all_targets)
    return results, base_price

async def main():
    os.makedirs("artifacts/availability", exist_ok=True)
    all_targets = ["FLR", "PRG", "WAW", "WRO", "HEL", "BLQ", "KRK", "BSL", "SJJ", "LIN", "PUY"]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            results, base_price = await run_elimination(page, all_targets)
            
            output = {
                "parameters": {
                    "origin": "FRA",
                    "theme": "Arts & Sights",
                    "outbound": "07.08.2026",
                    "return": "09.08.2026",
                    "travelers": 1,
                    "class": "Economy",
                    "flexibility": "Full Flex"
                },
                "baseline_price": base_price,
                "results": results,
                "ui_checks_performed": len(results) * 2 # rough estimate
            }
            
            with open("artifacts/availability/elimination_results.json", "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                
            md = "# Lufthansa Surprise Availability Elimination (Live)\n\n"
            md += f"**Baseline-Preis (Alle Ziele aktiv):** {base_price or 'Unbekannt'}\n\n"
            md += "## Bestätigt VERFÜGBAR:\n"
            avail_count = 0
            for t, data in results.items():
                if data["status"] == "available":
                    md += f"- **{t}**: {data['price'] or 'Preis nicht ausgelesen'}\n"
                    avail_count += 1
            if avail_count == 0:
                md += "- Keine Ziele als verfügbar bestätigt.\n"
                
            md += "\n## Bestätigt NICHT VERFÜGBAR:\n"
            unavail_count = 0
            for t, data in results.items():
                if data["status"] == "unavailable":
                    md += f"- **{t}**\n"
                    unavail_count += 1
            if unavail_count == 0:
                md += "- Keine Ziele eindeutig als nicht verfügbar bestätigt.\n"
                
            md += "\n## Uneindeutig / Fehlerhaft:\n"
            for t, data in results.items():
                if data["status"] not in ("available", "unavailable"):
                    md += f"- **{t}**: {data['status']}\n"
                    
            with open("artifacts/availability/tonight_availability.md", "w", encoding="utf-8") as f:
                f.write(md)
                
            print("Elimination complete. Artifacts written.")
            
        except Exception as e:
            traceback.print_exc()
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
