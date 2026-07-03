import sys
from pathlib import Path
import logging
import json

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.core import chat_flow

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_tests():
    test_queries = [
        # 1. Factual
        "What is the expense ratio of Nippon India Small Cap Fund?",
        # 2. Advisory
        "Should I invest in Nippon India Small Cap Fund?",
        "Which fund is better, ICICI Liquid or ABSL Gold?",
        # 3. Out of scope
        "What is the current stock price of Tesla?",
        "How do I open a bank account?",
        # 4. PII
        "My PAN is ABCDE1234F, what is the exit load?",
        "My Aadhaar is 1234 5678 9012, is this fund good?",
        "Call me at 9876543210 about this fund.",
    ]

    for i, query in enumerate(test_queries):
        print(f"\n{'='*70}")
        print(f"Test {i+1}: {query}")
        print(f"{'='*70}")

        result = chat_flow.process_chat_message(query)

        print("\nRESULT:")
        print(json.dumps(result, indent=2))
        print("\n")


if __name__ == "__main__":
    run_tests()
