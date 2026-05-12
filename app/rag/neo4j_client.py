from neo4j import GraphDatabase
from app.config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD
)

class Neo4jClient:

    def __init__(self):

        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(
                NEO4J_USER,
                NEO4J_PASSWORD
            )
        )

    def create_menu_item(self, item):

        with self.driver.session() as session:

            session.run(
                """
                CREATE (m:MenuItem {
                    name: $name,
                    price: $price,
                    category: $category,
                    description: $description
                })
                """,
                **item
            )