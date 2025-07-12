from tools.parse_hike_preferences import HikePreferences
from tools.munros import get_munros_near_station
from rag_retriever import rank_munros_by_preferences


def route_based_on_preferences(preferences: HikePreferences, user_prompt: str) -> dict:
    """
    Decides what tool or function to call next based on the parsed hike preferences.
    Handles:
    - Munros near stations only
    - Station + preferences (uses RAG to rank)
    - Origin city + travel time
    - Freeform / fallback queries
    """

    # ✅ Case 1: Station(s) + preferences => fetch nearby Munros, then rerank
    if preferences.station_keywords and any(
        [
            preferences.max_time_hours,
            preferences.max_distance_km,
            preferences.grade,
            preferences.bog_tolerance,
            preferences.features,
            preferences.soft_preferences,
        ]
    ):
        reranked_results = []

        for keyword in preferences.station_keywords:
            raw_text = get_munros_near_station.invoke({"station_name": keyword})

            munro_lines = raw_text.split("\n")[1:] if "\n" in raw_text else []
            munro_entries = []

            for line in munro_lines:
                if not line.strip():
                    continue
                try:
                    name_part = line.split(" (")[0].strip()
                    distance_km = float(line.split(" (")[1].replace(" km)", ""))
                    munro_entries.append(
                        {"name": name_part, "distance_km": distance_km, "raw": line}
                    )
                except (IndexError, ValueError):
                    continue

            # Limit to top 15 closest for reranking
            candidates = sorted(munro_entries, key=lambda x: x["distance_km"])[:15]

            # ✅ Debug print
            print(f"\n[🔍 Nearby Munros near '{keyword}' (before reranking)]")
            for m in candidates:
                print(f"  - {m['name']} ({m['distance_km']} km)")

            # Rerank based on structured + soft preferences
            reranked = rank_munros_by_preferences(preferences, candidates)[:3]

            # ✅ Debug: Show ranked results
            print(f"\n[🏅 Top-ranked Munros near '{keyword}']")
            for m in reranked:
                print(f"  - {m['name']} ({m['distance_km']} km)")

            reranked_results.append({"station_name": keyword, "top_munros": reranked})

        return {"action": "munros_reranked_by_preferences", "results": reranked_results}

    # ✅ Case 2: Station(s) only, no preferences
    elif preferences.station_keywords:
        station_results = []

        for keyword in preferences.station_keywords:
            raw_text = get_munros_near_station.invoke({"station_name": keyword})
            munro_lines = raw_text.split("\n")[1:] if "\n" in raw_text else []

            munro_entries = []
            for line in munro_lines:
                if not line.strip():
                    continue
                try:
                    name_part = line.split(" (")[0].strip()
                    distance_km = float(line.split(" (")[1].replace(" km)", ""))
                    munro_entries.append(
                        {"name": name_part, "distance_km": distance_km, "raw": line}
                    )
                except (IndexError, ValueError):
                    continue

            top_munros = sorted(munro_entries, key=lambda x: x["distance_km"])[:3]

            # ✅ Debug print
            print(f"\n[📍 Closest Munros near '{keyword}']")
            for m in top_munros:
                print(f"  - {m['name']} ({m['distance_km']} km)")

            station_results.append({"station_name": keyword, "top_munros": top_munros})

        return {"action": "munros_near_station", "results": station_results}

    # ✅ Case 3: Origin city + travel time (no station)
    elif preferences.origin_city and preferences.max_travel_time_minutes:
        return {
            "action": "stations_then_munros",
            "results": [
                f"→ Find reachable train stations from {preferences.origin_city} within {preferences.max_travel_time_minutes} minutes"
            ],
        }

    # ✅ Case 4: Freeform fallback
    elif user_prompt and len(user_prompt.split()) > 4:
        return {"action": "freeform_query", "query": user_prompt}

    # ❌ Fallback
    return {
        "action": "insufficient_input",
        "message": "⚠️ Please specify a train station, origin city with travel time, or ask a question about Munros.",
    }
