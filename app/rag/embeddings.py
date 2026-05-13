from sentence_transformers import SentenceTransformer
from app.queue.request_queue import run_with_queue

# Using a simpler multilingual embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def embed_text(text: str):
    """Synchronous embedding for single text"""
    vector = model.encode([text], normalize_embeddings=True)
    return vector[0].tolist()  # Return as list for Neo4j storage


async def embed_texts_batch(texts: list[str]):
    """Asynchronous batch embedding"""
    return await run_with_queue(lambda: model.encode(texts, normalize_embeddings=True).tolist())


async def embed_text_async(text: str):
    """Asynchronous embedding for single text"""
    vectors = await run_with_queue(lambda: model.encode([text], normalize_embeddings=True))
    return vectors[0].tolist()
