"""
Production LLM Client for vLLM / SGLang OpenAI-compatible server
- Async
- Cache-aware
- Streaming support
- Latency tracking
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, AsyncGenerator, Optional
from datetime import datetime

import httpx
from dotenv import load_dotenv

from app.cache.semantic_cache import SemanticCache

# Đảm bảo .env có hiệu lực dù import llm_client trước app.main (tests, worker khác).
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _ttft_budget() -> float:
    return float(os.getenv("TTFT_BUDGET", "0.2"))


_DEFAULT_LLM_BASE = "http://127.0.0.1:8001"


def _vllm_base_url_from_env() -> str:
    """Đọc VLLM_API_URL; cắt phần dính nhầm khi copy .env (vd: ...8001(venv))."""
    raw = (os.getenv("VLLM_API_URL") or _DEFAULT_LLM_BASE).strip()
    if "(" in raw:
        raw = raw.split("(", 1)[0].strip()
    raw = raw.split()[0] if raw else _DEFAULT_LLM_BASE
    raw = raw.split("#", 1)[0].strip()
    return raw.rstrip("/") or _DEFAULT_LLM_BASE.rstrip("/")


def _llm_model_from_env() -> str:
    """Ưu tiên LLM_MODEL; nếu chỉ có MODEL_NAME trong .env thì dùng luôn."""
    return (
        os.getenv("LLM_MODEL")
        or os.getenv("MODEL_NAME")
        or "Qwen/Qwen2.5-1.5B-Instruct"
    )


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
        api_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        self.api_url = (api_url or _vllm_base_url_from_env()).rstrip("/")
        self.model_name = model_name or _llm_model_from_env()
        self.timeout = (
            timeout if timeout is not None else float(os.getenv("LLM_TIMEOUT", "30"))
        )

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout)
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
            raise RuntimeError(
                f"LLM request failed (POST {self.api_url}/v1/chat/completions): {e}"
            )

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
        budget = _ttft_budget()
        if elapsed > budget:
            print(f"[WARN] TTFT exceeded: {elapsed:.3f}s > {budget}s")

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

            budget = _ttft_budget()
            if first_token_time > budget:
                print(f"[WARN] TTFT exceeded: {first_token_time:.3f}s")


# =========================
# GLOBAL SINGLETON
# =========================

_llm_client: Optional[LLMClient] = None
_llm_config_sig: Optional[tuple] = None


def _llm_env_signature() -> tuple:
    return (
        _vllm_base_url_from_env(),
        _llm_model_from_env(),
        os.getenv("LLM_TIMEOUT", "30"),
    )


async def get_llm_client() -> LLMClient:
    global _llm_client, _llm_config_sig
    sig = _llm_env_signature()
    if _llm_client is not None and _llm_config_sig == sig:
        return _llm_client
    if _llm_client is not None:
        await _llm_client.close()
    _llm_client = LLMClient()
    _llm_config_sig = sig
    return _llm_client


async def generate(prompt: str, **kwargs) -> str:
    client = await get_llm_client()
    return await client.generate(prompt, **kwargs)


async def stream_generate(prompt: str, **kwargs):
    client = await get_llm_client()
    async for token in client.stream_generate(prompt, **kwargs):
        yield token