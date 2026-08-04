"""Data extraction from DOM elements.

Strict separation of destination types:
- theme_name: name of the travel theme
- destination_pool: shown pool/region label
- excludable_destinations: cities user can explicitly exclude
- mentioned_cities: city names found in text (UNCONFIRMED, not bookable)
- confirmed_available: only True if explicit availability signal found
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .utils import extract_all_prices, extract_city_names_from_text, normalize_whitespace, parse_price

logger = logging.getLogger(__name__)


@dataclass
class ThemeData:
    """Extracted data for a single travel theme."""

    # Identity
    theme_name: str = ""
    theme_index: int = 0

    # Description
    description: str = ""

    # Destination fields – strictly separated
    destination_pool: list[str] = field(default_factory=list)
    """Labeled destination pool or region shown on page (not confirmed bookable)."""

    excludable_destinations: list[str] = field(default_factory=list)
    """Cities explicitly listed as excludable by user."""

    mentioned_cities: list[str] = field(default_factory=list)
    """City names found in free text – UNCONFIRMED, may not be bookable."""

    confirmed_available: Optional[bool] = None
    """True only if an explicit availability indicator was found. None = unknown."""

    # Pricing
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_raw: str = ""
    price_per_person: Optional[bool] = None
    """True if price is explicitly stated as per person. None = unknown."""

    # Flight information
    cabin_classes: list[str] = field(default_factory=list)
    flight_times: list[str] = field(default_factory=list)
    """Departure/arrival times if shown."""

    direct_flights_only: Optional[bool] = None
    """True if page explicitly states direct/non-stop. None = unknown."""

    # Metadata
    url: str = ""
    screenshot_path: str = ""
    extraction_warnings: list[str] = field(default_factory=list)
    raw_page_text: str = ""

    # Pride marking (set by exporter, not extractor)
    pride_cities_found: list[str] = field(default_factory=list)

    def add_warning(self, msg: str) -> None:
        logger.warning("[%s] %s", self.theme_name or f"theme_{self.theme_index}", msg)
        self.extraction_warnings.append(msg)

    def to_dict(self) -> dict:
        return {
            "theme_index": self.theme_index,
            "theme_name": self.theme_name,
            "description": self.description,
            "destination_pool": self.destination_pool,
            "excludable_destinations": self.excludable_destinations,
            "mentioned_cities": self.mentioned_cities,
            "confirmed_available": self.confirmed_available,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "price_raw": self.price_raw,
            "price_per_person": self.price_per_person,
            "cabin_classes": self.cabin_classes,
            "flight_times": self.flight_times,
            "direct_flights_only": self.direct_flights_only,
            "url": self.url,
            "screenshot_path": self.screenshot_path,
            "pride_cities_found": self.pride_cities_found,
            "extraction_warnings": self.extraction_warnings,
        }


async def extract_theme_data(
    page: Any,
    theme_index: int,
    pool_id: str = "",
    pool_desc: str = "",
) -> ThemeData:
    """
    Extract all publicly visible data from the currently open theme page.
    Uses stable selectors: roles, aria-labels, visible text, data-attributes.

    Args:
        page: Playwright Page object
        theme_index: 0-based index of the theme
        pool_id: Pool ID from radio input (e.g. 'FRA_SUN'), if known from overview
        pool_desc: Pool description text from .poolDesc, if already extracted
    """
    data = ThemeData(theme_index=theme_index)
    data.url = page.url

    try:
        data.raw_page_text = await page.evaluate("document.body.innerText")
        data.raw_page_text = normalize_whitespace(data.raw_page_text)
    except Exception as exc:
        data.add_warning(f"Could not read page text: {exc}")

    # --- Theme name ---
    data.theme_name = await _extract_theme_name(page, data)

    # --- Description (pool_desc from overview page, or extract from current) ---
    if pool_desc:
        data.description = normalize_whitespace(pool_desc)
    else:
        data.description = await _extract_description(page, data)

    # --- Destination pool ---
    data.destination_pool = await _extract_destination_pool(page, data)

    # --- Excludable destinations ---
    data.excludable_destinations = await _extract_excludable_destinations(page, data)

    # --- Pricing ---
    await _extract_pricing(page, data)

    # --- Availability ---
    await _extract_availability(page, data)

    # --- Cabin classes ---
    data.cabin_classes = await _extract_cabin_classes(page, data)

    # --- Flight times ---
    data.flight_times = await _extract_flight_times(page, data)

    # --- Direct/nonstop ---
    await _extract_direct_info(page, data)

    # --- Mentioned cities (heuristic, unconfirmed) ---
    if data.raw_page_text:
        candidates = extract_city_names_from_text(data.raw_page_text)
        # Exclude names already in structured fields
        known = set(data.destination_pool + data.excludable_destinations)
        data.mentioned_cities = [c for c in candidates if c not in known]
        if data.mentioned_cities:
            data.add_warning(
                f"Unconfirmed city mentions in text (not bookable): {data.mentioned_cities}"
            )

    return data


async def _try_text(page: Any, selectors: list[str]) -> str:
    """Try a list of selectors, return first non-empty text found."""
    for sel in selectors:
        try:
            el = page.locator(sel).first
            if await el.count() > 0:
                text = await el.inner_text(timeout=3000)
                text = normalize_whitespace(text)
                if text:
                    return text
        except Exception:
            continue
    return ""


async def _extract_theme_name(page: Any, data: ThemeData) -> str:
    # Real DOM: label.poolName on overview, h1 or heading on detail page
    name = await _try_text(page, [
        "label.poolName",
        ".pool.active label.poolName",
        "h1",
        "[data-testid*='theme-name']",
        "[data-testid*='themeName']",
        "h2.theme-title",
        ".theme-header h1",
        ".theme-header h2",
    ])
    if not name:
        data.add_warning("Theme name not found in DOM")
    return name


async def _extract_description(page: Any, data: ThemeData) -> str:
    return await _try_text(page, [
        "[data-testid*='description']",
        "[data-testid*='theme-description']",
        "h1 + p",
        "h2 + p",
        ".theme-description",
        ".theme-body p",
        "main p:first-of-type",
    ])


async def _extract_destination_pool(page: Any, data: ThemeData) -> list[str]:
    """Extract destination pool labels shown before booking."""
    pool: list[str] = []

    # Try structured list items under pool heading
    pool_selectors = [
        "[data-testid*='destination-pool'] li",
        "[data-testid*='destinations'] li",
        "[aria-label*='Ziele'] li",
        "[aria-label*='destinations'] li",
        ".destination-pool li",
        ".possible-destinations li",
        "[class*='destination'] li",
        "[class*='Destination'] li",
    ]
    for sel in pool_selectors:
        try:
            items = await page.locator(sel).all_inner_texts()
            cleaned = [normalize_whitespace(t) for t in items if t.strip()]
            if cleaned:
                pool.extend(cleaned)
                break
        except Exception:
            continue

    # Also look for heading + sibling list pattern
    if not pool:
        try:
            headings = await page.locator("h3, h4, strong, b").all()
            for heading in headings:
                text = await heading.inner_text(timeout=2000)
                if any(kw in text.lower() for kw in ["ziel", "destination", "mögliche"]):
                    # Get following sibling list
                    parent = await heading.evaluate_handle("el => el.parentElement")
                    sibling_items = await parent.query_selector_all("li")
                    for li in sibling_items:
                        t = await li.inner_text()
                        if t.strip():
                            pool.append(normalize_whitespace(t))
                    if pool:
                        break
        except Exception as exc:
            logger.debug("Destination pool heuristic failed: %s", exc)

    return list(dict.fromkeys(pool))  # deduplicate preserving order


async def _extract_excludable_destinations(page: Any, data: ThemeData) -> list[str]:
    """Extract cities that can be explicitly excluded."""
    exclude: list[str] = []

    selectors = [
        "[data-testid*='exclude'] li",
        "[data-testid*='exclusion'] li",
        "[aria-label*='ausschließen'] li",
        "[aria-label*='exclude'] li",
        ".exclude-destinations li",
        ".exclusion-list li",
    ]
    for sel in selectors:
        try:
            items = await page.locator(sel).all_inner_texts()
            cleaned = [normalize_whitespace(t) for t in items if t.strip()]
            if cleaned:
                exclude.extend(cleaned)
                break
        except Exception:
            continue

    # Heuristic: look for "ausschließen" / "exclude" keyword near checkboxes
    if not exclude:
        try:
            checkboxes = await page.locator("input[type='checkbox']").all()
            for cb in checkboxes:
                label_text = ""
                # Try aria-label
                label_text = await cb.get_attribute("aria-label") or ""
                if not label_text:
                    # Try associated label element
                    cb_id = await cb.get_attribute("id") or ""
                    if cb_id:
                        label_el = page.locator(f"label[for='{cb_id}']")
                        if await label_el.count() > 0:
                            label_text = await label_el.inner_text(timeout=2000)
                if label_text and normalize_whitespace(label_text):
                    exclude.append(normalize_whitespace(label_text))
        except Exception as exc:
            logger.debug("Excludable destinations heuristic failed: %s", exc)

    return list(dict.fromkeys(exclude))


async def _extract_pricing(page: Any, data: ThemeData) -> None:
    """Extract price information."""
    price_text = await _try_text(page, [
        "#totalPrice",
        ".total-value",
        "#bestAlternativePrice",
        ".total-price-container",
        ".offer-price",
        ".flight-price",
        "[data-testid*='price']",
        "[data-testid*='Price']",
    ])

    if price_text:
        data.price_raw = price_text
        
        # If price_text is just a bare number (e.g., from #totalPrice), append Euro sign for the regex parser
        parse_text = price_text
        if "€" not in parse_text and re.match(r'^\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{1,2})?\s*$', parse_text):
            parse_text += " €"
            
        prices = extract_all_prices(parse_text)
        if prices:
            data.price_min = min(prices)
            data.price_max = max(prices) if len(prices) > 1 else None
        else:
            data.add_warning(f"Price text found but could not parse: {price_text!r}")

        # Per-person detection
        per_person_kw = ["pro person", "per person", "p.p.", "pp"]
        if any(kw in price_text.lower() for kw in per_person_kw):
            data.price_per_person = True
        elif "gesamt" in price_text.lower() or "total" in price_text.lower():
            data.price_per_person = False
    else:
        # Scan full page text for price patterns as fallback
        if data.raw_page_text:
            prices = extract_all_prices(data.raw_page_text)
            if prices:
                data.price_min = min(prices)
                data.price_max = max(prices) if len(prices) > 1 else None
                data.add_warning("Price extracted from full page text (less reliable)")
            else:
                data.add_warning("No price found on page")


async def _extract_availability(page: Any, data: ThemeData) -> None:
    """Check for explicit availability indicators."""
    # Look for disabled state or sold-out indicators
    try:
        sold_out_selectors = [
            "[data-testid*='sold-out']",
            "[data-testid*='unavailable']",
            "[aria-label*='nicht verfügbar']",
            "[aria-label*='ausgebucht']",
            ".sold-out",
            ".unavailable",
        ]
        for sel in sold_out_selectors:
            if await page.locator(sel).count() > 0:
                data.confirmed_available = False
                return

        # Look for explicit available signal
        available_selectors = [
            "[data-testid*='available']",
            "[aria-label*='verfügbar']",
            ".available",
        ]
        for sel in available_selectors:
            if await page.locator(sel).count() > 0:
                data.confirmed_available = True
                return

        # Price present often implies bookable but we don't assume
        # confirmed_available remains None (unknown)

    except Exception as exc:
        logger.debug("Availability check failed: %s", exc)


async def _extract_cabin_classes(page: Any, data: ThemeData) -> list[str]:
    """Detect offered cabin classes."""
    classes: list[str] = []
    text_lower = (data.raw_page_text or "").lower()
    if "economy" in text_lower:
        classes.append("Economy")
    if "business" in text_lower:
        classes.append("Business")
    if "first" in text_lower and "first class" in text_lower:
        classes.append("First")
    return classes


async def _extract_flight_times(page: Any, data: ThemeData) -> list[str]:
    """Extract any displayed flight times (HH:MM format)."""
    times: list[str] = []
    time_pattern = re.compile(r"\b([01]?\d|2[0-3]):[0-5]\d\b")

    # Try structured elements first
    time_selectors = [
        "[data-testid*='time']",
        "[data-testid*='departure-time']",
        "[data-testid*='arrival-time']",
        ".flight-time",
        "time",
        "[aria-label*='Uhr']",
    ]
    for sel in time_selectors:
        try:
            items = await page.locator(sel).all_inner_texts()
            for t in items:
                for match in time_pattern.finditer(t):
                    times.append(match.group())
        except Exception:
            continue

    # Fallback: extract from full page text
    if not times and data.raw_page_text:
        for match in time_pattern.finditer(data.raw_page_text):
            times.append(match.group())

    return list(dict.fromkeys(times))[:20]  # deduplicate, cap at 20


async def _extract_direct_info(page: Any, data: ThemeData) -> None:
    """Detect if only direct/nonstop flights are offered."""
    text_lower = (data.raw_page_text or "").lower()
    nonstop_kw = ["nonstop", "non-stop", "direkt", "direct", "ohne umstieg", "without stopover"]
    connection_kw = ["umstieg", "stopover", "connecting", "zwischenstopp"]
    if any(kw in text_lower for kw in nonstop_kw):
        data.direct_flights_only = True
    elif any(kw in text_lower for kw in connection_kw):
        data.direct_flights_only = False
