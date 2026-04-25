"""
Project 21 — Company Deep-Dive Agent
Starter scaffold — implement each TODO to complete the multi-agent system.

Usage:
    python starter.py AAPL
    python starter.py "Apple"
    python starter.py "Reliance Industries"
    python starter.py TCS.NS
    python starter.py OpenAI

Requirements:
    pip install anthropic yfinance duckduckgo-search requests python-dotenv
"""

import os
import sys
import json
import time
import re
import warnings
from datetime import datetime

import requests
import yfinance as yf
from dotenv import load_dotenv
import anthropic

warnings.filterwarnings("ignore")

load_dotenv()


# ---------------------------------------------------------------------------
# Step 1 — Setup and Input Normalization
# ---------------------------------------------------------------------------

def setup() -> anthropic.Anthropic:
    """
    Load ANTHROPIC_API_KEY, validate it, return an Anthropic client.
    Raise ValueError with a clear message if the key is missing or invalid.

    TODO: implement
    """
    raise NotImplementedError("Step 1a: implement setup()")


def normalize_input(raw: str) -> dict:
    """
    Take a raw company name or ticker string.
    Return {"company_name": str, "ticker": str | None}.

    Ticker detection rule: all-caps, 1-6 characters, optional .NS / .BO suffix.
    If it looks like a ticker, set company_name = raw and ticker = raw.
    Otherwise set company_name = raw and ticker = None.

    TODO: implement
    """
    raise NotImplementedError("Step 1b: implement normalize_input()")


# ---------------------------------------------------------------------------
# Step 2 — Web Research Agent
# ---------------------------------------------------------------------------

class WebResearchAgent:
    """
    Runs three DuckDuckGo searches and returns structured results.
    """

    QUERIES = [
        "{company} company news 2025 2026",
        "{company} products services business model",
        "{company} CEO leadership strategy",
    ]

    def run(self, company_name: str) -> dict:
        """
        Run three searches and return:
        {
            "news": [{"title": str, "snippet": str, "url": str}, ...],
            "products": [...],
            "leadership": [...]
        }
        Each list has up to 5 results.

        TODO:
        - Import DDGS from duckduckgo_search
        - For each query template, format with company_name
        - Call ddgs.text(query, max_results=5) inside `with DDGS() as ddgs:`
        - Map result keys: body -> snippet, href -> url
        - Sleep 1 second between queries to avoid rate limiting
        - Return empty list on any exception for that query
        """
        raise NotImplementedError("Step 2: implement WebResearchAgent.run()")


# ---------------------------------------------------------------------------
# Step 3 — Financial Agent
# ---------------------------------------------------------------------------

class FinancialAgent:
    """
    Fetches public company financial data via yfinance.
    Gracefully handles private companies.
    """

    def run(self, identifier: str) -> dict:
        """
        Attempt yfinance lookup. Return financial dict or private-company flag.

        If info.get('marketCap') is None or missing → return:
            {"is_public": False, "reason": "No public listing found for '{identifier}'"}

        Otherwise return dict with:
            is_public, ticker, name, market_cap, revenue_ttm, revenue_growth,
            gross_margin, net_margin, debt_to_equity, current_ratio,
            free_cash_flow, pe_ratio

        TODO:
        - Use yfinance.Ticker(identifier).info
        - Check for marketCap as the public company guard
        - Format numeric values as human-readable strings
        - Use .get(key, 'N/A') for all fields
        """
        raise NotImplementedError("Step 3: implement FinancialAgent.run()")


# ---------------------------------------------------------------------------
# Step 4 — Competitor Identification
# ---------------------------------------------------------------------------

def identify_competitors(
    company_name: str, web_summary: str, client: anthropic.Anthropic
) -> list[str]:
    """
    Ask Claude to identify 3-4 competitor tickers or names.
    Return a list of strings (tickers if public, names if private).
    Return empty list on parse failure.

    TODO:
    - Build a prompt that gives Claude the company name + web_summary
    - Instruct Claude to return a raw JSON array of strings
    - Parse with json.loads — strip markdown fences if present
    - Return the list
    """
    raise NotImplementedError("Step 4: implement identify_competitors()")


# ---------------------------------------------------------------------------
# Step 5 — Competitor Agent
# ---------------------------------------------------------------------------

