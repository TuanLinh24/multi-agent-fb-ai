from typing import Literal


Intent = Literal[
    "faq",
    "consultant",
    "order",
    "ignore"
]


async def route_query(query: str) -> Intent:

    q = query.lower()

    # FAQ
    faq_keywords = [
        "wifi",
        "đóng cửa",
        "mở cửa",
        "giao hàng",
        "đậu xe",
        "password"
    ]

    # CONSULTANT
    consultant_keywords = [
        "recommend",
        "gợi ý",
        "món ngon",
        "uống gì",
        "best seller",
        "ngon"
    ]

    # ORDER
    order_keywords = [
        "đặt",
        "mua",
        "cho tôi",
        "order",
        "1 ly",
        "2 ly"
    ]

    if any(x in q for x in faq_keywords):
        return "faq"

    if any(x in q for x in consultant_keywords):
        return "consultant"

    if any(x in q for x in order_keywords):
        return "order"

    return "ignore"