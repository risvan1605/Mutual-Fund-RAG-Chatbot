"""
Pydantic request/response schemas for the FastAPI backend.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)


class Citation(BaseModel):
    url: str
    title: str


class ChatResponse(BaseModel):
    answer: str
    citation: Optional[Citation]
    last_updated: Optional[str]
    type: Literal["factual", "refusal", "no_match", "error"]
