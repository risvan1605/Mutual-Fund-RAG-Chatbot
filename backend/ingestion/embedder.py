"""
Embedder — generates embeddings and stores them in ChromaDB.
"""

import time
import logging
from typing import List, Dict
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

import sys
from pathlib import Path

# Ensure backend module is in path if running standalone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mutual_fund_facts"


class Embedder:
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

        logger.info(f"Initializing ChromaDB client at {settings.CHROMA_PERSIST_DIR}")
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Get or create the collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Mutual fund fact chunks from Groww pages"},
        )

    def embed_and_store(self, chunks: List[Dict]) -> None:
        """
        Generates embeddings for all chunks and stores them in ChromaDB.
        """
        if not chunks:
            logger.warning("No chunks provided to embed_and_store.")
            return

        start_time = time.time()
        logger.info(f"Preparing to embed and store {len(chunks)} chunks...")

        texts = []
        metadatas = []
        ids = []

        for chunk in chunks:
            meta = chunk.copy()
            # Remove text from metadata payload since Chroma stores it separately as document
            text = meta.pop("text", "")
            chunk_id = meta.get("chunk_id")

            if not text or not chunk_id:
                logger.warning(
                    f"Skipping chunk due to missing text or chunk_id: {meta}"
                )
                continue

            texts.append(text)
            metadatas.append(meta)
            ids.append(chunk_id)

        if not texts:
            logger.warning("No valid chunks found after validation.")
            return

        logger.info(
            f"Generating embeddings for {len(texts)} chunks using {settings.EMBEDDING_MODEL} (this may take a moment)..."
        )
        # Batch generation
        embeddings = self.model.encode(texts, show_progress_bar=False).tolist()

        logger.info(
            f"Upserting {len(texts)} chunks to ChromaDB collection '{COLLECTION_NAME}'..."
        )
        self.collection.upsert(
            documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids
        )

        elapsed = time.time() - start_time
        logger.info(
            f"Successfully embedded and stored {len(texts)} chunks in {elapsed:.2f} seconds."
        )


def embed_and_store(chunks: List[Dict]) -> None:
    embedder = Embedder()
    embedder.embed_and_store(chunks)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sample_chunks = [
        {
            "chunk_id": "test_fund_001",
            "text": "The test fund has an expense ratio of 0.5%.",
            "scheme_name": "Test Fund",
            "category": "Testing",
        }
    ]
    embed_and_store(sample_chunks)
