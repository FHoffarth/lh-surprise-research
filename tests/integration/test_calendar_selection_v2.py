import asyncio
from playwright.async_api import async_playwright
import traceback

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            url = "https://www.lufthansa-surprise.com/"
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            
            accept = page.locator("button:has-text('Einverstanden')")
            if await accept.count() > 0:
                await accept.first.click()
                await asyncio.sleep(1)
                
            fra = page.locator("text='Frankfurt/Main'")
            if await fra.count() > 0:
                await fra.first.click()
                await asyncio.sleep(2)
                
            arts = page.locator("text='Kunst und Kultur'")
            if await arts.count() > 0:
                await arts.first.click()
                await asyncio.sleep(1)
                
                ok_btn = page.locator("button:has-text('OK')")
                if await ok_btn.count() > 0:
                    await ok_btn.first.click()
                    await asyncio.sleep(2)
                
            reisedaten = page.locator("text='Reisedaten eingeben'")
            if await reisedaten.count() > 0:
                await reisedaten.first.click()
                await asyncio.sleep(3)
                
            # 1. Select Start Date
            print("Opening start date calendar...")
            await page.locator("#earliestOut").click()
            await asyncio.sleep(1)
            
            # Click 7. August 2026
            # Find day with exact text "7" in active month
            day7 = page.locator(".react-datepicker__day[aria-label*='7. August 2026']")
            if await day7.count() > 0:
                print("Found Day 7 by aria-label! Clicking...")
                await day7.first.click()
                await asyncio.sleep(1)
            else:
                print("Day 7 with aria-label not found, trying text...")
                day7_text = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="7")
                await day7_text.first.click()
                await asyncio.sleep(1)
                
            # 2. Select Return Date
            print("Opening return date calendar...")
            await page.locator("#latestRet").click()
            await asyncio.sleep(1)
            
            day9 = page.locator(".react-datepicker__day[aria-label*='9. August 2026']")
            if await day9.count() > 0:
                print("Found Day 9 by aria-label! Clicking...")
                await day9.first.click()
                await asyncio.sleep(1)
            else:
                print("Day 9 with aria-label not found, trying text...")
                day9_text = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="9")
                if await day9_text.count() > 0:
                    await day9_text.first.click()
                    await asyncio.sleep(1)
                else:
                    print("Day 9 still not found!")
                    
            val_out = await page.locator("#earliestOut").input_value()
            val_ret = await page.locator("#latestRet").input_value()
            print(f"Final verified earliestOut: {val_out}")
            print(f"Final verified latestRet: {val_ret}")
            
            await page.screenshot(path="artifacts/screenshots/calendar_final_verified.png")
            
        except Exception as e:
            traceback.print_exc()
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
