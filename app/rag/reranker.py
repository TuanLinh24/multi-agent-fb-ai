from sentence_transformers import CrossEncoder
from app.queue.request_queue import run_with_queue

# Using BGE Reranker v2 for cross-encoder reranking
MODEL_NAME = "BAAI/bge-reranker-base"  # Using base model for compatibility

reranker = CrossEncoder(MODEL_NAME)


def rerank(query: str, documents: list[dict], top_k: int = 1):
    """Rerank documents based on relevance to query"""
    if not documents:
        return []

    if len(documents) == 1:
        return documents[0]

    # Create pairs of (query, text)
    pairs = [[query, doc.get("question", doc.get("text", ""))] for doc in documents]

    # Get scores
    scores = reranker.predict(pairs)

    # Sort by scores (higher is better for cross-encoder)
    ranked = list(zip(scores, documents))
    ranked.sort(key=lambda x: x[0], reverse=True)

    if top_k == 1:
        return ranked[0][1]
    else:
        return [doc for _, doc in ranked[:top_k]]


async def rerank_async(query: str, documents: list[dict], top_k: int = 1):
    """Asynchronous reranking"""
    return await run_with_queue(lambda: rerank(query, documents, top_k))