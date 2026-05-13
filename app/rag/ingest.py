import pandas as pd
import numpy as np
import faiss

from app.rag.embeddings import embed_text
from app.rag.vector_store import save_index


def ingest_faq():

    df = pd.read_csv("data/faq.csv")

    questions = df["question"].tolist()

    embeddings = []

    metadata = []

    for idx, row in df.iterrows():

        vector = embed_text(
            row["question"]
        )[0]

        embeddings.append(vector)

        metadata.append({
            "question": row["question"],
            "answer": row["answer"]
        })

    embeddings = np.array(
        embeddings,
        dtype=np.float32
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    save_index(index, metadata)

    print("FAQ ingestion completed.")