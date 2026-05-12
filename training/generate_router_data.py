import json
import random

intents = [
    "order",
    "consultant",
    "faq",
    "ignore"
]

samples = []

for _ in range(5000):

    intent = random.choice(intents)

    if intent == "order":
        text = "Cho tôi 1 latte"

    elif intent == "consultant":
        text = "Có món nào ngon không?"

    elif intent == "faq":
        text = "Wifi là gì?"

    else:
        text = "haha"

    samples.append({
        "text": text,
        "intent": intent
    })

with open(
    "data/router_dataset.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        samples,
        f,
        ensure_ascii=False,
        indent=2
    )