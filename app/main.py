from fastapi import FastAPI
from app.agents.router_agent import route_query
from app.agents.order_agent import handle_order
from app.agents.consultant_agent import handle_consultant
from app.agents.faq_agent import handle_faq
from app.cache.session_store import SessionStore

app = FastAPI()

session_store = SessionStore()

@app.get("/")
def root():
    return {"status": "running"}

@app.post("/chat")
async def chat(payload: dict):

    session_id = payload["session_id"]
    message = payload["message"]

    history = session_store.get_history(session_id)

    intent = await route_query(message)

    if intent == "order":
        response = await handle_order(message, history)

    elif intent == "consultant":
        response = await handle_consultant(message, history)

    elif intent == "faq":
        response = await handle_faq(message, history)

    else:
        response = "Xin lỗi, tôi chưa hiểu yêu cầu của bạn."

    session_store.add_message(session_id, message, response)

    return {
        "intent": intent,
        "response": response
    }