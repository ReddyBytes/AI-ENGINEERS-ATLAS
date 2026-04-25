"""
Project 21 — Company Deep-Dive Agent
Complete working solution.

Usage:
    python solution.py AAPL
    python solution.py "Apple"
    python solution.py "Reliance Industries"
    python solution.py TCS.NS
    python solution.py OpenAI

Requirements:
    pip install anthropic yfinance duckduckgo-search requests python-dotenv
"""

import os
import sys
import json
import math
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
# Helpers
# ---------------------------------------------------------------------------

def _format_number(value) -> str:
    """Format raw integer/float as $2.94T, $150.3B, $400M, N/A."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    if v >= 1e12:
        return f"${v / 1e12:.2f}T"
    if v >= 1e9:
        return f"${v / 1e9:.1f}B"
    if v >= 1e6:
        return f"${v / 1e6:.0f}M"
    return f"${v:,.0f}"


def _pct(value) -> str:
    """Format decimal (0.147) as percentage string (14.7%)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "N/A"
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def _strip_json_fences(text: str) -> str:
    """Remove markdown code fences from a string."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove opening fence (```json or ```)
        lines = lines[1:]
        # Remove closing fence
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


# ---------------------------------------------------------------------------
# Step 1 — Setup and Input Normalization
# ---------------------------------------------------------------------------

def setup() -> anthropic.Anthropic:
    """Load and validate ANTHROPIC_API_KEY. Return Anthropic client."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. Add it to your .env file:\n"
            "  ANTHROPIC_API_KEY=sk-ant-..."
        )
    if not api_key.startswith("sk-ant-"):
        raise ValueError(
            f"ANTHROPIC_API_KEY looks invalid (should start with 'sk-ant-'): {api_key[:12]}..."
        )
    return anthropic.Anthropic(api_key=api_key)


def normalize_input(raw: str) -> dict:
    """
    Detect whether raw is a ticker symbol or a company name.
    Returns {"company_name": str, "ticker": str | None}.
    """
    raw = raw.strip()
    # Ticker pattern: 1-6 uppercase letters, optional .NS or .BO or .BSE suffix
    ticker_pattern = re.compile(r"^[A-Z]{1,6}(\.(NS|BO|BSE))?$")
    if ticker_pattern.match(raw):
        return {"company_name": raw, "ticker": raw}
    else:
        return {"company_name": raw, "ticker": None}


# ---------------------------------------------------------------------------
# Step 2 — Web Research Agent
# ---------------------------------------------------------------------------

class WebResearchAgent:
    """
    Runs three DuckDuckGo searches and returns structured results.
    Gracefully handles rate limits and empty results.
    """

    QUERY_TEMPLATES = [
        "{company} company news 2025 2026",
        "{company} products services business model revenue",
        "{company} CEO leadership executive strategy",
    ]

    RESULT_KEYS = ["news", "products", "leadership"]

    def run(self, company_name: str) -> dict:
        """Run three searches. Return {news, products, leadership} lists."""
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            print("  Warning: duckduckgo-search not installed. Run: pip install duckduckgo-search")
            return {"news": [], "products": [], "leadership": []}

        results = {}
        for key, template in zip(self.RESULT_KEYS, self.QUERY_TEMPLATES):
            query = template.format(company=company_name)
            try:
                with DDGS() as ddgs:
                    raw_results = list(ddgs.text(query, max_results=5))
                results[key] = [
                    {
                        "title": r.get("title", ""),
                        "snippet": r.get("body", "")[:200],
                        "url": r.get("href", ""),
                    }
                    for r in raw_results
                    if r.get("title")
                ]
            except Exception as exc:
                print(f"  Warning: search failed for '{query}' ({exc})")
                results[key] = []

            # Be polite to DuckDuckGo between queries
            time.sleep(1)

        return results


# ---------------------------------------------------------------------------
# Step 3 — Financial Agent
# ---------------------------------------------------------------------------

