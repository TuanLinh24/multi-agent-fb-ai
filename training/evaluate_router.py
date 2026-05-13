import asyncio
import json
import random
import time
from collections import defaultdict

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from app.agents.router_inference import classify

LABEL_ORDER = ["order", "consultant", "faq", "ignore"]


def _load_dataset(path: str = "data/router/router_dataset.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _split_balanced_test_set(data, test_fraction: float = 0.2, seed: int = 42):
    random.seed(seed)
    groups = defaultdict(list)
    for item in data:
        groups[item["intent"]].append(item)

    test_set = []
    for intent, items in groups.items():
        count = max(1, int(len(items) * test_fraction))
        test_set.extend(random.sample(items, count))

    return test_set


async def _classify_samples(samples):
    y_pred = []
    latencies = []

    for sample in samples:
        result = await classify(sample["text"])
        y_pred.append(result["action"])
        latencies.append(result["latency_ms"])

    return y_pred, latencies


def _summarize_latency(latencies):
    sorted_lat = sorted(latencies)
    return {
        "count": len(sorted_lat),
        "mean": sum(sorted_lat) / len(sorted_lat) if sorted_lat else 0,
        "p50": sorted_lat[int(0.5 * len(sorted_lat))] if sorted_lat else 0,
        "p90": sorted_lat[int(0.9 * len(sorted_lat))] if sorted_lat else 0,
        "p95": sorted_lat[int(0.95 * len(sorted_lat)) - 1] if len(sorted_lat) >= 1 else 0,
        "max": sorted_lat[-1] if sorted_lat else 0,
    }


def evaluate():
    data = _load_dataset()
    test_data = _split_balanced_test_set(data, test_fraction=0.2)

    print(f"Evaluating on {len(test_data)} balanced test samples")

    y_true = [item["intent"] for item in test_data]

    y_pred, latencies = asyncio.run(_classify_samples(test_data))

    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, labels=LABEL_ORDER, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=LABEL_ORDER)

    hard_items = [item for item in test_data if item.get("is_hard")]
    hard_true = [item["intent"] for item in hard_items]
    hard_pred = [pred for item, pred in zip(test_data, y_pred) if item.get("is_hard")]
    hard_acc = accuracy_score(hard_true, hard_pred) if hard_items else 0.0

    latency_stats = _summarize_latency(latencies)

    print("\n=== Router Evaluation ===")
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(report)
    print("\nConfusion Matrix:")
    print("labels:", LABEL_ORDER)
    print(cm)
    print(f"Hard sample accuracy: {hard_acc:.4f} ({len(hard_items)} hard samples)")
    print("\nLatency stats (ms):")
    print(latency_stats)

    return {
        "accuracy": acc,
        "hard_accuracy": hard_acc,
        "latency": latency_stats,
        "metrics_report": report,
        "confusion_matrix": cm.tolist(),
    }


if __name__ == "__main__":
    evaluate()
