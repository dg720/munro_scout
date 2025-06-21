from langchain.tools import tool
from typing import List
import requests
from bs4 import BeautifulSoup
import time
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@tool
def score_munro_relevance(munro_name: str, soft_preferences: List[str]) -> float:
    """
    Searches online for route descriptions about the Munro,
    and scores how well it aligns with the user's soft preferences (e.g. 'quiet', 'scrambling', 'scenic').
    Returns a semantic similarity score from 0.0 to 1.0.
    """

    # Step 1: Build query
    query = f"{munro_name} route description site:walkhighlands.co.uk"

    # Step 2: Perform search (basic scraping)
    search_url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [
            a["href"]
            for a in soup.select("a")
            if "walkhighlands.co.uk" in a.get("href", "")
        ]

        # Pick first result
        target_url = links[0].split("&")[0].replace("/url?q=", "")
        print(f"[🔗] Found route: {target_url}")

        time.sleep(1)  # polite delay
        route_res = requests.get(target_url, headers=headers)
        route_soup = BeautifulSoup(route_res.text, "html.parser")

        # Step 3: Extract text
        paragraphs = route_soup.find_all("p")
        route_description = " ".join(
            p.get_text() for p in paragraphs[:10]
        )  # top few paragraphs

        if not route_description.strip():
            return 0.0

        # Step 4: Send to OpenAI for scoring
        prompt = f"""
User is looking for a Munro route that matches these preferences: {", ".join(soft_preferences)}.
Based on the following route description, how well does this match? Respond with a single number between 0.0 (not at all) and 1.0 (very well).

Route Description:
\"\"\"
{route_description}
\"\"\"
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )

        score_text = response.choices[0].message.content.strip()

        try:
            score = float(score_text)
            return min(max(score, 0.0), 1.0)
        except ValueError:
            return 0.0

    except Exception as e:
        print(f"[⚠️] Error scoring {munro_name}: {e}")
        return 0.0
