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
            await fra.first.click()
            await asyncio.sleep(2)
            
            arts = page.locator("text='Kunst und Kultur'")
            await arts.first.click()
            await asyncio.sleep(1)
            
            ok_btn = page.locator("button:has-text('OK')")
            if await ok_btn.count() > 0:
                await ok_btn.first.click()
                await asyncio.sleep(2)
                
            reisedaten = page.locator("text='Reisedaten eingeben'")
            await reisedaten.first.click()
            await asyncio.sleep(3)
            
            # 1. Select Start Date
            print("Opening start date calendar...")
            await page.locator("#earliestOut").click()
            await asyncio.sleep(1)
            
            # Click 7. August 2026
            day7 = page.locator(".react-datepicker__day[aria-label*='7. August 2026']")
            if await day7.count() == 0:
                day7 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="7")
            await day7.first.click()
            await asyncio.sleep(1)
            
            # 2. Select Return Date
            print("Opening return date calendar...")
            await page.locator("#latestRet").click()
            await asyncio.sleep(1)
            
            day9 = page.locator(".react-datepicker__day[aria-label*='9. August 2026']")
            if await day9.count() == 0:
                day9 = page.locator(".react-datepicker__day:not(.react-datepicker__day--outside-month)", has_text="9")
            await day9.first.click()
            await asyncio.sleep(1)
            
            # 3. Close the modal if open
            close_btn = page.locator(".datepicker-modal button.close, button.closeButton")
            if await close_btn.count() > 0 and await close_btn.is_visible():
                print("Closing datepicker modal...")
                await close_btn.first.click()
                await asyncio.sleep(1)
            else:
                print("Modal close button not visible, pressing Escape...")
                await page.keyboard.press("Escape")
                await asyncio.sleep(1)
                
            val_out = await page.locator("#earliestOut").input_value()
            val_ret = await page.locator("#latestRet").input_value()
            print(f"Final verified earliestOut: {val_out}")
            print(f"Final verified latestRet: {val_ret}")
            
            # Try clicking Weiter
            weiter = page.locator("button:has-text('Weiter')")
            print("Clicking Weiter...")
            await weiter.first.click()
            await asyncio.sleep(5)
            
            text_content = await page.evaluate("document.body.innerText")
            print("Next page loaded! Content preview:", text_content[:200])
            await page.screenshot(path="artifacts/screenshots/next_page_after_weiter.png")
            
        except Exception as e:
            traceback.print_exc()
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
