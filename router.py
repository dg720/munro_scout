from tools.parse_hike_preferences import HikePreferences
from tools.transport import station_lookup


def route_based_on_preferences(preferences: HikePreferences) -> str:
    """
    Decides what tool or function to call next based on the parsed hike preferences.
    Returns a string instruction for now, but can later trigger actual tool calls.
    """
    if preferences.station_keywords:
        results = []
        for keyword in preferences.station_keywords:
            station_result = station_lookup.invoke({"location_name": keyword})
            results.append(station_result)
        return {"action": "station_lookup", "results": results}

    elif preferences.origin_city and preferences.max_travel_time_minutes:
        return f"→ Find reachable train stations from {preferences.origin_city} within {preferences.max_travel_time_minutes} minutes"

    else:
        return "⚠️ Not enough info — please specify a train station, or a city with max travel time."
