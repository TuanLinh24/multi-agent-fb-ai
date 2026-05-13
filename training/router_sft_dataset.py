import json
from pathlib import Path
from typing import List

LABELS = ["order", "consultant", "faq", "ignore"]
LABEL_TO_ID = {label: idx for idx, label in enumerate(LABELS)}
DEFAULT_DATA_PATH = Path("data/router/router_dataset.json")
DEFAULT_SFT_PATH = Path("data/router/router_sft.json")


def build_prompt(text: str, label: str) -> str:
    return f"""
### Instruction:
You are a routing classifier for a coffee shop AI system.
Classify the user request into exactly one action.
Possible actions: order, consultant, faq, ignore.
Support Vietnamese and English inputs.
Return only the label in the output.

### Input:
{text}

### Output:
{label}
"""


def convert_to_sft(source_path: str = str(DEFAULT_DATA_PATH), output_path: str = str(DEFAULT_SFT_PATH)):
    source = Path(source_path)
    output = Path(output_path)
    if not source.exists():
        raise FileNotFoundError(f"Source dataset not found: {source}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with source.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    sft_records: List[dict] = []
    for item in raw_data:
        text = item["text"]
        intent = item["intent"]
        prompt = build_prompt(text, intent)
        sft_records.append({"text": prompt})

    with output.open("w", encoding="utf-8") as f:
        json.dump(sft_records, f, ensure_ascii=False, indent=2)

    print(f"Converted {len(sft_records)} samples to SFT format at {output}")


def get_dataset(source_path: str = str(DEFAULT_SFT_PATH)) -> List[dict]:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(
            f"SFT dataset not found: {source}. Run convert_sft.py after generating router data."
        )

    with source.open("r", encoding="utf-8") as f:
        records = json.load(f)

    return [{"text": record["text"]} for record in records]
