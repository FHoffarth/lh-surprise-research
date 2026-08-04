"""Browser setup for Playwright Chromium.

- Headed mode by default
- No custom User-Agent (Playwright default is used)
- Single active page
- German locale and timezone
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

logger = logging.getLogger(__name__)

# Default navigation/action timeout in milliseconds
NAV_TIMEOUT_MS = 30_000
ACTION_TIMEOUT_MS = 15_000


@asynccontextmanager
async def create_browser_context(
    headless: bool = False,
) -> AsyncGenerator[tuple[Playwright, Browser, BrowserContext, Page], None]:
    """
    Async context manager that yields (playwright, browser, context, page).

    - Chromium browser (headed by default)
    - Locale: de-DE, timezone: Europe/Berlin
    - No custom User-Agent (uses Playwright default)
    - Single page; no parallel tabs
    """
    async with async_playwright() as pw:
        logger.info("Launching Chromium (headless=%s)", headless)
        browser = await pw.chromium.launch(headless=headless)
        context = await browser.new_context(
            locale="de-DE",
            timezone_id="Europe/Berlin",
            viewport={"width": 1280, "height": 800},
            # No user_agent override – Playwright default is used
        )
        context.set_default_timeout(NAV_TIMEOUT_MS)
        context.set_default_navigation_timeout(NAV_TIMEOUT_MS)

        page = await context.new_page()

        try:
            yield pw, browser, context, page
        finally:
            logger.info("Closing browser")
            await context.close()
            await browser.close()


async def get_playwright_version(pw: Playwright) -> str:
    """Return Playwright version string."""
    try:
        import importlib.metadata
        return importlib.metadata.version("playwright")
    except Exception:
        return "unknown"


async def get_browser_version(browser: Browser) -> str:
    """Return Chromium browser version string."""
    try:
        return browser.version
    except Exception:
        return "unknown"
