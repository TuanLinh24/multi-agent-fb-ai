import asyncio
from app.agents.router_inference import classify

async def test_router():
    test_texts = [
        "Cho tôi 1 trà đào",
        "Wifi password là gì?",
        "Có món nào ngon không?",
        "haha",
        "I want a latte",
        "Cho tôi bạc xỉu size L"
    ]

    for text in test_texts:
        result = await classify(text)
        print(f"Text: {text}")
        print(f"Action: {result['action']}, Latency: {result['latency_ms']} ms")
        print("---")

if __name__ == "__main__":
    asyncio.run(test_router())