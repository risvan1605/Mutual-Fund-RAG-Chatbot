"""
PII Detection module to catch sensitive info before LLM processing.
"""

import re
from typing import Dict, Any, Tuple

# Patterns for Indian PII formats
PII_PATTERNS = {
    "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", re.IGNORECASE),
    "Aadhaar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "Phone": re.compile(r"\b(?:\+91[\-\s]?)?[6789]\d{9}\b"),
    "Email": re.compile(r"\b[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,}\b"),
}


def detect_pii(query: str) -> Tuple[bool, str]:
    """
    Checks the query against PII patterns.
    Returns (has_pii, matched_type).
    """
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(query):
            return True, pii_type

    return False, ""
