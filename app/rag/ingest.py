import pandas as pd
import re
import hashlib
from pathlib import Path
from typing import List

from app.rag.embeddings import embed_text
from app.rag.neo4j_client import Neo4jClient


class DataIngestionPipeline:
    """Data ingestion pipeline for menu, FAQ, and documents"""

    def __init__(self):
        self.neo4j_client = Neo4jClient()
        self.chunk_size = 512  # Characters per chunk
        self.chunk_overlap = 50

    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += " " + sentence
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def extract_entities(self, text: str) -> List[str]:
        """Extract named entities (simple keyword extraction)"""
        # Vietnamese stopwords
        stopwords = {
            'là', 'cái', 'chiếc', 'của', 'và', 'với', 'trong', 'có', 'không',
            'được', 'là', 'hay', 'như', 'khi', 'những', 'bạn', 'đó', 'các'
        }

        # Split and filter
        words = text.lower().split()
        entities = []

        for word in words:
            cleaned_word = re.sub(r'[^\w\u0100-\uFFFF]', '', word)
            if (len(cleaned_word) > 3 and
                cleaned_word not in stopwords and
                cleaned_word.isalpha()):
                entities.append(cleaned_word)

        # Return unique entities
        return list(set(entities))[:10]  # Limit to top 10

    def ingest_menu(self, csv_path: str = "data/menu.csv"):
        """Ingest menu items from CSV"""
        print(f"Ingesting menu from {csv_path}...")

        df = pd.read_csv(csv_path)

        for idx, row in df.iterrows():
            menu_id = hashlib.md5(row['name'].encode()).hexdigest()[:8]

            # Create menu item node
            chunk_text = f"{row['name']}. {row['description']}. Price: {row['price']} VND."
            embedding = embed_text(chunk_text)

            self.neo4j_client.create_chunk({
                "id": menu_id,
                "text": chunk_text,
                "source": "menu",
                "chunk_type": "menu_item",
                "embedding": embedding
            })

            # Create BELONGS_TO relationship
            self.neo4j_client.create_relationship_belongs_to(
                menu_name=row['name'],
                category_name=row['category']
            )

            # Extract and create entities
            entities = self.extract_entities(chunk_text)
            for entity in entities:
                self.neo4j_client.create_entity({
                    "name": entity,
                    "type": "MenuItem",
                    "description": ""
                })
                self.neo4j_client.create_relationship_mentions(
                    chunk_id=menu_id,
                    entity_name=entity
                )

        print(f"✓ Ingested {len(df)} menu items")

    def ingest_faq(self, csv_path: str = "data/faq.csv"):
        """Ingest FAQ items from CSV"""
        print(f"Ingesting FAQ from {csv_path}...")

        df = pd.read_csv(csv_path)

        for idx, row in df.iterrows():
            question_id = hashlib.md5(row['question'].encode()).hexdigest()[:8]

            # Create Q&A text
            qa_text = f"Q: {row['question']} A: {row['answer']}"
            embedding = embed_text(qa_text)

            self.neo4j_client.create_chunk({
                "id": question_id,
                "text": qa_text,
                "source": "faq",
                "chunk_type": "faq",
                "embedding": embedding
            })

            # Extract entities and create relationships
            entities = self.extract_entities(qa_text)
            for entity in entities:
                self.neo4j_client.create_entity({
                    "name": entity,
                    "type": "FAQTopic",
                    "description": ""
                })
                self.neo4j_client.create_relationship_mentions(
                    chunk_id=question_id,
                    entity_name=entity
                )

        print(f"✓ Ingested {len(df)} FAQ items")

    def ingest_documents(self, doc_dir: str = "data/documents"):
        """Ingest documents (PDF, DOCX) with semantic chunking"""
        print(f"Ingesting documents from {doc_dir}...")

        doc_path = Path(doc_dir)
        if not doc_path.exists():
            print(f"Document directory {doc_dir} not found, skipping...")
            return

        doc_count = 0
        for doc_file in doc_path.glob("*.*"):
            if doc_file.suffix.lower() in ['.pdf', '.docx', '.txt']:
                try:
                    if doc_file.suffix.lower() == '.txt':
                        text = doc_file.read_text(encoding='utf-8')
                    else:
                        # Skip binary formats for now
                        continue

                    chunks = self.chunk_text(text)

                    for chunk_idx, chunk in enumerate(chunks):
                        if not chunk.strip():
                            continue

                        chunk_id = hashlib.md5(
                            f"{doc_file.name}_{chunk_idx}".encode()
                        ).hexdigest()[:8]

                        embedding = embed_text(chunk)

                        self.neo4j_client.create_chunk({
                            "id": chunk_id,
                            "text": chunk,
                            "source": "document",
                            "chunk_type": "document",
                            "embedding": embedding
                        })

                        # Create NEXT relationships for sequential chunks
                        if chunk_idx > 0:
                            prev_chunk_id = hashlib.md5(
                                f"{doc_file.name}_{chunk_idx - 1}".encode()
                            ).hexdigest()[:8]
                            self.neo4j_client.create_relationship_next(
                                prev_chunk_id,
                                chunk_id
                            )

                        # Extract entities
                        entities = self.extract_entities(chunk)
                        for entity in entities:
                            self.neo4j_client.create_entity({
                                "name": entity,
                                "type": "Topic",
                                "description": ""
                            })
                            self.neo4j_client.create_relationship_mentions(
                                chunk_id=chunk_id,
                                entity_name=entity
                            )

                    doc_count += 1

                except Exception as e:
                    print(f"✗ Error ingesting {doc_file.name}: {e}")

        print(f"✓ Ingested {doc_count} documents")

    def run_all(self):
        """Run complete ingestion pipeline"""
        print("=" * 50)
        print("Starting Data Ingestion Pipeline")
        print("=" * 50)

        try:
            self.ingest_menu()
            self.ingest_faq()
            self.ingest_documents()

            print("=" * 50)
            print("✓ Data ingestion completed successfully!")
            print("=" * 50)

        except Exception as e:
            print(f"✗ Ingestion error: {e}")
            raise


# Convenience functions for backward compatibility
def ingest_faq():
    """Legacy function for FAQ ingestion"""
    pipeline = DataIngestionPipeline()
    pipeline.ingest_faq()


def ingest_menu():
    """Ingest menu items"""
    pipeline = DataIngestionPipeline()
    pipeline.ingest_menu()


def run_ingestion():
    """Run complete ingestion"""
    pipeline = DataIngestionPipeline()
    pipeline.run_all()


if __name__ == "__main__":
    run_ingestion()