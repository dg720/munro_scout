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
    station_keywords: Optional[List[str]]
    soft_preferences: Optional[
        List[str]
    ]  # For semantic similarity e.g. "scenic", "quiet", "challenging"


prompt_template = PromptTemplate.from_template("""
Extract the following details from the user prompt:

- origin_city: The city the user wants to depart from (e.g. "Edinburgh", "Glasgow").
- max_travel_time_minutes: The maximum travel time by train or bus, in minutes. If only hours are given, convert to minutes (e.g. "2 hours" → 120).
- station_keywords: A list of **specific named train stations** only (e.g. "Corrour", "Bridge of Orchy"). 
  ❌ Do not include generic phrases like "train station", "nearby station", or "stations".
  ✅ Only include exact place names that correspond to real train stations.

- soft_preferences: A list of subjective or environmental hiking requirements mentioned in the prompt. These may include:

  ◦ **Terrain** - "scrambling", "ridge walking", "flat", "well-marked","exposed"
  ◦ **Scenery** - "scenic", "remote", "forest", "coastal", "lochside"
  ◦ **Weather** - "suitable for poor weather", "sheltered", "winter-friendly"
  ◦ **Suitability** - "dog-friendly", "child-friendly", "accessible by public transport", "quiet"
  ◦ **Intensity** - "challenging", "relaxing", "beginner-friendly", "multi-day"

Only include soft_preferences that are **explicitly or implicitly mentioned** in the prompt — do not default to generic terms unless the user clearly suggests them.

Return only a **valid JSON object** with the following keys:
- origin_city (string or null)
- max_travel_time_minutes (integer or null)
- station_keywords (list of strings)
- soft_preferences (list of strings)

Ensure:
- All values are properly typed
- JSON is strictly formatted and parsable

User prompt: {user_prompt}
""")


llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)

# Replace deprecated LLMChain with new RunnableSequence
chain = prompt_template | llm


@tool
def parse_hike_preferences(user_prompt: str) -> HikePreferences:
    """
    Parses a user's natural language hiking query to extract structured hike preferences.
    """
    response = chain.invoke({"user_prompt": user_prompt})
    content = response.content  # Extract JSON string from AIMessage

    try:
        parsed = HikePreferences.parse_raw(content)
        return parsed
    except Exception as e:
        raise ValueError(
            f"Failed to parse hike preferences: {e}\nLLM response content:\n{content}"
        )
