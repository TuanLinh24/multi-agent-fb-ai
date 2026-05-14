import asyncio
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

app = FastAPI()


def _build_chat_completion(prompt: str, model: str) -> dict:
    content = prompt.strip() or "Xin chào! Tôi là LLM mô phỏng."
    return {
        "id": "chatcmpl-mock",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": f"[mock] {content}"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": len(content.split()),
            "completion_tokens": len(content.split()),
            "total_tokens": len(content.split()) * 2,
        },
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    payload = await request.json()
    model = payload.get("model", "mock-model")
    messages = payload.get("messages", [])
    stream = payload.get("stream", False)

    prompt = ""
    if messages:
        prompt = messages[-1].get("content", "")

    if not stream:
        return JSONResponse(_build_chat_completion(prompt, model))

    async def event_generator():
        text = prompt.strip() or "Xin chào!"
        tokens = text.split() or ["Xin", "chào"]

        for idx, token in enumerate(tokens):
            data = {
                "token": token,
                "index": idx,
                "timestamp": time.time(),
                "is_final": False,
            }
            yield f"event: token\ndata: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.02)

        final_data = {
            "token": "",
            "index": len(tokens),
            "timestamp": time.time(),
            "is_final": True,
        }
        yield f"event: token\ndata: {json.dumps(final_data)}\n\n"
        yield f"event: complete\ndata: {json.dumps({'total_tokens': len(tokens), 'total_time': 0.0})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
