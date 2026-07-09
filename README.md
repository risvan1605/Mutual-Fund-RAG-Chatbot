# Mutual Fund FAQ Assistant

## Overview
The **Mutual Fund FAQ Assistant** is a Retrieval-Augmented Generation (RAG) chatbot designed to answer factual questions about specific mutual fund schemes from 5 major AMCs based on data from Groww. It scrapes live fund information, processes it into semantic chunks, and uses a Large Language Model to provide succinct, strictly factual answers accompanied by source citations. 

The chatbot includes query intent classification to actively refuse investment advice or out-of-scope questions, and detects PII to prevent sensitive information from being processed.

> **⚠️ Disclaimer**  
> **Facts-only. No investment advice.**  
> This assistant strictly provides educational and factual data points directly retrieved from mutual fund source documents. It does not provide personalized financial, investment, or legal advice. Always consult a certified financial advisor before making any investment decisions.

---

## Scope

### Supported AMCs and Schemes

The assistant has knowledge about the following **11 mutual fund schemes** (from 5 AMCs) whose data was successfully scraped and embedded:

| # | AMC | Scheme Name | Category | Source URL |
|---|-----|-------------|----------|------------|
| 1 | Nippon India Mutual Fund | Nippon India Small Cap Fund | Small Cap | [Groww](https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth) |
| 2 | Nippon India Mutual Fund | Nippon India Large Cap Fund | Large Cap | [Groww](https://groww.in/mutual-funds/nippon-india-large-cap-fund-direct-growth) |
| 3 | Nippon India Mutual Fund | Nippon India Multi Cap Fund | Multi Cap | [Groww](https://groww.in/mutual-funds/nippon-india-multi-cap-fund-direct-growth) |
| 4 | Motilal Oswal Mutual Fund | Motilal Oswal Midcap Fund | Mid Cap | [Groww](https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth) |
| 5 | Mirae Asset Mutual Fund | Mirae Asset Large & Midcap Fund | Large & Mid Cap | [Groww](https://groww.in/mutual-funds/mirae-asset-emerging-bluechip-fund-direct-growth) |
| 6 | Mirae Asset Mutual Fund | Mirae Asset Flexi Cap Fund | Flexi Cap | [Groww](https://groww.in/mutual-funds/mirae-asset-flexi-cap-fund-direct-growth) |
| 7 | Mirae Asset Mutual Fund | Mirae Asset Healthcare Fund | Sectoral/Thematic | [Groww](https://groww.in/mutual-funds/mirae-asset-healthcare-fund-direct-growth) |
| 8 | Aditya Birla Sun Life Mutual Fund | ABSL Gold Fund | Gold | [Groww](https://groww.in/mutual-funds/aditya-birla-sun-life-gold-fund-direct-growth) |
| 9 | Aditya Birla Sun Life Mutual Fund | ABSL Multi Asset Allocation Fund | Multi Asset Allocation | [Groww](https://groww.in/mutual-funds/aditya-birla-sun-life-multi-asset-allocation-fund-direct-growth) |
| 10 | ICICI Prudential Mutual Fund | ICICI Prudential Silver ETF FoF | Silver | [Groww](https://groww.in/mutual-funds/icici-prudential-silver-etf-fof-direct-growth) |
| 11 | ICICI Prudential Mutual Fund | ICICI Prudential Balanced Advantage Fund | Balanced Advantage | [Groww](https://groww.in/mutual-funds/icici-prudential-balanced-advantage-fund-direct-growth) |

For refusal responses (advisory, out-of-scope, PII queries), the assistant links to:
- [AMFI Investor Page](https://www.amfiindia.com/investor) — *Learn more about mutual fund investing here*

---

## Architecture Overview
The system relies on a typical RAG architecture paired with classification logic:
1. **Ingestion Pipeline**: Scrapes Groww pages using `requests` and `BeautifulSoup`, cleans the HTML, chunks it via LangChain, generates embeddings using `BAAI/bge-small-en-v1.5`, and persists them in `ChromaDB`.
2. **Query Classification**: A keyword-based classifier categorizes queries as Factual, Advisory, or Out-of-Scope. PII detection runs using Regex patterns beforehand.
3. **Retrieval and Generation**: Factual queries retrieve the top-3 most relevant chunks from ChromaDB. An LLM (`llama-3.3-70b-versatile` via Groq) generates a concise 3-sentence factual answer strictly constrained to the context, citing the source URL.

## Tech Stack
- **Frontend / Deployment:** Streamlit (deployed on Streamlit Community Cloud)
- **Vector Database:** ChromaDB (persisted in-repo at `data/chroma_db_v2/`)
- **LLM API:** Groq (`llama-3.3-70b-versatile`)
- **Embeddings:** `sentence-transformers` (`BAAI/bge-small-en-v1.5`)
- **Chunking:** LangChain (`RecursiveCharacterTextSplitter`)
- **Scraping:** Requests, BeautifulSoup4

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- A [Groq API key](https://console.groq.com/keys) (free tier available)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/risvan1605/Mutual-Fund-RAG-Chatbot.git
   cd Mutual-Fund-RAG-Chatbot
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API key:**
   Create a `.env` file in the `backend/` directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the Ingestion Pipeline** (optional — the repo already includes pre-embedded data):
   ```bash
   python scripts/ingest.py
   ```

6. **Start the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

### Streamlit Cloud Deployment

1. Push the repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and deploy `streamlit_app.py` from the `main` branch.
3. In **App Settings → Secrets**, add:
   ```toml
   GROQ_API_KEY="your_groq_api_key_here"
   ```

---

## Sample Q&A

Below are real responses generated by the assistant:

### Factual Queries

**Q: What is the expense ratio of Nippon India Small Cap Fund?**  
> The expense ratio of Nippon India Small Cap Fund Direct Growth is 0.73%.  
> The fund has an Asset Under Management of ₹74604.0674 Crores and is managed by Samir Rachh and Dhrumil Shah.  
> The expense ratio is a percentage of the fund's assets deducted to cover its operating expenses.  
>  
> **Source:** [Nippon India Small Cap Fund — Groww](https://groww.in/mutual-funds/nippon-india-small-cap-fund-direct-growth)

**Q: What is the exit load for ICICI Prudential Balanced Advantage Fund?**  
> The exit load for ICICI Prudential Balanced Advantage Direct Growth is 1% for units in excess of 30% of the investment, charged for redemption within 1 year.  
> The minimum investment to avoid exit load is 30% of the total investment.  
>  
> **Source:** [ICICI Prudential Balanced Advantage Fund — Groww](https://groww.in/mutual-funds/icici-prudential-balanced-advantage-fund-direct-growth)

**Q: What is the minimum SIP amount for Mirae Asset Flexi Cap Fund?**  
> The minimum SIP investment for Mirae Asset Flexi Cap Fund is ₹99. This fund has a direct growth option and is categorized under Equity (Flexi Cap).  
>  
> **Source:** [Mirae Asset Flexi Cap Fund — Groww](https://groww.in/mutual-funds/mirae-asset-flexi-cap-fund-direct-growth)

**Q: Who is the fund manager of Motilal Oswal Midcap Fund?**  
> The fund managers of Motilal Oswal Midcap Fund Direct Growth are Abhiroop Mukherjee, Akash Singhania, and Siddharth Bothra.  
>  
> **Source:** [Motilal Oswal Midcap Fund — Groww](https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth)

**Q: What is the AUM of Mirae Asset Large and Midcap Fund?**  
> The Asset Under Management (AUM) of Mirae Asset Large & Midcap Fund Direct Growth is ₹42792.1955 Crores.  
> The fund has a minimum SIP investment of ₹99 and a minimum lumpsum investment of ₹5000.  
>  
> **Source:** [Mirae Asset Large & Midcap Fund — Groww](https://groww.in/mutual-funds/mirae-asset-emerging-bluechip-fund-direct-growth)

### Refusal Queries

**Q: Should I invest in Nippon India Small Cap Fund?** *(Advisory)*  
> I can only provide factual information about mutual funds based on official documents. I cannot provide investment advice, recommendations, or predict future performance.  
>  
> [Learn more about mutual fund investing here](https://www.amfiindia.com/investor)

**Q: What is the price of Bitcoin?** *(Out-of-Scope)*  
> This question is outside my scope. I am a factual FAQ assistant specifically designed to answer queries about mutual fund schemes based on Groww.  
>  
> [Learn more about mutual fund investing here](https://www.amfiindia.com/investor)

**Q: My PAN is ABCDE1234F, what is the NAV?** *(PII Detected)*  
> Please avoid sharing personal information like PAN, Aadhaar, Phone Numbers, or Emails. I have blocked this query to protect your privacy.  
>  
> [Learn more about mutual fund investing here](https://www.amfiindia.com/investor)

---

## Known Limitations
- **Data Freshness:** Data is scraped from Groww pages at a point in time (the last ingestion run). It may become stale, especially for rapidly changing metrics like NAV or AUM.
- **Limited Scope:** Only the 11 successfully embedded schemes from the 5 selected AMCs are covered. 4 schemes failed during scraping and are not available.
- **No Real-time Updates:** Real-time metrics such as live NAV updates are not continuously pulled.
- **Stateless Chat:** The chatbot lacks multi-turn conversation memory (no history tracking).
- **Language Support:** English only.
- **API Dependency:** Fully dependent on the availability and rate limits of the Groq LLM API.
- **Max Token Limit:** Answers are capped at 150 tokens (~3 sentences) to enforce conciseness.
