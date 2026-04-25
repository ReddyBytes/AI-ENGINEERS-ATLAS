"""
Project 20 — Stock Market Analysis Agent
Starter scaffold — implement each TODO to complete the agent.

Usage:
    python starter.py AAPL
    python starter.py RELIANCE.NS TCS.NS INFY.NS
    python starter.py NVDA AAPL MSFT --pdf

Requirements:
    pip install anthropic yfinance requests pandas numpy reportlab python-dotenv
"""

import os
import sys
import json
import math
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
import anthropic

warnings.filterwarnings("ignore")

load_dotenv()


# ---------------------------------------------------------------------------
# Step 1 — API Setup and Verification
# ---------------------------------------------------------------------------

def setup_check() -> tuple[anthropic.Anthropic, str]:
    """
    Load API keys, validate them, return (anthropic_client, news_api_key).
    Raise ValueError with a clear message if a key is missing.

    TODO:
    - Load ANTHROPIC_API_KEY from environment
    - Load NEWS_API_KEY from environment (can be empty string — warn, don't fail)
    - Validate that ANTHROPIC_API_KEY starts with 'sk-ant-'
    - Create and return anthropic.Anthropic() client and news_api_key string
    """
    # TODO: implement
    raise NotImplementedError("Step 1: implement setup_check()")


# ---------------------------------------------------------------------------
# Step 2 — Price Data
# ---------------------------------------------------------------------------

def fetch_price_data(ticker: str) -> pd.DataFrame:
    """
    Download 1 year of daily OHLCV for ticker.
    Return DataFrame with columns: Open, High, Low, Close, Volume.
    Raise ValueError if ticker is invalid or data is empty.

    TODO:
    - Use yfinance.download(ticker, period='1y', auto_adjust=True)
    - Validate the result is not empty
    - Return the DataFrame
    """
    # TODO: implement
    raise NotImplementedError("Step 2: implement fetch_price_data()")


# ---------------------------------------------------------------------------
# Step 3 — Technical Indicators
# ---------------------------------------------------------------------------

def compute_indicators(df: pd.DataFrame) -> dict:
    """
    Compute technical indicators from price DataFrame.
    Return dict with keys:
        current_price, high_52w, low_52w,
        dma_50, dma_200,
        rsi, macd, macd_signal, macd_hist,
        bb_upper, bb_middle, bb_lower,
        volume_avg_20

    All values should be floats rounded to 2 decimal places.

    TODO:
    - 50/200 DMA: rolling(N).mean()
    - RSI: delta → gain/loss → RS → RSI formula (window=14)
    - MACD: EMA(12) - EMA(26), signal = EMA(9) of MACD
    - Bollinger: SMA(20) ± 2*STD(20)
    """
    # TODO: implement
    raise NotImplementedError("Step 3: implement compute_indicators()")


# ---------------------------------------------------------------------------
# Step 4 — Fundamentals
# ---------------------------------------------------------------------------

def fetch_fundamentals(ticker: str) -> dict:
    """
    Fetch key fundamental ratios from yfinance .info.
    Return dict with safe defaults for missing fields.

    Keys to fetch:
        trailingPE, priceToBook, debtToEquity, returnOnEquity,
        marketCap, dividendYield, sector, industry, shortName

    TODO:
    - Use yfinance.Ticker(ticker).info
    - Use .get(key, 'N/A') for all fields
    - Format marketCap as string: $2.94T, $150.3B, etc.
    - Multiply returnOnEquity by 100 for percentage display
    """
    # TODO: implement
    raise NotImplementedError("Step 4: implement fetch_fundamentals()")


def _format_market_cap(value) -> str:
    """Format raw market cap integer as human-readable string."""
    # TODO: implement — handle T, B, M thresholds
    return str(value)


# ---------------------------------------------------------------------------
# Step 5 — News and Sentiment
# ---------------------------------------------------------------------------

def fetch_news(ticker: str, api_key: str) -> list[dict]:
    """
    Fetch last 10 news articles about ticker from NewsAPI.
    Return list of dicts with keys: title, description.
    Return empty list if api_key is empty or request fails.

    NewsAPI endpoint: https://newsapi.org/v2/everything
    Params: q=ticker, pageSize=10, sortBy=publishedAt, apiKey=api_key

    TODO:
    - Build the URL with requests.get params
    - Handle non-200 status codes gracefully
    - Return list of {title, description} dicts from response['articles']
    """
    # TODO: implement
    raise NotImplementedError("Step 5a: implement fetch_news()")


def score_news_sentiment(articles: list[dict], ticker: str, client: anthropic.Anthropic) -> list[dict]:
    """
    Send all articles to Claude in one call.
    Return list of dicts with keys: headline, sentiment, reasoning.
    sentiment must be one of: bullish, bearish, neutral.

    If articles is empty, return empty list.

    TODO:
    - Format all article titles into a numbered list in the prompt
    - Ask Claude to return a raw JSON array (no markdown fences)
    - Parse with json.loads — strip backticks if present
    - Return the parsed list
    """
    # TODO: implement
    raise NotImplementedError("Step 5b: implement score_news_sentiment()")


