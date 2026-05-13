import numpy as np

from app.rag.embeddings import embed_text
from app.rag.vector_store import load_index
from app.rag.reranker import rerank


index, documents = load_index()


def hybrid_search(query, top_k=5):

    if index is None:
        return None

    query_embedding = embed_text(query)

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

            retrieved_docs.append(
                documents[idx]
            )

    if not retrieved_docs:
        return None

    best_doc = rerank(
        query,
        retrieved_docs
    )

    return best_doc