"""
Project 20 — Stock Market Analysis Agent
Complete working solution.

Usage:
    python solution.py AAPL
    python solution.py RELIANCE.NS TCS.NS INFY.NS
    python solution.py NVDA AAPL MSFT --pdf

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
# Step 1 — API Setup
# ---------------------------------------------------------------------------

def setup_check() -> tuple[anthropic.Anthropic, str]:
    """Load and validate API keys. Return (client, news_api_key)."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    news_key = os.getenv("NEWS_API_KEY", "")

    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. Add it to your .env file:\n"
            "  ANTHROPIC_API_KEY=sk-ant-..."
        )
    if not api_key.startswith("sk-ant-"):
        raise ValueError(
            f"ANTHROPIC_API_KEY looks invalid (should start with 'sk-ant-'): {api_key[:12]}..."
        )
    if not news_key:
        print("  Warning: NEWS_API_KEY not set — news section will be skipped.")

    client = anthropic.Anthropic(api_key=api_key)
    return client, news_key


# ---------------------------------------------------------------------------
# Step 2 — Price Data
# ---------------------------------------------------------------------------

def fetch_price_data(ticker: str) -> pd.DataFrame:
    """Download 1 year of daily OHLCV. Raise ValueError for invalid tickers."""
    df = yf.download(ticker, period="1y", auto_adjust=True, progress=False)

    if df.empty:
        raise ValueError(
            f"No price data found for ticker '{ticker}'. "
            "Check the symbol — Indian tickers need the .NS or .BO suffix."
        )

    # yfinance >= 0.2.x returns MultiIndex columns when downloading a single
    # ticker with auto_adjust. Flatten if needed.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


# ---------------------------------------------------------------------------
# Step 3 — Technical Indicators
# ---------------------------------------------------------------------------

def compute_indicators(df: pd.DataFrame) -> dict:
    """Compute all TA indicators from price DataFrame. Return flat dict."""
    close = df["Close"]
    volume = df["Volume"]

    # Moving averages
    dma_50 = close.rolling(50).mean()
    dma_200 = close.rolling(200).mean()

    # RSI (14-period)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    rsi = (100 - (100 / (1 + rs))).iloc[-1]

    # MACD (12, 26, 9)
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    # Bollinger Bands (20-period, 2 std)
    sma_20 = close.rolling(20).mean()
    std_20 = close.rolling(20).std()
    bb_upper = sma_20 + (2 * std_20)
    bb_lower = sma_20 - (2 * std_20)

    def r(val):
        try:
            v = float(val.iloc[-1]) if hasattr(val, "iloc") else float(val)
            return round(v, 2) if not math.isnan(v) else None
        except Exception:
            return None

    return {
        "current_price": r(close),
        "high_52w": r(close.max()),
        "low_52w": r(close.min()),
        "dma_50": r(dma_50),
        "dma_200": r(dma_200),
        "rsi": r(rsi),
        "macd": r(macd_line),
        "macd_signal": r(signal_line),
        "macd_hist": r(histogram),
        "bb_upper": r(bb_upper),
        "bb_middle": r(sma_20),
        "bb_lower": r(bb_lower),
        "volume_avg_20": round(float(volume.rolling(20).mean().iloc[-1])),
    }


def _rsi_signal(rsi) -> str:
    if rsi is None:
        return "N/A"
    if rsi > 70:
        return "Overbought"
    if rsi < 30:
        return "Oversold"
    return "Neutral"


# ---------------------------------------------------------------------------
# Step 4 — Fundamentals
# ---------------------------------------------------------------------------

def fetch_fundamentals(ticker: str) -> dict:
    """Fetch key fundamental ratios from yfinance .info."""
    info = yf.Ticker(ticker).info

    roe = info.get("returnOnEquity", None)
    roe_pct = f"{round(roe * 100, 1)}%" if isinstance(roe, float) else "N/A"

    div_yield = info.get("dividendYield", None)
    div_str = f"{round(div_yield * 100, 2)}%" if isinstance(div_yield, float) else "N/A"

    return {
        "name": info.get("shortName", ticker),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "pb_ratio": info.get("priceToBook", "N/A"),
        "debt_to_equity": info.get("debtToEquity", "N/A"),
        "roe": roe_pct,
        "market_cap": _format_market_cap(info.get("marketCap", None)),
        "dividend_yield": div_str,
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
    }


