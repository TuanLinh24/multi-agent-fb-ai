import numpy as np

from app.rag.embeddings import embed_text_async
from app.rag.vector_store import load_index
from app.rag.reranker import rerank
from app.graph.menu_graph import graph_expand


index, documents = load_index()


async def hybrid_search(query, top_k=5):
    if index is None:
        return []

    query_embedding = await embed_text_async(query)
    query_embedding = np.array(
        query_embedding,
        dtype=np.float32
    )

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    retrieved_docs = []
    for idx in indices[0]:
        if idx < len(documents):
            retrieved_docs.append(documents[idx])

    graph_docs = graph_expand(query)
    candidates = retrieved_docs + graph_docs

    if not candidates:
        return []

    best_doc = rerank(query, candidates)
    return best_doc


async def search(query, top_k=5):
    return await hybrid_search(query, top_k)
