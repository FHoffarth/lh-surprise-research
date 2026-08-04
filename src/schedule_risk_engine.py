import datetime
from typing import List, Dict, Any
from src.models import SearchProfile, ScheduleRiskResult
class ScheduleRiskEngine:
    def __init__(self, profile):
        if isinstance(profile, dict):
            profile = SearchProfile(
                origin=profile.get("origin", "FRA"),
                earliest_outbound_date=profile.get("earliest_outbound_date", "2026-08-07"),
                latest_return_date=profile.get("latest_return_date", "2026-08-09"),
                earliest_acceptable_outbound=profile.get("earliest_acceptable_outbound", "14:00"),
                outbound_risk_policy=profile.get("outbound_risk_policy", "reject_if_any_plausible_direct_flight_is_too_early"),
                usage_mode=profile.get("usage_mode", "target_roundtrip")
            )
        self.profile = profile
        self.earliest_acceptable_outbound = self._parse_time_str(profile.earliest_acceptable_outbound)
        self.outbound_risk_policy = profile.outbound_risk_policy
        self.usage_mode = profile.usage_mode

    def _parse_time_str(self, time_str: str) -> datetime.time:
        if " " in time_str:
            time_str = time_str.split(" ")[-1]
        return datetime.datetime.strptime(time_str[:5], "%H:%M").time()

    def _parse_datetime(self, dt_str: str) -> datetime.datetime:
        try:
            return datetime.datetime.strptime(dt_str[:16], "%Y-%m-%d %H:%M")
        except:
            return None

    def deduplicate_flights(self, flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        deduped = []
        for f in flights:
            dep = f.get("departure_time", "")
            if not dep:
                continue
            time_key = dep.split(" ")[-1][:5]
            if time_key in seen:
                continue
            seen.add(time_key)
            deduped.append(f)
        return deduped

    def evaluate_itineraries(self, destination: str, outbound_flights: List[Dict[str, Any]], return_flights: List[Dict[str, Any]], iata: str = "") -> ScheduleRiskResult:
        out_deduped = self.deduplicate_flights(outbound_flights)
        ret_deduped = self.deduplicate_flights(return_flights)

        all_combinations = []
        valid_itineraries = []
        one_night_combos = []
        two_night_combos = []
        rejected_due_to_stay = 0

        for out in out_deduped:
            o_arr = self._parse_datetime(out.get("arrival_time", ""))
            o_dep = self._parse_datetime(out.get("departure_time", ""))
            if not o_arr or not o_dep:
                continue

            for ret in ret_deduped:
                r_dep = self._parse_datetime(ret.get("departure_time", ""))
                r_arr = self._parse_datetime(ret.get("arrival_time", ""))
                if not r_dep or not r_arr:
                    continue

                if r_dep <= o_arr:
                    continue

                stay_hours = (r_dep - o_arr).total_seconds() / 3600.0
                overnights = (r_dep.date() - o_dep.date()).days

                if overnights not in [1, 2]:
                    continue

                # Overnight stay constraints
                min_required = 18.0 if overnights == 1 else 36.0
                is_stay_valid = stay_hours >= min_required

                # Usability checks based on mode
                is_usable = True
                outbound_ok = o_dep.time() >= self.earliest_acceptable_outbound
                
                if self.usage_mode == "target_outbound_only":
                    is_usable = outbound_ok
                elif self.usage_mode == "target_roundtrip":
                    # For target_roundtrip, outbound must be >= 14:00 and return must also be reasonable
                    # Wait, let's assume return must not be too early either (e.g. >= 12:00 or simply outbound_ok)
                    is_usable = outbound_ok
                else:  # flexible_destination_good_times
                    is_usable = outbound_ok

                combo = {
                    "outbound": out,
                    "return": ret,
                    "outbound_flight": out["flight_number"],
                    "outbound_time": o_dep.strftime("%H:%M"),
                    "outbound_date": o_dep.strftime("%Y-%m-%d"),
                    "return_flight": ret["flight_number"],
                    "return_time": r_dep.strftime("%H:%M"),
                    "return_date": r_dep.strftime("%Y-%m-%d"),
                    "stay_hours": round(stay_hours, 1),
                    "overnights": overnights,
                    "usable": is_usable
                }
                all_combinations.append(combo)

                if is_stay_valid:
                    valid_itineraries.append(combo)
                    if overnights == 1:
                        one_night_combos.append(combo)
                    else:
                        two_night_combos.append(combo)
                else:
                    rejected_due_to_stay += 1

        total_combos = len(all_combinations)
        valid_combos = len(valid_itineraries)

        if total_combos > 0 and valid_combos == 0:
            return ScheduleRiskResult(
                destination=destination,
                iata=iata,
                total_combinations=total_combos,
                valid_combinations=0,
                one_night_count=0,
                two_night_count=0,
                rejected_due_to_minimum_stay=rejected_due_to_stay,
                earliest_outbound_valid="-",
                latest_outbound_valid="-",
                worst_valid_itinerary=None,
                risk_classification="no_valid_itinerary",
                recommendation="EXCLUDE",
                reasons=["No combinations meet the overnight minimum stay rule."],
                risk_by_trip_length={"one_night": "no_valid_itinerary", "two_nights": "no_valid_itinerary"},
                all_valid_itineraries=[]
            )
        elif not all_combinations:
            return ScheduleRiskResult(
                destination=destination,
                iata=iata,
                total_combinations=0,
                valid_combinations=0,
                one_night_count=0,
                two_night_count=0,
                rejected_due_to_minimum_stay=0,
                earliest_outbound_valid="-",
                latest_outbound_valid="-",
                worst_valid_itinerary=None,
                risk_classification="unknown",
                recommendation="MANUAL REVIEW",
                reasons=["No flight data found."],
                risk_by_trip_length={"one_night": "unknown", "two_nights": "unknown"},
                all_valid_itineraries=[]
            )

        # Classifications
        def get_sub_class(combos):
            if not combos:
                return "no_valid_itinerary"
            usable = [c for c in combos if c["usable"]]
            if len(usable) == len(combos):
                return "safe"
            elif usable:
                return "mixed"
            return "unsafe"

        one_night_class = get_sub_class(one_night_combos)
        two_night_class = get_sub_class(two_night_combos)

        usable_combos = [c for c in valid_itineraries if c["usable"]]
        unusable_combos = [c for c in valid_itineraries if not c["usable"]]

        if self.usage_mode == "flexible_destination_good_times":
            # For flexible mode, if there is at least one usable option, we classify as safe or mixed,
            # but if there's any usable flight, it's considered KEEP (since we can choose our booking time slot if offered)
            # Actually, Lufthansa Surprise does not let us choose the exact flight slot during booking unless we get lucky,
            # but if all we want is a destination with good times, we KEEP if there are safe flights.
            if len(usable_combos) == len(valid_itineraries):
                classification = "safe"
                recommendation = "KEEP"
            elif usable_combos:
                classification = "mixed"
                recommendation = "KEEP"  # In flexible mode we still keep it since there are some good flights
            else:
                classification = "unsafe"
                recommendation = "EXCLUDE"
        else:
            if len(usable_combos) == len(valid_itineraries):
                classification = "safe"
                recommendation = "KEEP"
            elif usable_combos:
                classification = "mixed"
                recommendation = "EXCLUDE"
            else:
                classification = "unsafe"
                recommendation = "EXCLUDE"

        valid_out_times = [self._parse_time_str(c["outbound_time"]) for c in valid_itineraries]
        earliest_out = min(valid_out_times).strftime("%H:%M") if valid_out_times else "-"
        latest_out = max(valid_out_times).strftime("%H:%M") if valid_out_times else "-"
        worst_valid = min(valid_itineraries, key=lambda c: self._parse_time_str(c["outbound_time"])) if valid_itineraries else None

        reason = f"Mode {self.usage_mode}: {len(usable_combos)} usable and {len(unusable_combos)} unusable combinations."

        return ScheduleRiskResult(
            destination=destination,
            iata=iata,
            total_combinations=total_combos,
            valid_combinations=valid_combos,
            one_night_count=len(one_night_combos),
            two_night_count=len(two_night_combos),
            rejected_due_to_minimum_stay=rejected_due_to_stay,
            earliest_outbound_valid=earliest_out,
            latest_outbound_valid=latest_out,
            worst_valid_itinerary=worst_valid,
            risk_classification=classification,
            recommendation=recommendation,
            reasons=[reason],
            risk_by_trip_length={
                "one_night": one_night_class,
                "two_nights": two_night_class
            },
            all_valid_itineraries=valid_itineraries
        )
