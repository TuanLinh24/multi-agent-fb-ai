from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.router_agent import route_query
from app.rag.retriever import retrieve_faq
from app.serving.llm_client import generate
from app.serving.stream import stream_response
from fastapi.middleware.cors import CORSMiddleware
from app.rag.retriever import retrieve_faq
from app.rag.hybrid_search import hybrid_search

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
async def chat(payload: ChatRequest):

    intent = await route_query(payload.message)

    # FAQ AGENT
    if intent == "faq":

        faq = hybrid_search(payload.message)

        if faq:

            prompt = f"""
Rewrite this answer naturally in Vietnamese.

Answer:
{faq["answer"]}

Keep the meaning exactly the same.
Reply in one short sentence only.
"""

            response = await generate(prompt)

            response = response.replace(
                "Answer:",
                ""
            ).strip()

            response = response.split("\n")[0]

            response = f"{response}"

        else:

            response = "Tôi không tìm thấy thông tin phù hợp."

    # CONSULTANT AGENT
    elif intent == "consultant":

        prompt = f"""
You are a coffee consultant assistant.

Recommend drinks naturally in Vietnamese.

User Question:
{payload.message}

Recommendation:
"""

        response = await generate(prompt)

        response = response.replace(
            "Recommendation:",
            ""
        ).strip()

        response = response.split("\n")[0]

    # ORDER AGENT
    elif intent == "order":

        prompt = f"""
You are an order assistant.

Confirm the customer order politely in Vietnamese.

User Request:
{payload.message}

Order Confirmation:
"""

        response = await generate(prompt)

        response = response.replace(
            "Order Confirmation:",
            ""
        ).strip()

        response = response.split("\n")[0]

    # FALLBACK
    else:

        response = "Xin lỗi, tôi chưa hiểu yêu cầu của bạn."

    return await stream_response(response)