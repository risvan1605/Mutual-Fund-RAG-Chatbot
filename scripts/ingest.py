import sys
import time
import logging
from pathlib import Path

# Add project root to path so we can import backend modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ingestion.scraper import scrape_all_sources
from backend.ingestion.extractor import extract_text
from backend.ingestion.chunker import process_all_documents
from backend.ingestion.embedder import embed_and_store

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    start_time = time.time()

    # 1. Load sources.json and 2. Scrape all URLs
    sources_path = (
        Path(__file__).resolve().parent.parent
        / "backend"
        / "ingestion"
        / "sources.json"
    )
    logger.info(f"Starting ingestion pipeline. Reading sources from {sources_path}")

    scraped_data = scrape_all_sources(str(sources_path))
    if not scraped_data:
        logger.error("No data scraped. Exiting.")
        return

    logger.info(f"Total URLs scraped: {len(scraped_data)}")

    # 3. Extract and clean text
    documents = []
    for data in scraped_data:
        text = extract_text(data["html"])
        if text:
            # Add extracted text to metadata for the chunker
            doc_data = data.copy()
            doc_data["text"] = text
            del doc_data["html"]
            documents.append(doc_data)
        else:
            logger.warning(f"Failed to extract text from {data['scheme_name']}")

    logger.info(f"Extracted text from {len(documents)} pages")

    # 4. Chunk documents
    chunks = process_all_documents(documents)
    logger.info(f"Total chunks created: {len(chunks)}")

    if not chunks:
        logger.error("No chunks created. Exiting.")
        return

    # 5. Embed and store in ChromaDB
    logger.info("Embedding and storing chunks in ChromaDB...")
    embed_and_store(chunks)

    elapsed_time = time.time() - start_time

    # Print summary
    print("\n" + "=" * 50)
    print("INGESTION SUMMARY")
    print("=" * 50)
    print(f"Total URLs Scraped   : {len(scraped_data)}")
    print(f"Total Documents Extracted: {len(documents)}")
    print(f"Total Chunks Created : {len(chunks)}")
    print(f"Time Elapsed         : {elapsed_time:.2f} seconds")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
