from sentence_transformers import SentenceTransformer

from app.queue.request_queue import run_with_queue

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def embed_text(text: str):
    vector = model.encode([text])
    return vector


async def embed_text_async(text: str):
    return await run_with_queue(lambda: model.encode([text]))
