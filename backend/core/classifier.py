"""
Query Classifier using lightweight LLM to determine intent.
"""

import logging
from groq import Groq
import sys
from pathlib import Path

# Ensure backend module is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.config import settings

logger = logging.getLogger(__name__)

# Use a smaller/faster model for classification to save tokens on the primary model
CLASSIFIER_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """Classify the following user query into exactly one of these categories:
- FACTUAL: Questions about fund details (expense ratio, NAV, exit load, SIP, etc.)
- ADVISORY: Questions asking for investment advice, recommendations, predictions, or comparisons ("Should I invest?", "Which is better?")
- OUT_OF_SCOPE: Questions unrelated to mutual funds (e.g. stocks, crypto, banking, weather, general trivia)

Respond with ONLY the category name. Do not include any other text, punctuation, or explanation."""


class QueryClassifier:
    def __init__(self):
        logger.info(f"Initializing Query Classifier with model: {CLASSIFIER_MODEL}")
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def classify(self, query: str) -> str:
        """
        Classifies the query into FACTUAL, ADVISORY, or OUT_OF_SCOPE.
        """
        try:
            logger.info(f"Classifying query: '{query}'")
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": query},
                ],
                model=CLASSIFIER_MODEL,
                temperature=0.0,  # zero temp for deterministic classification
                max_tokens=10,  # we only need 1 word
            )

            category = response.choices[0].message.content.strip().upper()

            # Clean up potential LLM verbosity
            if "FACTUAL" in category:
                return "FACTUAL"
            if "ADVISORY" in category:
                return "ADVISORY"
            if "OUT_OF_SCOPE" in category:
                return "OUT_OF_SCOPE"

            # Default fallback if LLM returned something unexpected
            logger.warning(
                f"Unexpected classification response: {category}. Defaulting to OUT_OF_SCOPE."
            )
            return "OUT_OF_SCOPE"

        except Exception as e:
            logger.error(f"Error during classification: {e}")
            # Safe fallback
            return "OUT_OF_SCOPE"


# Singleton instance
_classifier = None


def get_classifier() -> QueryClassifier:
    global _classifier
    if _classifier is None:
        _classifier = QueryClassifier()
    return _classifier
