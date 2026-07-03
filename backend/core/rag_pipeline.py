"""
RAG Pipeline — handles context retrieval and answer generation.
"""

import os
# Suppress HuggingFace and Tokenizers warnings in constrained environments
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from groq import Groq

import sys
from pathlib import Path

# Ensure backend module is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.config import settings
from backend.core.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mutual_fund_facts"


class RAGPipeline:
    def __init__(self):
        logger.info(
            f"Initializing RAG Pipeline with embedding model: {settings.EMBEDDING_MODEL}"
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

        logger.info(f"Connecting to ChromaDB at {settings.CHROMA_PERSIST_DIR}")
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)

        logger.info(f"Initializing Groq client with model: {settings.LLM_MODEL}")
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)

    def retrieve_context(self, query: str) -> List[Dict[str, Any]]:
        """
        Embeds the query and retrieves the top most similar chunks from ChromaDB.
        """
        logger.info(f"Retrieving context for query: '{query}'")

        # Embed query
        query_embedding = self.embedding_model.encode(
            [query], show_progress_bar=False
        ).tolist()

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=5,
        )

        # Extract metadata and distances
        chunks = []
        if results and "metadatas" in results and results["metadatas"]:
            # Results are returned as lists of lists (batch size 1)
            metadatas = results["metadatas"][0]
            documents = (
                results["documents"][0]
                if "documents" in results and results["documents"]
                else []
            )

            for i in range(len(metadatas)):
                # Return chunks with metadata
                chunk_data = metadatas[i].copy()
                if i < len(documents):
                    chunk_data["text"] = documents[i]
                chunks.append(chunk_data)

        # Simple reranking: we just take the top 3 chunks (since they are already sorted by distance)
        top_chunks = chunks[:3]
        return top_chunks

    def handle_no_context(self) -> Dict[str, Any]:
        """
        Fallback when no matching context is found.
        """
        return {
            "answer": "I don't have this information in my current sources.",
            "citation": None,
            "last_updated": None,
            "type": "no_match",
        }

    def generate_answer(
        self, query: str, context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calls Groq API to generate an answer based on the provided context chunks.
        """
        if not context_chunks:
            return self.handle_no_context()

        # Format context string
        context_text = "\n\n".join(
            [
                f"--- Chunk {i+1} ---\n{chunk.get('text', '')}"
                for i, chunk in enumerate(context_chunks)
            ]
        )

        # Format prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            retrieved_chunks=context_text, user_query=query
        )

        try:
            logger.info("Generating answer with Groq API...")
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                model=settings.LLM_MODEL,
                temperature=0.1,  # Keep it highly factual
                max_tokens=150,
            )

            answer = response.choices[0].message.content.strip()

            # Extract citation from the top chunk (most relevant)
            top_chunk = context_chunks[0]
            citation = {
                "url": top_chunk.get("source_url", ""),
                "title": top_chunk.get("source_title", "Groww"),
            }
            last_updated = top_chunk.get("scraped_date", None)

            # Enforce fallback if the LLM output matched the fallback phrase
            if (
                "I don't have this information" in answer
                or "I do not have this information" in answer
            ):
                return self.handle_no_context()

            return {
                "answer": answer,
                "citation": citation,
                "last_updated": last_updated,
                "type": "factual",
            }

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Error generating answer: {e}\n{tb}")
            return {
                "answer": f"I encountered an error while trying to process your request:\n\n**Error:** {e}\n\n**Details:**\n```\n{tb}\n```",
                "citation": None,
                "last_updated": None,
                "type": "error",
            }

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        End-to-end RAG processing for a single query.
        """
        context_chunks = self.retrieve_context(query)
        return self.generate_answer(query, context_chunks)


# Create a singleton instance if needed for easy importing
_pipeline_instance = None


def get_rag_pipeline() -> RAGPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RAGPipeline()
    return _pipeline_instance


def process_query(query: str) -> Dict[str, Any]:
    pipeline = get_rag_pipeline()
    return pipeline.process_query(query)
