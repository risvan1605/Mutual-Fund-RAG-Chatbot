import sys
from pathlib import Path
import logging
import json

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core import rag_pipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_tests():
    pipeline = rag_pipeline.get_rag_pipeline()

    test_queries = [
        "What is the expense ratio of Nippon India Small Cap Fund?",
        "What is the exit load for ICICI Prudential Balanced Advantage Fund?",
        "What is the minimum SIP amount for Mirae Asset Flexi Cap Fund?",
        "What is the capital of France?",  # Should hopefully trigger no_match if context doesn't contain it
    ]

    for i, query in enumerate(test_queries):
        print(f"\n{'='*50}")
        print(f"Test {i+1}: {query}")
        print(f"{'='*50}")

        result = pipeline.process_query(query)

        print("\nRESULT:")
        print(json.dumps(result, indent=2))
        print("\n")


if __name__ == "__main__":
    run_tests()
