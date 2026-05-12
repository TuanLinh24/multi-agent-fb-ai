from app.rag.hybrid_search import search
from app.serving.llm_client import generate
from app.agents.prompts import FAQ_PROMPT

async def handle_faq(query, history):

    contexts = search(query)

    context_text = "\n".join(contexts)

    prompt = f"""
{FAQ_PROMPT}

Context:
{context_text}

Question:
{query}
"""

    return await generate(prompt)