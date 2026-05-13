"""
Production LLM Client for vLLM / SGLang OpenAI-compatible server
- Async
- Cache-aware
- Streaming support
- Latency tracking
"""

import os
import asyncio
import json
from typing import Any, Dict, AsyncGenerator, Optional
from datetime import datetime

import httpx

from app.cache.semantic_cache import SemanticCache


# =========================
# CONFIG
# =========================

VLLM_API_URL = os.getenv("VLLM_API_URL", "http://localhost:8001")
MODEL_NAME = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")

TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30"))
TTFT_BUDGET = float(os.getenv("TTFT_BUDGET", "0.2"))  # 200ms target


# =========================
# CACHE
# =========================

semantic_cache = SemanticCache()


# =========================
# CLIENT
# =========================

class LLMClient:
    """
    Async client for vLLM / SGLang OpenAI-compatible API
    """

    def __init__(
        self,
        api_url: str = VLLM_API_URL,
        model_name: str = MODEL_NAME,
        timeout: float = TIMEOUT,
    ):
        self.api_url = api_url.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout)
        )

    # -------------------------
    # lifecycle
    # -------------------------

    async def close(self):
        await self.client.aclose()

    # -------------------------
    # internal call
    # -------------------------

    async def _chat_completions(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.9,
        stream: bool = False,
    ) -> Dict[str, Any]:

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }

        try:
            resp = await self.client.post(
                f"{self.api_url}/v1/chat/completions",
                json=payload,
            )
            resp.raise_for_status()

            if stream:
                return resp  # raw response stream
            return resp.json()

        except httpx.TimeoutException:
            raise TimeoutError(f"LLM timeout after {self.timeout}s")

        except Exception as e:
            raise RuntimeError(f"LLM request failed: {e}")

    # =========================
    # NORMAL GENERATION
    # =========================

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        use_cache: bool = True,
    ) -> str:

        start = datetime.now()

        # -------- cache --------
        if use_cache:
            cached = await semantic_cache.get(prompt)
            if cached:
                return cached

        messages = [
            {"role": "user", "content": prompt}
        ]

        result = await self._chat_completions(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )

        try:
            text = result["choices"][0]["message"]["content"]

        except Exception:
            raise RuntimeError(f"Invalid response format: {result}")

        # cache store
        if use_cache:
            await semantic_cache.set(prompt, text)

        # latency tracking
        elapsed = (datetime.now() - start).total_seconds()
        if elapsed > TTFT_BUDGET:
            print(f"[WARN] TTFT exceeded: {elapsed:.3f}s > {TTFT_BUDGET}s")

        return text

    # =========================
    # STREAMING (SSE)
    # =========================

    async def stream_generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> AsyncGenerator[str, None]:

        start = datetime.now()
        first_token_time: Optional[float] = None
        token_count = 0

        messages = [{"role": "user", "content": prompt}]

        resp = await self._chat_completions(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        try:
            async for line in resp.aiter_lines():

                if not line:
                    continue

                if not line.startswith("data: "):
                    continue

                data = line[6:].strip()

                if data == "[DONE]":
                    break

                # TTFT tracking
                if first_token_time is None:
                    first_token_time = (datetime.now() - start).total_seconds()

                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content")

                    if delta:
                        token_count += 1
                        yield delta

                except json.JSONDecodeError:
                    continue

        except Exception as e:
            print(f"[STREAM ERROR] {e}")
            raise

        # metrics
        total = (datetime.now() - start).total_seconds()

        if first_token_time:
            throughput = token_count / max(total, 1e-6)

            print(
                f"[LLM METRICS] TTFT={first_token_time:.3f}s | "
                f"Tokens={token_count} | "
                f"Throughput={throughput:.1f} tok/s"
            )

            if first_token_time > TTFT_BUDGET:
                print(f"[WARN] TTFT exceeded: {first_token_time:.3f}s")


# =========================
# GLOBAL SINGLETON
# =========================

_llm_client: Optional[LLMClient] = None


async def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


async def generate(prompt: str, **kwargs) -> str:
    client = await get_llm_client()
    return await client.generate(prompt, **kwargs)


async def stream_generate(prompt: str, **kwargs):
    client = await get_llm_client()
    async for token in client.stream_generate(prompt, **kwargs):
        yield token