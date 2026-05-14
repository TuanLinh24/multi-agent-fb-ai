import traceback
from pathlib import Path

from dotenv import load_dotenv

# Phải load .env trước mọi import app.* (đặc biệt llm_client đọc VLLM_API_URL khi khởi tạo).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from app.agents.router_agent import route_query
from app.agents.faq_agent import handle_faq
from app.agents.consultant_agent import handle_consultant
from app.agents.order_agent import handle_order
from app.rag.neo4j_client import Neo4jClient
from neo4j.exceptions import Neo4jError

from app.cache.session_store import (
    add_message,
    get_history
)

from app.serving.stream import stream_text


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def init_neo4j_schema():
    client = Neo4jClient()
    try:
        client.create_constraints()
        client.create_vector_index("menu_vector_index", "MenuItem", "embedding")
        client.create_vector_index("chunk_vector_index", "Chunk", "embedding")
        client.create_vector_index("entity_vector_index", "Entity", "embedding")
    except Exception as exc:
        print(f"[WARN] Neo4j schema init failed: {exc}")
    finally:
        client.close()


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

    try:
        if intent == "faq":
            response = await handle_faq(payload.message, history)
        elif intent == "consultant":
            response = await handle_consultant(payload.message, history)
        elif intent == "order":
            response = await handle_order(payload.message, history)
        elif intent == "greeting":
            response = (
                "Chào bạn, mình là trợ lý Highlands Coffee. Bạn muốn hỏi Wi‑Fi, giờ mở cửa, "
                "gợi ý đồ uống hay đặt món? Cứ nói mình hỗ trợ nhé."
            )
        else:
            response = (
                "Sorry, I do not "
                "understand your request."
            )
    except Neo4jError as exc:
        traceback.print_exc()
        response = (
            "Lỗi Neo4j khi truy vấn dữ liệu (RAG). Kiểm tra NEO4J_URI, phiên bản Neo4j 5+, "
            "và chạy lại schema/index nếu cần. "
            f"Chi tiết: {exc}"
        )
    except MemoryError as exc:
        traceback.print_exc()
        response = (
            "Hết RAM khi xử lý (embedding / model). Đóng ứng dụng nặng, giảm bớt container Docker, "
            "hoặc tăng bộ nhớ ảo (page file) trên Windows. "
            f"Chi tiết: {exc}"
        )
    except OSError as exc:
        winerr = getattr(exc, "winerror", None)
        if winerr == 1455 or "paging file" in str(exc).lower():
            traceback.print_exc()
            response = (
                "Windows báo paging file quá nhỏ (lỗi 1455): RAM / bộ nhớ ảo không đủ cho thao tác hiện tại. "
                "Thường gặp khi vừa tải SentenceTransformer (embedding) vừa chạy Ollama/Neo4j. "
                "Cách xử lý: Control Panel → System → Advanced system settings → Performance → Settings → "
                "Advanced → Virtual memory → tăng page file (hoặc để System managed), khởi động lại máy; "
                "đồng thời đóng Docker Desktop / trình duyệt nhiều tab nếu không cần."
            )
        else:
            raise
    except Exception as exc:
        traceback.print_exc()
        response = (
            "Không gọi được model ngôn ngữ (LLM). "
            "Thêm VLLM_API_URL vào file .env ở thư mục gốc project (ví dụ VLLM_API_URL=http://127.0.0.1:8001) "
            "hoặc export biến trước khi chạy uvicorn, rồi bật server OpenAI-compatible (POST /v1/chat/completions). "
            f"Lỗi: {exc}"
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