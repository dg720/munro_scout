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


# Prompt template
prompt_template = PromptTemplate.from_template("""
Extract the following details from the user prompt:
- Origin city
- Max travel time in minutes
- Named or implied train station(s)
- Preferences like scenery, difficulty, solitude — label these as "soft_preferences"

Return a JSON object with keys:
origin_city, max_travel_time_minutes, station_keywords, soft_preferences

soft_preferences must be a list of strings

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
