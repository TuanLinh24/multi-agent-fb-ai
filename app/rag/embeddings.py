# Using a 768-dimensional multilingual embedding model
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_text(text: str):
    """Synchronous embedding for single text"""
    model = _get_model()
    vector = model.encode([text], normalize_embeddings=True)
    return vector[0].tolist()  # Return as list for Neo4j storage


async def embed_text_async(text: str):
    """Asynchronous embedding for single text"""
    return embed_text(text)
