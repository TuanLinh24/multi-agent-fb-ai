from app.serving.llm_client import generate
from app.agents.prompts import ORDER_PROMPT

async def handle_order(query, history):
    prompt = f"""
{ORDER_PROMPT}

User:
{query}
"""
    return await generate(prompt)