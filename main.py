from agent import parse_hike_preferences
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = input("Enter your hiking query: ")

    try:
        result = parse_hike_preferences.invoke({"user_prompt": user_prompt})
        print("\n[✅ Parsed Hike Preferences]")
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print("\n[❌ Failed to extract hike preferences]")
        print(str(e))

# Please suggest potential hikes 2 hours from Edinburgh by train which involve scrambling on quiet ridges
