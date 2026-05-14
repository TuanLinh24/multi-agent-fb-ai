import csv
from pathlib import Path

from app.rag.hybrid_search import search as hybrid_search
from app.serving.llm_client import generate
from app.agents.prompts import FAQ_PROMPT


FAQ_FALLBACK = [
    {
        "keywords": ["wifi", "mật khẩu", "password"],
        "answer": (
            "Mật khẩu WiFi dành cho khách tại cửa hàng Highlands Coffee là Highland123. "
            "Nếu không kết nối được, hãy hỏi nhân viên cửa hàng vì một số chi nhánh có thể dùng mật khẩu khác."
        ),
    },
    {
        "keywords": ["giờ mở cửa", "mở cửa", "đóng cửa", "giờ"],
        "answer": (
            "Đa số cửa hàng Highlands Coffee mở khoảng 7:00–22:00. "
            "Giờ cụ thể có thể khác nhau theo từng chi nhánh, nên bạn nên hỏi nhân viên hoặc kiểm tra trên Google Maps."
        ),
    },
    {
        "keywords": ["giao hàng", "grabfood", "foody", "now", "beamin"],
        "answer": (
            "Highlands Coffee thường hợp tác với các ứng dụng giao đồ ăn và dịch vụ giao hàng tùy khu vực. "
            "Bạn nên kiểm tra trên ứng dụng đặt đồ ăn tại địa chỉ cửa hàng của bạn."
        ),
    },
    {
        "keywords": ["chỗ ngồi ngoài trời", "ngoài trời", "ban công"],
        "answer": (
            "Nhiều cửa hàng Highlands Coffee có khu ngồi ngoài trời, nhưng không phải chi nhánh nào cũng có. "
            "Bạn vui lòng hỏi nhân viên cửa hàng khi đến."
        ),
    },
    {
        "keywords": ["thanh toán", "thẻ", "ví", "momo", "zalo pay", "pay"],
        "answer": (
            "Highlands Coffee thường chấp nhận thẻ ngân hàng và ví điện tử phổ biến tại Việt Nam. "
            "Tuy nhiên, một số cửa hàng nhỏ có thể chỉ nhận tiền mặt, nên bạn có thể hỏi quầy khi đến."
        ),
    },
]


def _normalize_text(text: str) -> str:
    return text.strip().lower()


def _faq_fallback(query: str) -> str | None:
    normalized = _normalize_text(query)
    for item in FAQ_FALLBACK:
        if any(keyword in normalized for keyword in item["keywords"]):
            return item["answer"]
    return None


def _load_faq_data() -> dict[str, str]:
    faq_path = Path(__file__).resolve().parents[2] / "data" / "faq.csv"
    if not faq_path.exists():
        return {}

    faq_map: dict[str, str] = {}
    try:
        with faq_path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                question = row.get("question", "").strip()
                answer = row.get("answer", "").strip()
                if question and answer:
                    faq_map[question.lower()] = answer
    except Exception:
        return {}

    return faq_map


FAQ_DATA = _load_faq_data()


def _context_from_doc(best_doc) -> str:
    if not best_doc:
        return ""
    if not isinstance(best_doc, dict):
        return str(best_doc)
    parts = []
    if best_doc.get("question"):
        parts.append(best_doc["question"])
    if best_doc.get("answer"):
        parts.append(best_doc["answer"])
    if best_doc.get("text"):
        parts.append(best_doc["text"])
    return "\n".join(parts).strip()


async def handle_faq(query, history):
    best_doc = await hybrid_search(query)
    context_text = _context_from_doc(best_doc)

    if not context_text:
        fallback = FAQ_DATA.get(query.strip().lower()) or _faq_fallback(query)
        if fallback:
            return fallback
        return (
            "Mình chưa có thông tin chính thức cho câu hỏi này. "
            "Xin vui lòng hỏi trực tiếp nhân viên Highlands Coffee hoặc kiểm tra thông tin trên trang chính thức."
        )

    prompt = f"""
{FAQ_PROMPT}

Context:
{context_text}

Question:
{query}
"""

    try:
        return await generate(prompt)
    except RuntimeError:
        return context_text
