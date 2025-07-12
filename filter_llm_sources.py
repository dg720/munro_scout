from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


def extract_top_munros_from_answer(prompt: str, answer: str, sources: list, top_k=3):
    """
    Use the LLM to analyze answer + source list and select the top K most relevant Munros.
    Returns a filtered list of sources with 'name' and 'url'.
    """
    source_text = "\n".join(
        f"- {s['name']} — {s['url']}" for s in sources if s.get("name") and s.get("url")
    )

    full_prompt = f"""
You are a Munro hiking assistant.

The user asked:
"{prompt}"

The assistant responded:
\"\"\"{answer}\"\"\"

Here are the candidate Munros and their links:
{source_text}

Please choose the top {top_k} Munros mentioned or implied by the answer that best match the user's intent.
Return a list with just the Munro names from the options above.
"""

    output = llm.invoke(full_prompt).content

    # Match names from LLM output with source list (fuzzy match or exact)
    ranked_names = [
        line.strip("-• ").strip()
        for line in output.strip().splitlines()
        if line.strip()
    ]
    filtered_sources = [s for s in sources if s["name"] in ranked_names]

    return filtered_sources[:top_k]
