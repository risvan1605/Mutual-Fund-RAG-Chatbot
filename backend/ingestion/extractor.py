"""
Text extractor — parses HTML and extracts highly structured JSON data from Groww pages.
"""

import json
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


def extract_text(html: str) -> str:
    """
    Parses HTML to find the __NEXT_DATA__ JSON blob.
    Extracts structured factual data and returns it as a formatted Markdown text block.
    """
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")

    if not script_tag or not script_tag.string:
        logger.warning("Could not find __NEXT_DATA__ block in the HTML.")
        return ""

    try:
        data = json.loads(script_tag.string)
        props = data.get("props", {}).get("pageProps", {})
        mf = props.get("mfServerSideData", {})

        if not mf:
            logger.warning("mfServerSideData not found in JSON.")
            return ""

        # Extract fields safely
        scheme_name = mf.get("scheme_name", "Unknown Scheme")
        aum = mf.get("aum", "Unknown")
        nav = mf.get("nav", "Unknown")
        expense_ratio = mf.get("expense_ratio", "Unknown")
        min_sip = mf.get("min_sip_investment", "Unknown")
        min_lumpsum = mf.get("min_investment_amount", "Unknown")
        exit_load = mf.get("exit_load", "Unknown")
        category = mf.get("category", "Unknown")
        sub_category = mf.get("sub_category", "Unknown")
        risk = mf.get("risk", "Unknown")
        fund_manager = mf.get("fund_manager", "Unknown")
        launch_date = mf.get("launch_date", "Unknown")

        # Build a highly structured text representation for the embedder and LLM
        structured_text = f"""Scheme Name: {scheme_name}
Category: {category} ({sub_category})
Risk Level: {risk}
Asset Under Management (AUM): ₹{aum} Crores
Current NAV: ₹{nav}
Expense Ratio: {expense_ratio}%
Minimum SIP Investment: ₹{min_sip}
Minimum Lumpsum Investment: ₹{min_lumpsum}
Exit Load: {exit_load}
Fund Manager: {fund_manager}
Launch Date: {launch_date}"""

        return structured_text

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from __NEXT_DATA__: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error during JSON extraction: {e}")
        return ""
