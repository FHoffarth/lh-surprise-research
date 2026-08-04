import asyncio
from playwright.async_api import async_playwright

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
            if await fra.count() > 0:
                await fra.first.click()
                await asyncio.sleep(3)
                
            arts = page.locator("text='Kunst und Kultur'")
            if await arts.count() > 0:
                await arts.first.click()
                await asyncio.sleep(2)
                
                ok_btn = page.locator("button:has-text('OK')")
                if await ok_btn.count() > 0:
                    await ok_btn.first.click()
                    await asyncio.sleep(2)
                
            reisedaten = page.locator("text='Reisedaten eingeben'")
            if await reisedaten.count() > 0:
                await reisedaten.first.click()
                await asyncio.sleep(3)
                
            html_content = await page.content()
            with open("artifacts/surprise_page_step5.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
        except Exception as e:
            pass
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
