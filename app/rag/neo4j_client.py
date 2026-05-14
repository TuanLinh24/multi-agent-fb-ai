from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
from app.config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD
)

VECTOR_INDEX_CONFIGS = {
    "menu_vector_index": ("MenuItem", "embedding"),
    "chunk_vector_index": ("Chunk", "embedding"),
    "entity_vector_index": ("Entity", "embedding"),
}

class Neo4jClient:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(
                NEO4J_USER,
                NEO4J_PASSWORD
            )
        )

    def close(self):
        self.driver.close()

    def create_constraints(self):
        """Create uniqueness constraints for nodes"""
        with self.driver.session() as session:
            # MenuItem name uniqueness
            session.run("CREATE CONSTRAINT menu_item_name IF NOT EXISTS FOR (m:MenuItem) REQUIRE m.name IS UNIQUE")
            # Chunk id uniqueness
            session.run("CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE")
            # Entity name uniqueness
            session.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")

    def create_menu_item(self, item):
        with self.driver.session() as session:
            session.run(
                """
                CREATE (m:MenuItem {
                    name: $name,
                    price: $price,
                    category: $category,
                    description: $description,
                    size: $size,
                    ingredients: $ingredients
                })
                """,
                **item
            )

    def create_chunk(self, chunk_data):
        """Create a Chunk node"""
        with self.driver.session() as session:
            session.run(
                """
                MERGE (c:Chunk {id: $id})
                SET c.text = $text,
                    c.source = $source,
                    c.chunk_type = $chunk_type,
                    c.embedding = $embedding
                """,
                **chunk_data
            )

    def create_entity(self, entity_data):
        """Create an Entity node"""
        with self.driver.session() as session:
            session.run(
                """
                MERGE (e:Entity {name: $name})
                SET e.type = $type,
                    e.description = $description
                """,
                **entity_data
            )

    def create_relationship_next(self, chunk_id1, chunk_id2):
        """Create NEXT relationship between chunks"""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (c1:Chunk {id: $id1}), (c2:Chunk {id: $id2})
                CREATE (c1)-[:NEXT]->(c2)
                """,
                id1=chunk_id1, id2=chunk_id2
            )

    def create_relationship_mentions(self, chunk_id, entity_name):
        """Create MENTIONS relationship between chunk and entity"""
        with self.driver.session() as session:
            session.run(
                """
                MATCH (c:Chunk {id: $chunk_id}), (e:Entity {name: $entity_name})
                MERGE (c)-[:MENTIONS]->(e)
                """,
                chunk_id=chunk_id, entity_name=entity_name
            )

    def create_relationship_belongs_to(self, menu_name, category_name):
        """Create BELONGS_TO relationship between menu item and category"""
        with self.driver.session() as session:
            # First create category node if not exists
            session.run(
                """
                MERGE (cat:Category {name: $category_name})
                """,
                category_name=category_name
            )
            # Then create relationship
            session.run(
                """
                MATCH (m:MenuItem {name: $menu_name}), (cat:Category {name: $category_name})
                CREATE (m)-[:BELONGS_TO]->(cat)
                """,
                menu_name=menu_name, category_name=category_name
            )

    def show_indexes(self):
        """Return all indexes from Neo4j."""
        with self.driver.session() as session:
            return list(session.run("SHOW INDEXES"))

    def resolve_vector_index_name(self, index_name, node_label, property_name):
        """Find the actual vector index name by configured name or label/property match."""
        for record in self.show_indexes():
            if record["type"] != "VECTOR":
                continue
            if record["name"] == index_name:
                return index_name
            if record["labelsOrTypes"] == [node_label] and record["properties"] == [property_name]:
                return record["name"]
        return None

    def drop_index(self, index_name):
        """Drop an index by name if it exists."""
        with self.driver.session() as session:
            session.run(f"DROP INDEX {index_name} IF EXISTS")

    def get_or_create_vector_index_name(self, index_name, node_label, property_name, dimensions=768):
        actual_name = self.resolve_vector_index_name(index_name, node_label, property_name)
        if actual_name:
            return actual_name

        with self.driver.session() as session:
            session.run(
                f"""
                CREATE VECTOR INDEX {index_name} IF NOT EXISTS
                FOR (n:{node_label}) ON (n.{property_name})
                OPTIONS {{
                    indexConfig: {{
                        `vector.dimensions`: {dimensions},
                        `vector.similarity_function`: 'cosine'
                    }}
                }}
                """
            )

        actual_name = self.resolve_vector_index_name(index_name, node_label, property_name)
        return actual_name or index_name

    def create_vector_index(self, index_name, node_label, property_name, dimensions=768):
        """Create vector index for semantic search"""
        return self.get_or_create_vector_index_name(index_name, node_label, property_name, dimensions=dimensions)

    def vector_search(self, index_name, query_embedding, top_k=5):
        """Perform vector search"""
        actual_name = None
        node_label = None
        property_name = None

        if index_name in VECTOR_INDEX_CONFIGS:
            node_label, property_name = VECTOR_INDEX_CONFIGS[index_name]
            actual_name = self.resolve_vector_index_name(index_name, node_label, property_name)

        if not actual_name:
            actual_name = index_name

        print(f"[DEBUG] vector_search index_name={index_name}, actual_name={actual_name}, query_len={len(query_embedding)}")

        with self.driver.session() as session:
            try:
                result = session.run(
                    f"""
                    CALL db.index.vector.queryNodes('{actual_name}', $top_k, $query_embedding)
                    YIELD node, score
                    RETURN node, score
                    """,
                    top_k=top_k, query_embedding=query_embedding
                )
                return [(record["node"], record["score"]) for record in result]
            except Neo4jError as exc:
                message = str(exc).lower()
                print(f"[DEBUG] vector_search neo4j error: {message}")
                if index_name in VECTOR_INDEX_CONFIGS:
                    if "no such vector schema index" in message or "schema index" in message or "index query vector has" in message:
                        dimensions = len(query_embedding)
                        node_label, property_name = VECTOR_INDEX_CONFIGS[index_name]
                        actual_name = self.resolve_vector_index_name(index_name, node_label, property_name)
                        print(f"[DEBUG] resolve_vector_index_name returned {actual_name}")
                        if actual_name:
                            self.drop_index(actual_name)
                        actual_name = self.create_vector_index(
                            index_name,
                            node_label,
                            property_name,
                            dimensions=dimensions,
                        )
                        print(f"[DEBUG] recreated index name={actual_name}, dimensions={dimensions}")
                        result = session.run(
                            f"""
                            CALL db.index.vector.queryNodes('{actual_name}', $top_k, $query_embedding)
                            YIELD node, score
                            RETURN node, score
                            """,
                            top_k=top_k, query_embedding=query_embedding
                        )
                        return [(record["node"], record["score"]) for record in result]
                raise

    def get_adjacent_chunks(self, chunk_id, direction="both"):
        """Get adjacent chunks via NEXT relationships"""
        direction_query = {
            "next": "-[:NEXT]->",
            "prev": "<-[:NEXT]-",
            "both": "-[:NEXT]-"
        }[direction]

        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (c:Chunk {{id: $chunk_id}}){direction_query}(adjacent:Chunk)
                RETURN adjacent
                """,
                chunk_id=chunk_id
            )
            return [record["adjacent"] for record in result]

    def get_related_entities(self, chunk_id):
        """Get entities mentioned by a chunk"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Chunk {id: $chunk_id})-[:MENTIONS]->(e:Entity)
                RETURN e
                """,
                chunk_id=chunk_id
            )
            return [record["e"] for record in result]

    def get_related_chunks(self, entity_name):
        """Get chunks that mention an entity"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Chunk)-[:MENTIONS]->(e:Entity {name: $entity_name})
                RETURN c
                """,
                entity_name=entity_name
            )
            return [record["c"] for record in result]

    def clear_database(self):
        """Clear all nodes and relationships"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")