from app.agents.consultant_agent import MENU


def graph_expand(query):
    lower_query = query.lower()
    results = []

    for item in MENU:
        item_name = item["name"].lower()
        item_description = item["description"].lower()
        if item_name in lower_query or item_description in lower_query:
            results.append({
                "question": f"What is {item['name']}?",
                "answer": item["description"]
            })

    return results
