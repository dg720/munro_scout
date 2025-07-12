from tools.parse_hike_preferences import HikePreferences
from tools.munros import get_munros_near_station
from rag_retriever import rank_munros_by_preferences  # You’ll define this


def route_based_on_preferences(preferences: HikePreferences, user_prompt: str) -> dict:
    """
    Decides what tool or function to call next based on the parsed hike preferences.
    Handles:
    - Munros near stations only
    - Station + preferences (uses RAG to rank)
    - Origin city + travel time
    - Freeform / fallback queries
    """

    # 🧠 Case 1 — Station + preferences => RAG reranking
    if preferences.station_keywords and any(
        [
            preferences.max_time_hours,
            preferences.max_distance_km,
            preferences.grade,
            preferences.bog_tolerance,
            preferences.features,
        ]
    ):
        reranked_results = []

        for keyword in preferences.station_keywords:
            raw_text = get_munros_near_station.invoke({"station_name": keyword})

            if "\n" in raw_text:
                munro_lines = raw_text.split("\n")[1:]  # skip header
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
                    continue
                munro_entries.append(
                    {"name": name_part, "distance_km": distance_km, "raw": line}
                )

            top_15 = sorted(munro_entries, key=lambda x: x["distance_km"])[:15]
            reranked = rank_munros_by_preferences(preferences, top_15)[:3]

            reranked_results.append({"station_name": keyword, "top_munros": reranked})

        return {"action": "munros_reranked_by_preferences", "results": reranked_results}

    # 🚉 Case 2 — Only station(s), no preferences
    elif preferences.station_keywords:
        station_results = []

        for keyword in preferences.station_keywords:
            munro_text = get_munros_near_station.invoke({"station_name": keyword})

            if "\n" in munro_text:
                munro_lines = munro_text.split("\n")[1:]
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
                    continue

                munro_entries.append(
                    {"name": name_part, "distance_km": distance_km, "raw": line}
                )

            top_munros = sorted(munro_entries, key=lambda x: x["distance_km"])[:3]
            station_results.append({"station_name": keyword, "top_munros": top_munros})

        return {"action": "munros_near_station", "results": station_results}

    # 🧭 Case 3 — Origin city + travel time, but no station
    elif preferences.origin_city and preferences.max_travel_time_minutes:
        return {
            "action": "stations_then_munros",
            "results": [
                f"→ Find reachable train stations from {preferences.origin_city} within {preferences.max_travel_time_minutes} minutes"
            ],
        }

    # 🤖 Case 4 — Minimal structured input: fallback to RAG-based freeform
    elif user_prompt and len(user_prompt.split()) > 4:
        return {"action": "freeform_query", "query": user_prompt}

    # ❌ Case 5 — Insufficient input
    return {
        "action": "insufficient_input",
        "message": "⚠️ Please specify a train station, origin city with travel time, or ask a question about Munros.",
    }
