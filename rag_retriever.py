import os
import re
from typing import List, Dict
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from munro_rag.retriever import get_retriever
from tools.parse_hike_preferences import HikePreferences


def answer_hiking_query(query: str) -> dict:
    """
    Answers a natural language question about Munros using RAG (Retriever-Augmented Generation).
    """
    retriever = get_retriever()
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
    )

    result = qa_chain(query)
    return {
        "answer": result["result"],
        "sources": [
            {"name": doc.metadata.get("name"), "url": doc.metadata.get("url")}
            for doc in result["source_documents"]
        ],
    }


def rank_munros_by_preferences(
    preferences: HikePreferences, munros: List[Dict]
) -> List[Dict]:
    """
    Uses RAG to semantically rank a list of Munro dictionaries against the user preferences.
    Returns a sorted list of top Munros by preference relevance.
    """
    if not munros:
        return []

    munro_names = [m["name"] for m in munros]
    prompt = f"""
You are a mountain guide. The user has asked for Munro recommendations based on these preferences:

- Max time: {preferences.max_time_hours or "any"} hours
- Max distance: {preferences.max_distance_km or "any"} km
- Max grade: {preferences.grade or "any"}
- Bog tolerance: {preferences.bog_tolerance or "any"}
- Desired features: {preferences.features or "unspecified"}

Please review the following list of Munros and return a list of up to 5 that best match these preferences, ordered from best to worst:

{", ".join(munro_names)}

Return the list using one Munro per line.
"""

    rag_result = answer_hiking_query(prompt)
    ranked_names = extract_ranked_names(rag_result["answer"], munros)

    # Reorder based on LLM ranking
    return [
        m for name in ranked_names for m in munros if m["name"].lower() == name.lower()
    ]


def extract_ranked_names(raw_answer: str, munros: List[Dict]) -> List[str]:
    """
    Extracts a ranked list of Munro names from the LLM's raw answer text.
    Uses fuzzy matching to match them against the known Munro list.
    """
    # Lowercase name set for fuzzy matching
    known_names = {m["name"].lower(): m["name"] for m in munros}
    matched = []

    lines = raw_answer.splitlines()
    for line in lines:
        # Remove bullet or number
        clean = re.sub(r"^[\-\d\.\)\s]+", "", line).strip().lower()
        for key in known_names:
            if key in clean and known_names[key] not in matched:
                matched.append(known_names[key])
                break

    return matched
