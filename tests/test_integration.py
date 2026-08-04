"""Integration test – requires a real browser.

Run explicitly:
    pytest tests/test_integration.py -m integration -v

This test is excluded from the default pytest run via pyproject.toml:
    addopts = "-m 'not integration'"

The test only runs a smoke test (single theme) and makes NO booking.
"""

from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path

import pytest

from src.config import Config
from src.network_monitor import NetworkMonitor
from src.scraper import run_scraper


@pytest.mark.integration
@pytest.mark.asyncio
async def test_smoke_run_single_theme(tmp_path):
    """
    Real browser smoke test: opens Lufthansa Surprise, processes ONE theme,
    verifies basic output. No booking is made.
    """
    config = Config(
        origin="FRA",
        departure=date(2026, 8, 7),
        return_date=date(2026, 8, 9),
        adults=1,
        headless=True,  # Headless for CI; use --headed flag for manual testing
        smoke_test_only=True,
        output_dir=tmp_path,
    )

    monitor = NetworkMonitor(config.output_dir)
    result = await run_scraper(config, monitor)

    # Basic assertions – the test is valid even if the site blocks us
    # or returns no themes (we verify the tool handles it gracefully)
    assert result is not None
    assert isinstance(result.themes, list)
    assert isinstance(result.failed_themes, list)
    assert result.end_time is not None

    if result.blocked:
        pytest.skip(f"Site blocked access: {result.abort_reason}")

    if result.abort_reason and "No theme cards found" in result.abort_reason:
        pytest.skip(f"No themes found – page structure may have changed: {result.abort_reason}")

    # If we got themes, validate their structure
    for theme in result.themes:
        assert hasattr(theme, "theme_name")
        assert hasattr(theme, "destination_pool")
        assert hasattr(theme, "confirmed_available")
        assert hasattr(theme, "price_min")
        # Verify destination type separation
        assert isinstance(theme.destination_pool, list)
        assert isinstance(theme.excludable_destinations, list)
        assert isinstance(theme.mentioned_cities, list)
        # confirmed_available must be True, False, or None – never inferred from city mention
        assert theme.confirmed_available in (True, False, None)

    # Max 1 theme processed in smoke mode
    assert len(result.themes) + len(result.failed_themes) <= 1

    # At least one screenshot should exist if a theme was processed
    if result.themes:
        assert len(result.screenshots_saved) >= 1
        for path in result.screenshots_saved:
            assert Path(path).exists(), f"Screenshot missing: {path}"
