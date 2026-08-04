import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Test deeplink
        url = "https://www.lufthansa.com/de/de/fluege?origin=FRA&destination=PRG"
        print(f"Going to {url}")
        await page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Accept cookies
        accept = page.locator("button:has-text('Nur erforderliche')")
        if await accept.count() > 0:
            await accept.first.click()
            await asyncio.sleep(2)
            
        await page.screenshot(path="artifacts/screenshots/test_deeplink2.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
