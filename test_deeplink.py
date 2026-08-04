import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Test deeplink
        url = "https://www.lufthansa.com/de/de/fluege?origin=FRA&destination=PRG&outboundDate=2026-08-07"
        print(f"Going to {url}")
        await page.goto(url)
        await asyncio.sleep(10)
        await page.screenshot(path="artifacts/screenshots/test_deeplink.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
