from app.rag.hybrid_search import hybrid_search
from app.serving.llm_client import generate

MENU = [
    {
        "name": "Latte",
        "description": "smooth milk coffee"
    },
    {
        "name": "Cappuccino",
        "description": "strong espresso with foam"
    },
    {
        "name": "Mocha",
        "description": "chocolate flavored coffee"
    }
]


def build_consultant_prompt(user_message, context_text=""):

    menu_text = ""

    for item in MENU:
        menu_text += (
            f"- {item['name']}: "
            f"{item['description']}\n"
        )

    prompt = f"""
You are a coffee consultant assistant.
Support Vietnamese and English.

Available drinks:

{menu_text}

{context_text}

User request:
{user_message}

Rules:
- Recommend ONLY drinks from menu
- Keep answer under 2 sentences
- Be friendly
- Do not invent drinks

Answer:
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
            context_text = "\n".join(parts)
        else:
            context_text = str(best_doc)

    prompt = build_consultant_prompt(user_message, context_text)
    return await generate(prompt)
