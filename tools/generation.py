from langchain.tools import tool
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)


@tool
def generate_munro_summary(recommendations: list) -> str:
    """
    Given a list of Munro recommendations (with metadata), generate a friendly route summary for the user.
    """

    # Create a text block the LLM can work with
    route_text = ""
    for item in recommendations:
        station = item["station_name"]
        for munro in item["top_munros"]:
            route_text += f"\n- {munro['name']} (approx. {munro['distance_km']} km from {station})"

    prompt = f"""
You are an experienced Scottish hiking guide. A user is looking for suitable Munro hikes near train stations.
Here are the current best options based on proximity:

{route_text}

For each Munro, provide a short description of what the route might be like, how to get there from the station, and what kind of experience to expect.
Keep it clear, detailed, and welcoming. Mention terrain, distance from the station, and any notable features if known.
"""

    return llm.invoke(prompt).content
