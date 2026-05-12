from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-m3")

CACHE = []


def cosine(a, b):

    return np.dot(a, b) / (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )


def get_cached(query):

    emb = model.encode([query])[0]

    for item in CACHE:

        sim = cosine(
            emb,
            item["embedding"]
        )

        if sim >= 0.92:
            return item["response"]

    return None


def add_cache(query, response):

    CACHE.append({
        "query": query,
        "response": response,
        "embedding": model.encode([query])[0]
    })