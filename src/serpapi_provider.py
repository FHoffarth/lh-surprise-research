import os
import json
import datetime
import logging
from typing import List, Tuple, Dict
from urllib.parse import urlencode

from dotenv import load_dotenv
import aiohttp

from src.destination_inference import Flight, FlightScheduleStatus, ProviderResult, FlightScheduleProvider

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SerpApiFlightScheduleProvider(FlightScheduleProvider):
    """
    Provider that fetches flight schedules using SerpApi's Google Flights Engine.
    Uses 'cash_shopping_result' as source_type and does not confirm LH Surprise inventory.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("SERPAPI_API_KEY")
        self.cache: Dict[Tuple[str, str, str, str, str, str], ProviderResult] = {}
        
    def _redact_key(self, text: str) -> str:
        if not self.api_key:
            return text
        return text.replace(self.api_key, "[REDACTED]")
        
    async def get_flights(self, origin: str, destination: str, date: str, direct_only: bool = True, airline: str = "LH") -> ProviderResult:
        if not self.api_key:
            return ProviderResult(
                flights=[],
                status=FlightScheduleStatus.PROVIDER_UNAVAILABLE,
                message="SERPAPI_API_KEY not set",
                metadata={"source_type": "cash_shopping_result"}
            )
            
        cache_key = (origin, destination, date, "", "Economy", "1")
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        metadata = {
            "requested_route": f"{origin}-{destination}",
            "requested_date": date,
            "source_type": "cash_shopping_result",
            "extraction_method": "serpapi",
            "retrieved_at": datetime.datetime.now().isoformat(),
            "status": FlightScheduleStatus.UNKNOWN.value,
            "parameters_verified": True
        }
        
        # Build SerpApi query
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": date,
            "currency": "EUR",
            "hl": "de",
            "api_key": self.api_key
        }
        if direct_only:
            params["type"] = "2" # "2" means oneway
            params["stops"] = "1" # "1" means nonstop in SerpApi google_flights (1 = nonstop, 2 = 1 stop)
            
        url = f"https://serpapi.com/search.json?{urlencode(params)}"
        redacted_url = self._redact_key(url)
        logger.debug(f"Requesting SerpApi: {redacted_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"SerpApi returned {resp.status} for {redacted_url}")
                        metadata["status"] = FlightScheduleStatus.BLOCKED.value # Treat non-200 as blocked/error
                        res = ProviderResult(flights=[], status=FlightScheduleStatus.BLOCKED, message=f"HTTP {resp.status}", metadata=metadata)
                        self.cache[cache_key] = res
                        return res
                        
                    data = await resp.json()
        except Exception as e:
            msg = self._redact_key(str(e))
            logger.error(f"Error fetching from SerpApi: {msg}")
            metadata["status"] = FlightScheduleStatus.PARSE_FAILED.value
            res = ProviderResult(flights=[], status=FlightScheduleStatus.PARSE_FAILED, message=msg, metadata=metadata)
            self.cache[cache_key] = res
            return res
            
        flights = self._parse_google_flights(data, origin, destination, date, airline)
        
        if not flights:
            metadata["status"] = FlightScheduleStatus.NO_SCHEDULE_FOUND.value
            res = ProviderResult(flights=[], status=FlightScheduleStatus.NO_SCHEDULE_FOUND, metadata=metadata)
            self.cache[cache_key] = res
            return res
            
        metadata["status"] = FlightScheduleStatus.SUCCESS.value
        res = ProviderResult(flights=flights, status=FlightScheduleStatus.SUCCESS, metadata=metadata)
        self.cache[cache_key] = res
        return res

    def _parse_google_flights(self, data: dict, expected_origin: str, expected_dest: str, expected_date: str, expected_airline: str) -> List[Flight]:
        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])
        all_flights = best_flights + other_flights
        
        results = []
        for fl_data in all_flights:
            try:
                flights_list = fl_data.get("flights", [])
                if not flights_list:
                    continue
                    
                first_leg = flights_list[0]
                last_leg = flights_list[-1]
                
                dep_port = first_leg.get("departure_airport", {}).get("id", "")
                arr_port = last_leg.get("arrival_airport", {}).get("id", "")
                
                dep_time_raw = first_leg.get("departure_airport", {}).get("time", "")
                
                if expected_origin not in dep_port or expected_dest not in arr_port:
                    continue
                    
                if expected_date not in dep_time_raw:
                    continue
                    
                marketing_carrier = first_leg.get("airline", "")
                flight_number = first_leg.get("flight_number", "")
                op_carrier = first_leg.get("operating_carrier", "")
                
                # Check for "ticket_also_sold_by" in flight extensions
                ticket_also_sold_by_list = first_leg.get("ticket_also_sold_by", [])
                if isinstance(ticket_also_sold_by_list, list):
                    ticket_also_sold_by = ", ".join(ticket_also_sold_by_list)
                else:
                    ticket_also_sold_by = str(ticket_also_sold_by_list)
                
                is_direct = len(flights_list) == 1
                
                arr_time_raw = last_leg.get("arrival_airport", {}).get("time", "")
                
                flight = Flight(
                    flight_number=f"{marketing_carrier} {flight_number}",
                    airline=marketing_carrier,
                    origin=expected_origin,
                    destination=expected_dest,
                    departure_time=dep_time_raw,
                    arrival_time=arr_time_raw,
                    marketing_carrier=marketing_carrier,
                    operating_carrier=op_carrier,
                    ticket_also_sold_by=ticket_also_sold_by,
                    is_direct=is_direct
                )
                results.append(flight)
            except Exception as e:
                msg = self._redact_key(str(e))
                logger.error(f"Error parsing SerpApi flight: {msg}")
                pass
                
        return results
