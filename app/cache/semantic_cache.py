import numpy as np

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
_model = None
CACHE = []


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def cosine(a, b):

    return np.dot(a, b) / (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )


def get_cached(query):

    emb = _get_model().encode([query])[0]

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
        "embedding": _get_model().encode([query])[0]
    })


class SemanticCache:
    """Simple in-memory semantic cache wrapper."""

    def __init__(self):
        self._cache = CACHE

    async def get(self, query: str):
        return get_cached(query)

    async def set(self, query: str, response: str):
        add_cache(query, response)
        return True
