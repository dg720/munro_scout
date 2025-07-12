from agent import parse_hike_preferences
from router import route_based_on_preferences
from tools.generation import generate_munro_summary
from rag_retriever import answer_hiking_query
from filter_llm_sources import extract_top_munros_from_answer
import sys
import json

# Load all Munros into memory for enrichment
with open("munro_descriptions.json") as f:
    all_munros = json.load(f)


def enrich_munro_metadata(selected: list, all_munros: list) -> list:
    """
    Given a list of top Munros (with just names), match them to the full database and enrich with metadata.
    """
    name_map = {m["name"].lower(): m for m in all_munros}
    enriched = []

    for m in selected:
        match = name_map.get(m["name"].lower())
        if match:
            enriched.append(
                {
                    "name": match["name"],
                    "distance_km": m.get("distance_km", 0.0),
                    "terrain": match.get("terrain", "N/A"),
                    "public_transport": match.get("public_transport", "N/A"),
                    "gpx_file": match.get("gpx_file", "N/A"),
                    "raw": match["name"],
                }
            )

    return enriched


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = input("Enter your hiking query: ")

    try:
        # Step 1: Parse user input into structured preferences
        result = parse_hike_preferences.invoke({"user_prompt": user_prompt})
        print("\n[✅ Parsed Hike Preferences]")
        print(result.model_dump_json(indent=2))

        # Step 2: Route based on preferences + original prompt
        print("\n[🚦 Routing Decision]")
        routing_decision = route_based_on_preferences(result, user_prompt)

        action = routing_decision.get("action")
        results = routing_decision.get("results", [])

        if action == "munros_near_station":
            print("\n[📍 Top 3 Closest Munros per Station]")
            for station in results:
                print(f"\n🚉 {station['station_name']}")
                for m in station["top_munros"]:
                    print(f"  - {m['raw']}")

            print("\n[📝 Generating Summary]")
            summary = generate_munro_summary.invoke({"recommendations": results})
            print("\n[📖 Suggested Routes Summary]")
            print(summary)

        elif action == "munros_reranked_by_preferences":
            print("\n[📊 Reranked Munros Based on Your Preferences]")
            for station in results:
                print(f"\n🚉 {station['station_name']}")
                for m in station["top_munros"]:
                    print(f"  - {m['raw']}")

            print("\n[📝 Generating Summary]")
            summary = generate_munro_summary.invoke({"recommendations": results})
            print("\n[📖 Suggested Routes Summary]")
            print(summary)

        elif action == "stations_then_munros":
            print("\n[ℹ️ Station lookup required]")
            for item in results:
                print("-", item)

        elif action == "freeform_query":
            print("\n[🧠 Freeform Munro Question Detected]")
            print(f"Query: {routing_decision['query']}")

            response = answer_hiking_query(routing_decision["query"])

            print("\n[🧭 Answer]")
            print(response["answer"])

            print("\n📚 Sources:")
            for src in response["sources"]:
                print(f"- {src['name']} — {src['url']}")

            # Step 1: Pick the top 3 relevant Munros using the LLM
            top_munros = extract_top_munros_from_answer(
                prompt=routing_decision["query"],
                answer=response["answer"],
                sources=response["sources"],
                top_k=3,
            )

            # Step 2: Enrich with full metadata
            enriched_munros = enrich_munro_metadata(top_munros, all_munros)

            recommendation_block = [
                {
                    "station_name": "Not specified",
                    "top_munros": enriched_munros,
                }
            ]

            print("\n[📝 Generating Summary]")
            summary = generate_munro_summary.invoke(
                {"recommendations": recommendation_block}
            )

            print("\n[📖 Suggested Routes Summary]")
            print(summary)

        elif action == "insufficient_input":
            print("\n[⚠️ Not enough information to generate suggestions]")
            print(routing_decision.get("message"))

        else:
            print("\n[⚠️ Unexpected routing action]")
            print(routing_decision)

    except Exception as e:
        print("\n[❌ Failed to extract hike preferences]")
        print(str(e))