class FinancialAgent:
    """
    Fetches financial data for public companies via yfinance.
    Gracefully handles private/unlisted companies.
    """

    def run(self, identifier: str) -> dict:
        """
        Attempt yfinance lookup. Return financial dict or private-company flag.
        """
        if not identifier:
            return {"is_public": False, "reason": "No identifier provided"}

        try:
            info = yf.Ticker(identifier).info
        except Exception as exc:
            return {"is_public": False, "reason": f"yfinance error: {exc}"}

        # Guard: if no marketCap, treat as private/unlisted
        market_cap = info.get("marketCap")
        if not market_cap:
            return {
                "is_public": False,
                "reason": f"No public listing found for '{identifier}'",
            }

        return {
            "is_public": True,
            "ticker": info.get("symbol", identifier),
            "name": info.get("shortName", identifier),
            "market_cap": _format_number(market_cap),
            "revenue_ttm": _format_number(info.get("totalRevenue")),
            "revenue_growth": _pct(info.get("revenueGrowth")),
            "gross_margin": _pct(info.get("grossMargins")),
            "net_margin": _pct(info.get("profitMargins")),
            "debt_to_equity": info.get("debtToEquity", "N/A"),
            "current_ratio": info.get("currentRatio", "N/A"),
            "free_cash_flow": _format_number(info.get("freeCashflow")),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
        }


# ---------------------------------------------------------------------------
# Step 4 — Competitor Identification
# ---------------------------------------------------------------------------

