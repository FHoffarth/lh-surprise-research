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
            
            # accept cookies
            accept = page.locator("button:has-text('Einverstanden')")
            if await accept.count() > 0:
                await accept.first.click()
                await asyncio.sleep(1)
                
            # Click Frankfurt
            fra = page.locator("text='Frankfurt/Main'")
            if await fra.count() > 0:
                await fra.first.click()
                await asyncio.sleep(3)
                
            # Click Kunst und Kultur
            arts = page.locator("text='Kunst und Kultur'")
            if await arts.count() > 0:
                await arts.first.click()
                await asyncio.sleep(2)
                
                # OK button
                ok_btn = page.locator("button:has-text('OK')")
                if await ok_btn.count() > 0:
                    await ok_btn.first.click()
                    await asyncio.sleep(2)
                
            # Click Reisedaten eingeben
            reisedaten = page.locator("text='Reisedaten eingeben'")
            if await reisedaten.count() > 0:
                await reisedaten.first.click()
                await asyncio.sleep(3)
                
            # Now we are on step 3 (Dates)
            # Dump text
            text_content = await page.evaluate("document.body.innerText")
            with open("artifacts/surprise_page_text5.txt", "w", encoding="utf-8") as f:
                f.write(text_content)
                
            await page.screenshot(path="artifacts/screenshots/surprise_page_step5.png")
            print("Done step 5")
            
        except Exception as e:
            traceback.print_exc()
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
