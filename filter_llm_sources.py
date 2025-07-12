from langchain_openai import ChatOpenAI
from difflib import get_close_matches

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


def extract_top_munros_from_answer(prompt: str, answer: str, sources: list, top_k=3):
    """
    Use the LLM to analyze the user prompt, assistant's answer, and source list to extract the top Munros.
    Allows the LLM to include Munros not in sources, but gracefully falls back to source list if needed.
    """
    source_text = "\n".join(
        f"- {s['name']} — {s['url']}" for s in sources if s.get("name") and s.get("url")
    )

    full_prompt = f"""
You are a Munro hiking assistant helping interpret an AI-generated response and a list of reference Munros.

The user asked:
"{prompt}"

The assistant responded:
\"\"\"{answer}\"\"\"

Here is a list of candidate Munros and their associated links:
{source_text}

Please infer the Munros most relevant to the user's intent — either because they were named, clearly implied, or closely aligned with the user's request.

Return ONLY the top {top_k} Munro names — one per line. 
If you name a Munro that was not in the original list, that’s okay — but try to stay relevant to the user’s question.
"""
    try:
        output = llm.invoke(full_prompt).content
        print("\n[🧠 LLM Output]")
        print(output)

        ranked_names = [
            line.strip("-• ").strip()
            for line in output.strip().splitlines()
            if line.strip()
        ]

        if not ranked_names:
            raise ValueError("LLM returned no Munros")

        # Match ranked names to sources (fuzzy match if possible)
        final = []
        used = set()

        for name in ranked_names:
            # First try exact match
            match = next((s for s in sources if s["name"] == name), None)

            # If not found, try fuzzy
            if not match:
                names = [s["name"] for s in sources]
                close = get_close_matches(name, names, n=1, cutoff=0.8)
                if close:
                    match = next((s for s in sources if s["name"] == close[0]), None)

            if match and match["name"] not in used:
                final.append(match)
                used.add(match["name"])
            else:
                # Include name anyway (no metadata)
                final.append({"name": name, "url": None})

        return final[:top_k]

    except Exception as e:
        print(f"[⚠️ Fallback: using top-{top_k} from sources] — {e}")
        return sources[:top_k]
