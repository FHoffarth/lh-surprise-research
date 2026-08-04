"""Tests for price parsing, Pride-city matching, and result normalization."""

from __future__ import annotations

import pytest

from src.utils import (
    extract_all_prices,
    find_pride_cities_in_pool,
    is_pride_city,
    parse_price,
)


class TestPriceParsing:
    """Test all supported price formats."""

    def test_simple_euro_suffix(self):
        assert parse_price("99 €") == 99.0

    def test_decimal_comma(self):
        assert parse_price("99,00 €") == 99.0

    def test_thousand_dot(self):
        assert parse_price("1.299 €") == 1299.0

    def test_thousand_dot_decimal_comma(self):
        assert parse_price("1.299,50 €") == pytest.approx(1299.50)

    def test_euro_prefix_en_format(self):
        assert parse_price("€1,299.50") == pytest.approx(1299.50)

    def test_prefix_ab(self):
        assert parse_price("ab 99,00 €") == 99.0

    def test_prefix_von(self):
        assert parse_price("von 149 €") == 149.0

    def test_prefix_from(self):
        assert parse_price("from €199.99") == pytest.approx(199.99)

    def test_none_for_empty(self):
        assert parse_price("") is None

    def test_none_for_no_price(self):
        assert parse_price("Kein Preis verfügbar") is None

    def test_none_for_letters_only(self):
        assert parse_price("Preis auf Anfrage") is None

    def test_large_price(self):
        assert parse_price("9.999,99 €") == pytest.approx(9999.99)

    def test_round_number_en(self):
        assert parse_price("€500") == 500.0

    def test_whitespace_stripping(self):
        assert parse_price("  1.299,50 €  ") == pytest.approx(1299.50)

    def test_text_with_embedded_price(self):
        # Price embedded in sentence
        result = parse_price("Preis ab 299,00 € pro Person")
        assert result == pytest.approx(299.0)


class TestExtractAllPrices:
    def test_multiple_prices(self):
        text = "Economy ab 99 €, Business ab 299 €"
        prices = extract_all_prices(text)
        assert 99.0 in prices
        assert 299.0 in prices

    def test_single_price(self):
        prices = extract_all_prices("Nur 149,00 €")
        assert prices == [pytest.approx(149.0)]

    def test_no_prices(self):
        assert extract_all_prices("Keine Preisangabe") == []

    def test_de_and_en_mixed(self):
        text = "von 99,00 € oder €120.00"
        prices = extract_all_prices(text)
        assert len(prices) == 2
        assert pytest.approx(99.0) in prices
        assert pytest.approx(120.0) in prices


class TestPrideCityMatching:
    PRIDE_CITIES = [
        "Amsterdam", "Prag", "Antwerpen", "Reykjavík",
        "Nürnberg", "Braunschweig", "Kopenhagen"
    ]

    def test_exact_match(self):
        assert is_pride_city("Amsterdam", self.PRIDE_CITIES) is True

    def test_accent_insensitive(self):
        # Reykjavík vs Reykjavik (no accent)
        assert is_pride_city("Reykjavik", self.PRIDE_CITIES) is True

    def test_umlaut_match(self):
        assert is_pride_city("Nürnberg", self.PRIDE_CITIES) is True

    def test_case_insensitive(self):
        assert is_pride_city("amsterdam", self.PRIDE_CITIES) is True
        assert is_pride_city("AMSTERDAM", self.PRIDE_CITIES) is True

    def test_non_pride_city(self):
        assert is_pride_city("Berlin", self.PRIDE_CITIES) is False

    def test_partial_name_no_match(self):
        assert is_pride_city("Amster", self.PRIDE_CITIES) is False

    def test_empty_string(self):
        assert is_pride_city("", self.PRIDE_CITIES) is False

    def test_find_pride_cities_in_pool(self):
        pool = ["Berlin", "Amsterdam", "München", "Kopenhagen", "Paris"]
        found = find_pride_cities_in_pool(pool, self.PRIDE_CITIES)
        assert "Amsterdam" in found
        assert "Kopenhagen" in found
        assert "Berlin" not in found

    def test_find_pride_cities_empty_pool(self):
        assert find_pride_cities_in_pool([], self.PRIDE_CITIES) == []

    def test_find_pride_cities_no_match(self):
        pool = ["London", "Paris", "Madrid"]
        assert find_pride_cities_in_pool(pool, self.PRIDE_CITIES) == []


class TestResultNormalization:
    """Test that ThemeData to_dict produces expected structure."""

    def test_theme_data_defaults(self):
        from src.extractor import ThemeData
        t = ThemeData()
        d = t.to_dict()
        assert "theme_name" in d
        assert "destination_pool" in d
        assert "excludable_destinations" in d
        assert "mentioned_cities" in d
        assert "confirmed_available" in d
        assert "price_min" in d
        assert "pride_cities_found" in d
        assert "extraction_warnings" in d

    def test_empty_theme_data(self):
        from src.extractor import ThemeData
        t = ThemeData()
        assert t.confirmed_available is None
        assert t.price_min is None
        assert t.destination_pool == []
        assert t.mentioned_cities == []

    def test_theme_data_with_values(self):
        from src.extractor import ThemeData
        t = ThemeData(
            theme_name="Kunst & Kultur",
            price_min=99.0,
            confirmed_available=True,
            destination_pool=["Amsterdam", "Paris"],
        )
        d = t.to_dict()
        assert d["theme_name"] == "Kunst & Kultur"
        assert d["price_min"] == 99.0
        assert d["confirmed_available"] is True
        assert "Amsterdam" in d["destination_pool"]

    def test_destination_type_separation(self):
        """Ensure destination_pool, excludable, and mentioned are separate fields."""
        from src.extractor import ThemeData
        t = ThemeData()
        t.destination_pool = ["Sonnenziele"]
        t.excludable_destinations = ["Mallorca"]
        t.mentioned_cities = ["München"]  # unconfirmed
        t.confirmed_available = None  # unknown

        d = t.to_dict()
        # Separate fields, no cross-contamination
        assert d["destination_pool"] == ["Sonnenziele"]
        assert d["excludable_destinations"] == ["Mallorca"]
        assert d["mentioned_cities"] == ["München"]
        assert d["confirmed_available"] is None  # never assumed True from a city mention

    def test_add_warning(self):
        from src.extractor import ThemeData
        t = ThemeData(theme_name="Test")
        t.add_warning("Test warning")
        assert len(t.extraction_warnings) == 1
        assert "Test warning" in t.extraction_warnings[0]