def identify_competitors(
    company_name: str, web_summary: str, client: anthropic.Anthropic
) -> list[str]:
    """
    Ask Claude to identify 3-4 competitors. Return list of tickers or names.
    Returns empty list on failure.
    """
    prompt = f"""You are a financial analyst. Identify the top 3 to 4 direct competitors of {company_name}.

Context about {company_name} from recent news:
{web_summary}

Respond with a JSON array of ticker symbols for public competitors,
or company names for private ones.
Example: ["MSFT", "GOOGL", "OpenAI", "META"]

Respond with the JSON array only — no explanation, no markdown."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = _strip_json_fences(response.content[0].text)
        return json.loads(raw)
    except Exception as exc:
        print(f"  Warning: competitor identification failed ({exc})")
        return []


# ---------------------------------------------------------------------------
# Step 5 — Competitor Agent
# ---------------------------------------------------------------------------

class CompetitorAgent:
    """
    Identifies competitors, then fetches their financial snapshots.
    """

    def run(
        self, company_name: str, web_summary: str, client: anthropic.Anthropic
    ) -> list[dict]:
        """
        Phase 1: identify competitors.
        Phase 2: fetch yfinance data for each.
        """
        identifiers = identify_competitors(company_name, web_summary, client)
        if not identifiers:
            return []

        competitors = []
        for identifier in identifiers:
            try:
                info = yf.Ticker(identifier).info
                market_cap = info.get("marketCap")

                if market_cap:
                    competitors.append({
                        "identifier": identifier,
                        "name": info.get("shortName", identifier),
                        "market_cap": _format_number(market_cap),
                        "pe_ratio": info.get("trailingPE", "N/A"),
                        "revenue_growth": _pct(info.get("revenueGrowth")),
                        "sector": info.get("sector", "N/A"),
                        "is_public": True,
                    })
                else:
                    competitors.append({
                        "identifier": identifier,
                        "name": identifier,
                        "market_cap": "Private",
                        "pe_ratio": "N/A",
                        "revenue_growth": "N/A",
                        "sector": "N/A",
                        "is_public": False,
                    })
            except Exception:
                competitors.append({
                    "identifier": identifier,
                    "name": identifier,
                    "market_cap": "N/A",
                    "pe_ratio": "N/A",
                    "revenue_growth": "N/A",
                    "sector": "N/A",
                    "is_public": False,
                })

        return competitors


# ---------------------------------------------------------------------------
# Step 6 — Data Packager
# ---------------------------------------------------------------------------

def build_briefing(
    company: str,
    web_data: dict,
    financial_data: dict,
    competitor_data: list[dict],
) -> str:
    """Format all agent outputs into a structured briefing string for Claude."""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [f"=== COMPANY INTELLIGENCE BRIEFING: {company} (compiled {today}) ===\n"]

    # --- Web Research ---
    lines.append("--- COMPANY PROFILE (from web research) ---")

    # News section
    news = web_data.get("news", [])
    if news:
        lines.append(f"\nRecent News:")
        for i, r in enumerate(news, 1):
            snippet = r["snippet"][:150] if r["snippet"] else "(no snippet)"
            lines.append(f"  {i}. [{r['title']}]")
            lines.append(f"     {snippet}")
    else:
        lines.append("\nRecent News: No results found.")

    # Products/business section
    products = web_data.get("products", [])
    if products:
        lines.append(f"\nProducts & Business Model:")
        for i, r in enumerate(products, 1):
            snippet = r["snippet"][:150] if r["snippet"] else "(no snippet)"
            lines.append(f"  {i}. [{r['title']}]")
            lines.append(f"     {snippet}")
    else:
        lines.append("\nProducts & Business Model: No results found.")

    # Leadership section
    leadership = web_data.get("leadership", [])
    if leadership:
        lines.append(f"\nLeadership & Strategy:")
        for i, r in enumerate(leadership[:3], 1):
            snippet = r["snippet"][:150] if r["snippet"] else "(no snippet)"
            lines.append(f"  {i}. [{r['title']}]")
            lines.append(f"     {snippet}")
    else:
        lines.append("\nLeadership & Strategy: No results found.")

    lines.append("")

    # --- Financial Data ---
    lines.append("--- FINANCIAL DATA ---")
    if financial_data.get("is_public"):
        fd = financial_data
        lines.append(f"Status:           Public Company (Ticker: {fd.get('ticker', 'N/A')})")
        lines.append(f"Company Name:     {fd.get('name', company)}")
        lines.append(f"Sector:           {fd.get('sector', 'N/A')}")
        lines.append(f"Industry:         {fd.get('industry', 'N/A')}")
        lines.append(f"Market Cap:       {fd.get('market_cap', 'N/A')}")
        lines.append(f"Revenue (TTM):    {fd.get('revenue_ttm', 'N/A')}")
        lines.append(f"Revenue Growth:   {fd.get('revenue_growth', 'N/A')}")
        lines.append(f"Gross Margin:     {fd.get('gross_margin', 'N/A')}")
        lines.append(f"Net Margin:       {fd.get('net_margin', 'N/A')}")
        lines.append(f"Debt-to-Equity:   {fd.get('debt_to_equity', 'N/A')}")
        lines.append(f"Current Ratio:    {fd.get('current_ratio', 'N/A')}")
        lines.append(f"Free Cash Flow:   {fd.get('free_cash_flow', 'N/A')}")
        lines.append(f"P/E Ratio:        {fd.get('pe_ratio', 'N/A')}")
    else:
        reason = financial_data.get("reason", "Unknown reason")
        lines.append(f"Status: Private or Unlisted Company")
        lines.append(f"Note:   {reason}")
        lines.append("Financial metrics are not available for private companies.")

    lines.append("")

    # --- Competitor Data ---
    lines.append("--- COMPETITOR DATA ---")
    if competitor_data:
        ids = [c["identifier"] for c in competitor_data]
        lines.append(f"Identified Competitors: {', '.join(ids)}\n")
        for comp in competitor_data:
            lines.append(f"Competitor: {comp['name']} ({comp['identifier']})")
            if comp["is_public"]:
                lines.append(f"  Market Cap: {comp['market_cap']}  |  P/E: {comp['pe_ratio']}  |  Revenue Growth: {comp['revenue_growth']}")
                lines.append(f"  Sector: {comp['sector']}")
            else:
                lines.append("  (Private company — no public financial data available)")
    else:
        lines.append("No competitor data available.")

    lines.append("")

    return "\n".join(lines)


def _build_web_summary(web_data: dict, max_headlines: int = 3) -> str:
    """Build a short summary from web news for competitor identification context."""
    headlines = [
        r["title"]
        for r in web_data.get("news", [])[:max_headlines]
        if r.get("title")
    ]
    if not headlines:
        return "No recent news available."
    return ". ".join(headlines)


# ---------------------------------------------------------------------------
# Step 7 — Claude Synthesis Agent
# ---------------------------------------------------------------------------

def synthesize_report(briefing: str, company: str, client: anthropic.Anthropic) -> str:
    """Send briefing to Claude and return the full intelligence report."""
    system_prompt = (
        "You are a senior corporate intelligence analyst. "
        "You produce structured company briefings for investment committees. "
        "You are rigorous: every claim must be grounded in the provided data. "
        "You do not fabricate statistics. When data is missing or thin, "
        "you say so explicitly rather than filling with generic statements. "
        "Every SWOT bullet must reference a specific data point from the briefing."
    )

    user_prompt = f"""You have received an intelligence briefing on {company}.
Write a comprehensive company deep-dive report based solely on the provided data.

<data>
{briefing}
</data>

Write these sections in order:

## Company Overview
Describe the company's products, business model, and revenue streams.
Use the products and news search results as your primary source.
If the company is private, note that explicitly.

## Recent News and Sentiment
Summarize the last 30 days of news (or most recent available).
What is the overall tone — positive, negative, mixed?
Reference specific news headlines from the briefing.

## Financial Health
If the company is public: analyze revenue trend, margins, debt levels, and cash flow.
Reference the actual numbers. If any metric is concerning, say why.
If the company is private: state that financial data is not publicly available,
and note any revenue or funding figures mentioned in news snippets.

