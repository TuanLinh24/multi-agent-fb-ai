from app.rag.hybrid_search import hybrid_search
from app.serving.llm_client import generate
from app.agents.prompts import FAQ_PROMPT

async def handle_faq(query, history):
    best_doc = await hybrid_search(query)
    context_text = ""

    if best_doc:
        if isinstance(best_doc, dict):
            parts = []
            if best_doc.get("question"):
                parts.append(best_doc["question"])
            if best_doc.get("answer"):
                parts.append(best_doc["answer"])
            context_text = "\n".join(parts)
        else:
            context_text = str(best_doc)

    prompt = f"""
{FAQ_PROMPT}

Context:
{context_text}

Question:
{query}
"""

    return await generate(prompt)