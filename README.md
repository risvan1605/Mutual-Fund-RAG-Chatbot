# Mutual Fund FAQ Assistant

## Overview
The **Mutual Fund FAQ Assistant** is a Retrieval-Augmented Generation (RAG) chatbot designed to answer factual questions about 15 specific mutual fund schemes from 5 major AMCs based on data from Groww. It scrapes live fund information, processes it into semantic chunks, and uses a Large Language Model to provide succinct, strictly factual answers accompanied by source citations. 

The chatbot includes query intent classification to actively refuse investment advice or out-of-scope questions, and detects PII to prevent sensitive information from being processed.

## Selected AMCs and Schemes

| AMC | Scheme Name | Category |
|---|---|---|
| **Nippon India Mutual Fund** | Nippon India Small Cap Fund | Small Cap |
| | Nippon India Large Cap Fund | Large Cap |
| | Nippon India Multi Cap Fund | Multi Cap |
| **Motilal Oswal Mutual Fund** | Motilal Oswal Midcap Fund | Mid Cap |
| | Motilal Oswal ELSS Tax Saver Fund | ELSS |
| | Motilal Oswal Flexi Cap Fund | Flexi Cap |
| **Mirae Asset Mutual Fund** | Mirae Asset Large & Midcap Fund | Large & Mid Cap |
| | Mirae Asset Flexi Cap Fund | Flexi Cap |
| | Mirae Asset Healthcare Fund | Sectoral/Thematic |
| **Aditya Birla Sun Life Mutual Fund** | Aditya Birla Sun Life Gold Fund | Gold |
| | Aditya Birla Sun Life Enhanced Arbitrage Fund | Arbitrage |
| | Aditya Birla Sun Life Multi Asset Allocation Fund | Multi Asset Allocation |
| **ICICI Prudential Mutual Fund** | ICICI Prudential Silver ETF FoF | Silver |
| | ICICI Prudential Liquid Fund | Liquid |
| | ICICI Prudential Balanced Advantage Fund | Balanced Advantage |

## Architecture Overview
The system relies on a typical RAG architecture paired with advanced classification logic:
1. **Ingestion Pipeline**: Scrapes Groww pages using `requests` and `BeautifulSoup`, cleans the HTML, chunks it via LangChain, generates embeddings using `BAAI/bge-small-en-v1.5`, and persists them in `ChromaDB`.
2. **Query Classification**: A smaller LLM (`llama-3.1-8b-instant`) categorizes queries as Factual, Advisory, or Out-of-Scope. PII detection runs using Regex patterns beforehand.
3. **Retrieval and Generation**: Factual queries retrieve the top-3 most relevant chunks from ChromaDB. A larger LLM (`llama-3.3-70b-versatile`) generates a concise 3-sentence factual answer strictly constrained to the context, citing the source URL.

## Tech Stack
- **Backend Framework:** Python, FastAPI, Uvicorn
- **Frontend Framework:** Vanilla HTML, CSS, JavaScript
- **Vector Database:** ChromaDB
- **LLM APIs:** Groq (`llama-3.3-70b-versatile` & `llama-3.1-8b-instant`)
- **Embeddings:** `sentence-transformers` (`BAAI/bge-small-en-v1.5`)
- **Chunking/Orchestration:** LangChain (`RecursiveCharacterTextSplitter`)
- **Scraping:** Requests, BeautifulSoup4

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd "RAG Chatbot"
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Add API keys:**
   Create a `.env` file in the `backend/` directory with the following variables:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
   LLM_MODEL=llama-3.3-70b-versatile
   CHROMA_PERSIST_DIR=./data/chroma_db
   ```

5. **Run the Ingestion Pipeline:**
   This step will scrape Groww data and populate ChromaDB.
   ```bash
   python scripts/ingest.py
   ```

6. **Start the Backend Server:**
   ```bash
   uvicorn backend.main:app --port 8000 --reload
   ```

7. **Open the Frontend:**
   Open `frontend/index.html` in your web browser or use a Live Server (e.g. port 5500).

## Usage Examples

- **Factual Question** (Returns answer and citation): 
  - *"What is the expense ratio of Nippon India Small Cap Fund?"*
- **Advisory Question** (Returns a polite refusal):
  - *"Should I invest in Motilal Oswal Midcap Fund?"*
- **Out-of-Scope Question** (Returns a polite refusal):
  - *"What is the price of Bitcoin?"*
- **PII Query** (Returns privacy protection warning):
  - *"My PAN is ABCDE1234F, what is the exit load?"*

## Known Limitations
- **Data Freshness:** Data is scraped from Groww pages at a point in time (the last ingestion run). It may become stale, especially for rapidly changing metrics.
- **Limited Scope:** Only the 15 pre-configured schemes from the 5 selected AMCs are covered.
- **No Real-time Updates:** Real-time metrics such as live NAV updates are not continuously pulled.
- **Stateless Chat:** The chatbot lacks multi-turn conversation memory (no history tracking).
- **Language Support:** English only.
- **Dependency Restrictions:** Fully dependent on the availability and rate limits of the Groq LLM APIs.

## Disclaimer
> **Facts-only. No investment advice.**
> This assistant strictly provides educational and factual data points directly retrieved from mutual fund source documents. It does not provide personalized financial, investment, or legal advice. Always consult a certified financial advisor before making any investment decisions.
