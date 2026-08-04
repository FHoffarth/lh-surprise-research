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
            accept = page.locator("button:has-text('Einverstanden'), button:has-text('Alle akzeptieren'), button:has-text('Accept')")
            if await accept.count() > 0:
                await accept.first.click()
                await asyncio.sleep(1)
                
            # Click Frankfurt
            fra = page.locator("text=Frankfurt/Main")
            if await fra.count() > 0:
                await fra.first.click()
                await asyncio.sleep(3)
                
            # Click Kunst und Kultur
            arts = page.locator("text=Kunst und Kultur")
            if await arts.count() > 0:
                await arts.first.click()
                await asyncio.sleep(2)
                
                # Check if there is an OK button
                ok_btn = page.locator("button:has-text('OK'), button:has-text('Weiter')")
                if await ok_btn.count() > 0:
                    await ok_btn.first.click()
                    await asyncio.sleep(4)
                
            # Click Reisedaten eingeben
            reisedaten = page.locator("button:has-text('Reisedaten eingeben'), text=Reisedaten eingeben")
            if await reisedaten.count() > 0:
                await reisedaten.first.click()
                await asyncio.sleep(4)
                
            # dump text
            text_content = await page.evaluate("document.body.innerText")
            with open("artifacts/surprise_page_text4.txt", "w", encoding="utf-8") as f:
                f.write(text_content)
                
            await page.screenshot(path="artifacts/screenshots/surprise_page_step4.png")
            print("Done step 4")
            
        except Exception as e:
            traceback.print_exc()
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
