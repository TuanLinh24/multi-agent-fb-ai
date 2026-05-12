from app.serving.llm_client import generate
from app.agents.prompts import CONSULTANT_PROMPT

async def handle_consultant(query, history):

    prompt = f"""
{CONSULTANT_PROMPT}

User:
{query}
"""

    return await generate(prompt)