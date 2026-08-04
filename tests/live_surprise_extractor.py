import asyncio
from playwright.async_api import async_playwright
import json

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        url = "https://www.lufthansa-surprise.com/"
        print(f"Trying {url}...")
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)
            title = await page.title()
            print(f"Title: {title}")
        except Exception as e:
            print(f"Failed to load {url}: {e}")
                
        # accept cookies if any
        try:
            accept = page.locator("button:has-text('Nur erforderliche'), button:has-text('Alle akzeptieren'), button:has-text('Accept')")
            if await accept.count() > 0:
                await accept.first.click()
                await asyncio.sleep(2)
        except:
            pass

        # We need to fill in:
        # Abflug: FRA
        # Hinflug: 07.08.2026
        # Rückflug: 09.08.2026
        # 1 Erwachsener, Economy, Arts & Sights
        
        # Since the UI is dynamic, let's just dump the text and save a screenshot, and let the user interact or parse what's there
        # Wait, if I am extracting from the DOM, let's dump the DOM elements and their text
        
        text_content = await page.evaluate("document.body.innerText")
        with open("artifacts/surprise_page_text.txt", "w", encoding="utf-8") as f:
            f.write(text_content)
            
        await page.screenshot(path="artifacts/screenshots/surprise_page_live.png")
        
        await browser.close()
        print("Done. Saved text to artifacts/surprise_page_text.txt and screenshot to artifacts/screenshots/surprise_page_live.png")

if __name__ == "__main__":
    asyncio.run(main())
