from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def embed_text(text: str):

    vector = model.encode([text])

    return vector