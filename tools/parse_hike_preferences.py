from pydantic import BaseModel
from langchain_core.tools import tool
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()


# Define structured output model
class HikePreferences(BaseModel):
    origin_city: Optional[str]
    max_travel_time_minutes: Optional[int]
    max_time_hours: Optional[int]
    max_distance_km: Optional[float]
    grade: Optional[int]
    bog_tolerance: Optional[int]
    features: Optional[List[str]]
    station_keywords: Optional[List[str]]
    soft_preferences: Optional[List[str]]


prompt_template = PromptTemplate.from_template("""
Extract the following details from the user's hiking prompt:

- origin_city: The city they want to depart from (e.g. "Edinburgh", "Glasgow").
- max_travel_time_minutes: Max travel time by public transport, in minutes. Convert hours if needed.
- max_time_hours: Maximum desired hiking time (e.g. "under 5 hours").
- max_distance_km: Maximum desired hiking distance in kilometers (e.g. "under 15km").
- grade: Difficulty on a scale from 1 (easy) to 5 (very hard), if implied by terms like "steep", "technical", "challenging", etc.
- bog_tolerance: 1 (low) to 5 (high) based on how tolerant they are of boggy/muddy conditions. Estimate from phrasing.
- features: List any route characteristics explicitly mentioned like "ridge", "loop", "summit", "scrambling", "views", etc.
- station_keywords: Specific named train stations (e.g. "Corrour", "Fort William"). Do NOT include generic terms like "station".
- soft_preferences: Subjective or environmental hiking needs (e.g. "scenic", "dog-friendly", "quiet", "challenging").

Return a valid JSON object with keys:
- origin_city (string or null)
- max_travel_time_minutes (int or null)
- max_time_hours (int or null)
- max_distance_km (float or null)
- grade (int or null)
- bog_tolerance (int or null)
- features (list of strings or null)
- station_keywords (list of strings)
- soft_preferences (list of strings)

User prompt: {user_prompt}
""")


llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

chain = prompt_template | llm


@tool
def parse_hike_preferences(user_prompt: str) -> HikePreferences:
    """
    Parses a user's natural language hiking query to extract structured hike preferences.
    """
    response = chain.invoke({"user_prompt": user_prompt})
    content = response.content

    try:
        parsed = HikePreferences.parse_raw(content)
        return parsed
    except Exception as e:
        raise ValueError(
            f"Failed to parse hike preferences: {e}\nLLM response content:\n{content}"
        )
