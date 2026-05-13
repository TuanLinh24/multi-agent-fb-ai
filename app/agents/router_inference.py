
import asyncio
import inspect
import time

from transformers import AutoTokenizer, AutoModelForCausalLM

from app.queue.request_queue import run_with_queue
from app.utils.router_parser import safe_parse_router_output

MODEL_PATH = "./router_model/final"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="auto"
)

SYSTEM_PROMPT = (
    "You are a router classifier for a coffee shop AI system. "
    "Classify the user text into exactly one action. "
    "Return valid JSON only, with a single field named \"action\". "
    "Possible actions: order, consultant, faq, ignore. "
    "Support Vietnamese and English inputs."
)

VALID_ACTIONS = {"order", "consultant", "faq", "ignore"}

async def classify(text: str):
    start = time.time()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text}
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    async def _generate():
        outputs = model.generate(
            **inputs,
            max_new_tokens=16,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    decoded = await run_with_queue(_generate)

    result = safe_parse_router_output(decoded)
    action = result.get("action", "ignore")
    if action not in VALID_ACTIONS:
        action = "ignore"

    latency_ms = (time.time() - start) * 1000

    return {
        "action": action,
        "latency_ms": round(latency_ms, 2)
    }
