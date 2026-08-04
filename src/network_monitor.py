"""Passive network response monitor using page.on('response').

Requests are never modified, repeated, or blocked.
Only JSON responses matching relevant URL patterns are captured.
Sensitive headers and body fields are redacted before saving.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# URL patterns that likely contain booking-relevant data
_RELEVANT_URL_PATTERNS = re.compile(
    r"(destination|price|flight|theme|offer|availab|travel|product|search|booking)",
    re.IGNORECASE,
)

# Response headers to never save
_SENSITIVE_HEADERS = frozenset(
    [
        "set-cookie",
        "cookie",
        "authorization",
        "x-auth-token",
        "x-session-id",
        "x-api-key",
        "x-csrf-token",
        "x-request-id",
    ]
)

# JSON body keys whose values are replaced with [REDACTED]
_SENSITIVE_KEYS = frozenset(
    [
        "token",
        "session",
        "sessionid",
        "sessiontoken",
        "cookie",
        "auth",
        "authorization",
        "password",
        "secret",
        "apikey",
        "api_key",
        "csrf",
        "nonce",
        "accesstoken",
        "refreshtoken",
        "idtoken",
    ]
)


def _redact_json_body(data: Any, depth: int = 0) -> Any:
    """Recursively redact sensitive keys from a JSON object. Max depth 10."""
    if depth > 10:
        return data
    if isinstance(data, dict):
        return {
            k: "[REDACTED]" if k.lower().replace("-", "").replace("_", "") in _SENSITIVE_KEYS
            else _redact_json_body(v, depth + 1)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [_redact_json_body(item, depth + 1) for item in data]
    return data


class NetworkMonitor:
    """
    Passively captures relevant JSON responses from a Playwright page.

    Usage:
        monitor = NetworkMonitor(output_dir)
        monitor.attach(page)
        # ... perform actions ...
        responses = monitor.captured_responses
    """

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir / "network"
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._captured: list[dict] = []
        self._lock = asyncio.Lock()

    def attach(self, page: Any) -> None:
        """Register the response listener on the page. Non-blocking."""
        page.on("response", self._on_response)
        logger.debug("NetworkMonitor attached to page")

    def detach(self, page: Any) -> None:
        """Remove the response listener."""
        page.remove_listener("response", self._on_response)
        logger.debug("NetworkMonitor detached from page")

    async def _on_response(self, response: Any) -> None:
        """
        Async callback for every network response.
        Only processes JSON responses matching relevant URL patterns.
        Does not modify, repeat, or block any request.
        """
        try:
            url = response.url
            status = response.status
            content_type = response.headers.get("content-type", "")

            # Only capture JSON with OK status and relevant URL
            if status != 200:
                return
            if "json" not in content_type.lower():
                return
            if not _RELEVANT_URL_PATTERNS.search(url):
                return

            # Read body (non-blocking)
            try:
                body_bytes = await response.body()
                body_text = body_bytes.decode("utf-8", errors="replace")
                body_data = json.loads(body_text)
            except Exception as exc:
                logger.debug("Could not parse response body from %s: %s", url, exc)
                return

            # Redact sensitive fields
            body_redacted = False
            redacted_body = _redact_json_body(body_data)
            if redacted_body != body_data:
                body_redacted = True

            # Build safe record (no sensitive headers)
            parsed_url = urlparse(url)
            slug = re.sub(r"[^a-zA-Z0-9_-]", "_", parsed_url.path)[:60]
            timestamp = time.strftime("%Y%m%dT%H%M%S")
            filename = f"response_{timestamp}_{slug}.json"

            record = {
                "url": url,
                "status": status,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "content_type": content_type,
                "body_redacted": body_redacted,
                "body": redacted_body,
            }

            # Save to disk
            output_path = self._output_dir / filename
            with output_path.open("w", encoding="utf-8") as fh:
                json.dump(record, fh, ensure_ascii=False, indent=2)

            async with self._lock:
                self._captured.append(record)

            logger.info("Captured network response: %s → %s", url, filename)

        except Exception as exc:
            # Never let monitor errors affect the main scraper
            logger.debug("NetworkMonitor error (ignored): %s", exc)

    @property
    def captured_responses(self) -> list[dict]:
        """Return list of all captured and redacted response records."""
        return list(self._captured)

    @property
    def response_count(self) -> int:
        return len(self._captured)
