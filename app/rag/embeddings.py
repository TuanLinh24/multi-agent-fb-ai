from sentence_transformers import SentenceTransformer

# Using a simpler multilingual embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def embed_text(text: str):
    """Synchronous embedding for single text"""
    vector = model.encode([text], normalize_embeddings=True)
    return vector[0].tolist()  # Return as list for Neo4j storage


async def embed_text_async(text: str):
    """Asynchronous embedding for single text"""
    # Simple async wrapper for now
    return embed_text(text)
