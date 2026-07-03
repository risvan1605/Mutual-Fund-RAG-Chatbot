"""
Refusal handler to generate standard responses for out-of-scope or advisory queries.
"""

from typing import Dict, Any


def get_refusal_response(category: str) -> Dict[str, Any]:
    """
    Returns a standardized refusal response based on the category.
    """

    if category == "ADVISORY":
        answer = "I can only provide factual information about mutual funds based on official documents. I cannot provide investment advice, recommendations, or predict future performance."
        citation = {
            "title": "AMFI Knowledge Center",
            "url": "https://www.amfiindia.com/investor-corner/knowledge-center",
        }
    elif category == "OUT_OF_SCOPE":
        answer = "This question is outside my scope. I am a factual FAQ assistant specifically designed to answer queries about mutual fund schemes based on Groww."
        citation = {"title": "AMFI India Homepage", "url": "https://www.amfiindia.com/"}
    elif category == "PII_DETECTED":
        answer = "Please avoid sharing personal information like PAN, Aadhaar, Phone Numbers, or Emails. I have blocked this query to protect your privacy."
        citation = None
    else:
        # Generic refusal
        answer = "I cannot process this query based on my current constraints."
        citation = None

    return {
        "answer": answer,
        "citation": citation,
        "last_updated": None,
        "type": "refusal",
    }
