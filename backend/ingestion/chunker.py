"""
Document chunker — packages extracted structured text into chunks.
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def chunk_document(text: str, metadata: Dict) -> List[Dict]:
    """
    Since the extractor now returns highly structured, concise JSON-derived text,
    we can treat the entire text as a single chunk for perfect context retention.
    """
    if not text:
        return []

    scheme_name = metadata.get("scheme_name", "Unknown")
    safe_scheme_name = scheme_name.lower().replace(" ", "_").replace("&", "and")

    # We only need 1 chunk per fund now because the text is very concise.
    chunk_metadata = {
        "chunk_id": f"{safe_scheme_name}_chunk_000",
        "source_url": metadata.get("url", ""),
        "source_title": f"{scheme_name} — Groww",
        "scheme_name": scheme_name,
        "category": metadata.get("category", ""),
        "amc": metadata.get("amc", ""),
        "scraped_date": metadata.get("scraped_date", ""),
        "chunk_index": 0,
        "total_chunks": 1,
        "text": text,
    }

    return [chunk_metadata]


def process_all_documents(documents: List[Dict]) -> List[Dict]:
    """
    Takes a list of dictionaries (where each dict has 'text' and metadata)
    and returns a flat list of chunks.
    """
    all_chunks = []
    for doc in documents:
        text = doc.get("text", "")
        if not text:
            continue

        chunks = chunk_document(text, doc)
        all_chunks.extend(chunks)

    logger.info(f"Packaged {len(documents)} documents into {len(all_chunks)} chunks.")
    return all_chunks
