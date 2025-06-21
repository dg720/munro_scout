from tools.parse_hike_preferences import HikePreferences
from tools.munros import get_munros_near_station


def route_based_on_preferences(preferences: HikePreferences) -> dict:
    """
    Decides what tool or function to call next based on the parsed hike preferences.
    Returns the 3 closest Munros to each station (by distance).
    """
    if preferences.station_keywords:
        station_results = []

        for keyword in preferences.station_keywords:
            munro_text = get_munros_near_station.invoke({"station_name": keyword})

            if "\n" in munro_text:
                munro_lines = munro_text.split("\n")[1:]  # skip header
            else:
                munro_lines = []

            munro_entries = []

            for line in munro_lines:
                if not line.strip():
                    continue

                try:
                    name_part = line.split(" (")[0].strip()
                    distance_km = float(line.split(" (")[1].replace(" km)", ""))
                except (IndexError, ValueError):
                    continue  # malformed entry

                munro_entries.append(
                    {"name": name_part, "distance_km": distance_km, "raw": line}
                )

            # Sort by distance ascending and return top 3
            top_munros = sorted(munro_entries, key=lambda x: x["distance_km"])[:3]

            station_results.append({"station_name": keyword, "top_munros": top_munros})

        return {"action": "munros_near_station", "results": station_results}

    elif preferences.origin_city and preferences.max_travel_time_minutes:
        return {
            "action": "stations_then_munros",
            "results": [
                f"→ Find reachable train stations from {preferences.origin_city} within {preferences.max_travel_time_minutes} minutes"
            ],
        }

    else:
        return {
            "action": "insufficient_input",
            "message": "⚠️ Please specify a train station, or a city with travel time.",
        }
