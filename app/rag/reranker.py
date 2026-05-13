from sentence_transformers import CrossEncoder


reranker = CrossEncoder(
    "BAAI/bge-reranker-base"
)


def rerank(query, documents):

    if len(documents) == 1:
        return documents[0]

    pairs = []

    for doc in documents:

        pairs.append([
            query,
            doc["question"]
        ])

    scores = reranker.predict(pairs)

    ranked = list(zip(scores, documents))

    ranked.sort(
        key=lambda x: x[0],
        reverse=True
    )

    best_doc = ranked[0][1]

    return best_doc