from app.rag.hybrid_search import search as hybrid_search
from app.serving.llm_client import generate
from app.agents.prompts import CONSULTANT_PROMPT

MENU = [
    {"name": "Phin Sữa Đá", "description": "Cà phê phin pha sẵn, sữa đặc, đá."},
    {"name": "Trà Sen Vàng", "description": "Trà ô long, hương sen."},
    {"name": "Americano", "description": "Espresso pha loãng."},
    {"name": "Freeze Trà Xanh", "description": "Đồ uống đá xay, trà xanh."},
]


def build_consultant_prompt(user_message, context_text=""):

    menu_text = ""

    for item in MENU:
        menu_text += (
            f"- {item['name']}: "
            f"{item['description']}\n"
        )

    prompt = f"""
{CONSULTANT_PROMPT}

Menu mẫu (chỉ giới thiệu món có trong danh sách; nếu Context RAG có món khác thì ưu tiên Context):

{menu_text}

Ngữ cảnh từ CSDL (nếu có):
{context_text}

Yêu cầu của khách:
{user_message}

Trả lời (tiếng Việt nếu khách dùng tiếng Việt):
"""

    return prompt


async def handle_consultant(user_message, history):
    best_doc = await hybrid_search(user_message)
    context_text = ""
    if best_doc:
        if isinstance(best_doc, dict):
            parts = []
            if best_doc.get("question"):
                parts.append(best_doc["question"])
            if best_doc.get("answer"):
                parts.append(best_doc["answer"])
            if best_doc.get("text"):
                parts.append(best_doc["text"])
            context_text = "\n".join(parts).strip()
        else:
            context_text = str(best_doc)

    prompt = build_consultant_prompt(user_message, context_text)
    try:
        return await generate(prompt)
    except RuntimeError:
        if context_text:
            return context_text
        raise
