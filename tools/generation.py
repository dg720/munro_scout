from langchain.tools import tool
from langchain_openai import ChatOpenAI
import os  # TEST

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)


@tool
def generate_munro_summary(recommendations: list) -> str:
    """
    Given a list of Munro recommendations (with metadata), generate a structured and friendly route summary.
    """

    # Build structured text block for the LLM
    route_text = ""
    for item in recommendations:
        station = item["station_name"]
        for munro in item["top_munros"]:
            name = munro.get("name", "Unknown Munro")
            distance = munro.get("distance_km", "N/A")
            terrain = munro.get("terrain", "N/A")
            transport = munro.get("public_transport", "N/A")
            gpx = munro.get("gpx_file", "N/A")

            route_text += (
                f"\n---\n"
                f"Name: {name}\n"
                f"Distance from Station: {distance} km from {station}\n"
                f"Transport Info: {transport}\n"
                f"Terrain: {terrain}\n"
                f"GPX File: {gpx}\n"
            )

    prompt = f"""
You are an experienced Scottish hiking guide helping a user choose from several Munro hikes near train stations.

Below is a list of options, each with metadata:

{route_text}

For each Munro, return a structured recommendation in this format:

---
🏔️ Name: [Munro Name]  
📍 Distance from Station: X km from [Station]  
🚆 Transport Info: [Info on public transport or access]  
🌄 Terrain: [Brief description]  
📎 GPX File: [file path or link]  
📝 Route Summary: [Describe the route in clear, friendly terms. Mention type of terrain, difficulty, highlights, views, and anything to prepare for.]

Make the summaries helpful, informative, and welcoming for someone planning a hike.
"""

    return llm.invoke(prompt).content