def _format_market_cap(value) -> str:
    """Format raw integer market cap as $2.94T, $150.3B, $400M."""
    if not isinstance(value, (int, float)) or math.isnan(value):
        return "N/A"
    value = float(value)
    if value >= 1e12:
        return f"${value / 1e12:.2f}T"
    if value >= 1e9:
        return f"${value / 1e9:.1f}B"
    if value >= 1e6:
        return f"${value / 1e6:.0f}M"
    return f"${value:,.0f}"


# ---------------------------------------------------------------------------
# Step 5 — News and Sentiment
# ---------------------------------------------------------------------------

def fetch_news(ticker: str, api_key: str) -> list[dict]:
    """Fetch last 10 news articles from NewsAPI. Return [] on failure."""
    if not api_key:
        return []

    # Use base ticker without exchange suffix for better news results
    query = ticker.split(".")[0]

    try:
        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "pageSize": 10,
                "sortBy": "publishedAt",
                "language": "en",
                "apiKey": api_key,
            },
            timeout=10,
        )
        if response.status_code != 200:
            print(f"  Warning: NewsAPI returned {response.status_code} — skipping news.")
            return []

        articles = response.json().get("articles", [])
        return [
            {"title": a.get("title", ""), "description": a.get("description", "")}
            for a in articles
            if a.get("title")
        ]
    except Exception as exc:
        print(f"  Warning: News fetch failed ({exc}) — skipping news section.")
        return []


