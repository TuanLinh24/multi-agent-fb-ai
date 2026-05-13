import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from app.agents.router_agent import route_query
from app.agents.faq_agent import handle_faq
from app.agents.consultant_agent import handle_consultant
from app.agents.order_agent import handle_order

from app.cache.session_store import (
    add_message,
    get_history
)

from app.serving.stream import stream_text


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

    add_message(
        payload.session_id,
        "user",
        payload.message
    )

    intent = await route_query(payload.message)
    history = get_history(payload.session_id)

    if intent == "faq":
        response = await handle_faq(payload.message, history)
    elif intent == "consultant":
        response = await handle_consultant(payload.message, history)
    elif intent == "order":
        response = await handle_order(payload.message, history)
    else:
        response = (
            "Sorry, I do not "
            "understand your request."
        )

    add_message(
        payload.session_id,
        "assistant",
        response
    )

    print(get_history(payload.session_id))

    return StreamingResponse(
        stream_text(response),
        media_type="text/event-stream"
    )