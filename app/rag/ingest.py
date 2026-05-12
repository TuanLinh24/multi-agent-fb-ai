import pandas as pd
from app.rag.neo4j_client import Neo4jClient
from app.rag.hybrid_search import build_index

neo = Neo4jClient()


def ingest_menu():

    df = pd.read_csv("data/menu.csv")

    for _, row in df.iterrows():

        neo.create_menu_item({
            "name": row["name"],
            "price": int(row["price"]),
            "category": row["category"],
            "description": row["description"]
        })


def ingest_faq():

    df = pd.read_csv("data/faq.csv")

    docs = []

    for _, row in df.iterrows():

        docs.append(
            f"Q: {row['question']} A: {row['answer']}"
        )

    build_index(docs)