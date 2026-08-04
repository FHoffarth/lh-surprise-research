"""Tests for the Safety Guard – allowlist, blocklist, and confirm-context logic."""

from __future__ import annotations

import pytest

from src.utils import is_safe_to_click


class TestBlockedTerms:
    """Hard-blocked terms must always be refused."""

    @pytest.mark.parametrize("term", [
        "Jetzt buchen",
        "buchen",
        "kaufen",
        "bestellen",
        "bezahlen",
        "Zahlung",
        "pay",
        "payment",
        "checkout",
        "book now",
        "buy now",
        "purchase",
        "order now",
        "weiter zur Zahlung",
        "Proceed to payment",
        "kauf abschließen",
        "Buchung bestätigen",
    ])
    def test_blocked_in_visible_text(self, term):
        safe, reason = is_safe_to_click(
            action_context="theme_card",
            visible_text=term,
        )
        assert safe is False, f"Expected block for {term!r}, got: {reason}"

    def test_blocked_in_aria_label(self):
        safe, reason = is_safe_to_click(
            action_context="back_navigation",
            visible_text="Zurück",
            aria_label="Jetzt buchen",
        )
        assert safe is False

    def test_blocked_in_title(self):
        safe, reason = is_safe_to_click(
            action_context="back_navigation",
            visible_text="Weiter",
            title="checkout",
        )
        assert safe is False

    def test_blocked_in_href(self):
        safe, reason = is_safe_to_click(
            action_context="back_navigation",
            visible_text="Weiter",
            href="/checkout/payment",
        )
        assert safe is False

    def test_blocked_in_surrounding_text(self):
        safe, reason = is_safe_to_click(
            action_context="theme_card",
            visible_text="Weiter",
            surrounding_text="Klicken Sie hier zum Buchen",
        )
        assert safe is False

    def test_blocked_case_insensitive(self):
        safe, reason = is_safe_to_click(
            action_context="theme_card",
            visible_text="BUCHEN",
        )
        assert safe is False


class TestAllowedActions:
    """Actions in the allowlist with no blocked terms should be permitted."""

    def test_cookie_accept(self):
        safe, reason = is_safe_to_click(
            action_context="cookie_accept",
            visible_text="Alle akzeptieren",
        )
        assert safe is True, reason

    def test_airport_select(self):
        safe, reason = is_safe_to_click(
            action_context="airport_select",
            aria_label="Abflughafen auswählen",
        )
        assert safe is True, reason

    def test_date_input(self):
        safe, reason = is_safe_to_click(
            action_context="date_input",
            aria_label="Hinflugdatum",
        )
        assert safe is True, reason

    def test_passenger_stepper(self):
        safe, reason = is_safe_to_click(
            action_context="passenger_stepper",
            aria_label="Erwachsene erhöhen",
        )
        assert safe is True, reason

    def test_theme_card(self):
        safe, reason = is_safe_to_click(
            action_context="theme_card",
            visible_text="Kunst & Kultur",
        )
        assert safe is True, reason

    def test_back_navigation(self):
        safe, reason = is_safe_to_click(
            action_context="back_navigation",
            visible_text="Zurück zur Übersicht",
            href="/travel-theme",
        )
        assert safe is True, reason

    def test_learn_more(self):
        safe, reason = is_safe_to_click(
            action_context="learn_more",
            visible_text="Mehr erfahren",
        )
        assert safe is True, reason


class TestUnknownContext:
    """Unknown action contexts should be refused."""

    def test_unknown_context_refused(self):
        safe, reason = is_safe_to_click(
            action_context="unknown_action",
            visible_text="Weiter",
        )
        assert safe is False
        assert "allowlist" in reason.lower() or "not in" in reason.lower()


class TestConfirmHandling:
    """'confirm'/'bestätigen' must be context-aware, not pauschal blocked."""

    def test_confirm_in_cookie_context_allowed(self):
        safe, reason = is_safe_to_click(
            action_context="cookie_accept",
            visible_text="Bestätigen",
        )
        assert safe is True, f"Should allow confirm in cookie context: {reason}"

    def test_confirm_in_date_context_allowed(self):
        safe, reason = is_safe_to_click(
            action_context="date_input",
            visible_text="Bestätigen",
        )
        assert safe is True, f"Should allow confirm in date context: {reason}"

    def test_confirm_in_payment_form_blocked(self):
        safe, reason = is_safe_to_click(
            action_context="payment_form",
            visible_text="Confirm",
        )
        assert safe is False, f"Should block confirm in payment context: {reason}"

    def test_confirm_in_booking_form_blocked(self):
        safe, reason = is_safe_to_click(
            action_context="booking_form",
            visible_text="Bestätigung",
        )
        assert safe is False

    def test_confirm_in_ambiguous_context_refused(self):
        """In ambiguous (unknown) context, confirm should be refused as precaution."""
        safe, reason = is_safe_to_click(
            action_context="theme_card",
            visible_text="confirm",
        )
        assert safe is False, f"Should refuse confirm in ambiguous context: {reason}"

    def test_confirm_pay_always_blocked(self):
        """'confirm and pay' contains a hard-blocked term regardless of context."""
        safe, reason = is_safe_to_click(
            action_context="cookie_accept",
            visible_text="confirm and pay",
        )
        assert safe is False


class TestFinalBookingStepProtection:
    """Specific scenarios that simulate a final booking step."""

    def test_full_booking_button(self):
        safe, _ = is_safe_to_click(
            action_context="theme_card",
            visible_text="Jetzt buchen",
            aria_label="Reise jetzt buchen",
            href="/booking/checkout",
            surrounding_text="Gesamtpreis: 199,00 €",
        )
        assert safe is False

    def test_payment_page_submit(self):
        safe, _ = is_safe_to_click(
            action_context="payment_form",
            visible_text="Zahlung abschließen",
            form_action="/api/payment/complete",
        )
        assert safe is False

    def test_legitimate_back_button_not_blocked(self):
        """A back button on a booking page is still safe."""
        safe, reason = is_safe_to_click(
            action_context="back_navigation",
            visible_text="Zurück",
            aria_label="Zurück zur Übersicht",
            href="/travel-theme",
        )
        assert safe is True, reason
