import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Loading page...")
        await page.goto("https://www.lufthansa-surprise.com/travel-theme")
        await page.wait_for_selector(".chip-span.origins")
        await page.locator("#cookie_agree").click()
        await page.locator("span[role='button']:has-text('Frankfurt/Main')").click()
        print("Waiting for theme section...")
        await page.wait_for_selector(".pools-region")
        await page.evaluate("document.querySelector('input[type=\"radio\"]').click()")
        await page.wait_for_timeout(1000)
        print("Clicking weiter...")
        await page.evaluate("document.getElementById('whereToMain').click()")
        print("Waiting for next page...")
        await page.wait_for_selector("h1, h2")
        await page.wait_for_timeout(3000)
        
        html = await page.content()
        with open("artifacts/compose_trip.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved compose_trip.html")
        await browser.close()

asyncio.run(main())
