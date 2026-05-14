import time

VALID_ACTIONS = {"order", "consultant", "faq", "greeting", "ignore"}

FALLBACK_KEYWORDS = {
    "faq": [
        "wifi", "mật khẩu", "password", "wifi là gì", "wifi password",
        "mở cửa", "đóng cửa", "giờ", "giờ mở cửa", "giờ đóng cửa",
        "giờ hoạt động", "khi nào mở", "khi nào đóng", "giờ hoạt động"
    ],
    "order": [
        "đặt", "mua", "order", "ship", "giao", "thanh toán", "đơn hàng",
        "cốc", "ly", "bình", "coffee", "cafe", "latte", "mocha", "espresso",
        "trà", "bakery", "bánh"
    ],
    "consultant": [
        "menu", "loại", "giá", "thức uống", "đồ uống", "suggest", "gợi ý",
        "tư vấn", "quán", "coffee", "cà phê", "địa chỉ", "hỏi"
    ],
}


def _fallback_route(text: str) -> str:
    lowered = text.strip().lower()
    if not lowered:
        return "ignore"

    if lowered.startswith(("xin chào", "xin chao")):
        return "greeting"
    if lowered in {"good morning", "good afternoon", "good evening"}:
        return "greeting"
    first = lowered.split()[0]
    if first.rstrip("!?.,") in {"hello", "hi", "hey", "chào", "chao", "hallo"}:
        return "greeting"

    for action in ["faq", "order", "consultant"]:
        for keyword in FALLBACK_KEYWORDS[action]:
            if keyword in lowered:
                return action

    return "ignore"


async def classify(text: str):
    start = time.time()

    action = _fallback_route(text)
    latency_ms = (time.time() - start) * 1000

    return {
        "action": action,
        "latency_ms": round(latency_ms, 2),
    }