def score_news_sentiment(
    articles: list[dict], ticker: str, client: anthropic.Anthropic
) -> list[dict]:
    """Send all articles to Claude. Return list of {headline, sentiment, reasoning}."""
    if not articles:
        return []

    numbered = "\n".join(
        f"{i+1}. {a['title']}" for i, a in enumerate(articles)
    )

    prompt = f"""You are a financial analyst. Analyze the sentiment of each headline
about {ticker} stock. Respond with a raw JSON array only — no markdown, no explanation
outside the JSON.

Each item must have exactly these keys:
- "headline": the original headline text
- "sentiment": one of "bullish", "bearish", or "neutral"
- "reasoning": one sentence explaining the signal

Headlines:
{numbered}

Respond with the JSON array only."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if Claude wraps its response
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("  Warning: Could not parse sentiment JSON — returning raw articles.")
        return [{"headline": a["title"], "sentiment": "neutral", "reasoning": "parse error"} for a in articles]


# ---------------------------------------------------------------------------
# Step 6 — Earnings Trend
# ---------------------------------------------------------------------------

def fetch_earnings(ticker: str) -> list[dict]:
    """Fetch last 4 quarters of revenue and net income."""
    try:
        financials = yf.Ticker(ticker).quarterly_financials
        if financials is None or financials.empty:
            return []

        # Transpose: quarters become row index
        df = financials.T.sort_index(ascending=False)

        results = []
        for i, (date, row) in enumerate(df.iterrows()):
            if i >= 4:
                break

            revenue = None
            net_income = None

            # Row labels vary — try common names
            for rev_key in ["Total Revenue", "Revenue"]:
                if rev_key in row.index:
                    revenue = row[rev_key]
                    break
            for inc_key in ["Net Income", "Net Income Common Stockholders"]:
                if inc_key in row.index:
                    net_income = row[inc_key]
                    break

            quarter_label = date.strftime("Q%m %Y") if hasattr(date, "strftime") else str(date)

            results.append({
                "quarter": quarter_label,
                "revenue": _format_market_cap(revenue) if revenue is not None else "N/A",
                "net_income": _format_market_cap(net_income) if net_income is not None else "N/A",
            })

        return results

    except Exception as exc:
        print(f"  Warning: Earnings fetch failed ({exc}) — skipping earnings section.")
        return []


# ---------------------------------------------------------------------------
# Step 7 — Peer Comparison
# ---------------------------------------------------------------------------

def fetch_peers(peer_tickers: list[str]) -> list[dict]:
    """Fetch P/E and revenue growth for each peer. Skip failures silently."""
    peers = []
    for peer in peer_tickers:
        try:
            info = yf.Ticker(peer).info
            rev_growth = info.get("revenueGrowth", None)
            rev_growth_str = f"{round(rev_growth * 100, 1)}%" if isinstance(rev_growth, float) else "N/A"
            peers.append({
                "ticker": peer,
                "name": info.get("shortName", peer),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "revenue_growth": rev_growth_str,
            })
        except Exception:
            pass
    return peers


# ---------------------------------------------------------------------------
# Step 8 — Briefing Packager + Claude Analyst
# ---------------------------------------------------------------------------

def build_briefing(
    ticker: str,
    indicators: dict,
    fundamentals: dict,
    news_scored: list[dict],
    earnings: list[dict],
    peers: list[dict],
) -> str:
    """Format all data into a structured briefing text for Claude."""
    today = datetime.now().strftime("%Y-%m-%d")
    sections = [f"=== STOCK ANALYSIS DATA: {ticker} (as of {today}) ===\n"]

    # --- Price & Technical ---
    ind = indicators
    rsi_signal = _rsi_signal(ind.get("rsi"))
    sections.append("--- PRICE & TECHNICAL INDICATORS ---")
    sections.append(f"Current Price:     {ind.get('current_price', 'N/A')}")
    sections.append(f"52-Week High:      {ind.get('high_52w', 'N/A')}   52-Week Low: {ind.get('low_52w', 'N/A')}")
    sections.append(f"50-Day DMA:        {ind.get('dma_50', 'N/A')}   200-Day DMA: {ind.get('dma_200', 'N/A')}")
    sections.append(f"RSI (14):          {ind.get('rsi', 'N/A')}   Signal: {rsi_signal}")
    sections.append(f"MACD:              {ind.get('macd', 'N/A')}   Signal Line: {ind.get('macd_signal', 'N/A')}   Histogram: {ind.get('macd_hist', 'N/A')}")
    sections.append(f"Bollinger Upper:   {ind.get('bb_upper', 'N/A')}   Middle: {ind.get('bb_middle', 'N/A')}   Lower: {ind.get('bb_lower', 'N/A')}")
    sections.append(f"Volume (20-day avg): {ind.get('volume_avg_20', 'N/A'):,}\n")

    # --- Fundamentals ---
    fund = fundamentals
    sections.append("--- FUNDAMENTAL DATA ---")
    sections.append(f"Company:           {fund.get('name', ticker)}")
    sections.append(f"Market Cap:        {fund.get('market_cap', 'N/A')}")
    sections.append(f"P/E Ratio:         {fund.get('pe_ratio', 'N/A')}")
    sections.append(f"P/B Ratio:         {fund.get('pb_ratio', 'N/A')}")
    sections.append(f"Debt-to-Equity:    {fund.get('debt_to_equity', 'N/A')}")
    sections.append(f"ROE:               {fund.get('roe', 'N/A')}")
    sections.append(f"Dividend Yield:    {fund.get('dividend_yield', 'N/A')}")
    sections.append(f"Sector:            {fund.get('sector', 'N/A')}")
    sections.append(f"Industry:          {fund.get('industry', 'N/A')}\n")

    # --- News Sentiment ---
    if news_scored:
        counts = {"bullish": 0, "bearish": 0, "neutral": 0}
        for item in news_scored:
            s = item.get("sentiment", "neutral").lower()
            counts[s] = counts.get(s, 0) + 1

        sections.append("--- NEWS SENTIMENT (last 10 articles) ---")
        sections.append(f"Overall: {counts['bullish']} Bullish | {counts['neutral']} Neutral | {counts['bearish']} Bearish")
        for i, item in enumerate(news_scored, 1):
            sections.append(
                f"{i}. [{item.get('sentiment','?').upper()}] {item.get('headline','')} — {item.get('reasoning','')}"
            )
        sections.append("")
    else:
        sections.append("--- NEWS SENTIMENT ---")
        sections.append("News data unavailable for this analysis.\n")

    # --- Earnings Trend ---
    if earnings:
        sections.append("--- EARNINGS TREND (last 4 quarters) ---")
        for q in earnings:
            sections.append(f"{q['quarter']}: Revenue {q['revenue']}  | Net Income {q['net_income']}")
        sections.append("")
    else:
        sections.append("--- EARNINGS TREND ---")
        sections.append("Earnings data not available.\n")

    # --- Competitor Comparison ---
    if peers:
        sections.append("--- COMPETITOR COMPARISON ---")
        header = f"{'Ticker':<10} | {'P/E':>8} | {'Rev Growth':>12}"
        sections.append(header)
        sections.append("-" * len(header))

        # Include subject ticker first
        pe = fundamentals.get("pe_ratio", "N/A")
        sections.append(f"{ticker:<10} | {str(pe):>8} | {'(subject)':>12}")

        for p in peers:
            sections.append(f"{p['ticker']:<10} | {str(p.get('pe_ratio','N/A')):>8} | {p.get('revenue_growth','N/A'):>12}")
        sections.append("")
    else:
        sections.append("--- COMPETITOR COMPARISON ---")
        sections.append("No peer data available.\n")

    return "\n".join(sections)


def generate_report(briefing: str, ticker: str, client: anthropic.Anthropic) -> str:
    """Send briefing to Claude analyst. Return full report text."""
    system_prompt = (
        "You are a senior equity research analyst with 20 years of experience. "
        "You are rigorous, data-driven, and clear. You do not speculate beyond "
        "the provided data. When data is missing, you note it explicitly rather "
        "than inferring. Your reports are read by institutional investors."
    )

    user_prompt = f"""You have received a structured data briefing for {ticker}.
