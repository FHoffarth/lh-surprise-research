"""Tests for network response monitoring – parsing, redaction, unknown structures."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.network_monitor import NetworkMonitor, _redact_json_body


class TestRedaction:
    def test_token_field_redacted(self):
        data = {"token": "secret123", "results": ["item1"]}
        redacted = _redact_json_body(data)
        assert redacted["token"] == "[REDACTED]"
        assert redacted["results"] == ["item1"]

    def test_session_field_redacted(self):
        data = {"session": "sess-abc", "price": 99}
        redacted = _redact_json_body(data)
        assert redacted["session"] == "[REDACTED]"
        assert redacted["price"] == 99

    def test_nested_redaction(self):
        data = {
            "user": {"token": "secret", "name": "Alice"},
            "offers": [{"apiKey": "key123", "price": 199}],
        }
        redacted = _redact_json_body(data)
        assert redacted["user"]["token"] == "[REDACTED]"
        assert redacted["user"]["name"] == "Alice"
        assert redacted["offers"][0]["apiKey"] == "[REDACTED]"
        assert redacted["offers"][0]["price"] == 199

    def test_non_sensitive_fields_preserved(self):
        data = {"theme": "Kunst & Kultur", "price": 99.0, "available": True}
        redacted = _redact_json_body(data)
        assert redacted == data

    def test_list_input(self):
        data = [{"token": "x"}, {"price": 99}]
        redacted = _redact_json_body(data)
        assert redacted[0]["token"] == "[REDACTED]"
        assert redacted[1]["price"] == 99

    def test_null_values_preserved(self):
        data = {"theme": None, "price": None}
        redacted = _redact_json_body(data)
        assert redacted["theme"] is None

    def test_empty_dict(self):
        assert _redact_json_body({}) == {}

    def test_deep_recursion_limit(self):
        """Should not crash on deeply nested structures."""
        nested = {"level": 0}
        current = nested
        for i in range(15):
            current["child"] = {"level": i + 1}
            current = current["child"]
        # Should not raise
        result = _redact_json_body(nested)
        assert result is not None


class TestNetworkMonitorCapture:
    """Test monitor capture logic with mocked responses."""

    def _make_response(self, url: str, status: int, content_type: str, body: dict) -> AsyncMock:
        response = AsyncMock()
        response.url = url
        response.status = status
        response.headers = {"content-type": content_type}
        response.body = AsyncMock(return_value=json.dumps(body).encode("utf-8"))
        return response

    @pytest.mark.asyncio
    async def test_relevant_json_response_captured(self, tmp_path):
        monitor = NetworkMonitor(tmp_path)
        response = self._make_response(
            url="https://api.lufthansa-surprise.com/v1/themes?origin=FRA",
            status=200,
            content_type="application/json",
            body={"themes": ["Kunst & Kultur"], "prices": [99]},
        )
        await monitor._on_response(response)
        assert monitor.response_count == 1

    @pytest.mark.asyncio
    async def test_non_json_response_ignored(self, tmp_path):
        monitor = NetworkMonitor(tmp_path)
        response = self._make_response(
            url="https://api.lufthansa-surprise.com/v1/themes",
            status=200,
            content_type="text/html",
            body={},
        )
        response.body = AsyncMock(return_value=b"<html></html>")
        await monitor._on_response(response)
        assert monitor.response_count == 0

    @pytest.mark.asyncio
    async def test_error_status_ignored(self, tmp_path):
        monitor = NetworkMonitor(tmp_path)
        response = self._make_response(
            url="https://api.lufthansa-surprise.com/v1/destinations",
            status=404,
            content_type="application/json",
            body={"error": "not found"},
        )
        await monitor._on_response(response)
        assert monitor.response_count == 0

    @pytest.mark.asyncio
    async def test_irrelevant_url_ignored(self, tmp_path):
        monitor = NetworkMonitor(tmp_path)
        response = self._make_response(
            url="https://cdn.example.com/static/logo.png.json",
            status=200,
            content_type="application/json",
            body={"version": "1.0"},
        )
        await monitor._on_response(response)
        assert monitor.response_count == 0

    @pytest.mark.asyncio
    async def test_sensitive_fields_redacted_in_saved_file(self, tmp_path):
        monitor = NetworkMonitor(tmp_path)
        response = self._make_response(
            url="https://api.lufthansa-surprise.com/v1/offers?destination=FRA",
            status=200,
            content_type="application/json",
            body={"offers": [{"price": 99}], "session": "should-be-redacted"},
        )
        await monitor._on_response(response)
        # Find saved file
        network_dir = tmp_path / "network"
        files = list(network_dir.glob("*.json"))
        assert len(files) == 1
        saved = json.loads(files[0].read_text(encoding="utf-8"))
        assert saved["body"]["session"] == "[REDACTED]"
        assert saved["body"]["offers"][0]["price"] == 99

    @pytest.mark.asyncio
    async def test_unknown_json_structure_does_not_crash(self, tmp_path):
        """Unknown or unexpected JSON structures should be handled gracefully."""
        monitor = NetworkMonitor(tmp_path)
        response = self._make_response(
            url="https://api.lufthansa-surprise.com/v1/availability",
            status=200,
            content_type="application/json",
            body={"unexpectedField": [1, 2, 3], "nested": {"deeply": {"nested": "value"}}},
        )
        await monitor._on_response(response)
        # Should not raise, may or may not capture
        assert True  # no exception

    @pytest.mark.asyncio
    async def test_malformed_json_body_handled(self, tmp_path):
        """Malformed JSON body should be ignored without crashing."""
        monitor = NetworkMonitor(tmp_path)
        response = AsyncMock()
        response.url = "https://api.lufthansa-surprise.com/v1/destinations"
        response.status = 200
        response.headers = {"content-type": "application/json"}
        response.body = AsyncMock(return_value=b"not-valid-json{{{")
        await monitor._on_response(response)
        assert monitor.response_count == 0  # malformed → not captured

    @pytest.mark.asyncio
    async def test_monitor_error_does_not_propagate(self, tmp_path):
        """Errors inside monitor should never crash the caller."""
        monitor = NetworkMonitor(tmp_path)
        broken_response = MagicMock()
        broken_response.url = "https://api.lufthansa-surprise.com/v1/destinations"
        broken_response.status = 200
        broken_response.headers = {"content-type": "application/json"}
        broken_response.body = AsyncMock(side_effect=RuntimeError("Connection reset"))
        # Should not raise
        await monitor._on_response(broken_response)
        assert monitor.response_count == 0
