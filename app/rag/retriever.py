import numpy as np

from app.rag.embeddings import embed_text
from app.rag.vector_store import load_index


def retrieve_faq(query: str):

    index, metadata = load_index()

    if index is None:
        return None

    vector = embed_text(query)

    distances, indices = index.search(
        np.array(vector, dtype=np.float32),
        k=1
    )

    best_idx = indices[0][0]

    return metadata[best_idx]