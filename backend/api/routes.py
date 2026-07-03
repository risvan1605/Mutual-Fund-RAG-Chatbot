"""
API route definitions.
"""

import re
from fastapi import APIRouter, HTTPException
from backend.api.schemas import ChatRequest, ChatResponse
from backend.core.classifier import get_classifier
from backend.core.refusal_handler import get_refusal_response
from backend.core.rag_pipeline import get_rag_pipeline

router = APIRouter()


def detect_pii(query: str) -> bool:
    patterns = [
        r"[A-Z]{5}[0-9]{4}[A-Z]{1}",  # PAN
        r"[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}",  # Aadhaar
        r"(\+91)?[6-9][0-9]{9}",  # Phone
        r"[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}",  # Email
    ]
    for pattern in patterns:
        if re.search(pattern, query):
            return True
    return False


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. PII Check
    if detect_pii(query):
        return get_refusal_response("PII_DETECTED")

    # 2. Classify Query
    classifier = get_classifier()
    category = classifier.classify(query)

    # 3. Route to handler
    if category == "FACTUAL":
        pipeline = get_rag_pipeline()
        return pipeline.process_query(query)
    else:
        return get_refusal_response(category)


@router.get("/health")
async def health_check():
    try:
        pipeline = get_rag_pipeline()
        count = pipeline.collection.count()
        return {"status": "ok", "documents": count}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
