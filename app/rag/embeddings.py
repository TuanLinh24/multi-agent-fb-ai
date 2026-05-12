from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer(
    "BAAI/bge-m3"
)


def embed_text(texts):

    return embedding_model.encode(texts)