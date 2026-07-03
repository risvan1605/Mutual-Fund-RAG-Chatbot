"""
Chat Flow orchestrator — combines PII detection, classification, and RAG generation.
"""

import logging
from typing import Dict, Any

from backend.core.pii_detector import detect_pii
from backend.core.classifier import get_classifier
from backend.core.refusal_handler import get_refusal_response
from backend.core.rag_pipeline import get_rag_pipeline

logger = logging.getLogger(__name__)


def process_chat_message(query: str) -> Dict[str, Any]:
    """
    Main entry point for a user chat message.
    1. Checks for PII
    2. Classifies query
    3. Returns refusal OR delegates to RAG pipeline
    """

    # 1. PII Detection (regex-based, no LLM call)
    has_pii, pii_type = detect_pii(query)
    if has_pii:
        logger.warning(f"PII Detected ({pii_type}) in query. Blocking request.")
        return get_refusal_response("PII_DETECTED")

    # 2. Query Classification
    classifier = get_classifier()
    category = classifier.classify(query)

    # 3. Route accordingly
    if category == "FACTUAL":
        logger.info("Query classified as FACTUAL. Routing to RAG pipeline.")
        rag_pipeline = get_rag_pipeline()
        return rag_pipeline.process_query(query)
    else:
        logger.info(f"Query classified as {category}. Routing to Refusal Handler.")
        return get_refusal_response(category)
