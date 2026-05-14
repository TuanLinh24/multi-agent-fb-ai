import sys
sys.path.insert(0, '.')

from app.rag.embeddings import embed_text
from app.rag.neo4j_client import Neo4jClient

# Test embedding
print("Testing embedding...")
query = "What coffee do you have?"
embedding = embed_text(query)
print(f"Embedding length: {len(embedding)}")

# Test Neo4j connection
print("Testing Neo4j...")
client = Neo4jClient()
results = client.vector_search("chunk_vector_index", embedding, top_k=3)
print(f"Vector search results: {len(results)}")

for node, score in results:
    print(f"  Text: {node.get('text', '')[:100]}...")
    print(f"  Score: {score}")