from app.serving.llm_client import generate
from app.agents.prompts import ROUTER_PROMPT
from app.utils.json_parser import parse_router_output

async def route_query(query: str):

    prompt = f"""
{ROUTER_PROMPT}

User:
{query}
"""

    output = await generate(prompt, 20)

    result = parse_router_output(output)

    return result["action"]