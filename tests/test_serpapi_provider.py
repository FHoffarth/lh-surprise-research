import os
import pytest
import logging
from unittest.mock import patch
from src.serpapi_provider import SerpApiFlightScheduleProvider
from src.destination_inference import FlightScheduleStatus

@pytest.fixture
def clean_env():
    # Make sure we don't have lingering env vars during tests
    if "SERPAPI_API_KEY" in os.environ:
        del os.environ["SERPAPI_API_KEY"]
    yield

def test_key_missing(clean_env):
    provider = SerpApiFlightScheduleProvider()
    assert provider.api_key is None

@pytest.mark.asyncio
async def test_provider_unavailable_when_key_missing(clean_env):
    provider = SerpApiFlightScheduleProvider()
    res = await provider.get_flights("FRA", "PRG", "2026-08-07")
    assert res.status == FlightScheduleStatus.PROVIDER_UNAVAILABLE
    assert res.metadata["source_type"] == "cash_shopping_result"

def test_key_present():
    with patch.dict(os.environ, {"SERPAPI_API_KEY": "secret123"}):
        provider = SerpApiFlightScheduleProvider()
        assert provider.api_key == "secret123"

def test_url_redaction():
    provider = SerpApiFlightScheduleProvider("my_secret_key")
    url = "https://serpapi.com/search.json?engine=google_flights&api_key=my_secret_key"
    redacted = provider._redact_key(url)
    assert redacted == "https://serpapi.com/search.json?engine=google_flights&api_key=[REDACTED]"
    assert "my_secret_key" not in redacted

def test_error_redaction():
    provider = SerpApiFlightScheduleProvider("my_secret_key")
    error_msg = "Exception: Failed to connect, token my_secret_key is invalid"
    redacted = provider._redact_key(error_msg)
    assert redacted == "Exception: Failed to connect, token [REDACTED] is invalid"
    assert "my_secret_key" not in redacted
    
def test_no_key_redaction():
    provider = SerpApiFlightScheduleProvider(None)
    msg = "Some normal message"
    assert provider._redact_key(msg) == msg
