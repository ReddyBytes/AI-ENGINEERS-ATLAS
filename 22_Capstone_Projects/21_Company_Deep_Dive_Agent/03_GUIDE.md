# Project 21 — Build Guide

## Format: Minimal Hints — you figure out the how, hints only where non-obvious

Work through each step in sequence. Each step produces verifiable output. Test each component before wiring them together.

---

## Step 1 — Setup and Input Normalization

**Requirement:** Write a `setup()` function that loads `ANTHROPIC_API_KEY` from `.env`, validates it starts with `sk-ant-`, and returns an `anthropic.Anthropic` client. Also write `normalize_input(raw: str) -> dict` that takes a raw company name or ticker and returns `{"company_name": str, "ticker": str | None}`.

For normalization: if the input looks like a ticker (all caps, 1-6 characters, optionally ending in `.NS` or `.BO`), treat it as a ticker and set `company_name` to the same string. Otherwise treat it as a company name and set `ticker` to `None`. The Financial Agent will attempt to resolve a ticker from the name later.

---

## Step 2 — Web Research Agent

**Requirement:** Write a `WebResearchAgent` class with a `run(company_name: str) -> dict` method. It runs three DuckDuckGo searches and returns a dict with keys `news`, `products`, `leadership` — each a list of up to 5 result dicts with `title`, `snippet`, `url`.

**Hint for DuckDuckGo:** Install `duckduckgo-search`. Use:
```python
from duckduckgo_search import DDGS
with DDGS() as ddgs:
    results = list(ddgs.text(query, max_results=5))
```
Each result has keys `title`, `body`, and `href`. Map `body` to `snippet` and `href` to `url`.

**Hint for rate limiting:** DuckDuckGo will throttle rapid requests. Add a `time.sleep(1)` between each of the three queries to avoid HTTP 202 "Ratelimit" responses.

---

## Step 3 — Financial Agent

**Requirement:** Write a `FinancialAgent` class with a `run(identifier: str) -> dict` method. `identifier` can be a ticker or a company name. The agent attempts `yfinance.Ticker(identifier).info` and returns structured financial data or `{"is_public": False, "reason": "..."}`.

A company has usable data when `.info` contains a `marketCap` key with a non-None value. Without it, treat the company as private/unlisted.

**Hint for private detection:** `yfinance.Ticker("OpenAI").info` returns a near-empty dict — check `info.get('marketCap')` is not `None` as your guard. If `identifier` is a company name like `"Apple"`, try both the raw name and common ticker formats — but the simplest approach is to rely on the caller passing a ticker when known, and marking `is_public=False` when not.

---

## Step 4 — Competitor Identification (Phase 1)

**Requirement:** Write `identify_competitors(company_name: str, web_summary: str, client) -> list[str]` that asks Claude to identify 3-4 competitor ticker symbols. Pass the company name and a short (200-word) summary from web research results as context. Claude should return a raw JSON list of ticker strings.

**Hint:** Include a fallback. If Claude returns company names instead of tickers (e.g., `["Microsoft", "Google"]`), keep them as-is — the Phase 2 fetcher will handle the case where a yfinance lookup on a company name fails.

**Hint for the prompt:** Ask Claude explicitly: "Respond with a JSON array of ticker symbols only. If a competitor is private and has no ticker, include their company name. Example: [\"MSFT\", \"GOOGL\", \"OpenAI\"]"

---

## Step 5 — Competitor Agent (Phase 2)

**Requirement:** Write a `CompetitorAgent` class with a `run(company_name: str, web_summary: str, client) -> list[dict]` method that calls `identify_competitors()` then fetches yfinance data for each. Return a list of dicts with: `identifier`, `name`, `market_cap`, `pe_ratio`, `revenue_growth`, `is_public`.

Wrap each yfinance fetch in `try/except`. If a competitor identifier returns no meaningful data, store `is_public=False` and keep it in the list for the briefing.

---

## Step 6 — Data Packager

**Requirement:** Write `build_briefing(company: str, web_data: dict, financial_data: dict, competitor_data: list) -> str` that formats all agent outputs into a structured multi-section string. See `02_ARCHITECTURE.md` for the expected format.

The web section should include actual search snippets — these are the richest source of recent information. Do not truncate them aggressively: up to 150 characters per snippet is appropriate.

---

## Step 7 — Claude Synthesis Agent

**Requirement:** Write `synthesize_report(briefing: str, company: str, client) -> str` that sends the briefing to Claude with an intelligence analyst system prompt and returns the full report. The report must contain all six sections: Company Overview, Recent News and Sentiment, Financial Health, Competitive Position, SWOT Analysis, Key Risks.

**Hint for SWOT:** Instruct Claude explicitly that every SWOT bullet must reference a specific data point from the briefing. Generic SWOT bullets like "Strength: Brand recognition" without evidence from the data are not acceptable. If the briefing is thin, the SWOT should be short but grounded.

**Hint for private companies:** In the system prompt, tell Claude: "If financial data is marked as unavailable, write the Financial Health section based on any revenue or funding information found in the news snippets, or note that the company is private."

---

## Step 8 — Report Saver

**Requirement:** Write `save_report(report_text: str, company: str, output_dir: str = "output") -> str` that creates the output directory, writes `{company_slug}_deep_dive.md`, and returns the path. The company slug should be lowercase with spaces replaced by underscores: `"Apple Inc"` → `"apple_inc_deep_dive.md"`.

---

## Step 9 — Orchestrator

**Requirement:** Write a `main(raw_input: str)` function that calls all agents in the correct order, prints status for each step, and saves the report. The order:

1. `setup()` → client
2. `normalize_input(raw_input)` → `{company_name, ticker}`
3. `WebResearchAgent().run(company_name)` → `web_data`
4. `FinancialAgent().run(ticker or company_name)` → `financial_data`
5. Build `web_summary` string from first 3 news headlines (for competitor identification context)
6. `CompetitorAgent().run(company_name, web_summary, client)` → `competitor_data`
7. `build_briefing(...)` → `briefing`
8. `synthesize_report(briefing, company_name, client)` → `report`
9. `save_report(report, company_name)` → `path`

---

## Step 10 — CLI Entry Point and Testing

**Requirement:** Wire `main()` to a CLI entry point that reads `sys.argv[1]` as the company name or ticker. Test the following cases:

- `python solution.py AAPL` — US ticker, full public data
- `python solution.py "Reliance Industries"` — company name, Indian market
- `python solution.py TCS.NS` — Indian ticker
- `python solution.py OpenAI` — private company, no financial data
- `python solution.py "a company that does not exist"` — graceful degradation

For each case, verify: the script completes without crashing, and the output `.md` file contains all six report sections (even if some say "data unavailable").

---

## Testing Checklist

- [ ] DuckDuckGo returns results for at least 2 of 3 queries per company
- [ ] Financial Agent correctly detects a private company (try `"Anthropic"` or `"SpaceX"`)
- [ ] Competitor identification returns a valid JSON list
- [ ] At least 2 competitors resolve to yfinance data
- [ ] SWOT section references specific data from the briefing, not generic statements
- [ ] Output file is created in the `output/` directory
- [ ] Entire pipeline completes in under 90 seconds on a normal network connection

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 01_MISSION.md](./01_MISSION.md) | Mission briefing |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| 📄 **03_GUIDE.md** | ← you are here |
| [📄 src/starter.py](./src/starter.py) | Starter scaffold |
| [📄 src/solution.py](./src/solution.py) | Complete solution |
| [📄 04_RECAP.md](./04_RECAP.md) | What you built |

⬅️ **Prev:** [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [src/starter.py](./src/starter.py)
