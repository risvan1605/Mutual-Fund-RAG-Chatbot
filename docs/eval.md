# Evaluation Criteria — Mutual Fund FAQ Assistant

> **Reference:** [implementation_plan.md](file:///Users/ris/Cursor/RAG%20Chatbot/implementation_plan.md) · [architecture.md](file:///Users/ris/Cursor/RAG%20Chatbot/architecture.md) · [edge_cases.md](file:///Users/ris/Cursor/RAG%20Chatbot/edge_cases.md)

This document defines **testable evaluation criteria** for each phase of the implementation plan. Each phase has structured test cases, expected outputs, pass/fail conditions, and scoring rubrics.

---

## Evaluation Summary

| Phase | Tests | Pass Threshold | Critical Failures |
|---|---|---|---|
| **Phase 0** — Project Setup | 8 checks | 8/8 (100%) | Missing dependency, broken config |
| **Phase 1** — Data Ingestion | 14 checks | 12/14 (85%) | 0 chunks indexed, scraper crash |
| **Phase 2** — RAG Pipeline | 18 checks | 15/18 (83%) | Wrong fund data returned, no citation |
| **Phase 3** — Classification & Refusal | 22 checks | 20/22 (91%) | Advisory query answered, PII leaked |
| **Phase 4** — FastAPI Backend | 16 checks | 14/16 (87%) | Server crash, 500 on valid input |
| **Phase 5** — Chat UI | 14 checks | 12/14 (85%) | UI broken, XSS vulnerability |
| **Phase 6** — Integration & Testing | 30 checks | 27/30 (90%) | End-to-end failure, compliance breach |
| **Phase 7** — Polish & Documentation | 10 checks | 9/10 (90%) | API key exposed, setup fails |

---

## Phase 0 — Project Setup & Scaffolding

### Evaluation Criteria

| # | Test | Command / Method | Expected Result | Pass/Fail |
|---|---|---|---|---|
| 0.1 | Directory structure exists | `find backend/ frontend/ scripts/ -type f` | All files from architecture §4 are present | ☐ |
| 0.2 | `requirements.txt` is valid | `pip install -r backend/requirements.txt` | Installs without errors | ☐ |
| 0.3 | Virtual environment works | `python -c "import fastapi; import chromadb; import groq"` | No import errors | ☐ |
| 0.4 | `.env` file exists | `cat backend/.env` | Contains `GROQ_API_KEY`, `EMBEDDING_MODEL`, `LLM_MODEL`, `CHROMA_PERSIST_DIR` | ☐ |
| 0.5 | `config.py` loads env vars | `python -c "from backend.config import *; print(GROQ_API_KEY)"` | Prints the key value (not `None`) | ☐ |
| 0.6 | `.gitignore` configured | `cat .gitignore` | Contains `.env`, `chroma_db/`, `__pycache__/`, `*.pyc` | ☐ |
| 0.7 | `sources.json` has 15 URLs | `python -c "import json; d=json.load(open('backend/ingestion/sources.json')); print(sum(len(a['schemes']) for a in d['amcs']))"` | Prints `15` | ☐ |
| 0.8 | All `__init__.py` files exist | `ls backend/api/__init__.py backend/core/__init__.py backend/ingestion/__init__.py` | All exist | ☐ |

### Scoring
- **Pass:** 8/8
- **Acceptable:** 7/8 (minor file missing)
- **Fail:** < 7/8

---

## Phase 1 — Data Ingestion Pipeline

### 1A. Scraping Tests

| # | Test | Method | Expected Result | Pass/Fail |
|---|---|---|---|---|
| 1.1 | All 15 URLs are reachable | `scraper.scrape_all_sources()` | 15/15 return HTTP 200 | ☐ |
| 1.2 | Scraper handles 404 gracefully | Mock a bad URL, run scraper | Logs warning, skips URL, continues | ☐ |
| 1.3 | Scraper handles timeout | Set timeout=0.001 for one URL | Retries, logs failure, continues | ☐ |
| 1.4 | Rate limiting works | Measure time for 15 requests | ≥ 14 seconds (1s delay × 14 gaps) | ☐ |
| 1.5 | Scraped HTML is non-empty | Check `len(html)` for each URL | > 5000 characters for each page | ☐ |

### 1B. Extraction Tests

| # | Test | Method | Expected Result | Pass/Fail |
|---|---|---|---|---|
| 1.6 | Extracted text contains fund name | `"Nippon India Small Cap Fund" in extracted_text` | True for each scheme | ☐ |
| 1.7 | Extracted text contains key data | Search for "expense ratio", "exit load", "NAV" | At least 2 of 3 present per scheme | ☐ |
| 1.8 | No HTML tags in extracted text | `re.search(r'<[a-zA-Z]', extracted_text)` | Returns `None` | ☐ |
| 1.9 | No script/style content | Search for "function()", "display:", "var " | None found | ☐ |

### 1C. Chunking Tests

| # | Test | Method | Expected Result | Pass/Fail |
|---|---|---|---|---|
| 1.10 | Chunks are within size limit | `len(chunk) <= 600` (tokens, with tolerance) | True for all chunks | ☐ |
| 1.11 | Chunk metadata is complete | Check every chunk has all metadata fields | All 8 fields present: `chunk_id`, `source_url`, `source_title`, `scheme_name`, `category`, `amc`, `scraped_date`, `chunk_index` | ☐ |
| 1.12 | Total chunks are reasonable | Count total chunks across 15 URLs | Between 50 and 300 chunks | ☐ |

### 1D. Embedding & Storage Tests

| # | Test | Method | Expected Result | Pass/Fail |
|---|---|---|---|---|
| 1.13 | ChromaDB collection exists | `chroma_client.get_collection("mutual_fund_facts")` | Returns collection object, no error | ☐ |
| 1.14 | ChromaDB document count matches | `collection.count()` | Equals total chunks from step 1.12 | ☐ |

### Scoring
- **Pass:** 12/14
- **Critical Fail:** Tests 1.1, 1.13, 1.14 fail (no data indexed)
- **Acceptable:** 11/14 (minor extraction issues)

### Quantitative Metrics

| Metric | Target | How to Measure |
|---|---|---|
| URLs successfully scraped | 15/15 | Count successful HTTP 200 responses |
| Avg extracted text per page | > 500 chars | `sum(len(t) for t in texts) / 15` |
| Total chunks indexed | 50–300 | `collection.count()` |
| Ingestion time | < 5 minutes | `time.time()` around full pipeline |
| Embedding dimension | 384 (BGE-small) | `collection.peek()["embeddings"][0]` length |

---

## Phase 2 — RAG Core Pipeline

### 2A. Retrieval Tests

| # | Test Query | Expected Retrieval | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 2.1 | "What is the expense ratio of Nippon India Small Cap Fund?" | Chunks from Nippon Small Cap page | Top-1 chunk is from correct fund | ☐ |
| 2.2 | "Exit load for ICICI Prudential Balanced Advantage Fund" | Chunks from ICICI Balanced page | Top-1 chunk is from correct fund | ☐ |
| 2.3 | "Minimum SIP for Mirae Asset Flexi Cap Fund" | Chunks from Mirae Flexi Cap page | Top-1 chunk is from correct fund | ☐ |
| 2.4 | "What is the benchmark for ABSL Gold Fund?" | Chunks from ABSL Gold page | Top-1 chunk is from correct fund | ☐ |
| 2.5 | "NAV of Motilal Oswal Midcap 30" | Chunks from Motilal Midcap page | Top-1 chunk is from correct fund | ☐ |
| 2.6 | Query about non-existent fund: "HDFC Top 100" | No relevant chunks | All similarity scores < 0.7 | ☐ |

### 2B. Generation Tests

| # | Test Query | Expected Answer Contains | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 2.7 | "What is the expense ratio of Nippon India Small Cap Fund?" | A percentage value (e.g., "0.XX%") | Contains a number + "%" | ☐ |
| 2.8 | Same as 2.7 | ≤ 3 sentences | `answer.count('.') <= 4` (approximate) | ☐ |
| 2.9 | Same as 2.7 | Citation URL is a Groww link | `citation.url.startswith("https://groww.in/")` | ☐ |
| 2.10 | Same as 2.7 | `last_updated` is a date string | Matches `YYYY-MM-DD` format | ☐ |
| 2.11 | Same as 2.7 | `type` is `"factual"` | Exact match | ☐ |

### 2C. Fallback Tests

| # | Test Query | Expected Behavior | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 2.12 | "What is the ISIN of HDFC Top 100?" | No context found | `type` is `"no_match"` | ☐ |
| 2.13 | "Fund manager's phone number" | No context found | Answer contains "don't have this information" | ☐ |

### 2D. Response Quality Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 2.14 | No investment advice in response | Search for "should", "recommend", "better", "good investment" | None found | ☐ |
| 2.15 | No filler phrases | Search for "Based on the document", "According to" | None found | ☐ |
| 2.16 | Plain language | Flesch reading ease score | > 60 (plain English) | ☐ |
| 2.17 | Citation URL is accessible | `requests.head(citation.url)` | Returns 200 OK | ☐ |
| 2.18 | Answer is factually correct | Manual comparison with Groww page | Matches source data | ☐ |

### Scoring
- **Pass:** 15/18
- **Critical Fail:** Tests 2.1–2.5 mostly fail (retrieval broken), or 2.9 fails (no citation)
- **Acceptable:** 14/18

### Quantitative Metrics

| Metric | Target | How to Measure |
|---|---|---|
| Retrieval accuracy (Top-1) | ≥ 80% (4/5 test queries) | Correct fund in top-1 result |
| Retrieval accuracy (Top-3) | ≥ 90% (5/5) | Correct fund in top-3 results |
| Answer length | ≤ 3 sentences | Sentence count per response |
| Citation accuracy | 100% | Every response has valid Groww URL |
| Avg response latency | < 3 seconds | `time.time()` around `process_query()` |
| Fallback trigger rate | 100% for non-corpus queries | Correctly returns `no_match` |

---

## Phase 3 — Query Classification & Refusal Handling

### 3A. Classification Accuracy Tests

| # | Query | Expected Class | Pass/Fail |
|---|---|---|---|
| 3.1 | "What is the expense ratio of Nippon India Small Cap Fund?" | `FACTUAL` | ☐ |
| 3.2 | "What is the exit load for ICICI fund?" | `FACTUAL` | ☐ |
| 3.3 | "How do I download my capital gains statement?" | `FACTUAL` | ☐ |
| 3.4 | "What is the minimum SIP amount?" | `FACTUAL` | ☐ |
| 3.5 | "What is the benchmark index for this fund?" | `FACTUAL` | ☐ |
| 3.6 | "Should I invest in this fund?" | `ADVISORY` | ☐ |
| 3.7 | "Which fund is better for long term?" | `ADVISORY` | ☐ |
| 3.8 | "Recommend a mutual fund for me" | `ADVISORY` | ☐ |
| 3.9 | "Will this fund give good returns?" | `ADVISORY` | ☐ |
| 3.10 | "Is this fund a good investment?" | `ADVISORY` | ☐ |
| 3.11 | "What is the price of Reliance stock?" | `OUT_OF_SCOPE` | ☐ |
| 3.12 | "How do I open a bank account?" | `OUT_OF_SCOPE` | ☐ |
| 3.13 | "What is Bitcoin?" | `OUT_OF_SCOPE` | ☐ |
| 3.14 | "Tell me a joke" | `OUT_OF_SCOPE` | ☐ |

### 3B. PII Detection Tests

| # | Input | PII Type | Expected Result | Pass/Fail |
|---|---|---|---|---|
| 3.15 | `"My PAN is ABCDE1234F"` | PAN | Blocked | ☐ |
| 3.16 | `"Aadhaar: 1234 5678 9012"` | Aadhaar | Blocked | ☐ |
| 3.17 | `"Call me at 9876543210"` | Phone | Stripped | ☐ |
| 3.18 | `"Email: user@example.com"` | Email | Stripped | ☐ |
| 3.19 | `"What is the expense ratio?"` (no PII) | None | Not blocked | ☐ |
| 3.20 | `"ICICI Prudential fund"` (fund name, not PII) | None (false positive check) | Not blocked | ☐ |

### 3C. Refusal Response Quality Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 3.21 | Refusal is polite | Manual review of refusal text | No rude/dismissive language | ☐ |
| 3.22 | Refusal includes educational link | Check `citation.url` in refusal response | URL is AMFI/SEBI resource | ☐ |

### Scoring
- **Pass:** 20/22
- **Critical Fail:** Any advisory query classified as `FACTUAL` (3.6–3.10), or PII leaks to LLM (3.15–3.18)
- **Acceptable:** 19/22

### Quantitative Metrics

| Metric | Target | How to Measure |
|---|---|---|
| Classification accuracy (FACTUAL) | 100% (5/5) | All factual queries classified correctly |
| Classification accuracy (ADVISORY) | 100% (5/5) | All advisory queries refused |
| Classification accuracy (OUT_OF_SCOPE) | ≥ 75% (3/4) | Out-of-scope queries refused |
| PII detection rate | 100% (4/4) | All PII patterns caught |
| PII false positive rate | 0% | No legitimate queries blocked |
| Classifier latency | < 500ms | `time.time()` around `classify_query()` |

---

## Phase 4 — FastAPI Backend

### 4A. Endpoint Tests

| # | Method | Endpoint | Input | Expected Status | Expected Response | Pass/Fail |
|---|---|---|---|---|---|---|
| 4.1 | `GET` | `/api/health` | — | 200 | `{ "status": "ok", "documents": N }` where N > 0 | ☐ |
| 4.2 | `POST` | `/api/chat` | `{ "query": "What is the expense ratio of Nippon India Small Cap Fund?" }` | 200 | Factual response with citation | ☐ |
| 4.3 | `POST` | `/api/chat` | `{ "query": "Should I invest?" }` | 200 | Refusal response | ☐ |
| 4.4 | `POST` | `/api/chat` | `{ "query": "" }` | 400 / 422 | Validation error | ☐ |
| 4.5 | `POST` | `/api/chat` | `{ "query": "a" * 501 }` | 400 / 422 | "Query too long" | ☐ |
| 4.6 | `POST` | `/api/chat` | `{}` (missing query) | 422 | Pydantic validation error | ☐ |
| 4.7 | `POST` | `/api/chat` | Invalid JSON | 422 | JSON parse error | ☐ |
| 4.8 | `GET` | `/api/nonexistent` | — | 404 | Not found | ☐ |

### 4B. Response Schema Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 4.9 | Factual response matches `ChatResponse` schema | Validate JSON against Pydantic model | All fields present and typed correctly | ☐ |
| 4.10 | Refusal response matches `ChatResponse` schema | Validate JSON | `type` is `"refusal"`, `last_updated` is `null` | ☐ |
| 4.11 | Error response matches schema | Validate JSON | `type` is `"error"` | ☐ |

### 4C. CORS & Headers Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 4.12 | CORS headers present | `OPTIONS /api/chat` | `Access-Control-Allow-Origin` header set | ☐ |
| 4.13 | Content-Type is JSON | Check response headers | `Content-Type: application/json` | ☐ |

### 4D. Error Handling Tests

| # | Scenario | Method | Expected Behavior | Pass/Fail |
|---|---|---|---|---|
| 4.14 | Groq API key invalid | Set bad key in `.env` | Returns error response, doesn't crash | ☐ |
| 4.15 | ChromaDB empty | Delete collection | Health check fails with clear message | ☐ |
| 4.16 | Concurrent requests | Send 5 requests simultaneously | All return valid responses, no crash | ☐ |

### Scoring
- **Pass:** 14/16
- **Critical Fail:** Tests 4.1, 4.2 fail (core functionality broken), server crashes (4.14–4.16)
- **Acceptable:** 13/16

### Quantitative Metrics

| Metric | Target | How to Measure |
|---|---|---|
| Health check response time | < 200ms | `time.time()` around request |
| Chat endpoint avg latency | < 3 seconds | Average over 10 test queries |
| Error rate on valid input | 0% | No 5xx on valid queries |
| Correct HTTP status codes | 100% | All endpoints return appropriate codes |

---

## Phase 5 — Chat UI (Frontend)

### 5A. Rendering Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 5.1 | Page loads without errors | Open `index.html`, check browser console | No JavaScript errors | ☐ |
| 5.2 | Welcome message displayed | Visual inspection | Greeting text visible on load | ☐ |
| 5.3 | 3 example questions visible | Visual inspection | Three clickable question chips/buttons | ☐ |
| 5.4 | Disclaimer banner visible | Visual inspection | "Facts-only. No investment advice." visible | ☐ |
| 5.5 | Chat input + send button visible | Visual inspection | Input field and send button present | ☐ |

### 5B. Interaction Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 5.6 | Clicking example question sends query | Click first example | User message appears + API call fires | ☐ |
| 5.7 | Typing + Enter sends query | Type query, press Enter | User message appears + API call fires | ☐ |
| 5.8 | Loading spinner shows during API call | Send query, observe | Spinner/indicator visible while waiting | ☐ |
| 5.9 | Send button disabled while loading | Click send, try clicking again | Button disabled / no duplicate request | ☐ |
| 5.10 | Empty input prevented | Click send with empty input | Nothing happens (no API call) | ☐ |

### 5C. Response Display Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 5.11 | User message on right | Send query, observe | Right-aligned, distinct color | ☐ |
| 5.12 | Assistant message on left | Observe response | Left-aligned, different styling | ☐ |
| 5.13 | Citation link clickable | Click citation in response | Opens Groww URL in new tab | ☐ |
| 5.14 | "Last updated" footer visible | Observe factual response | Date footer shown below answer | ☐ |

### 5D. Responsive Design Tests

| # | Viewport | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 5.15 | Desktop (1920×1080) | Browser resize | Layout intact, readable | ☐ |
| 5.16 | Tablet (768×1024) | DevTools responsive mode | Layout adapts, no overflow | ☐ |
| 5.17 | Mobile (375×667) | DevTools responsive mode | Full functionality, no horizontal scroll | ☐ |

### Scoring
- **Pass:** 12/14 (excluding responsive tests as optional)
- **Critical Fail:** Tests 5.1 (JS errors), 5.6–5.7 (can't send queries)
- **Acceptable:** 11/14

---

## Phase 6 — Integration & Testing

### 6A. End-to-End Flow Tests

| # | Scenario | Steps | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 6.1 | Happy path — factual query | Type "What is the expense ratio of Nippon India Small Cap Fund?" → Send | Correct answer + citation + date footer displayed | ☐ |
| 6.2 | Happy path — example click | Click first example question | Same result as 6.1 | ☐ |
| 6.3 | Refusal — advisory query | Type "Should I invest in this fund?" → Send | Polite refusal + educational link displayed | ☐ |
| 6.4 | Refusal — out-of-scope | Type "What is Bitcoin?" → Send | Out-of-scope refusal displayed | ☐ |
| 6.5 | PII blocking | Type "My PAN is ABCDE1234F" → Send | PII warning displayed | ☐ |
| 6.6 | No context fallback | Type "HDFC Top 100 Fund details" → Send | "I don't have this information" displayed | ☐ |

### 6B. Factual Accuracy Test Suite (Per Fund)

> Run one query per fund to verify corpus coverage.

| # | Query | Expected: Contains | Pass/Fail |
|---|---|---|---|
| 6.7 | "Expense ratio of Nippon India Small Cap Fund" | A percentage | ☐ |
| 6.8 | "Exit load of Nippon India Large Cap Fund" | Exit load details | ☐ |
| 6.9 | "NAV of Nippon India Multi Cap Fund" | A NAV value | ☐ |
| 6.10 | "Benchmark of Motilal Oswal Midcap 30 Fund" | Benchmark name | ☐ |
| 6.11 | "Category of Motilal Oswal Long Term Fund" | ELSS or related | ☐ |
| 6.12 | "Minimum SIP of Motilal Oswal Multicap 35 Fund" | Amount in ₹ | ☐ |
| 6.13 | "Risk level of Mirae Asset Large & Midcap Fund" | Risk category | ☐ |
| 6.14 | "Fund manager of Mirae Asset Flexi Cap Fund" | A person's name | ☐ |
| 6.15 | "AUM of Mirae Asset Healthcare Fund" | AUM value | ☐ |
| 6.16 | "Category of ABSL Gold Fund" | Gold / commodity | ☐ |
| 6.17 | "Expense ratio of ABSL Enhanced Arbitrage Fund" | A percentage | ☐ |
| 6.18 | "Minimum investment of ABSL Multi-Asset Allocation Fund" | Amount in ₹ | ☐ |
| 6.19 | "NAV of ICICI Prudential Silver ETF FoF" | A NAV value | ☐ |
| 6.20 | "Exit load of ICICI Prudential Liquid Fund" | Exit load details | ☐ |
| 6.21 | "Benchmark of ICICI Prudential Balanced Advantage Fund" | Benchmark name | ☐ |

### 6C. Response Format Validation

| # | Check | Test Across All Responses | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 6.22 | Answer ≤ 3 sentences | Count sentences in each factual response | All ≤ 3 | ☐ |
| 6.23 | Exactly 1 citation | Count citations per response | Exactly 1 for factual, 1 for refusal | ☐ |
| 6.24 | Date footer present | Check `last_updated` field | Non-null for factual responses | ☐ |
| 6.25 | Citation URL is Groww link | Validate URL domain | All start with `https://groww.in/` | ☐ |
| 6.26 | No investment advice in any response | Scan all responses | No advisory language detected | ☐ |

### 6D. Performance Tests

| # | Metric | Test | Target | Pass/Fail |
|---|---|---|---|---|
| 6.27 | Average response latency | 10 sequential queries | < 3 seconds | ☐ |
| 6.28 | P95 response latency | 20 queries, measure 95th percentile | < 5 seconds | ☐ |
| 6.29 | Concurrent handling | 5 simultaneous requests | All return valid responses | ☐ |
| 6.30 | Memory usage | Monitor during 20-query session | < 500MB | ☐ |

### Scoring
- **Pass:** 27/30
- **Critical Fail:** Factual query returns wrong data (6.7–6.21), advisory query not refused (6.3), PII leaks (6.5)
- **Acceptable:** 25/30

### Quantitative Scorecard

| Category | Total Tests | Target Pass Rate | Weight |
|---|---|---|---|
| E2E Flow | 6 | 100% | 25% |
| Factual Accuracy (per fund) | 15 | ≥ 80% (12/15) | 35% |
| Response Format | 5 | 100% | 20% |
| Performance | 4 | ≥ 75% (3/4) | 20% |

**Overall Phase 6 Score = Σ (pass_rate × weight)**  
**Target: ≥ 85%**

---

## Phase 7 — Polish & Documentation

### 7A. README Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 7.1 | README.md exists | File check | Present in project root | ☐ |
| 7.2 | Contains setup instructions | Read README | Steps 1–7 (clone → run) are documented | ☐ |
| 7.3 | Contains AMC/scheme table | Read README | All 15 schemes listed | ☐ |
| 7.4 | Contains architecture overview | Read README | Diagram or link to `architecture.md` | ☐ |
| 7.5 | Contains known limitations | Read README | At least 4 limitations listed | ☐ |
| 7.6 | Contains disclaimer | Read README | "Facts-only. No investment advice." present | ☐ |

### 7B. Security Tests

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 7.7 | No API keys in source code | `grep -r "GROQ_API_KEY\|gsk_" backend/ --include="*.py"` | No hardcoded keys found | ☐ |
| 7.8 | `.env` is gitignored | `git status` (if git init'd) | `.env` not tracked | ☐ |

### 7C. Fresh Setup Test

| # | Check | Method | Pass Criteria | Pass/Fail |
|---|---|---|---|---|
| 7.9 | Clean install works | Delete `chroma_db/`, run ingestion, start server, open UI | Full flow works from scratch | ☐ |
| 7.10 | Code is formatted | Run `black --check backend/` | No formatting issues (or manually reviewed) | ☐ |

### Scoring
- **Pass:** 9/10
- **Critical Fail:** Tests 7.7 (API key exposed), 7.9 (fresh setup fails)
- **Acceptable:** 8/10

---

## Overall Evaluation Scorecard

### Per-Phase Results

| Phase | Tests | Passed | Rate | Status |
|---|---|---|---|---|
| Phase 0 — Setup | 8 | _/8 | _% | ☐ Pass ☐ Fail |
| Phase 1 — Ingestion | 14 | _/14 | _% | ☐ Pass ☐ Fail |
| Phase 2 — RAG Pipeline | 18 | _/18 | _% | ☐ Pass ☐ Fail |
| Phase 3 — Classification | 22 | _/22 | _% | ☐ Pass ☐ Fail |
| Phase 4 — Backend | 16 | _/16 | _% | ☐ Pass ☐ Fail |
| Phase 5 — Chat UI | 14 | _/14 | _% | ☐ Pass ☐ Fail |
| Phase 6 — Integration | 30 | _/30 | _% | ☐ Pass ☐ Fail |
| Phase 7 — Polish | 10 | _/10 | _% | ☐ Pass ☐ Fail |
| **TOTAL** | **132** | **_/132** | **_% ** | |

### Success Criteria (from [context.md §7](file:///Users/ris/Cursor/RAG%20Chatbot/context.md))

| Criteria | Eval Tests | Status |
|---|---|---|
| Accurate retrieval of factual mutual fund information | 2.1–2.5, 6.7–6.21 | ☐ |
| Strict adherence to facts-only responses | 2.14, 3.6–3.10, 6.26 | ☐ |
| Consistent inclusion of valid source citations | 2.9, 2.17, 6.23, 6.25 | ☐ |
| Proper refusal of advisory queries | 3.6–3.14, 6.3–6.4 | ☐ |
| Clean, minimal, and user-friendly interface | 5.1–5.14 | ☐ |

### Critical Failure Conditions (Any = Project Fail)

| # | Condition | Relevant Tests |
|---|---|---|
| ❌ 1 | Advisory query answered as factual | 3.6–3.10, 6.3 |
| ❌ 2 | PII data sent to Groq API | 3.15–3.18, 6.5 |
| ❌ 3 | API key exposed in source code | 7.7 |
| ❌ 4 | Factual response cites wrong fund | 2.1–2.5, 6.7–6.21 |
| ❌ 5 | Server crashes on valid input | 4.14–4.16 |
| ❌ 6 | No data indexed (empty ChromaDB) | 1.13, 1.14 |

---

## Automated Test Script Template

```python
"""
eval_runner.py — Automated evaluation script
Run: python scripts/eval_runner.py
"""
import requests
import time
import json
import re

BASE_URL = "http://localhost:8000"
RESULTS = {"passed": 0, "failed": 0, "errors": []}

def test(name, condition, details=""):
    if condition:
        RESULTS["passed"] += 1
        print(f"  ✅ {name}")
    else:
        RESULTS["failed"] += 1
        RESULTS["errors"].append(f"{name}: {details}")
        print(f"  ❌ {name} — {details}")

def run_eval():
    print("\n=== Phase 4: Health Check ===")
    r = requests.get(f"{BASE_URL}/api/health")
    test("4.1 Health returns 200", r.status_code == 200)
    test("4.1 Health has documents", r.json().get("documents", 0) > 0)

    print("\n=== Phase 6: Factual Query ===")
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "query": "What is the expense ratio of Nippon India Small Cap Fund?"
    })
    data = r.json()
    test("6.1 Returns 200", r.status_code == 200)
    test("6.1 Type is factual", data.get("type") == "factual")
    test("6.1 Has citation", data.get("citation") is not None)
    test("6.1 Citation is Groww URL", 
         data.get("citation", {}).get("url", "").startswith("https://groww.in/"))
    test("6.1 Has last_updated", data.get("last_updated") is not None)
    test("6.1 Answer ≤ 3 sentences", 
         len(re.split(r'[.!?]+', data.get("answer", ""))) <= 4)

    print("\n=== Phase 6: Advisory Refusal ===")
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "query": "Should I invest in this fund?"
    })
    data = r.json()
    test("6.3 Type is refusal", data.get("type") == "refusal")
    test("6.3 Has educational link", data.get("citation") is not None)

    print("\n=== Phase 6: PII Blocking ===")
    r = requests.post(f"{BASE_URL}/api/chat", json={
        "query": "My PAN is ABCDE1234F, what is the exit load?"
    })
    data = r.json()
    test("6.5 PII blocked", "personal information" in data.get("answer", "").lower() 
         or data.get("type") in ("refusal", "error"))

    print(f"\n{'='*50}")
    print(f"TOTAL: {RESULTS['passed']} passed, {RESULTS['failed']} failed")
    if RESULTS["errors"]:
        print(f"\nFailed tests:")
        for e in RESULTS["errors"]:
            print(f"  • {e}")

if __name__ == "__main__":
    run_eval()
```

> Save as `scripts/eval_runner.py` and run after Phases 4–6 are complete.
