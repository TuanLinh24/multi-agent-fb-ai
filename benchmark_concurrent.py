import asyncio
import aiohttp
import time


URL = "http://127.0.0.1:8000/chat"


payload = {
    "session_id": "1",
    "message": "What is the wifi password?"
}


async def send_request(session, idx):

    start = time.time()

    async with session.post(
        URL,
        json=payload
    ) as response:

        text = await response.text()

        latency = time.time() - start

        print(
            f"Request {idx} "
            f"| {latency:.2f}s"
        )

        return text


async def main():

    tasks = []

    async with aiohttp.ClientSession() as session:

        for i in range(20):

            tasks.append(
                send_request(
                    session,
                    i
                )
            )

        await asyncio.gather(*tasks)


asyncio.run(main())