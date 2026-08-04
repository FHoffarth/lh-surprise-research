import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        url = "https://www.lufthansa.com/de/de/homepage"
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Accept cookies
        accept = page.locator("button:has-text('Nur erforderliche'), button:has-text('Alle akzeptieren')")
        if await accept.count() > 0:
            await accept.first.click()
            await asyncio.sleep(2)
        else:
            await page.evaluate("document.getElementById('onetrust-consent-sdk')?.remove()")
            
        # Select One way
        # Look for the dropdown that says "Round trip" or "Hin- und Rückflug"
        dropdown = page.locator("button:has-text('Round trip'), button:has-text('Hin- und Rückflug')")
        if await dropdown.count() > 0:
            await dropdown.first.click()
            await asyncio.sleep(1)
            oneway = page.locator("button:has-text('One way'), button:has-text('Nur Hinflug'), li:has-text('Nur Hinflug')")
            if await oneway.count() > 0:
                await oneway.first.click()
        await asyncio.sleep(1)
        
        # Fill origin
        origin = page.locator("input[placeholder*='Von'], input[aria-label*='Von']")
        await origin.first.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await origin.first.type("FRA", delay=100)
        await asyncio.sleep(1)
        await page.keyboard.press("Enter")
        
        # Fill dest
        dest = page.locator("input[placeholder*='Nach'], input[aria-label*='Nach']")
        await dest.first.click()
        await dest.first.type("PRG", delay=100)
        await asyncio.sleep(1)
        await page.keyboard.press("Enter")
        
        # Fill date
        date_input = page.locator("input[placeholder*='Hin'], input[placeholder*='Outbound']")
        await date_input.first.click()
        await asyncio.sleep(0.5)
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await date_input.first.type("07.08.2026", delay=100)
        await asyncio.sleep(0.5)
        await page.keyboard.press("Enter")
        
        await asyncio.sleep(1)
        
        # Click search
        search = page.locator("button[type='submit']:has-text('Suchen'), button:has-text('Flüge suchen'), button:has-text('Search flights')")
        if await search.count() > 0:
            await search.first.click()
            
        await asyncio.sleep(5)
        await page.screenshot(path="artifacts/screenshots/test_homepage.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
