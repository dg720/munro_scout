from tools.parse_hike_preferences import HikePreferences


def route_based_on_preferences(preferences: HikePreferences) -> str:
    """
    Decides what tool or function to call next based on the parsed hike preferences.
    Returns a string instruction for now, but can later trigger actual tool calls.
    """
    if preferences.station_keywords:
        return f"→ Search for Munros near station(s): {preferences.station_keywords}"

    elif preferences.origin_city and preferences.max_travel_time_minutes:
        return f"→ Find reachable train stations from {preferences.origin_city} within {preferences.max_travel_time_minutes} minutes"

    else:
        return "⚠️ Not enough info — please specify a train station, or a city with max travel time."
