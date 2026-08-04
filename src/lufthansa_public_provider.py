import asyncio
import json
import logging
import datetime
from typing import List, Dict, Optional, Tuple
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PWTimeoutError

from src.destination_inference import Flight, FlightScheduleStatus, ProviderResult

logger = logging.getLogger(__name__)

class PublicLufthansaTimetableProvider:
    """
    Scrapes LH offers/timetable data from public lufthansa.com search.
    Implements Phase 2b rules with navigation attempts logging.
    """
    
    def __init__(self, page: Page):
        self.page = page
        self.cache: Dict[Tuple[str, str, str], ProviderResult] = {}
        self._offers_data: Optional[Dict] = None
        self._setup_passive_listener()
        self.consent_method = "not_present"
        
    def _setup_passive_listener(self):
        async def handle_response(response):
            try:
                if response.status == 200 and "application/json" in response.headers.get("content-type", ""):
                    logger.info(f"Intercepted JSON response: {response.url}")
                    if "api/offers" in response.url or "/ond/" in response.url or "api/flight-search" in response.url or "flight-search-api" in response.url or "graphql" in response.url.lower():
                        data = await response.json()
                        # We just save the last one, or maybe we append it? For now, just save it.
                        self._offers_data = data
            except Exception:
                pass
        self.page.on("response", handle_response)
        
    async def get_flights(self, origin: str, destination: str, date: str, direct_only: bool = True) -> ProviderResult:
        cache_key = (origin, destination, date)
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        attempts = []
        successful_method = None
        
        # Base metadata
        metadata = {
            "requested_route": f"{origin}-{destination}",
            "requested_date": date,
            "response_routes": [],
            "response_dates": [],
            "parameters_verified": False,
            "navigation_attempts": attempts,
            "successful_navigation_method": None,
            "final_url_redacted": "",
            "source_type": "shopping_offer",
            "extraction_method": "network",
            "status": FlightScheduleStatus.UNKNOWN.value,
            "status_reason": ""
        }
            
        # Try Deeplink first
        res = await self._run_deeplink_search(origin, destination, date, direct_only)
        attempts.append({
            "method": "deeplink",
            "status": res.status.value,
            "final_url_redacted": res.metadata.get("final_url_redacted", ""),
            "parameters_verified": res.metadata.get("parameters_verified", False)
        })
        
        if res.status == FlightScheduleStatus.SUCCESS:
            successful_method = "deeplink"
            metadata.update(res.metadata)
            metadata["navigation_attempts"] = attempts
            metadata["successful_navigation_method"] = successful_method
            metadata["status"] = res.status.value
            metadata["status_reason"] = res.message
            res.metadata = metadata
            self.cache[cache_key] = res
            return res
            
        # Fallback to UI search if Deeplink fails
        logger.info(f"Deeplink failed with {res.status.value}, falling back to UI")
        if res.status == FlightScheduleStatus.BLOCKED:
            logger.info("Skipping UI fallback because IP is blocked.")
            # We don't want to retry if blocked
            return res
            
        res_ui = await self._run_ui_search(origin, destination, date, direct_only)
        
        attempts.append({
            "method": "ui",
            "status": res_ui.status.value,
            "final_url_redacted": res_ui.metadata.get("final_url_redacted", ""),
            "parameters_verified": res_ui.metadata.get("parameters_verified", False)
        })
        
        if res_ui.status == FlightScheduleStatus.SUCCESS:
            successful_method = "ui"
            
        # Merge metadata
        metadata.update(res_ui.metadata)
        metadata["navigation_attempts"] = attempts
        metadata["successful_navigation_method"] = successful_method
        metadata["status"] = res_ui.status.value
        metadata["status_reason"] = res_ui.message
        res_ui.metadata = metadata
        
        self.cache[cache_key] = res_ui
        return res_ui

    async def _handle_consent(self):
        # 1. Reject
        reject_btn = self.page.locator("button:has-text('Nur erforderliche'), button:has-text('Ablehnen')")
        if await reject_btn.count() > 0:
            try:
                await reject_btn.first.click(timeout=3000)
                self.consent_method = "regular_reject"
                await asyncio.sleep(1)
                return
            except Exception:
                pass
                
        # 2. Accept
        accept_btn = self.page.locator("button:has-text('Alle akzeptieren')")
        if await accept_btn.count() > 0:
            try:
                await accept_btn.first.click(timeout=3000)
                self.consent_method = "regular_accept"
                await asyncio.sleep(1)
                return
            except Exception:
                pass
                
        # 3. DOM fallback
        try:
            await self.page.evaluate("document.getElementById('onetrust-consent-sdk')?.remove()")
            self.consent_method = "dom_fallback"
        except Exception:
            pass

    async def _check_for_bot_protection(self, metadata: dict) -> Optional[ProviderResult]:
        """
        Checks the page DOM for known bot detection / Security check markers.
        """
        try:
            content = await self.page.content()
            content_lower = content.lower()
            if "security check" in content_lower or "sicherheitscheck" in content_lower or "resembles that of a bot" in content_lower:
                logger.warning("Bot protection triggered (Security check detected).")
                await self.page.screenshot(path="artifacts/screenshots/bot_protection.png")
                
                # Extract Reference ID if possible
                ref_id = ""
                try:
                    ref_loc = self.page.locator("text='Reference-ID', text='Reference ID', text='Referenz-ID'")
                    if await ref_loc.count() > 0:
                        ref_id = "extracted_reference_id" # REDACTED in actual code or just don't parse deeply
                except Exception:
                    pass
                    
                return ProviderResult(
                    flights=[], 
                    status=FlightScheduleStatus.BLOCKED, 
                    message="Security check blocked access",
                    metadata=metadata
                )
        except Exception:
            pass
        return None

    async def _run_deeplink_search(self, origin: str, destination: str, date: str, direct_only: bool) -> ProviderResult:
        self._offers_data = None
        
        url = f"https://www.lufthansa.com/de/de/fluege?flightQuery.flightJourneys[0].origin={origin}&flightQuery.flightJourneys[0].destination={destination}&flightQuery.flightJourneys[0].outboundDate={date}"
        
        metadata = {
            "parameters_verified": False,
            "final_url_redacted": "",
            "response_routes": [],
            "response_dates": []
        }
        
        try:
            logger.info(f"Navigating to Deeplink for {origin}-{destination}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            
            bot_block = await self._check_for_bot_protection(metadata)
            if bot_block:
                return bot_block
            
            await self._handle_consent()
            
            final_url = self.page.url
            metadata["final_url_redacted"] = final_url.split("?")[0] if "?" in final_url else final_url
            
            if "homepage" in final_url or "home" in final_url:
                return ProviderResult(flights=[], status=FlightScheduleStatus.REDIRECTED_TO_HOME, metadata=metadata)
                
            for i in range(15):
                if self._offers_data is not None:
                    break
                await asyncio.sleep(1.0)
                
            if not self._offers_data:
                return ProviderResult(flights=[], status=FlightScheduleStatus.UNVERIFIED_RESPONSE, metadata=metadata)
                
            flights = self._parse_passive_json(self._offers_data, origin, destination, date, direct_only)
            
            if not flights:
                return ProviderResult(flights=[], status=FlightScheduleStatus.NO_SCHEDULE_FOUND, metadata=metadata)
                
            verified, reason = self._verify_flights(flights, origin, destination, date)
            metadata["parameters_verified"] = verified
            
            routes = set(f"{f.origin}-{f.destination}" for f in flights)
            dates = set(f.departure_time for f in flights)
            metadata["response_routes"] = list(routes)
            metadata["response_dates"] = list(dates)
            
            if not verified:
                return ProviderResult(flights=[], status=FlightScheduleStatus.PARAMETER_MISMATCH, message=reason, metadata=metadata)
                
            return ProviderResult(flights=flights, status=FlightScheduleStatus.SUCCESS, metadata=metadata)
            
        except PWTimeoutError:
            return ProviderResult(flights=[], status=FlightScheduleStatus.TIMEOUT, metadata=metadata)
        except Exception as e:
            return ProviderResult(flights=[], status=FlightScheduleStatus.PARSE_FAILED, message=str(e), metadata=metadata)
            
    async def _run_ui_search(self, origin: str, destination: str, date: str, direct_only: bool) -> ProviderResult:
        self._offers_data = None
        
        metadata = {
            "parameters_verified": False,
            "final_url_redacted": "",
            "response_routes": [],
            "response_dates": []
        }
        
        try:
            logger.info(f"Navigating to Homepage for UI search")
            await self.page.goto("https://www.lufthansa.com/de/de/homepage", wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            
            bot_block = await self._check_for_bot_protection(metadata)
            if bot_block:
                return bot_block
            
            await self._handle_consent()
            
            try:
                dropdown = self.page.locator("button:has-text('Round trip'), button:has-text('Hin- und Rückflug')")
                if await dropdown.count() > 0:
                    await dropdown.first.click(force=True)
                    await asyncio.sleep(1)
                    oneway = self.page.locator("button:has-text('One way'), button:has-text('Nur Hinflug'), li:has-text('Nur Hinflug')")
                    if await oneway.count() > 0:
                        await oneway.first.click(force=True)
                await asyncio.sleep(1)
                await self.page.keyboard.press("Escape")
            except Exception:
                pass
                
            origin_input = self.page.locator("input[name='flightQuery.flightJourneys[0].origin'], input[placeholder*='Von'], input[aria-label*='Von']")
            if await origin_input.count() > 0:
                await origin_input.first.click(force=True)
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
                await origin_input.first.type(origin, delay=100)
                await asyncio.sleep(0.5)
                await self.page.keyboard.press("Enter")
            
            dest_input = self.page.locator("input[name='flightQuery.flightJourneys[0].destination'], input[placeholder*='Nach'], input[aria-label*='Nach']")
            if await dest_input.count() > 0:
                await dest_input.first.click(force=True)
                await dest_input.first.type(destination, delay=100)
                await asyncio.sleep(0.5)
                await self.page.keyboard.press("Enter")
                
            date_input = self.page.locator("input[name='flightQuery.flightJourneys[0].outboundDate'], input[placeholder*='Hin'], input[placeholder*='Outbound']")
            if await date_input.count() > 0:
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                date_str = date_obj.strftime("%d.%m.%Y")
                await date_input.first.click(force=True)
                await asyncio.sleep(0.5)
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
                await date_input.first.type(date_str, delay=100)
                await asyncio.sleep(0.5)
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(0.5)
                await self.page.keyboard.press("Escape")
                await asyncio.sleep(0.5)
                
            search_btn = self.page.locator("button[type='submit']:has-text('Suchen'), button:has-text('Flüge suchen'), button:has-text('Search flights')")
            if await search_btn.count() > 0:
                await search_btn.first.click(force=True)
                
            for i in range(15):
                if self._offers_data is not None:
                    break
                await asyncio.sleep(1.0)
                
            final_url = self.page.url
            metadata["final_url_redacted"] = final_url.split("?")[0] if "?" in final_url else final_url
                
            if not self._offers_data:
                return ProviderResult(flights=[], status=FlightScheduleStatus.UNVERIFIED_RESPONSE, metadata=metadata)
                
            flights = self._parse_passive_json(self._offers_data, origin, destination, date, direct_only)
            
            if not flights:
                return ProviderResult(flights=[], status=FlightScheduleStatus.NO_SCHEDULE_FOUND, metadata=metadata)
                
            verified, reason = self._verify_flights(flights, origin, destination, date)
            metadata["parameters_verified"] = verified
            
            routes = set(f"{f.origin}-{f.destination}" for f in flights)
            dates = set(f.departure_time for f in flights)
            metadata["response_routes"] = list(routes)
            metadata["response_dates"] = list(dates)
            
            if not verified:
                return ProviderResult(flights=[], status=FlightScheduleStatus.PARAMETER_MISMATCH, message=reason, metadata=metadata)
                
            return ProviderResult(flights=flights, status=FlightScheduleStatus.SUCCESS, metadata=metadata)
            
        except PWTimeoutError:
            return ProviderResult(flights=[], status=FlightScheduleStatus.TIMEOUT, metadata=metadata)
        except Exception as e:
            return ProviderResult(flights=[], status=FlightScheduleStatus.PARSE_FAILED, message=str(e), metadata=metadata)

    def _verify_flights(self, flights: List[Flight], expected_origin: str, expected_dest: str, expected_date: str) -> Tuple[bool, str]:
        if not flights:
            return False, "No flights to verify"
            
        # The user wants at least ONE exactly matching flight to give `success`.
        # Since _parse_passive_json filters by origin, destination, and expected_date,
        # anything left in `flights` is technically already verified!
        # But let's double check them just in case.
        valid_flights = []
        for f in flights:
            if f.origin == expected_origin and f.destination == expected_dest:
                # Our departure_time currently holds "YYYY-MM-DDTHH:MM" or just "HH:MM".
                # If we updated _parse_passive_json to store the full ISO string, we can do:
                if expected_date in f.departure_time:
                    valid_flights.append(f)
                    
        if len(valid_flights) > 0:
            return True, "Verified"
        return False, "No flights exactly matched the requested parameters"

    def _parse_passive_json(self, data: Optional[Dict], expected_origin: str, expected_dest: str, expected_date: str, direct_only: bool) -> List[Flight]:
        """
        Parses Lufthansa offers/schedule JSON.
        We look for flights inside journey or offer arrays.
        """
        if not data:
            return []
            
        def find_segments(obj):
            found = []
            if isinstance(obj, dict):
                if "segments" in obj and isinstance(obj["segments"], list):
                    found.extend(obj["segments"])
                elif "flightNumber" in obj and "departure" in obj and "arrival" in obj:
                    found.append(obj)
                for k, v in obj.items():
                    found.extend(find_segments(v))
            elif isinstance(obj, list):
                for item in obj:
                    found.extend(find_segments(item))
            return found
            
        segments = find_segments(data)
        result_flights = []
        
        for seg in segments:
            try:
                fn = seg.get("flightNumber", "")
                airline = seg.get("marketingCarrier", {}).get("airlineId", "LH")
                if not fn:
                    fn = str(seg.get("operatingCarrier", {}).get("flightNumber", ""))
                    
                dep = seg.get("departure", {})
                arr = seg.get("arrival", {})
                
                dep_port = dep.get("airport", {}).get("airportCode", "")
                arr_port = arr.get("airport", {}).get("airportCode", "")
                
                dep_time_raw = dep.get("time", {}).get("local", "") or dep.get("localTime", "")
                arr_time_raw = arr.get("time", {}).get("local", "") or arr.get("localTime", "")
                
                # Keep full timestamp for verification
                dep_time = dep_time_raw
                arr_time = arr_time_raw
                
                if not dep_port or not arr_port or not dep_time:
                    continue
                    
                # We do NOT rigidly filter here so that we can accurately log parameter_mismatch
                f = Flight(
                    flight_number=f"{airline}{fn}",
                    airline=airline,
                    origin=dep_port,
                    destination=arr_port,
                    departure_time=dep_time,
                    arrival_time=arr_time,
                    is_direct=True 
                )
                result_flights.append(f)
            except Exception:
                pass
                
        # Clean up flights: keep only the matching ones, but if ALL are mismatch, we keep them to fail verification.
        matching = [f for f in result_flights if f.origin == expected_origin and f.destination == expected_dest and expected_date in f.departure_time]
        
        if matching:
            return matching
        return result_flights
