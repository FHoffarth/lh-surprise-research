"""Price parsing, date utilities, safety guard, and Pride-city matching."""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Price parsing
# ---------------------------------------------------------------------------

# Matches European (DE) style: optional prefix, digits with optional
# thousand-dot and decimal-comma, then €
_RE_PRICE_DE = re.compile(
    r"""
    (?:ab\s*|von\s*|from\s*)?          # optional prefix
    (\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?) # number with DE formatting
    \s*€                               # currency symbol
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Matches EN style: € then digits with optional thousand-comma and decimal-dot
_RE_PRICE_EN = re.compile(
    r"""
    €\s*
    (\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?) # EN number
    """,
    re.VERBOSE | re.IGNORECASE,
)


def _normalize_de(raw: str) -> float:
    """Convert German number string '1.299,50' → 1299.50."""
    # Remove thousand separator (dot), replace decimal comma with dot
    cleaned = raw.replace(".", "").replace(",", ".")
    return float(cleaned)


def _normalize_en(raw: str) -> float:
    """Convert EN number string '1,299.50' → 1299.50."""
    cleaned = raw.replace(",", "")
    return float(cleaned)


def parse_price(text: str) -> Optional[float]:
    """
    Parse a price from a text string.

    Supported formats:
        '99 €'         → 99.0
        '99,00 €'      → 99.0
        '1.299 €'      → 1299.0
        '1.299,50 €'   → 1299.50
        '€1,299.50'    → 1299.50
        'ab 99,00 €'   → 99.0

    Returns None if no valid price can be extracted.
    """
    if not text:
        return None

    text = text.strip()

    # Try EN style first (€ prefix)
    m = _RE_PRICE_EN.search(text)
    if m:
        try:
            return _normalize_en(m.group(1))
        except ValueError:
            pass

    # Try DE style (€ suffix)
    m = _RE_PRICE_DE.search(text)
    if m:
        raw = m.group(1)
        try:
            return _normalize_de(raw)
        except ValueError:
            pass

    logger.debug("Could not parse price from text: %r", text)
    return None


def extract_all_prices(text: str) -> list[float]:
    """Extract all prices from a text block."""
    prices: list[float] = []

    # EN style
    for m in _RE_PRICE_EN.finditer(text):
        try:
            prices.append(_normalize_en(m.group(1)))
        except ValueError:
            pass

    # DE style – avoid duplicates by checking positions
    seen_spans: list[tuple[int, int]] = [m.span() for m in _RE_PRICE_EN.finditer(text)]
    for m in _RE_PRICE_DE.finditer(text):
        # Skip if this span overlaps with an EN match already found
        overlaps = any(
            not (m.end() <= s[0] or m.start() >= s[1]) for s in seen_spans
        )
        if not overlaps:
            try:
                prices.append(_normalize_de(m.group(1)))
            except ValueError:
                pass

    return prices


# ---------------------------------------------------------------------------
# Safety Guard
# ---------------------------------------------------------------------------

# Positive allowlist – these action types are permitted
ALLOWED_ACTION_CONTEXTS = frozenset(
    [
        "cookie_accept",
        "airport_select",
        "date_input",
        "passenger_stepper",
        "theme_card",
        "back_navigation",
        "learn_more",
        "dropdown_item",
        "search_submit",
    ]
)

# Hard-blocked terms – checked in visible text, aria-label, title, href, form action
# and surrounding context (up to 2 DOM levels)
_BLOCKED_TERMS = [
    r"\bbuchen\b",
    r"\bjetzt buchen\b",
    r"\bkaufen\b",
    r"\bbestellen\b",
    r"\bbezahlen\b",
    r"\bzahlung\b",
    r"\bpay\b",
    r"\bpayment\b",
    r"\bcheckout\b",
    r"\bbook now\b",
    r"\bbuy now\b",
    r"\bpurchase\b",
    r"\border now\b",
    r"\bweiter zur zahlung\b",
    r"\bproceed to payment\b",
    r"\bconfirm (and )?pay\b",
    r"\bplace order\b",
    r"\bcomplete booking\b",
    r"\babschließen\b",
    r"\bkauf abschließen\b",
    r"\bbuchung bestätigen\b",
]

_BLOCKED_RE = re.compile("|".join(_BLOCKED_TERMS), re.IGNORECASE)

# Contexts where "confirm" / "bestätigen" is allowed
_SAFE_CONFIRM_CONTEXTS = frozenset(
    [
        "cookie_accept",
        "date_input",
        "passenger_stepper",
        "airport_select",
    ]
)

# Contexts where "confirm" / "bestätigen" is blocked
_UNSAFE_CONFIRM_CONTEXTS = frozenset(
    [
        "payment_form",
        "booking_form",
        "checkout_page",
    ]
)


def is_safe_to_click(
    *,
    action_context: str,
    visible_text: str = "",
    aria_label: str = "",
    title: str = "",
    href: str = "",
    form_action: str = "",
    surrounding_text: str = "",
) -> tuple[bool, str]:
    """
    Determine whether a UI element is safe to click.

    Returns (is_safe, reason).
    """
    # Combine all text signals for blocking check
    all_text = " ".join(
        [visible_text, aria_label, title, href, form_action, surrounding_text]
    ).lower()

    # Hard block: any blocked term found anywhere → refuse
    blocked_match = _BLOCKED_RE.search(all_text)
    if blocked_match:
        return False, f"Blocked term found: {blocked_match.group()!r}"

    # Context-aware "confirm" check
    confirm_pattern = re.compile(r"\b(confirm|bestätigen|bestätigung)\b", re.IGNORECASE)
    if confirm_pattern.search(all_text):
        if action_context in _SAFE_CONFIRM_CONTEXTS:
            # Allowed in safe context
            pass
        elif action_context in _UNSAFE_CONFIRM_CONTEXTS:
            return False, f"'confirm' in unsafe context: {action_context!r}"
        else:
            # Ambiguous – refuse as precaution
            return False, f"'confirm' in ambiguous context: {action_context!r} – refusing as precaution"

    # Must be in allowlist
    if action_context not in ALLOWED_ACTION_CONTEXTS:
        return False, f"Action context {action_context!r} not in allowlist"

    return True, "ok"


# ---------------------------------------------------------------------------
# Pride-city matching
# ---------------------------------------------------------------------------

def _normalize_city(name: str) -> str:
    """Normalize city name: lowercase, strip accents, strip whitespace."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_name.lower().strip()


def is_pride_city(city_name: str, pride_cities: list[str]) -> bool:
    """Check if a city name matches any of the Pride cities (accent-insensitive)."""
    normalized_input = _normalize_city(city_name)
    for pride in pride_cities:
        if _normalize_city(pride) == normalized_input:
            return True
    return False


def find_pride_cities_in_pool(destination_pool: list[str], pride_cities: list[str]) -> list[str]:
    """Return subset of destination_pool entries that match Pride cities."""
    return [city for city in destination_pool if is_pride_city(city, pride_cities)]


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters into a single space."""
    return re.sub(r"\s+", " ", text).strip()


def extract_city_names_from_text(text: str) -> list[str]:
    """
    Heuristic extraction of potential city names from free text.
    Returns a list of candidates – these are UNCONFIRMED mentions only.
    """
    # Match capitalized words (potential proper nouns) not at sentence start
    # This is intentionally conservative to avoid false positives
    candidates = re.findall(r"\b([A-ZÄÖÜ][a-zäöüß]{2,}(?:\s[A-ZÄÖÜ][a-zäöüß]{2,})?)\b", text)
    # Remove common non-city words
    stop_words = {
        "Economy", "Business", "Klasse", "Class", "Flug", "Flight",
        "Reise", "Travel", "Thema", "Theme", "Überraschung", "Surprise",
        "Lufthansa", "August", "September", "Oktober",
    }
    return [c for c in candidates if c not in stop_words]
