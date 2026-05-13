import asyncio


async def stream_text(text: str):

    words = text.split()

    for word in words:

        yield (
            f"event: message\n"
            f"data: {word}\n\n"
        )

        await asyncio.sleep(0)