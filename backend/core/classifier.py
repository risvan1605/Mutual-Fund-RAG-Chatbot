"""
Query Classifier — keyword-based classification for reliability.

Uses pattern matching instead of an LLM call to avoid silent failures
on Streamlit Cloud. Defaults to FACTUAL so the RAG pipeline gets a
chance to answer (it has its own "no info" fallback).
"""

import re
import logging

logger = logging.getLogger(__name__)

# --- Advisory patterns (checked first) ---
ADVISORY_PATTERNS = [
    r"\bshould\s+i\b",
    r"\bwhich\s+(is|fund|one)\s+(better|best|good)\b",
    r"\bwhich\b.*\bbetter\b",
    r"\brecommend\b",
    r"\badvice\b",
    r"\badvise\b",
    r"\bsuggest\b",
    r"\bworth\s+(investing|buying)\b",
    r"\bgood\s+(investment|time\s+to)\b",
    r"\bbetter\s+(option|choice|fund)\b",
    r"\bpredict\b",
    r"\bforecast\b",
    r"\bfuture\s+(returns?|performance|value)\b",
    r"\bwill\s+(it|the\s+fund)\s+(go\s+up|grow|increase|rise)\b",
    r"\binvest\s+in\b.*\bor\b",
    r"\bcompare\b.*\bfund\b",
]

# --- Mutual fund / factual signal words ---
FACTUAL_SIGNALS = [
    r"\bexpense\s+ratio\b",
    r"\bnav\b",
    r"\bexit\s+load\b",
    r"\baum\b",
    r"\basset\s+under\s+management\b",
    r"\bsip\b",
    r"\bminimum\b.*\b(investment|sip|amount)\b",
    r"\bmutual\s+fund\b",
    r"\bfund\s+(manager|house|name|type|category|size)\b",
    r"\brisk\s*(level|category|rating)?\b",
    r"\bbenchmark\b",
    r"\breturns?\b",
    r"\bcagr\b",
    r"\block.?in\b",
    r"\bnippon\b",
    r"\bmotilal\b",
    r"\bmirae\b",
    r"\babsl\b",
    r"\baditya\s+birla\b",
    r"\bicici\b",
    r"\bgroww\b",
    r"\bscheme\b",
    r"\bdirect\s+(growth|plan)\b",
    r"\bflexi\s*cap\b",
    r"\bsmall\s*cap\b",
    r"\blarge\s*cap\b",
    r"\bmid\s*cap\b",
    r"\bmulti\s*cap\b",
    r"\belss\b",
    r"\btax\s+saver\b",
    r"\bbalanced\s+advantage\b",
    r"\bbluechip\b",
    r"\bpsu\b",
    r"\bvalue\s+discovery\b",
    r"\bliquid\s+fund\b",
]

# --- Out-of-scope keywords (clearly not mutual funds) ---
OUT_OF_SCOPE_SIGNALS = [
    r"\bweather\b",
    r"\bcricket\b",
    r"\bfootball\b",
    r"\bmovie\b",
    r"\brecipe\b",
    r"\bcook\b",
    r"\bpolitics\b",
    r"\belection\b",
    r"\bcrypto\b",
    r"\bbitcoin\b",
    r"\betherre?um\b",
    r"\bforex\b",
    r"\bjoke\b",
    r"\bwho\s+(is|are|was)\s+(the\s+)?(president|prime\s+minister|king|queen)\b",
    r"\bcapital\s+of\b",
    r"\bpopulation\b",
    r"\bhello\b",
    r"\bhi\b$",
    r"^hey\b",
    r"\bhow\s+are\s+you\b",
    r"\btell\s+me\s+a\b",
]


class QueryClassifier:
    def classify(self, query: str) -> str:
        """
        Classifies the query into FACTUAL, ADVISORY, or OUT_OF_SCOPE
        using keyword / regex matching.
        """
        q = query.lower().strip()
        logger.info(f"Classifying query: '{query}'")

        # 1. Check advisory patterns first
        for pattern in ADVISORY_PATTERNS:
            if re.search(pattern, q, re.IGNORECASE):
                logger.info("Classified as ADVISORY (keyword match)")
                return "ADVISORY"

        # 2. Check for clear out-of-scope queries
        has_factual_signal = any(
            re.search(p, q, re.IGNORECASE) for p in FACTUAL_SIGNALS
        )
        if not has_factual_signal:
            for pattern in OUT_OF_SCOPE_SIGNALS:
                if re.search(pattern, q, re.IGNORECASE):
                    logger.info("Classified as OUT_OF_SCOPE (keyword match)")
                    return "OUT_OF_SCOPE"

        # 3. Default to FACTUAL — let the RAG pipeline decide if it can answer.
        #    The RAG pipeline has its own "no info" fallback for unmatched queries.
        logger.info("Classified as FACTUAL (default / keyword match)")
        return "FACTUAL"


# Singleton instance
_classifier = None


def get_classifier() -> QueryClassifier:
    global _classifier
    if _classifier is None:
        _classifier = QueryClassifier()
    return _classifier

