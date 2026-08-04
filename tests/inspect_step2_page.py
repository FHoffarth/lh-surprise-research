import re

# Let's inspect the page content text
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        url = "https://www.lufthansa-surprise.com/"
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # cookies
        accept = page.locator("button:has-text('Einverstanden')")
        if await accept.count() > 0:
            await accept.first.click()
            await asyncio.sleep(1)
            
        await page.locator("text='Frankfurt/Main'").first.click()
        await asyncio.sleep(2)
        
        await page.locator("text='Kunst und Kultur'").first.click()
        await asyncio.sleep(1)
        ok_btn = page.locator("button:has-text('OK')")
        if await ok_btn.count() > 0:
            await ok_btn.first.click()
            await asyncio.sleep(2)
            
        await page.locator("text='Reisedaten eingeben'").first.click()
        await asyncio.sleep(3)
        
        # Dates
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
        
        # Close modal
        close_btn = page.locator(".datepicker-modal button.close, button.closeButton")
        if await close_btn.count() > 0 and await close_btn.is_visible():
            await close_btn.first.click()
        else:
            await page.keyboard.press("Escape")
        await asyncio.sleep(1)
        
        # Click Weiter
        await page.locator("button:has-text('Weiter')").first.click()
        await asyncio.sleep(6)
        
        text = await page.evaluate("document.body.innerText")
        print("=== PAGE TEXT FULL ===")
        print(text)
        print("=======================")
        
        with open("artifacts/step2_page_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
