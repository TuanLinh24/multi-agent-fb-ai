"""
B2.2: Streaming & Token-level Output
SSE streaming with performance monitoring
"""

import asyncio
import time
from typing import AsyncGenerator


async def stream_text(text: str) -> AsyncGenerator[str, None]:
    """Stream text as Server-Sent Events with token-level output"""
    words = text.split()
    start_time = time.time()

    for i, word in enumerate(words):
        # Simulate token-level streaming (in real implementation, this would come from LLM)
        token_data = {
            "token": word,
            "index": i,
            "timestamp": time.time() - start_time,
            "is_final": i == len(words) - 1
        }

        # SSE format
        yield (
            f"event: token\n"
            f"data: {token_data}\n\n"
        )

        # Small delay to simulate streaming
        await asyncio.sleep(0.05)

    # Send completion event
    yield (
        f"event: complete\n"
        f"data: {{\"total_tokens\": {len(words)}, \"total_time\": {time.time() - start_time:.3f}}}\n\n"
    )


async def stream_llm_response(token_generator: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """Stream LLM response tokens as SSE events"""
    start_time = time.time()
    token_count = 0

    async for token in token_generator:
        token_count += 1
        timestamp = time.time() - start_time

        token_data = {
            "token": token,
            "index": token_count - 1,
            "timestamp": timestamp,
            "is_final": False
        }

        yield (
            f"event: token\n"
            f"data: {token_data}\n\n"
        )

    # Send completion event
    yield (
        f"event: complete\n"
        f"data: {{\"total_tokens\": {token_count}, \"total_time\": {time.time() - start_time:.3f}}}\n\n"
    )