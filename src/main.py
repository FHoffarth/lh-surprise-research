"""CLI entry point for lh-surprise-scraper.

Usage:
    python -m src.main --origin FRA --departure 2026-08-07 \\
        --return-date 2026-08-09 --adults 1 --headed --smoke-test
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from .browser import get_browser_version, get_playwright_version
from .config import load_config
from .exporter import Exporter
from .network_monitor import NetworkMonitor
from .scraper import run_scraper


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        datefmt="%H:%M:%S",
    )


async def _async_main() -> int:
    _setup_logging()
    logger = logging.getLogger(__name__)

    config = load_config()
    logger.info("Config: origin=%s dep=%s ret=%s adults=%d headless=%s smoke=%s",
                config.origin, config.departure_iso, config.return_iso,
                config.adults, config.headless, config.smoke_test_only)

    network_monitor = NetworkMonitor(config.output_dir)

    logger.info("Starting scraper (NO BOOKING WILL BE MADE)")
    result = await run_scraper(config, network_monitor)

    # Collect browser info (approximate – browser already closed)
    playwright_version = "unknown"
    browser_version = "unknown"
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as pw:
            playwright_version = await get_playwright_version(pw)
            b = await pw.chromium.launch(headless=True)
            browser_version = await get_browser_version(b)
            await b.close()
    except Exception:
        pass

    exporter = Exporter(config)
    paths = exporter.export_all(
        themes=result.themes,
        failed_themes=result.failed_themes,
        screenshots_saved=result.screenshots_saved,
        network_response_count=network_monitor.response_count,
        start_time=result.start_time,
        end_time=result.end_time or result.start_time,
        blocked=result.blocked,
        captcha_detected=result.captcha_detected,
        abort_reason=result.abort_reason,
        playwright_version=playwright_version,
        browser_version=browser_version,
        smoke_test_mode=config.smoke_test_only,
    )

    logger.info("=== Run complete ===")
    logger.info("Themes successful: %d", len(result.themes))
    logger.info("Themes failed:     %d", len(result.failed_themes))
    logger.info("Blocked:           %s", result.blocked)
    if result.abort_reason:
        logger.warning("Abort reason: %s", result.abort_reason)
    for name, path in paths.items():
        logger.info("Output [%s]: %s", name, path)

    return 0 if not result.blocked else 1


def main() -> None:
    sys.exit(asyncio.run(_async_main()))


if __name__ == "__main__":
    main()
