import numpy as np
from typing import List, Dict, Any

from app.rag.embeddings import embed_text_async
from app.rag.neo4j_client import Neo4jClient
from app.rag.reranker import rerank_async


class HybridSearch:
    def __init__(self):
        self.neo4j_client = Neo4jClient()

    async def vector_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Perform vector search on chunks"""
        query_embedding = await embed_text_async(query)

        # Search in chunk vector index
        results = self.neo4j_client.vector_search(
            index_name="chunk_vector_index",
            query_embedding=query_embedding,
            top_k=top_k
        )

        # Convert to dict format
        docs = []
        for node, score in results:
            docs.append({
                "id": node.id,
                "text": node.get("text", ""),
                "score": score,
                "type": "vector"
            })

        return docs

    async def graph_expand(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Expand search using graph relationships"""
        # Find relevant entities first via vector search on entities
        query_embedding = await embed_text_async(query)

        entity_results = self.neo4j_client.vector_search(
            index_name="entity_vector_index",
            query_embedding=query_embedding,
            top_k=3  # Fewer entities for expansion
        )

        expanded_docs = []
        for entity_node, _ in entity_results:
            entity_name = entity_node.get("name", "")

            # Get related chunks via MENTIONS relationships
            related_chunks = self.neo4j_client.get_related_chunks(entity_name)

            for chunk in related_chunks[:2]:  # Limit per entity
                expanded_docs.append({
                    "id": chunk.id,
                    "text": chunk.get("text", ""),
                    "score": 0.8,  # Lower score for graph expansion
                    "type": "graph"
                })

        return expanded_docs[:top_k]

    async def hybrid_search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform hybrid search combining vector and graph-based retrieval"""
        # Get vector search results
        vector_docs = await self.vector_search(query, top_k=top_k*2)

        # Get graph expansion results
        graph_docs = await self.graph_expand(query, top_k=top_k//2)

        # Combine candidates
        candidates = vector_docs + graph_docs

        if not candidates:
            return {"text": "", "score": 0.0}

        # For now, just return the first result (skip reranking due to model issues)
        best_doc = candidates[0]

        return {
            "text": best_doc["text"],
            "score": best_doc["score"],
            "type": best_doc["type"]
        }


# Global instance
hybrid_search = HybridSearch()


async def search(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Main search function"""
    return await hybrid_search.hybrid_search(query, top_k)
