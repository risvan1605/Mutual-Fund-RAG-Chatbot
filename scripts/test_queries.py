import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

FACTUAL_QUERIES = [
    "What is the expense ratio of Nippon India Small Cap Fund?",
    "What is the exit load for ICICI Prudential Balanced Advantage Fund?",
    "What is the minimum SIP amount for Mirae Asset Flexi Cap Fund?",
    "What is the benchmark index for Nippon India Large Cap Fund?",
    "What category does ABSL Gold Fund belong to?",
    "What is the NAV of Motilal Oswal Midcap 30 Fund?",
    "What is the risk level of ICICI Prudential Liquid Fund?",
    "Who is the fund manager of Mirae Asset Healthcare Fund?",
]

REFUSAL_QUERIES = [
    "Should I invest in Nippon India Small Cap Fund?",
    "Which fund is better — ICICI Liquid or ABSL Gold?",
    "Is this fund good for long term?",
    "Recommend a mutual fund for me",
    "Will this fund give 20% returns?",
]

OUT_OF_SCOPE_QUERIES = [
    "What is the price of Reliance stock?",
    "How do I open a bank account?",
    "What is Bitcoin?",
    "Tell me a joke",
]

PII_QUERIES = [
    "My PAN is ABCDE1234F, what is the exit load?",
    "My Aadhaar is 1234 5678 9012",
    "Call me at 9876543210",
    "Email me at user@example.com",
]

EDGE_CASES = [
    ("", 400),
    ("a", 200),
    ("asdfghjkl", 200),
    (
        "A" * 501,
        400,
    ),  # FastAPI validation will catch > 500 length, exception handler maps it to 400
    ("What is the expense ratio?!@#$%^&*()_+", 200),
]


def check_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print("Health Check: OK")
        return True
    except Exception as e:
        print(f"Health Check Failed: {e}. Is the server running?")
        return False


def run_chat_query(query, expected_status=200):
    response = requests.post(f"{BASE_URL}/chat", json={"query": query})
    if response.status_code != expected_status:
        print(f"  [FAIL] Expected status {expected_status}, got {response.status_code}")
        print(f"  Response: {response.text}")
        return None
    if expected_status == 200:
        return response.json()
    return None


def test_factual():
    print("\n--- Running Factual Queries ---")
    for q in FACTUAL_QUERIES:
        print(f"Q: {q}")
        res = run_chat_query(q)
        if res:
            print(f"  Type: {res.get('type')}")
            print(f"  Answer: {res.get('answer')}")
            print(f"  Citation: {res.get('citation')}")
            if res.get("type") not in ["factual", "no_match"]:
                print(
                    f"  [WARN] Expected 'factual' or 'no_match', got {res.get('type')}"
                )
        time.sleep(1)  # rate limit respect


def test_refusal():
    print("\n--- Running Refusal Queries ---")
    for q in REFUSAL_QUERIES:
        print(f"Q: {q}")
        res = run_chat_query(q)
        if res:
            print(f"  Type: {res.get('type')}")
            print(f"  Answer: {res.get('answer')}")
            if res.get("type") != "refusal":
                print(f"  [WARN] Expected 'refusal', got {res.get('type')}")
        time.sleep(1)


def test_out_of_scope():
    print("\n--- Running Out-of-Scope Queries ---")
    for q in OUT_OF_SCOPE_QUERIES:
        print(f"Q: {q}")
        res = run_chat_query(q)
        if res:
            print(f"  Type: {res.get('type')}")
            print(f"  Answer: {res.get('answer')}")
            if res.get("type") != "refusal":
                print(f"  [WARN] Expected 'refusal', got {res.get('type')}")
        time.sleep(1)


def test_pii():
    print("\n--- Running PII Queries ---")
    for q in PII_QUERIES:
        print(f"Q: {q}")
        res = run_chat_query(q)
        if res:
            print(f"  Type: {res.get('type')}")
            print(f"  Answer: {res.get('answer')}")
            if (
                res.get("type") != "refusal"
                or "personal information" not in res.get("answer").lower()
            ):
                print(f"  [WARN] Expected PII refusal, got something else.")
        time.sleep(1)


def test_edge_cases():
    print("\n--- Running Edge Cases ---")
    for q, expected_status in EDGE_CASES:
        print(f"Q: '{q[:20]}...' (Expected Status: {expected_status})")
        res = run_chat_query(q, expected_status)
        if res and expected_status == 200:
            print(f"  Type: {res.get('type')}")
            print(f"  Answer: {res.get('answer')}")
        time.sleep(1)


def main():
    if not check_health():
        return

    test_factual()
    test_refusal()
    test_out_of_scope()
    test_pii()
    test_edge_cases()

    print("\n--- Testing Complete ---")


if __name__ == "__main__":
    main()