class CompetitorAgent:
    """
    Identifies competitors via Claude, then fetches their financial data.
    """

    def run(
        self, company_name: str, web_summary: str, client: anthropic.Anthropic
    ) -> list[dict]:
        """
        Phase 1: Call identify_competitors() to get list of identifiers.
        Phase 2: For each identifier, try yfinance.Ticker(id).info.
                 Build a dict with: identifier, name, market_cap, pe_ratio,
                 revenue_growth, is_public.
                 Wrap each fetch in try/except — skip failures silently.

        TODO: implement
        """
        raise NotImplementedError("Step 5: implement CompetitorAgent.run()")


# ---------------------------------------------------------------------------
# Step 6 — Data Packager
# ---------------------------------------------------------------------------

def build_briefing(
    company: str,
    web_data: dict,
    financial_data: dict,
    competitor_data: list[dict],
) -> str:
    """
    Format all agent outputs into a structured briefing string.
    See 02_ARCHITECTURE.md for the expected section format.

    Sections:
    1. COMPANY PROFILE (web research results — news, products, leadership)
    2. FINANCIAL DATA (from FinancialAgent)
    3. COMPETITOR DATA (from CompetitorAgent)

    TODO:
    - Format each section with clear headers separated by ---
    - Include actual snippets from web results (up to 150 chars each)
    - Mark financial section clearly as public/private
    """
    raise NotImplementedError("Step 6: implement build_briefing()")


def _build_web_summary(web_data: dict, max_headlines: int = 3) -> str:
    """
    Build a short text summary from web news results.
    Used as context for competitor identification.

    TODO: join the first max_headlines news titles into a string.
    """
    raise NotImplementedError("Step 6b: implement _build_web_summary()")


# ---------------------------------------------------------------------------
# Step 7 — Claude Synthesis Agent
# ---------------------------------------------------------------------------

def synthesize_report(briefing: str, company: str, client: anthropic.Anthropic) -> str:
    """
    Send briefing to Claude with intelligence analyst system prompt.
    Return full report text.

    Required sections: Company Overview, Recent News & Sentiment,
    Financial Health, Competitive Position, SWOT Analysis, Key Risks.

    TODO:
    - System prompt: intelligence analyst, data-driven, no speculation beyond provided data
    - User prompt: structured section instructions with <data> XML block
    - Model: claude-sonnet-4-6, max_tokens: 4000
    - Return response.content[0].text
    """
    raise NotImplementedError("Step 7: implement synthesize_report()")


# ---------------------------------------------------------------------------
# Step 8 — Report Saver
# ---------------------------------------------------------------------------

def save_report(report_text: str, company: str, output_dir: str = "output") -> str:
    """
    Save report as {company_slug}_deep_dive.md.
    company_slug: lowercase, spaces → underscores, remove special chars.
    Return the file path.

    TODO: implement
    """
    raise NotImplementedError("Step 8: implement save_report()")


def _company_slug(company: str) -> str:
    """Convert company name to filesystem-safe slug. TODO: implement."""
    raise NotImplementedError("Implement _company_slug()")


# ---------------------------------------------------------------------------
# Step 9 — Orchestrator
# ---------------------------------------------------------------------------

def main(raw_input: str):
    """
    Orchestrate the full pipeline in order:
    1. setup() → client
    2. normalize_input() → {company_name, ticker}
    3. WebResearchAgent().run() → web_data
    4. FinancialAgent().run() → financial_data
    5. _build_web_summary() → web_summary
    6. CompetitorAgent().run() → competitor_data
    7. build_briefing() → briefing
    8. synthesize_report() → report_text
    9. save_report() → path

    Print status at each step.

    TODO: implement
    """
    print(f"\nCompany Deep-Dive Agent")
    print("=" * 40)
    print(f"Target: {raw_input}\n")
    raise NotImplementedError("Step 9: implement main()")


# ---------------------------------------------------------------------------
# Step 10 — CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python starter.py <company name or ticker>")
        print("Examples:")
        print("  python starter.py AAPL")
        print('  python starter.py "Apple"')
        print('  python starter.py TCS.NS')
        sys.exit(1)

    # Join all args in case company name has spaces and no quotes
    raw = " ".join(sys.argv[1:])
    main(raw)
