from agent import parse_hike_preferences
from router import route_based_on_preferences
from tools.generation import generate_munro_summary
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = input("Enter your hiking query: ")

    try:
        # Step 1: Parse the user's input into structured fields
        result = parse_hike_preferences.invoke({"user_prompt": user_prompt})
        print("\n[✅ Parsed Hike Preferences]")
        print(result.model_dump_json(indent=2))

        # Step 2: Route based on those preferences
        print("\n[🚦 Routing Decision]")
        routing_decision = route_based_on_preferences(result)

        action = routing_decision.get("action")
        results = routing_decision.get("results", [])

        if action == "munros_near_station":
            print("\n[📍 Top 3 Closest Munros per Station]")

            for station in results:
                print(f"\n🚉 {station['station_name']}")
                for m in station["top_munros"]:
                    print(f"  - {m['raw']}")

            # Step 3: Generate LLM-powered route summary
            print("\n[📝 Generating Summary]")
            summary = generate_munro_summary.invoke({"recommendations": results})
            print("\n[📖 Suggested Routes Summary]")
            print(summary)

        elif action == "stations_then_munros":
            print("\n[ℹ️ Station lookup required]")
            for item in results:
                print("-", item)

        elif action == "insufficient_input":
            print("\n[⚠️ Not enough information to generate suggestions]")
            print(routing_decision.get("message"))

        else:
            print("\n[⚠️ Unexpected routing action]")
            print(routing_decision)

    except Exception as e:
        print("\n[❌ Failed to extract hike preferences]")
        print(str(e))