## Competitive Position
Compare the company to its identified competitors.
Reference specific market cap, P/E, and revenue growth numbers.
Where does the company stand relative to its peers?

## SWOT Analysis
Write 2 items per quadrant (Strengths, Weaknesses, Opportunities, Threats).
Every bullet MUST cite specific evidence from the briefing.
Do not write generic SWOT items like "Strong brand" without citing data.

## Key Risks
Three numbered, specific risks grounded in the briefing data.
Tie each risk to an actual data point (a metric, a news headline, a competitive fact).

Use only the provided data. State clearly when information is unavailable."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return response.content[0].text


# ---------------------------------------------------------------------------
# Step 8 — Report Saver
# ---------------------------------------------------------------------------

def save_report(report_text: str, company: str, output_dir: str = "output") -> str:
    """Save {company_slug}_deep_dive.md. Return file path."""
    os.makedirs(output_dir, exist_ok=True)
    slug = _company_slug(company)
    filename = f"{slug}_deep_dive.md"
    path = os.path.join(output_dir, filename)

    header = (
        f"# Company Intelligence Report: {company}\n\n"
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(report_text)

    return path


def _company_slug(company: str) -> str:
    """Convert company name to filesystem-safe lowercase slug."""
    slug = company.lower()
    # Replace spaces and common separators with underscores
    slug = re.sub(r"[\s\-\.]+", "_", slug)
    # Remove characters that aren't alphanumeric or underscores
    slug = re.sub(r"[^\w]", "", slug)
    # Collapse multiple underscores
    slug = re.sub(r"_+", "_", slug)
    return slug.strip("_")


# ---------------------------------------------------------------------------
# Step 9 — Orchestrator
# ---------------------------------------------------------------------------

def main(raw_input: str):
    print(f"\nCompany Deep-Dive Agent")
    print("=" * 40)
    print(f"Target: {raw_input}\n")

    # Step 1 — Setup
    print("[Setup] Verifying API keys...", end=" ", flush=True)
    client = setup()
    info = normalize_input(raw_input)
    company_name = info["company_name"]
    ticker = info["ticker"]
    print(f"done  (company='{company_name}', ticker={ticker})")

    # Step 2 — Web Research
    print("[Web Research Agent] Searching company profile...", end=" ", flush=True)
    web_data = WebResearchAgent().run(company_name)
    total_results = sum(len(web_data.get(k, [])) for k in ["news", "products", "leadership"])
    print(f"done  ({total_results} results across 3 queries)")

    # Step 3 — Financial Data
    print("[Financial Agent] Fetching financial data...", end=" ", flush=True)
    identifier = ticker if ticker else company_name
    financial_data = FinancialAgent().run(identifier)
    if financial_data.get("is_public"):
        print(f"done  (public: {financial_data.get('ticker', identifier)}, cap: {financial_data.get('market_cap')})")
    else:
        print(f"done  (private/unlisted — {financial_data.get('reason', 'no data')})")

    # Step 4/5 — Competitor Agent
    print("[Competitor Agent] Identifying and researching competitors...")
    web_summary = _build_web_summary(web_data)
    competitor_data = CompetitorAgent().run(company_name, web_summary, client)
    print(f"  Found {len(competitor_data)} competitor(s)")

    # Step 6 — Briefing
    print("[Data Packager] Assembling briefing...", end=" ", flush=True)
    briefing = build_briefing(company_name, web_data, financial_data, competitor_data)
    word_count = len(briefing.split())
    print(f"done  (~{word_count} words)")

    # Step 7 — Synthesis
    print("[Synthesis Agent] Generating intelligence report...", end=" ", flush=True)
    report_text = synthesize_report(briefing, company_name, client)
    print("done")

    # Step 8 — Save
    print("\nSaving report...", end=" ", flush=True)
    path = save_report(report_text, company_name)
    print(f"done")
    print(f"  Report saved: {path}")

    print(f"\nDeep-dive complete for '{company_name}'.")
    return report_text


# ---------------------------------------------------------------------------
# Step 10 — CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python solution.py <company name or ticker>")
        print("Examples:")
        print("  python solution.py AAPL")
        print('  python solution.py "Apple"')
        print('  python solution.py "Reliance Industries"')
        print("  python solution.py TCS.NS")
        print("  python solution.py OpenAI")
        sys.exit(1)

    raw = " ".join(sys.argv[1:])
    main(raw)