Based solely on the data provided, write a professional equity research report.

<data>
{briefing}
</data>

Write the following sections in order:

## Executive Summary
Two to three paragraphs. What is the key story for this stock right now?
Synthesize the technical, fundamental, and sentiment picture into a coherent narrative.

## Technical Analysis
Interpret the price action and indicators. Reference the actual RSI, MACD, and DMA values.
What trend is the stock in? Where is it relative to its Bollinger Bands?

## Fundamental Analysis
Evaluate the valuation ratios. Is the P/E justified relative to peers and growth?
Comment on balance sheet health using the debt-to-equity and ROE.
What does the earnings trend say about the business trajectory?

## Risk Factors
Three numbered, specific risks. Avoid generic statements like "market risk" —
tie each risk to actual data points in the briefing.

## Recommendation
**Rating:** Buy / Hold / Sell
**Price Target:** (provide a target based on peer P/E or earnings growth, or state "Insufficient data for target")
**Rationale:** Two to three sentences explaining the call.

Use only the provided data. Do not invent statistics or reference events not in the briefing."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return response.content[0].text


# ---------------------------------------------------------------------------
# Step 9 — Save Report
# ---------------------------------------------------------------------------

def save_report(report_text: str, ticker: str, output_dir: str = "output") -> str:
    """Write {TICKER}_analysis.md. Return file path."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{ticker.replace('.', '_')}_analysis.md"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Equity Research Report: {ticker}\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n")
        f.write(report_text)
    return path


def save_pdf(report_text: str, ticker: str, output_dir: str = "output") -> str:
    """Generate PDF from report text using reportlab. Return file path."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except ImportError:
        print("  Warning: reportlab not installed — skipping PDF. Run: pip install reportlab")
        return ""

    os.makedirs(output_dir, exist_ok=True)
    filename = f"{ticker.replace('.', '_')}_analysis.pdf"
    path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        path,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"Equity Research Report: {ticker}", styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    for line in report_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.1 * inch))
            continue

        # Map markdown heading levels to styles
        if stripped.startswith("## "):
            text = stripped[3:].replace("**", "").replace("*", "")
            story.append(Paragraph(text, styles["Heading2"]))
        elif stripped.startswith("# "):
            text = stripped[2:].replace("**", "").replace("*", "")
            story.append(Paragraph(text, styles["Heading1"]))
        else:
            # Clean markdown bold/italic
            text = stripped.replace("**", "").replace("*", "")
            # Escape XML special chars for reportlab
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(text, styles["Normal"]))

    doc.build(story)
    return path


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------

