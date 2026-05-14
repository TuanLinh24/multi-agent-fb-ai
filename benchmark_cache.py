import asyncio
import time
from app.cache.semantic_cache import SemanticCache

async def benchmark_cache():
    cache = SemanticCache()

    # Sample queries
    queries = [
        "Wifi password là gì?",
        "Quán mở cửa lúc mấy giờ?",
        "Các loại coffee của quán?",
        "Tôi muốn đặt 2 ly latte",
        "Quán có chỗ ngồi ngoài trời không?",
        "Món nào bán chạy nhất?",
        "Wifi là gì?",  # Similar to first
        "Password wifi quán?",  # Similar
        "Giờ mở cửa của quán?",  # Similar
        "Menu coffee quán?",  # Similar
        "Đặt hàng latte",  # Similar
        "Chỗ ngồi ngoài trời?",  # Similar
        "Món bán chạy?",  # Similar
    ]

    responses = [
        "Highlands123",
        "7h sáng đến 10h tối",
        "Latte, Americano, Mocha",
        "Đơn hàng đã được xử lý",
        "Có khu vực ngoài trời",
        "Latte là món bán chạy nhất",
        "Highlands123",  # Same as first
        "Highlands123",  # Same
        "7h sáng đến 10h tối",  # Same
        "Latte, Americano, Mocha",  # Same
        "Đơn hàng đã được xử lý",  # Same
        "Có khu vực ngoài trời",  # Same
        "Latte là món bán chạy nhất",  # Same
    ]

    # Add some to cache
    for i in range(6):
        await cache.set(queries[i], responses[i])

    # Now test
    hits = 0
    total = len(queries)
    latencies = []

    for query in queries:
        start = time.time()
        result = await cache.get(query)
        latency = (time.time() - start) * 1000  # ms

        if result is not None:
            hits += 1
            latencies.append(latency)

    hit_rate = (hits / total) * 100
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print(f"Cache Hit Rate: {hit_rate:.2f}%")
    print(f"Latency Cache-hit: {avg_latency:.2f} ms")
    print(f"Total queries: {total}, Hits: {hits}")

if __name__ == "__main__":
    asyncio.run(benchmark_cache())