"""Main scraping logic for Lufthansa Surprise.

Workflow:
1. Open page
2. Handle cookie banner
3. Set departure airport
4. Set dates
5. Set passengers
6. List themes
7. For each theme (or just first in smoke-test mode):
   a. Click theme (safety-checked)
   b. Wait for concrete UI state
   c. Extract data
   d. Screenshot
   e. Navigate back (reproducible path)
   f. Verify we're back at overview
   g. Wait 1-3 seconds
8. Final screenshot
9. Export

Safety: no booking, no payment, no purchase is ever triggered.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from pathlib import Path
from typing import Any, Optional

from playwright.async_api import Page, TimeoutError as PWTimeoutError

from .config import BASE_URL, Config
from .extractor import ThemeData, extract_theme_data
from .network_monitor import NetworkMonitor
from .utils import is_safe_to_click

logger = logging.getLogger(__name__)

# Selectors for the theme overview page – based on actual DOM inspection
# The theme overview is the page showing the airport selection + pool grid
OVERVIEW_INDICATORS = [
    ".pools-region",
    "div.pool",
    "h2:has-text('Reisethema')",
    "[role='grid']",
    "label.poolName",
]

# Selectors for individual theme cards in the overview
# Real DOM structure: div[role='gridcell'].pool with label.poolName inside
THEME_CARD_SELECTORS = [
    ".pools-region [role='gridcell'].pool",
    "[role='gridcell'].pool",
    "div.pool",
    "[data-testid*='theme-card']",
    "[aria-label*='Reisethema']",
]

# Selectors to wait for theme section to appear after airport click
THEME_SECTION_INDICATORS = [
    ".pools-region",
    ".pools-region [role='gridcell']",
    "div.pool",
    ".chip-span:not(.origins)",
    "h2:has-text('Reisethema')",
]

# Selectors for the theme overview page indicators
OVERVIEW_INDICATORS = [
    ".pools-region",
    "[role='grid'][class*='pools']",
    "div.pool",
    "h2:has-text('Reisethema')",
    "h2:has-text('Wählen Sie Ihr Reisethema')",
    "[data-testid*='theme-list']",
]

# Cookie banner accept button selectors – based on actual DOM
COOKIE_ACCEPT_SELECTORS = [
    "#cookie_agree",
    "button:has-text('Einverstanden')",
    "button:has-text('Akzeptieren')",
    "button:has-text('Accept')",
    "button[aria-label*='akzeptieren' i]",
    "[data-testid*='cookie-accept']",
    "[data-testid*='consent-accept']",
    "#onetrust-accept-btn-handler",
]

# Selectors for back navigation to theme overview
BACK_NAVIGATION_SELECTORS = [
    "a:has-text('Reisethema')",
    "a.checkinpath_step_title:has-text('Reisethema')",
    "a:has-text('Travel Themes')",
    "a:has-text('Übersicht')",
    "a:has-text('zurück')",
    "a:has-text('Back')",
    "button:has-text('zurück')",
    "button:has-text('Back')",
    "[aria-label*='zurück']",
    "[aria-label*='back']",
    "nav a[href*='travel-theme']",
    ".breadcrumb a:last-of-type",
    # Breadcrumb step 1: "Reisethema auswählen"
    ".checkinpath_step.path_retrieve a",
]


class BlockedError(Exception):
    """Raised when bot protection or CAPTCHA is detected."""


class SafetyViolation(Exception):
    """Raised when a safety check prevents an action."""


class ScraperResult:
    def __init__(self) -> None:
        self.themes: list[ThemeData] = []
        self.failed_themes: list[dict] = []
        self.blocked: bool = False
        self.captcha_detected: bool = False
        self.abort_reason: Optional[str] = None
        self.screenshots_saved: list[str] = []
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None


async def run_scraper(config: Config, network_monitor: NetworkMonitor) -> ScraperResult:
    """
    Main scraping orchestrator.

    Returns ScraperResult with all extracted data and run metadata.
    Raises nothing – all errors are caught and recorded in the result.
    """
    from .browser import create_browser_context, get_browser_version, get_playwright_version

    result = ScraperResult()
    screenshots_dir = config.output_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    async with create_browser_context(headless=config.headless) as (pw, browser, context, page):
        # Attach passive network monitor
        network_monitor.attach(page)

        try:
            # Step 1: Open page
            logger.info("Opening %s", BASE_URL)
            await page.goto(BASE_URL, timeout=30_000)

            # Wait for the SPA to fully render – airport chips are a reliable indicator
            logger.info("Waiting for page to render airport selection...")
            try:
                await page.wait_for_selector(
                    ".chip-span.origins, span[role='button']",
                    state="visible",
                    timeout=15_000
                )
                logger.info("Page rendered – airport chips visible")
            except PWTimeoutError:
                logger.warning("Airport chips not found within 15s – page may not have fully loaded")

            # Check for bot-protection / CAPTCHA
            if await _is_blocked(page):
                result.blocked = True
                result.abort_reason = "Bot protection or CAPTCHA detected on initial load"
                await _save_error_screenshot(page, screenshots_dir, "blocked_initial")
                return result

            # Step 2: Cookie banner (after page is rendered)
            await _handle_cookie_banner(page)
            # Brief pause for cookie dismissal animation
            await asyncio.sleep(1.0)

            # Step 3: Set departure airport
            await _set_departure_airport(page, config.origin)

            # Note: Dates and passengers are set on the NEXT page (Reise zusammenstellen)

            # Step 6: List themes
            theme_elements = await _get_theme_elements(page)
            if not theme_elements:
                result.abort_reason = "No theme cards found on overview page"
                await _save_error_screenshot(page, screenshots_dir, "no_themes_found")
                return result

            theme_count = len(theme_elements)
            logger.info("Found %d theme(s) on overview page", theme_count)

            # Limit to 1 in smoke-test mode
            themes_to_process = 1 if config.smoke_test_only else theme_count
            logger.info(
                "Processing %d theme(s) (%s)",
                themes_to_process,
                "smoke-test mode" if config.smoke_test_only else "full mode",
            )

            # Step 7: Process themes
            for i in range(themes_to_process):
                if await _is_blocked(page):
                    result.blocked = True
                    result.abort_reason = f"Blocked after processing {i} theme(s)"
                    await _save_error_screenshot(page, screenshots_dir, f"blocked_theme_{i}")
                    break

                theme_name_hint = f"theme_{i}"
                try:
                    # Re-fetch theme elements after each navigation
                    theme_elements = await _get_theme_elements(page)
                    if i >= len(theme_elements):
                        logger.warning("Theme index %d no longer exists on page", i)
                        break

                    el = theme_elements[i]

                    # Get theme name hint for logging
                    try:
                        el_text = await el.inner_text(timeout=3000)
                        theme_name_hint = el_text.strip()[:50]
                    except Exception:
                        pass

                    logger.info("Processing theme %d: %s", i, theme_name_hint)

                    # Safety check before clicking
                    el_text_full = theme_name_hint
                    safe, reason = is_safe_to_click(
                        action_context="theme_card",
                        visible_text=el_text_full,
                        aria_label=await el.get_attribute("aria-label") or "",
                        title=await el.get_attribute("title") or "",
                        href=await el.get_attribute("href") or "",
                    )
                    if not safe:
                        raise SafetyViolation(f"Theme card blocked by safety guard: {reason}")

                    # Step 1: Select theme via radio check
                    try:
                        radio = el.locator("input[type='radio']")
                        if await radio.count() > 0:
                            await radio.check(force=True, timeout=5000)
                            logger.info("Checked theme radio: %s", theme_name_hint)
                        else:
                            # Fallback to click if no radio
                            await el.click(timeout=10_000)
                            logger.info("Clicked theme card: %s", theme_name_hint)
                    except Exception as exc:
                        logger.warning("Theme selection failed: %s", exc)
                        continue

                    # Step 2: Wait briefly for poolDesc to populate
                    await asyncio.sleep(1.5)

                    # Step 3: Extract pool destinations from current page state
                    pool_desc = ""
                    try:
                        pool_desc_el = el.locator(".poolDesc")
                        if await pool_desc_el.count() > 0:
                            pool_desc = await pool_desc_el.inner_text(timeout=3000)
                            logger.debug("Pool description: %s", pool_desc[:100])
                    except Exception:
                        pass

                    # Also read the "Weiter" button to confirm it's enabled now
                    weiter_ready = False
                    try:
                        weiter = page.locator("#whereToMain, button.bttn_forw, button:has-text('Weiter')").first
                        if await weiter.count() > 0:
                            # Use evaluate to check if it's disabled, as is_disabled() can be flaky with some frameworks
                            is_disabled = await weiter.evaluate("el => el.disabled")
                            weiter_ready = not is_disabled
                            logger.debug("Weiter button ready: %s", weiter_ready)
                    except Exception:
                        pass

                    # Step 4: Click "Weiter" to go to the trip-building page (prices & dates)
                    # The safety guard prevents advancing to payment - this is just the
                    # "Reise zusammenstellen" page (step 2 of 6), not booking.
                    if weiter_ready:
                        try:
                            weiter_el = page.locator("#whereToMain").first
                            if await weiter_el.count() == 0:
                                weiter_el = page.locator("button.js-submit.bttn_forw").first
                            weiter_text = await weiter_el.inner_text(timeout=2000) if await weiter_el.count() > 0 else "Weiter"
                            safe3, reason3 = is_safe_to_click(
                                action_context="theme_card",
                                visible_text=weiter_text,
                            )
                            if not safe3:
                                logger.warning("Weiter button blocked by safety guard: %s", reason3)
                                weiter_ready = False
                            else:
                                # Use evaluate to bypass visibility/scroll issues
                                await weiter_el.evaluate("el => el.click()")
                                logger.info("Clicked 'Weiter' to proceed to trip builder (via JS)")
                                # Wait for trip builder page (step 2 - Destinations)
                                await _wait_for_theme_page(page)

                                # Step 4b: On the destinations page, we need to click "Reisedaten eingeben" to get to the dates
                                try:
                                    logger.info("Looking for 'Reisedaten eingeben' button...")
                                    next_btn = page.locator("#whereToMain, button:has-text('Reisedaten eingeben'), button.js-submit.bttn_forw").first
                                    await next_btn.wait_for(state="visible", timeout=5000)
                                    await next_btn.evaluate("el => el.click()")
                                    logger.info("Clicked 'Reisedaten eingeben' to proceed to dates page (via JS)")
                                    
                                    # Wait for dates page to appear
                                    await page.wait_for_selector("#earliestOut", state="visible", timeout=10_000)
                                except Exception as e:
                                    logger.warning("Could not find/click 'Reisedaten eingeben': %s", e)

                                # Step 4c: Set dates and passengers on the dates page
                                await _set_dates(page, config)
                                await _set_passengers(page, config.adults)
                                
                                # Step 4d: Click "Weiter" on the Dates page to get the Prices
                                try:
                                    logger.info("Looking for 'Weiter' button on Dates page...")
                                    final_weiter = page.locator("#whereToMain").first
                                    
                                    # Wait for the availability response to get the price
                                    async with page.expect_response(lambda r: "availability" in r.url and r.status == 200, timeout=15000) as response_info:
                                        await final_weiter.evaluate("el => el.click()")
                                        logger.info("Clicked 'Weiter' to load Prices (via JS)")
                                        
                                    logger.info("Availability response received!")
                                    
                                    # Wait a tiny bit more for DOM to update with the price
                                    await page.wait_for_timeout(1000)
                                except Exception as e:
                                    logger.warning("Could not click final Weiter for prices or wait for response: %s", e)
                        except Exception as exc:
                            logger.warning("Could not click Weiter: %s", exc)
                            weiter_ready = False
                    else:
                        logger.warning("Weiter button not ready after theme selection")

                    # Step 5: Extract data from current page
                    theme_data = await extract_theme_data(
                        page, theme_index=i, pool_id=f"pool_{i}", pool_desc=pool_desc,
                    )

                    # Step 6: Screenshot and HTML snapshot
                    ts = int(time.time())
                    screenshot_name = f"theme_{i:02d}_{_slugify(theme_data.theme_name)}_{ts}.png"
                    screenshot_path = screenshots_dir / screenshot_name
                    await page.screenshot(path=str(screenshot_path), full_page=True, timeout=10_000)
                    theme_data.screenshot_path = str(screenshot_path)
                    result.screenshots_saved.append(str(screenshot_path))
                    logger.info("Screenshot saved: %s", screenshot_path)
                    
                    # Save HTML snapshot for debugging
                    html_name = f"theme_{i:02d}_{_slugify(theme_data.theme_name)}_{ts}.html"
                    html_path = screenshots_dir / html_name
                    html_content = await page.content()
                    html_path.write_text(html_content, encoding="utf-8")
                    logger.info("DOM snapshot saved: %s", html_path)

                    result.themes.append(theme_data)

                    # Navigate back to overview
                    await _navigate_back_to_overview(page, config, screenshots_dir)

                    # Verify we are back at overview
                    if not await _verify_overview(page):
                        logger.warning("Could not verify return to overview after theme %d", i)
                        # Try direct navigation
                        await page.goto(BASE_URL, timeout=30_000)
                        await _wait_for_overview(page)

                    # Polite wait between themes
                    wait_s = random.uniform(1.0, 3.0)
                    logger.info("Waiting %.1f s before next theme", wait_s)
                    await asyncio.sleep(wait_s)

                except SafetyViolation as exc:
                    logger.error("Safety violation for theme %d: %s", i, exc)
                    result.failed_themes.append({
                        "index": i,
                        "name": theme_name_hint,
                        "error": str(exc),
                        "error_type": "SafetyViolation",
                    })
                    await _save_error_screenshot(page, screenshots_dir, f"safety_violation_theme_{i}")

                except PWTimeoutError as exc:
                    logger.error("Timeout on theme %d: %s", i, exc)
                    result.failed_themes.append({
                        "index": i,
                        "name": theme_name_hint,
                        "error": str(exc),
                        "error_type": "Timeout",
                    })
                    await _save_error_screenshot(page, screenshots_dir, f"timeout_theme_{i}")
                    # Try to recover by going back to overview
                    try:
                        await page.goto(BASE_URL, timeout=30_000)
                        await _wait_for_overview(page)
                    except Exception:
                        pass

                except Exception as exc:
                    logger.error("Error processing theme %d: %s", i, exc)
                    result.failed_themes.append({
                        "index": i,
                        "name": theme_name_hint,
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                    })
                    await _save_error_screenshot(page, screenshots_dir, f"error_theme_{i}")
                    try:
                        await page.goto(BASE_URL, timeout=30_000)
                        await _wait_for_overview(page)
                    except Exception:
                        pass

            # Step 8: Final overview screenshot
            try:
                ts = int(time.time())
                final_screenshot = screenshots_dir / f"final_overview_{ts}.png"
                await page.screenshot(path=str(final_screenshot), full_page=True, timeout=10_000)
                result.screenshots_saved.append(str(final_screenshot))
                logger.info("Final overview screenshot saved: %s", final_screenshot)
            except Exception as exc:
                logger.warning("Could not save final screenshot: %s", exc)

        except BlockedError as exc:
            result.blocked = True
            result.abort_reason = str(exc)
            logger.error("Aborted: %s", exc)
        except Exception as exc:
            result.abort_reason = f"Unexpected error: {exc}"
            logger.exception("Unexpected scraper error")
        finally:
            network_monitor.detach(page)
            result.end_time = time.time()

    return result


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

async def _is_blocked(page: Page) -> bool:
    """Detect common bot-protection indicators."""
    try:
        title = await page.title()
        text = await page.evaluate("document.body?.innerText || ''")
        blocked_signals = [
            "captcha",
            "robot",
            "access denied",
            "403 forbidden",
            "cloudflare",
            "challenge",
            "blocked",
        ]
        combined = (title + " " + text).lower()
        return any(sig in combined for sig in blocked_signals)
    except Exception:
        return False


async def _handle_cookie_banner(page: Page) -> None:
    """Handle cookie consent banner if present. Non-fatal if not found."""
    for sel in COOKIE_ACCEPT_SELECTORS:
        try:
            btn = page.locator(sel).first
            if await btn.count() > 0 and await btn.is_visible(timeout=3000):
                safe, reason = is_safe_to_click(
                    action_context="cookie_accept",
                    visible_text=await btn.inner_text(timeout=2000),
                    aria_label=await btn.get_attribute("aria-label") or "",
                )
                if safe:
                    await btn.click(timeout=5000)
                    logger.info("Cookie banner accepted via: %s", sel)
                    await asyncio.sleep(0.5)
                    return
        except Exception:
            continue
    logger.info("No cookie banner found or could not interact")


async def _set_departure_airport(page: Page, origin: str) -> None:
    """
    Select departure airport from chip buttons.

    The page shows chip-spans with role='button' for Frankfurt/Main and München.
    After clicking, the theme section should appear on the page.
    """
    # Map IATA codes to display texts used on the page
    origin_to_display = {
        "FRA": ["Frankfurt/Main", "Frankfurt"],
        "MUC": ["München", "Munich", "Muenchen"],
    }
    display_names = origin_to_display.get(origin.upper(), [origin])

    # Try chip-span buttons (actual DOM structure)
    for display_name in display_names:
        try:
            sel = f"span[role='button']:has-text('{display_name}')"
            btn = page.locator(sel).first
            if await btn.count() > 0 and await btn.is_visible(timeout=3000):
                safe, reason = is_safe_to_click(
                    action_context="airport_select",
                    visible_text=await btn.inner_text(timeout=2000),
                )
                if safe:
                    await btn.click(timeout=5000)
                    logger.info("Clicked airport chip: %s", display_name)
                    # Wait for theme section to appear after selection
                    await _wait_for_theme_section(page)
                    return
        except Exception as exc:
            logger.debug("Airport chip %s failed: %s", display_name, exc)

    # Fallback: try broader .chip-span.origins
    try:
        origins = await page.locator(".chip-span.origins").all()
        for origin_el in origins:
            text = await origin_el.inner_text(timeout=2000)
            if any(dn.lower() in text.lower() for dn in display_names):
                safe, _ = is_safe_to_click(
                    action_context="airport_select",
                    visible_text=text,
                )
                if safe:
                    await origin_el.click(timeout=5000)
                    logger.info("Clicked airport via .origins chip: %s", text)
                    await _wait_for_theme_section(page)
                    return
    except Exception as exc:
        logger.debug("Origins fallback failed: %s", exc)

    logger.warning("Could not set departure airport – proceeding with default")


async def _wait_for_theme_section(page: Page) -> None:
    """Wait for the theme selection section to appear after airport is chosen."""
    for sel in THEME_SECTION_INDICATORS:
        try:
            await page.wait_for_selector(sel, state="visible", timeout=10_000)
            logger.info("Theme section appeared via: %s", sel)
            return
        except Exception:
            continue
    logger.warning("Theme section did not appear after airport selection")



async def _set_dates(page: Page, config: Config) -> None:
    """Set outbound and return dates."""
    # Convert YYYY-MM-DD to DD.MM.YYYY
    dep_parts = config.departure_iso.split("-")
    dep_de = f"{dep_parts[2]}.{dep_parts[1]}.{dep_parts[0]}" if len(dep_parts) == 3 else config.departure_iso
    
    ret_parts = config.return_iso.split("-")
    ret_de = f"{ret_parts[2]}.{ret_parts[1]}.{ret_parts[0]}" if len(ret_parts) == 3 else config.return_iso

    try:
        # Evaluate to set readonly inputs and dispatch events
        await page.evaluate(f"""() => {{
            let dep = document.getElementById('earliestOut');
            if (dep) {{
                dep.value = '{dep_de}';
                dep.dispatchEvent(new Event('change', {{bubbles: true}}));
                dep.dispatchEvent(new Event('input', {{bubbles: true}}));
            }}
            let ret = document.getElementById('latestRet');
            if (ret) {{
                ret.value = '{ret_de}';
                ret.dispatchEvent(new Event('change', {{bubbles: true}}));
                ret.dispatchEvent(new Event('input', {{bubbles: true}}));
            }}
        }}""")
        logger.info("Dates set via JS evaluate (#earliestOut, #latestRet)")
    except Exception as exc:
        logger.debug("Failed to set dates via JS evaluate: %s", exc)


async def _set_passengers(page: Page, adults: int) -> None:
    """Set number of adult passengers."""
    # Look for stepper/counter
    stepper_selectors = [
        "input[aria-label*='Erwachsene' i]",
        "input[aria-label*='Adults' i]",
        "[data-testid*='adults'] input",
        "[data-testid*='passengers'] input",
    ]
    for sel in stepper_selectors:
        try:
            el = page.locator(sel).first
            if await el.count() > 0:
                current = await el.input_value(timeout=3000)
                target = str(adults)
                if current != target:
                    await el.fill(target, timeout=5000)
                logger.info("Adults set to %d", adults)
                return
        except Exception:
            continue

    # Try +/- stepper buttons
    plus_selectors = [
        "button[aria-label*='Erwachsene erhöhen' i]",
        "button[aria-label*='Add adult' i]",
        "[data-testid*='adults-increment']",
        "[data-testid*='adults-plus']",
    ]
    current_count = 1  # Assume default is 1
    if adults > current_count:
        for _ in range(adults - current_count):
            for sel in plus_selectors:
                try:
                    btn = page.locator(sel).first
                    if await btn.count() > 0:
                        safe, reason = is_safe_to_click(
                            action_context="passenger_stepper",
                            aria_label=await btn.get_attribute("aria-label") or "",
                        )
                        if safe:
                            await btn.click(timeout=5000)
                            await asyncio.sleep(0.3)
                            logger.info("Clicked adult + button")
                            break
                except Exception:
                    continue

    if adults == 1:
        logger.info("Adults=1 is default, no action needed")


async def _get_theme_elements(page: Page) -> list[Any]:
    """Return list of theme card locators from the overview page."""
    for sel in THEME_CARD_SELECTORS:
        try:
            elements = await page.locator(sel).all()
            if elements:
                logger.info("Found %d theme elements via selector: %s", len(elements), sel)
                return elements
        except Exception as exc:
            logger.debug("Theme selector %s failed: %s", sel, exc)

    # Fallback: look for clickable cards with theme-like text
    logger.warning("No theme cards found with structured selectors")
    return []


async def _wait_for_theme_page(page: Page) -> None:
    """
    Wait for a theme detail page to load.
    Waits for a heading (h1 or h2) to be visible, not networkidle.
    """
    try:
        await page.wait_for_selector("h1, h2", state="visible", timeout=15_000)
        # Also wait for any loading spinner to disappear
        await _wait_for_no_spinner(page, timeout_ms=10_000)
    except PWTimeoutError:
        logger.warning("Timeout waiting for theme page heading")


async def _wait_for_overview(page: Page) -> None:
    """Wait for theme overview page to be ready."""
    for sel in OVERVIEW_INDICATORS:
        try:
            await page.wait_for_selector(sel, state="visible", timeout=15_000)
            logger.info("Overview confirmed via: %s", sel)
            return
        except Exception:
            continue

    # Fallback: wait for any heading
    try:
        await page.wait_for_selector("h1, h2", state="visible", timeout=15_000)
    except Exception:
        logger.warning("Could not confirm overview state")


async def _wait_for_no_spinner(page: Page, timeout_ms: int = 5000) -> None:
    """Wait until any visible loading spinner disappears."""
    spinner_selectors = [
        "[aria-label*='Laden' i]",
        "[aria-label*='Loading' i]",
        "[role='progressbar']",
        ".loading",
        ".spinner",
        "[data-testid*='loading']",
        "[data-testid*='spinner']",
    ]
    for sel in spinner_selectors:
        try:
            spinner = page.locator(sel).first
            if await spinner.count() > 0 and await spinner.is_visible(timeout=500):
                await spinner.wait_for(state="hidden", timeout=timeout_ms)
                logger.debug("Spinner disappeared: %s", sel)
        except Exception:
            pass


async def _navigate_back_to_overview(page: Page, config: Config, screenshots_dir: Path) -> None:
    """Navigate back to the main theme overview."""
    logger.info("Forcing hard reload via about:blank to reset SPA state")
    try:
        await page.goto("about:blank")
        await page.goto(BASE_URL, timeout=30_000, wait_until="domcontentloaded")
        
        # Wait for airport chips and set departure airport again
        await page.wait_for_selector(".chip-span.origins, span[role='button']", state="visible", timeout=15_000)
        await _set_departure_airport(page, config.origin)
        await _wait_for_overview(page)
    except Exception as exc:
        logger.warning("Direct navigation back failed: %s", exc)


async def _verify_overview(page: Page) -> bool:
    """Verify that the current page is the theme overview."""
    for sel in OVERVIEW_INDICATORS:
        try:
            if await page.locator(sel).count() > 0:
                return True
        except Exception:
            continue

    # Check URL
    current_url = page.url
    if "travel-theme" in current_url:
        return True

    return False


async def _save_error_screenshot(page: Page, screenshots_dir: Path, name: str) -> None:
    """Save error screenshot and DOM snapshot."""
    try:
        ts = int(time.time())
        screenshot_path = screenshots_dir / f"error_{name}_{ts}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True, timeout=10_000)
        logger.info("Error screenshot saved: %s", screenshot_path)

        # DOM snapshot
        dom_path = screenshots_dir / f"error_{name}_{ts}.html"
        content = await page.content()
        dom_path.write_text(content, encoding="utf-8")
        logger.info("DOM snapshot saved: %s", dom_path)
    except Exception as exc:
        logger.debug("Could not save error artifacts: %s", exc)


def _slugify(text: str) -> str:
    """Create a filesystem-safe slug from text."""
    import re
    text = text.lower().strip()
    text = re.sub(r"[äÄ]", "ae", text)
    text = re.sub(r"[öÖ]", "oe", text)
    text = re.sub(r"[üÜ]", "ue", text)
    text = re.sub(r"[ß]", "ss", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text[:40]