def main(ticker: str, peer_tickers: list[str], generate_pdf: bool = False):
    print(f"\nStock Market Analysis Agent")
    print("=" * 40)
    print(f"Ticker:  {ticker}")
    print(f"Peers:   {', '.join(peer_tickers)}\n")

    # Step 1 — Setup
    print("[1/8] Verifying API keys...", end=" ", flush=True)
    client, news_api_key = setup_check()
    print("done")

    # Step 2 — Price data
    print("[2/8] Fetching 1-year price data...", end=" ", flush=True)
    df = fetch_price_data(ticker)
    print(f"done  ({len(df)} trading days)")

    # Step 3 — Technical indicators
    print("[3/8] Computing technical indicators...", end=" ", flush=True)
    indicators = compute_indicators(df)
    print(f"done  (RSI: {indicators.get('rsi', 'N/A')}, MACD: {indicators.get('macd', 'N/A')})")

    # Step 4 — Fundamentals
    print("[4/8] Fetching fundamentals...", end=" ", flush=True)
    fundamentals = fetch_fundamentals(ticker)
    print(f"done  (P/E: {fundamentals.get('pe_ratio', 'N/A')}, Market Cap: {fundamentals.get('market_cap', 'N/A')})")

    # Step 5 — News + sentiment
    print("[5/8] Fetching and scoring news...", end=" ", flush=True)
    articles = fetch_news(ticker, news_api_key)
    if articles:
        news_scored = score_news_sentiment(articles, ticker, client)
        counts = {s: sum(1 for n in news_scored if n.get("sentiment") == s) for s in ["bullish", "neutral", "bearish"]}
        print(f"done  ({counts['bullish']} bullish, {counts['neutral']} neutral, {counts['bearish']} bearish)")
    else:
        news_scored = []
        print("skipped (no NEWS_API_KEY or fetch failed)")

    # Step 6 — Earnings
    print("[6/8] Fetching earnings trend...", end=" ", flush=True)
    earnings = fetch_earnings(ticker)
    print(f"done  ({len(earnings)} quarters)" if earnings else "skipped")

    # Step 7 — Peers
    print("[7/8] Fetching competitor data...", end=" ", flush=True)
    peers = fetch_peers(peer_tickers)
    print(f"done  ({len(peers)} peers loaded)")

    # Step 8 — Build briefing + generate report
    print("[8/8] Building briefing and calling Claude analyst...", end=" ", flush=True)
    briefing = build_briefing(ticker, indicators, fundamentals, news_scored, earnings, peers)
    report_text = generate_report(briefing, ticker, client)
    print("done")

    # Step 9 — Save outputs
    print("\nSaving report...", end=" ", flush=True)
    md_path = save_report(report_text, ticker)
    print(f"done")
    print(f"  Report saved: {md_path}")

    if generate_pdf:
        print("Generating PDF...", end=" ", flush=True)
        pdf_path = save_pdf(report_text, ticker)
        if pdf_path:
            print(f"done\n  PDF saved: {pdf_path}")
        else:
            print("skipped")

    print(f"\nAnalysis complete for {ticker}.")
    return report_text


if __name__ == "__main__":
    ticker_arg = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    args = sys.argv[2:]
    generate_pdf_flag = "--pdf" in args
    peer_args = [a for a in args if not a.startswith("--")]
    if not peer_args:
        peer_args = ["MSFT", "GOOGL", "META"]
    main(ticker_arg, peer_args, generate_pdf=generate_pdf_flag)
