#!/usr/bin/env python3
"""
Setup Neo4j Graph Database Schema for Coffee Shop RAG
"""

from app.rag.neo4j_client import Neo4jClient

def setup_schema():
    client = Neo4jClient()

    try:
        # Create constraints
        print("Creating constraints...")
        client.create_constraints()

        # Create vector indexes
        print("Creating vector indexes...")
        client.create_vector_index("menu_embedding", "MenuItem", "embedding")
        client.create_vector_index("chunk_embedding", "Chunk", "embedding")

        print("Schema setup completed successfully!")

    except Exception as e:
        print(f"Error setting up schema: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    setup_schema()