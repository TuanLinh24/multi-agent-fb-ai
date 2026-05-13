from sse_starlette.sse import EventSourceResponse
import asyncio


async def fake_token_stream(text: str):

    words = text.split()

    for word in words:

        yield {
            "event": "message",
            "data": word + " "
        }

        await asyncio.sleep(0.03)


async def stream_response(text: str):

    return EventSourceResponse(
        fake_token_stream(text)
    )