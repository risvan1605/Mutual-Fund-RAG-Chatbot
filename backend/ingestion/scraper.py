"""
Web scraper — fetches raw HTML from Groww scheme pages.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
TIMEOUT = 10
MAX_RETRIES = 2
RATE_LIMIT_DELAY = 1.0  # seconds


def scrape_url(url: str, retries: int = MAX_RETRIES) -> Optional[str]:
    """
    Scrapes a single URL and returns the raw HTML content.
    Includes retry logic and basic error handling.
    """
    for attempt in range(retries + 1):
        try:
            logger.info(f"Scraping URL (Attempt {attempt + 1}/{retries + 1}): {url}")
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except RequestException as e:
            logger.warning(f"Failed to scrape {url} on attempt {attempt + 1}: {e}")
            if attempt < retries:
                time.sleep(RATE_LIMIT_DELAY * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"Max retries reached for {url}")
                return None


def scrape_all_sources(sources_path: str) -> List[Dict]:
    """
    Loads sources.json and scrapes all URLs, returning a list of dictionaries
    containing the metadata and raw HTML.
    """
    path = Path(sources_path)
    if not path.exists():
        logger.error(f"Sources file not found: {sources_path}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse sources JSON: {e}")
        return []

    results = []
    scraped_date = datetime.now().strftime("%Y-%m-%d")

    amcs = data.get("sources", [])
    total_schemes = sum(len(amc.get("schemes", [])) for amc in amcs)
    logger.info(f"Found {total_schemes} schemes to scrape across {len(amcs)} AMCs.")

    processed = 0
    for amc_data in amcs:
        amc_name = amc_data.get("amc", "Unknown AMC")
        for scheme in amc_data.get("schemes", []):
            processed += 1
            url = scheme.get("url")
            scheme_name = scheme.get("name", "Unknown Scheme")
            category = scheme.get("category", "Unknown Category")

            if not url:
                logger.warning(f"Skipping {scheme_name}: No URL provided.")
                continue

            logger.info(f"[{processed}/{total_schemes}] Processing {scheme_name}...")

            html = scrape_url(url)
            if html:
                results.append(
                    {
                        "url": url,
                        "html": html,
                        "scheme_name": scheme_name,
                        "amc": amc_name,
                        "category": category,
                        "scraped_date": scraped_date,
                    }
                )
                logger.info(f"Successfully scraped {scheme_name}")
            else:
                logger.error(f"Failed to scrape {scheme_name} completely.")

            # Rate limiting
            if processed < total_schemes:
                logger.debug(f"Waiting {RATE_LIMIT_DELAY}s before next request...")
                time.sleep(RATE_LIMIT_DELAY)

    logger.info(
        f"Scraping completed. Successfully scraped {len(results)}/{total_schemes} URLs."
    )
    return results
