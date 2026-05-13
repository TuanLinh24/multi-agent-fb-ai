import asyncio
import inspect

MAX_CONCURRENT = 3
DEFAULT_TIMEOUT = 60
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 0.5

_queue = asyncio.Queue()
_worker_tasks = []
_workers_started = False


async def _worker_loop():
    while True:
        item = await _queue.get()
        if item is None:
            _queue.task_done()
            break

        func, args, kwargs, future, retries, backoff = item

        if future.cancelled():
            _queue.task_done()
            continue

        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result
            else:
                result = await asyncio.to_thread(func, *args, **kwargs)
            if not future.cancelled():
                future.set_result(result)
        except Exception as exc:
            if retries > 1:
                await asyncio.sleep(backoff)
                await _queue.put((func, args, kwargs, future, retries - 1, backoff * 2))
            else:
                if not future.cancelled():
                    future.set_exception(exc)
        finally:
            _queue.task_done()


async def _ensure_workers():
    global _workers_started
    if _workers_started:
        return

    loop = asyncio.get_running_loop()
    for _ in range(MAX_CONCURRENT):
        task = loop.create_task(_worker_loop())
        _worker_tasks.append(task)

    _workers_started = True


async def run_with_queue(func, *args, timeout=DEFAULT_TIMEOUT, retries=DEFAULT_RETRIES, backoff=DEFAULT_BACKOFF, **kwargs):
    await _ensure_workers()
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    await _queue.put((func, args, kwargs, future, retries, backoff))
    return await asyncio.wait_for(future, timeout)


async def shutdown_queue():
    for _ in _worker_tasks:
        await _queue.put(None)
    await _queue.join()
    for task in _worker_tasks:
        task.cancel()