# ---------------------------------------------------------------------------
# Step 6 — Earnings Trend
# ---------------------------------------------------------------------------

def fetch_earnings(ticker: str) -> list[dict]:
    """
    Fetch last 4 quarters of revenue and net income.
    Return list of dicts: [{quarter, revenue, net_income}, ...]
    Return empty list if data is unavailable.

    TODO:
    - Use yfinance.Ticker(ticker).quarterly_financials
    - Transpose with .T to get quarters as rows
    - Look for 'Total Revenue' and 'Net Income' rows
    - Handle KeyError if either metric is missing
    - Format as: quarter = "Q1 2026", revenue/net_income as human-readable strings
    """
    # TODO: implement
    raise NotImplementedError("Step 6: implement fetch_earnings()")


# ---------------------------------------------------------------------------
# Step 7 — Peer Comparison
# ---------------------------------------------------------------------------

def fetch_peers(peer_tickers: list[str]) -> list[dict]:
    """
    Fetch P/E and revenue growth for each peer ticker.
    Return list of dicts: [{ticker, name, pe_ratio, revenue_growth}, ...]
    Skip any peer that raises an exception.

    TODO:
    - For each peer, call yfinance.Ticker(peer).info
    - Extract trailingPE and revenueGrowth (multiply by 100 for %)
    - Wrap each fetch in try/except — skip silently on failure
    """
    # TODO: implement
    raise NotImplementedError("Step 7: implement fetch_peers()")


# ---------------------------------------------------------------------------
# Step 8 — Briefing Packager and Claude Analyst
# ---------------------------------------------------------------------------

def build_briefing(
    ticker: str,
    indicators: dict,
    fundamentals: dict,
    news_scored: list[dict],
    earnings: list[dict],
    peers: list[dict],
) -> str:
    """
    Format all data into a structured multi-section briefing string.
    See 02_ARCHITECTURE.md for the expected format.

    TODO:
    - Assemble sections: Price & Technical, Fundamentals, News Sentiment,
      Earnings Trend, Competitor Comparison
    - Use clear section headers separated by ---
    - Compute sentiment counts (bullish/bearish/neutral) for the summary line
    """
    # TODO: implement
    raise NotImplementedError("Step 8a: implement build_briefing()")


def generate_report(briefing: str, ticker: str, client: anthropic.Anthropic) -> str:
    """
    Send briefing to Claude with equity analyst system prompt.
    Return the full report text.

    TODO:
    - Use the prompt structure from 02_ARCHITECTURE.md
    - Model: claude-sonnet-4-6
    - max_tokens: 4000
    - Return response.content[0].text
    """
    # TODO: implement
    raise NotImplementedError("Step 8b: implement generate_report()")


# ---------------------------------------------------------------------------
# Step 9 — Save Report
# ---------------------------------------------------------------------------

def save_report(report_text: str, ticker: str, output_dir: str = "output") -> str:
    """
    Create output_dir if needed. Write {TICKER}_analysis.md.
    Return the file path.

    TODO: implement
    """
    # TODO: implement
    raise NotImplementedError("Step 9a: implement save_report()")


def save_pdf(report_text: str, ticker: str, output_dir: str = "output") -> str:
    """
    Generate a PDF from report_text using reportlab.
    Return the PDF file path.

    TODO:
    - Use SimpleDocTemplate with getSampleStyleSheet()
    - Split report_text into lines, create Paragraph objects
    - Use Heading2 style for lines that start with '##'
    - Strip markdown syntax before rendering
    - Return the PDF path
    """
    # TODO: implement
    raise NotImplementedError("Step 9b: implement save_pdf()")


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------

def main(ticker: str, peer_tickers: list[str], generate_pdf: bool = False):
    """
    Orchestrate the full pipeline and print progress at each step.

    TODO:
    1. setup_check() → client, news_api_key
    2. fetch_price_data(ticker) → df
    3. compute_indicators(df) → indicators
    4. fetch_fundamentals(ticker) → fundamentals
    5. fetch_news(ticker, news_api_key) → articles
    6. score_news_sentiment(articles, ticker, client) → news_scored
    7. fetch_earnings(ticker) → earnings
    8. fetch_peers(peer_tickers) → peers
    9. build_briefing(...) → briefing
    10. generate_report(briefing, ticker, client) → report
    11. save_report(report, ticker) → md_path
    12. optionally save_pdf(report, ticker) → pdf_path
    """
    print(f"\nStock Market Analysis Agent")
    print(f"=" * 40)
    print(f"Ticker: {ticker}\n")

    # TODO: implement the orchestration steps above
    raise NotImplementedError("Wire up main()")


if __name__ == "__main__":
    ticker_arg = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    # Collect any additional args as peers, filtering out --pdf flag
    args = sys.argv[2:]
    generate_pdf_flag = "--pdf" in args
    peer_args = [a for a in args if not a.startswith("--")]
    if not peer_args:
        peer_args = ["MSFT", "GOOGL", "META"]
    main(ticker_arg, peer_args, generate_pdf=generate_pdf_flag)
