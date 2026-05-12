import asyncio

class RequestQueue:

    def __init__(self, max_concurrent=3):

        self.semaphore = asyncio.Semaphore(
            max_concurrent
        )

    async def run(self, coro):

        async with self.semaphore:
            return await coro