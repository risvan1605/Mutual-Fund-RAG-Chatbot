# Project Context — Mutual Fund FAQ Assistant

## 1. Project Overview

This project is a **facts-only FAQ assistant** for mutual fund schemes, built with **Groww** as the reference product context. The assistant answers objective, verifiable queries about mutual funds by retrieving information exclusively from **official public sources** — AMC (Asset Management Company) websites, AMFI, and SEBI.

> **Core Principle:** The system must **never** provide investment advice, opinions, or recommendations. Every response must be factual, concise, source-backed, and compliant.

---

## 2. Objective

Design and implement a lightweight **Retrieval-Augmented Generation (RAG)** based assistant that:

- Answers **factual queries** about mutual fund schemes
- Uses a **curated corpus** of official documents
- Provides **concise, source-backed** responses

---

## 3. Target Users

| User Segment | Use Case |
|---|---|
| **Retail Investors** | Comparing mutual fund schemes using verified facts |
| **Customer Support / Content Teams** | Handling repetitive mutual fund queries efficiently |

---

## 4. Scope of Work

### 4.1 Corpus Definition

- **Data Source:** All data is scraped from **Groww** mutual fund scheme pages (HTML only — no PDFs, no other sources)
- **AMCs Covered:** 5 AMCs with diverse fund categories
- **Total URLs:** 15 Groww scheme pages

