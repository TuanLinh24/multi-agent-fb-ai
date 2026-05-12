import json


def parse_router_output(text: str):

    try:

        start = text.find("{")
        end = text.rfind("}") + 1

        return json.loads(text[start:end])

    except:

        return {
            "action": "ignore"
        }