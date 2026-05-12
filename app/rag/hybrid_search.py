import faiss
import numpy as np
from app.rag.embeddings import embed_text

DOCUMENTS = []
INDEX = None


def build_index(texts):

    global INDEX
    global DOCUMENTS

    DOCUMENTS = texts

    embeddings = embed_text(texts)

    embeddings = np.array(
        embeddings,
        dtype=np.float32
    )

    dim = embeddings.shape[1]

    INDEX = faiss.IndexFlatL2(dim)

    INDEX.add(embeddings)


def search(query, top_k=3):

    q = embed_text([query])

    q = np.array(q, dtype=np.float32)

    distances, indices = INDEX.search(q, top_k)

    results = []

    for idx in indices[0]:
        results.append(DOCUMENTS[idx])

    return results