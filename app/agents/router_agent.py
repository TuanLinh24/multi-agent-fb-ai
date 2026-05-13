from app.agents.router_inference import classify


async def route_query(text: str):
    result = await classify(text)
    return result["action"]
