
import asyncio
import importlib
import json
import os
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_httpx_spec = importlib.util.find_spec("httpx")
httpx = importlib.import_module("httpx") if _httpx_spec else None

INTENT_LABELS = ["order", "consultant", "faq", "ignore"]
INTENT_TO_ID = {label: idx for idx, label in enumerate(INTENT_LABELS)}

TOTAL_SAMPLES = 4000
HARD_RATIO = 0.08
HARD_SAMPLES = int(TOTAL_SAMPLES * HARD_RATIO)
HARD_PER_INTENT = HARD_SAMPLES // len(INTENT_LABELS)
NORMAL_PER_INTENT = (TOTAL_SAMPLES // len(INTENT_LABELS)) - HARD_PER_INTENT

OUTPUT_DIR = Path("data/router")
DATA_FILE = OUTPUT_DIR / "router_dataset.json"
CHECKPOINT_FILE = OUTPUT_DIR / "router_dataset.checkpoint.json"
API_URL = os.getenv("ROUTER_DATA_API_URL", "").strip()
API_KEY = os.getenv("ROUTER_DATA_API_KEY", "").strip()
REMOTE_TIMEOUT = 60.0
CONCURRENCY = 8
BATCH_SIZE = 50

INTENT_TEMPLATES = {
    "order": {
        "vi": [
            "Cho tôi một ly cà phê sữa",
            "Tính tiền giúp em",
            "Thêm một phần bánh mì",
            "Cho tôi một bạc xỉu",
            "Mình muốn order một latte",
            "Gọi thêm một dĩa bánh ngọt",
            "Giúp tôi đặt một cà phê đá",
            "Tôi muốn gọi một trà đào",
        ],
        "en": [
            "I want a latte",
            "Please add a croissant",
            "Give me one cappuccino",
            "Can I order a mocha?",
            "I would like a cold brew",
            "Add a sandwich to my order",
            "I'd like one espresso",
            "Please charge me for the drinks",
        ],
    },
    "consultant": {
        "vi": [
            "Có món gì ngon không?",
            "Món nào bán chạy nhất?",
            "Tôi nên chọn gì hôm nay?",
            "Cho tôi gợi ý đồ uống",
            "Món nào hợp với tôi?",
            "Lời khuyên của bạn là gì?",
            "Tôi muốn uống đồ ngọt, bạn gợi ý gì?",
            "Cái nào thơm và không quá ngọt?",
        ],
        "en": [
            "What do you recommend?",
            "Suggest something sweet",
            "Which drink is best today?",
            "I need a recommendation",
            "Can you recommend a coffee?",
            "What should I order?",
            "Any ideas for something light?",
            "Recommend me a specialty drink",
        ],
    },
    "faq": {
        "vi": [
            "Wifi password là gì?",
            "Quán mở cửa mấy giờ?",
            "Thanh toán bằng thẻ được không?",
            "Có chỗ đậu xe không?",
            "Quán có giao hàng không?",
            "Giờ nghỉ trưa là khi nào?",
            "Có ưu đãi hôm nay không?",
            "Menu có món chay không?",
        ],
        "en": [
            "What are your opening hours?",
            "Do you have parking?",
            "Can I pay by card?",
            "Is there Wi-Fi available?",
            "Do you offer delivery?",
            "When do you close?",
            "Is the menu vegetarian friendly?",
            "Are pets allowed?",
        ],
    },
    "ignore": {
        "vi": [
            "Haha",
            "Ăn thử thôi",
            "Ờm...",
            "Hello",
            "Alo",
            "Chỉ thử xem",
            "Hôm nay thế nào?",
            "Cảm ơn nhé",
        ],
        "en": [
            "Hello",
            "haha",
            "Just checking",
            "What's up?",
            "I'm bored",
            "Test message",
            "Hi there",
            "Random noise",
        ],
    },
}

HARD_TEMPLATES: Dict[str, List[Tuple[str, str]]] = {
    "order": [
        ("Có gì ngon rẻ không?", "consultant"),
        ("I want something cheap and tasty", "consultant"),
        ("Should I order a drink or ask for a suggestion?", "consultant"),
        ("Muốn gọi một món nào đó ngon và rẻ", "consultant"),
    ],
    "consultant": [
        ("Nên gọi gì bây giờ?", "order"),
        ("What should I order if I want something sweet?", "order"),
        ("Cho tôi gợi ý một thứ để order", "order"),
        ("Tôi nên chọn đồ uống nào?", "order"),
    ],
    "faq": [
        ("Do you have any drinks for a quick visit?", "order"),
        ("Quán có phục vụ mang về không?", "order"),
        ("Is there a fast option on the menu?", "order"),
        ("Có món nào phù hợp cho take away không?", "order"),
    ],
    "ignore": [
        ("Hello, are you open now?", "faq"),
        ("Em đang thử mic", "ignore"),
        ("Just saying hi", "ignore"),
        ("Ơ... tôi không hiểu", "ignore"),
    ],
}

PREFIXES = [
    "Please",
    "Xin hãy",
    "Có thể",
    "Could you",
    "Mình muốn",
    "Can I",
    "Cho mình",
    "Help me",
]

SUFFIXES = [
    "please",
    "làm ơn",
    "giúp tôi",
    "thanks",
    "cảm ơn",
    "nếu được",
    "với",
    "nha",
]

EXTRA_DETAILS = {
    "order": [
        "with extra sugar",
        "with no ice",
        "without milk",
        "with oat milk",
        "as a takeaway",
        "for pickup",
        "as a gift",
        "for later",
        "as a small size",
        "as a large size",
    ],
    "consultant": [
        "for a gift",
        "for a sweet tooth",
        "for a light option",
        "for breakfast",
        "for a dessert",
        "for an iced drink",
        "for a hot drink",
        "for a beginner",
        "with low sugar",
        "that is not too strong",
    ],
    "faq": [
        "for the cafe",
        "about the menu",
        "about the opening hours",
        "about delivery",
        "about parking",
        "about vegetarian options",
        "about Wi-Fi",
        "about payment methods",
        "about seating",
        "about the coffee beans",
    ],
    "ignore": [
        "just checking",
        "not important",
        "just saying hi",
        "no question",
        "only a test",
        "not asking anything",
        "for nothing",
        "just random",
        "no intent",
        "just chat",
    ],
}


def _detect_language(text: str) -> str:
    has_vi = any(ord(ch) > 127 for ch in text)
    if has_vi and any(ch.isalpha() for ch in text):
        return "vi"
    return "en"


def _build_sample(text: str, intent: str, is_hard: bool) -> Dict:
    language = _detect_language(text)
    return {
        "text": text.strip(),
        "intent": intent,
        "label": INTENT_TO_ID[intent],
        "is_noise": intent == "ignore",
        "language": language,
        "is_hard": is_hard,
    }


async def _call_remote_generation(prompt: str) -> str:
    if httpx is None:
        raise RuntimeError(
            "httpx is required for remote generation. Install it or unset ROUTER_DATA_API_URL."
        )

    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    async with httpx.AsyncClient(timeout=REMOTE_TIMEOUT) as client:
        response = await client.post(
            API_URL,
            json={"prompt": prompt, "max_tokens": 64},
            headers=headers,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("text") or payload.get("generated_text") or response.text


def _apply_extra_detail(text: str, intent: str) -> str:
    details = EXTRA_DETAILS.get(intent, [])
    if not details:
        return text
    detail = random.choice(details)
    return f"{text} {detail}"


def _apply_prefix_suffix(text: str) -> str:
    if random.random() < 0.35:
        prefix = random.choice(PREFIXES)
        text = f"{prefix} {text}"
    if random.random() < 0.35:
        suffix = random.choice(SUFFIXES)
        text = f"{text} {suffix}"
    return text


def _local_template_generate(intent: str, is_hard: bool) -> str:
    if is_hard:
        candidate_pool = HARD_TEMPLATES[intent]
        text, _ = random.choice(candidate_pool)
    else:
        language = random.choices(["vi", "en"], weights=[0.55, 0.45], k=1)[0]
        text = random.choice(INTENT_TEMPLATES[intent][language])

    text = _apply_prefix_suffix(text)
    if random.random() < 0.45:
        text = _apply_extra_detail(text, intent)

    return text


async def generate_text(intent: str, is_hard: bool) -> str:
    if API_URL:
        prompt_type = "hard" if is_hard else "normal"
        prompt = (
            f"Generate one {prompt_type} coffee shop user utterance for the intent '{intent}'. "
            "Support Vietnamese and English. Output only the raw utterance."
        )
        answer = await _call_remote_generation(prompt)
        return answer.strip().splitlines()[0].strip()

    return await asyncio.to_thread(_local_template_generate, intent, is_hard)


async def _generate_one(intent: str, is_hard: bool) -> Dict:
    text = await generate_text(intent, is_hard)
    return _build_sample(text, intent, is_hard)


def _save_checkpoint(samples: List[Dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": time.time(),
        "sample_count": len(samples),
        "samples": samples,
    }
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _load_checkpoint() -> Optional[List[Dict]]:
    if not CHECKPOINT_FILE.exists():
        return None

    try:
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        print(f"Warning: checkpoint file {CHECKPOINT_FILE} is corrupt or unavailable, skipping it.")
        return None

    return payload.get("samples", [])


def _load_existing_dataset() -> Optional[List[Dict]]:
    if not DATA_FILE.exists():
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _sample_counts(samples: List[Dict]) -> Dict[str, int]:
    counts = {intent: 0 for intent in INTENT_LABELS}
    for sample in samples:
        counts[sample["intent"]] += 1
    return counts


async def generate_dataset() -> List[Dict]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    samples = _load_checkpoint() or _load_existing_dataset() or []
    seen_texts = {item["text"] for item in samples}
    counts = _sample_counts(samples)

    target_counts = {intent: NORMAL_PER_INTENT + HARD_PER_INTENT for intent in INTENT_LABELS}
    target_hard_counts = {intent: HARD_PER_INTENT for intent in INTENT_LABELS}

    generated_count = len(samples)
    print(f"Resuming generation: {generated_count} samples already loaded")

    async def generate_batch(batch: List[Tuple[str, bool]]) -> List[Dict]:
        semaphore = asyncio.Semaphore(CONCURRENCY)

        async def worker(intent: str, is_hard: bool) -> Dict:
            async with semaphore:
                sample = await _generate_one(intent, is_hard)
                return sample

        tasks = [asyncio.create_task(worker(intent, is_hard)) for intent, is_hard in batch]
        return await asyncio.gather(*tasks)

    def _build_target_list() -> List[Tuple[str, bool]]:
        hard_needed = {
            intent: max(
                0,
                target_hard_counts[intent]
                - sum(1 for s in samples if s["intent"] == intent and s["is_hard"])
            )
            for intent in INTENT_LABELS
        }
        normal_needed = {
            intent: max(0, target_counts[intent] - counts[intent])
            for intent in INTENT_LABELS
        }
        batch = []
        for intent in INTENT_LABELS:
            batch.extend([(intent, True)] * hard_needed[intent])
            batch.extend([(intent, False)] * normal_needed[intent])
        random.shuffle(batch)
        return batch

    while True:
        work_items = _build_target_list()
        if not work_items:
            break

        for i in range(0, len(work_items), BATCH_SIZE):
            batch = work_items[i : i + BATCH_SIZE]
            generated = await generate_batch(batch)

            added = 0
            for sample in generated:
                if sample["text"] in seen_texts:
                    continue
                samples.append(sample)
                seen_texts.add(sample["text"])
                counts[sample["intent"]] += 1
                added += 1

            _save_checkpoint(samples)
            generated_count = len(samples)
            print(
                f"Batch {i // BATCH_SIZE + 1}: attempted={len(batch)} added={added} "
                f"total={generated_count} order={counts['order']} consultant={counts['consultant']} "
                f"faq={counts['faq']} ignore={counts['ignore']}"
            )

    deduped = samples
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()

    print(f"Saved {len(deduped)} samples to {DATA_FILE}")
    return deduped


if __name__ == "__main__":
    asyncio.run(generate_dataset())
