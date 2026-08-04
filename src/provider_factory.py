import os
from src.destination_inference import FlightScheduleProvider, FlightScheduleStatus, ProviderResult, Flight
from src.lufthansa_public_provider import PublicLufthansaTimetableProvider
from src.serpapi_provider import SerpApiFlightScheduleProvider
from src.destination_inference import MockScheduleProvider

class UnavailableProvider(FlightScheduleProvider):
    async def get_flights(self, origin: str, destination: str, date: str, direct_only: bool = True, airline: str = "LH") -> ProviderResult:
        return ProviderResult(
            flights=[],
            status=FlightScheduleStatus.PROVIDER_UNAVAILABLE,
            message="Selected provider is unavailable"
        )

def get_provider(name: str, playwright_page=None) -> FlightScheduleProvider:
    if name == "mock":
        return MockScheduleProvider()
    elif name == "serpapi":
        return SerpApiFlightScheduleProvider()
    elif name == "lufthansa_public":
        if playwright_page is None:
            raise ValueError("playwright_page is required for lufthansa_public provider")
        return PublicLufthansaTimetableProvider(playwright_page)
    elif name == "auto":
        if os.environ.get("SERPAPI_API_KEY"):
            return SerpApiFlightScheduleProvider()
        else:
            return UnavailableProvider()
    else:
        raise ValueError(f"Unknown provider: {name}")
