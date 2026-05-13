from app.agents.router_agent import route_query


class AgentManager:

    async def process(self, text):

        intent = await route_query(text)

        return {
            "intent": intent
        }