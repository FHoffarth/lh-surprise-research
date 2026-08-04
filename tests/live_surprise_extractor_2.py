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
            print(f"Loading {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            
            # accept cookies
            accept = page.locator("button:has-text('Einverstanden'), button:has-text('Alle akzeptieren'), button:has-text('Accept')")
            if await accept.count() > 0:
                await accept.first.click()
                await asyncio.sleep(1)
                
            # Click Frankfurt
            fra = page.locator("text=Frankfurt/Main")
            if await fra.count() > 0:
                await fra.first.click()
                await asyncio.sleep(3)
                
            # Now dump text
            text_content = await page.evaluate("document.body.innerText")
            with open("artifacts/surprise_page_text2.txt", "w", encoding="utf-8") as f:
                f.write(text_content)
                
            await page.screenshot(path="artifacts/screenshots/surprise_page_step2.png")
            print("Done step 2")
            
        except Exception as e:
            traceback.print_exc()
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