#### Nippon India Mutual Fund (3 schemes)
| # | Scheme | Category | URL |
|---|---|---|---|
| 1 | Nippon India Small Cap Fund (Direct Growth) | Small Cap | [Link](https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth) |
| 2 | Nippon India Large Cap Fund (Direct Growth) | Large Cap | [Link](https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth) |
| 3 | Nippon India Multi Cap Fund (Direct Growth) | Multi Cap | [Link](https://groww.in/mutual-funds/nippon-india-multi-cap-fund-direct-growth) |

#### Motilal Oswal Mutual Fund (3 schemes)
| # | Scheme | Category | URL |
|---|---|---|---|
| 4 | Motilal Oswal Midcap 30 Fund (Direct Growth) | Mid Cap | [Link](https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth) |
| 5 | Motilal Oswal Long Term Fund (Direct Growth) | ELSS / Long Term | [Link](https://groww.in/mutual-funds/motilal-oswal-most-focused-long-term-fund-direct-growth) |
| 6 | Motilal Oswal Multicap 35 Fund (Direct Growth) | Multi Cap | [Link](https://groww.in/mutual-funds/motilal-oswal-most-focused-multicap-35-fund-direct-growth) |

#### Mirae Asset Mutual Fund (3 schemes)
| # | Scheme | Category | URL |
|---|---|---|---|
| 7 | Mirae Asset Large & Midcap Fund (Direct Growth) | Large & Mid Cap | [Link](https://groww.in/mutual-funds/mirae-asset-large-midcap-fund-direct-growth) |
| 8 | Mirae Asset Flexi Cap Fund (Direct Growth) | Flexi Cap | [Link](https://groww.in/mutual-funds/mirae-asset-flexi-cap-fund-direct-growth) |
| 9 | Mirae Asset Healthcare Fund (Direct Growth) | Sectoral / Healthcare | [Link](https://groww.in/mutual-funds/mirae-asset-healthcare-fund-direct-growth) |

#### Aditya Birla Sun Life Mutual Fund (3 schemes)
| # | Scheme | Category | URL |
|---|---|---|---|
| 10 | ABSL Gold Fund (Direct Growth) | Gold / Commodity | [Link](https://groww.in/mutual-funds/aditya-birla-sun-life-gold-fund-direct-growth) |
| 11 | ABSL Enhanced Arbitrage Fund (Direct Growth) | Arbitrage / Hybrid | [Link](https://groww.in/mutual-funds/birla-sun-life-enhanced-arbitrage-fund-direct-growth) |
| 12 | ABSL Multi-Asset Allocation Fund (Direct Growth) | Multi-Asset | [Link](https://groww.in/mutual-funds/aditya-birla-sun-life-multi-asset-allocation-fund-direct-growth) |

#### ICICI Prudential Mutual Fund (3 schemes)
| # | Scheme | Category | URL |
|---|---|---|---|
| 13 | ICICI Prudential Silver ETF FoF (Direct Growth) | Silver / Commodity | [Link](https://groww.in/mutual-funds/icici-prudential-silver-etf-fof-direct-growth) |
| 14 | ICICI Prudential Liquid Fund (Direct Growth) | Liquid / Debt | [Link](https://groww.in/mutual-funds/icici-prudential-liquid-fund-direct-plan-growth) |
| 15 | ICICI Prudential Balanced Advantage Fund (Direct Growth) | Balanced / Hybrid | [Link](https://groww.in/mutual-funds/icici-prudential-balanced-direct-growth) |

> **Category Diversity:** Small Cap, Large Cap, Multi Cap, Mid Cap, Flexi Cap, ELSS, Large & Mid Cap, Sectoral, Gold, Arbitrage, Multi-Asset, Silver, Liquid, Balanced Advantage

### 4.2 FAQ Assistant — Functional Requirements

The assistant must handle **facts-only queries** such as:

| Query Type | Example |
|---|---|
| Expense Ratio | "What is the expense ratio of X fund?" |
| Exit Load | "What is the exit load for Y scheme?" |
| Minimum SIP | "What is the minimum SIP amount for Z fund?" |
| ELSS Lock-in | "What is the lock-in period for ELSS?" |
| Riskometer | "What is the riskometer classification?" |
| Benchmark Index | "What benchmark does this fund track?" |
| Statement Downloads | "How do I download my capital gains report?" |

**Response Format Rules:**

1. Each response is limited to a **maximum of 3 sentences**
2. Each response includes **exactly one citation link**
3. Each response includes a footer: `"Last updated from sources: <date>"`

### 4.3 Refusal Handling

The assistant must **refuse** non-factual or advisory queries.

**Examples of queries to refuse:**
- "Should I invest in this fund?"
- "Which fund is better?"

**Refusal response requirements:**
- Be **polite** and clearly worded
- **Reinforce** the facts-only limitation
- Provide a **relevant educational link** (e.g., AMFI or SEBI resource)

### 4.4 User Interface (Minimal)

The solution must include a simple interface with:

- A **welcome message**
- **Three example questions** to guide the user
- A **visible disclaimer:** `"Facts-only. No investment advice."`

---

## 5. Constraints

### 5.1 Data & Sources
- Use **only** official public sources (AMC, AMFI, SEBI)
- **Do not** use third-party blogs or aggregator websites

### 5.2 Privacy & Security
- **Do not** collect, store, or process any of the following:
  - PAN or Aadhaar numbers
  - Account numbers
  - OTPs
  - Email addresses or phone numbers

### 5.3 Content Restrictions
- **No** investment advice or recommendations
- **No** performance comparisons or return calculations
- For performance-related queries → provide a **link to the official factsheet only**

### 5.4 Transparency
- Responses must be **short, factual, and verifiable**
- Every answer must include a **source link** and **last updated date**

---

## 6. Expected Deliverables

| # | Deliverable | Details |
|---|---|---|
| 1 | **README Document** | Setup instructions, selected AMC & schemes, architecture overview (RAG approach), known limitations |
| 2 | **Disclaimer Snippet** | `"Facts-only. No investment advice."` |
| 3 | **Working FAQ Assistant** | RAG-based chatbot with UI, corpus, retrieval pipeline, and response generation |

---

## 7. Success Criteria

- [ ] Accurate retrieval of factual mutual fund information
- [ ] Strict adherence to facts-only responses
- [ ] Consistent inclusion of valid source citations
- [ ] Proper refusal of advisory queries
- [ ] Clean, minimal, and user-friendly interface

---

## 8. Technical Architecture (High-Level)

```
┌──────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  User Query   │────▶│  RAG Pipeline     │────▶│  LLM Generation   │
│  (Chat UI)    │     │  (Retrieval +     │     │  (Facts-only      │
│               │     │   Ranking)        │     │   constrained)    │
└──────────────┘     └──────────────────┘     └───────────────────┘
                              │                         │
                     ┌────────▼────────┐       ┌────────▼────────┐
                     │  Vector Store    │       │  Response with   │
                     │  (Embedded       │       │  Citation +      │
                     │   Official Docs) │       │  Date Footer     │
                     └─────────────────┘       └─────────────────┘
```

**Key Components:**
1. **Document Ingestion** — Scrape/collect official URLs, extract text, chunk documents
2. **Embedding & Indexing** — Embed chunks into a vector store for semantic search
3. **Retrieval** — On user query, retrieve top-k relevant chunks
4. **Generation** — Use an LLM with strict prompting to generate facts-only answers (max 3 sentences, 1 citation, date footer)
5. **Refusal Logic** — Detect advisory/opinion queries and return polite refusal + educational link
6. **UI Layer** — Minimal chat interface with welcome message, examples, and disclaimer

---

## 9. Key Design Decisions

| Decision | Status | Choice / Notes |
|---|---|---|
| **AMC Selection** | ✅ Finalized | 5 AMCs: Nippon India, Motilal Oswal, Mirae Asset, ABSL, ICICI Prudential |
| **Data Source** | ✅ Finalized | 15 Groww scheme pages (HTML only — no PDFs, no other sources) |
| **LLM Provider** | ✅ Finalized | Groq API (ultra-fast inference for open-source LLMs like Llama / Mixtral) |
| **Vector Store** | TBD | FAISS, ChromaDB, Pinecone, Weaviate, etc. |
| **Embedding Model** | ✅ Finalized | BGE (BAAI General Embedding — `BAAI/bge-small-en-v1.5` or `BAAI/bge-base-en-v1.5`) |
| **Framework** | TBD | LangChain, LlamaIndex, or custom RAG pipeline |
| **Frontend** | TBD | Simple HTML/CSS/JS, Streamlit, Gradio, or React-based |
| **Hosting** | TBD | Local, cloud (Vercel, Railway, etc.), or containerized |

---

## 10. Summary

> The goal is to build a **trustworthy, transparent, and compliant** mutual fund FAQ assistant that prioritizes **accuracy over intelligence**. The system should ensure that users receive only **verified, source-backed financial information**, without any advisory bias or speculative content.
