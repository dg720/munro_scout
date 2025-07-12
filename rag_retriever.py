import os
import re
import unicodedata
from typing import List, Dict
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from munro_rag.retriever import get_retriever
from tools.parse_hike_preferences import HikePreferences

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


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


def rank_munros_by_preferences(preferences: HikePreferences, munros: list) -> list:
    """
    Uses the LLM to semantically rank a provided list of Munros based on the user's preferences.
    """
    if not munros:
        return []

    # Clean any leading symbols from names at the source
    for m in munros:
        m["name"] = m["name"].lstrip("-• ").strip()

    munro_names = [m["name"] for m in munros]

    preference_block = f"""
The user is looking for a Munro hike with the following preferences:

🕒 Max time: {preferences.max_time_hours or "any"} hours  
📏 Max distance: {preferences.max_distance_km or "any"} km  
🎯 Grade (difficulty 1–5): {preferences.grade or "any"}  
💧 Bog tolerance (1 = hates bog, 5 = doesn't mind): {preferences.bog_tolerance or "any"}  
🔍 Features of interest: {", ".join(preferences.features or []) or "none specified"}  
✨ Other preferences (subjective): {", ".join(preferences.soft_preferences or []) or "none specified"}
"""

    munro_list = "\n".join([f"- {name}" for name in munro_names])

    prompt = f"""
You are a Scottish hiking guide.

{preference_block}

Below is a list of Munros near a specific train station:

{munro_list}

Please carefully consider the user's preferences and rank the top 3–5 Munros from this list that best match them.

🚫 Do NOT suggest any Munros that are not in the list.  
✅ Only use the options provided.

Return only the Munro names, one per line.
"""

    result = llm.invoke(prompt).content
    ranked_names = [
        line.strip("-• ").strip()
        for line in result.strip().splitlines()
        if line.strip()
    ]

    print("\n[🔎 LLM Ranked Names]")
    print(ranked_names)

    print("\n[📋 Candidate Munros]")
    for m in munros:
        print(f"  - {m['name']}")

    return match_ranked_munros(ranked_names, munros)


def normalize_name(name: str) -> str:
    """
    Normalize a string to ASCII, lowercase, and remove apostrophes and accents.
    """
    return (
        unicodedata.normalize("NFKD", name)
        .encode("ascii", "ignore")
        .decode("utf-8")
        .lower()
        .replace("’", "'")
        .strip()
    )


def match_ranked_munros(ranked_names: list, munros: list) -> list:
    """
    Match LLM-ranked names back to full munro objects with robust matching.
    """
    matches = []
    for ranked in ranked_names:
        norm_ranked = normalize_name(ranked)
        for m in munros:
            if normalize_name(m["name"]) == norm_ranked:
                matches.append(m)
                break
    return matches
