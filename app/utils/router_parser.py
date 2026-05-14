
import json
import re

VALID_ACTIONS = {"order", "consultant", "faq", "greeting", "ignore"}


def safe_parse_router_output(text: str):
    text = text.strip()

    # Try exact JSON parse first
    try:
        parsed = json.loads(text)
        action = parsed.get("action")
        if action in VALID_ACTIONS:
            return {"action": action}
    except Exception:
        pass

    # Try to extract JSON-like payload from mixed output
    match = re.search(r'\{.*\}', text)
    if match:
        try:
            parsed = json.loads(match.group())
            action = parsed.get("action")
            if action in VALID_ACTIONS:
                return {"action": action}
        except Exception:
            pass

    # Fallback: detect label words in the output string
    lowered = text.lower()
    for action in VALID_ACTIONS:
        if action in lowered:
            return {"action": action}

    return {"action": "ignore"}
