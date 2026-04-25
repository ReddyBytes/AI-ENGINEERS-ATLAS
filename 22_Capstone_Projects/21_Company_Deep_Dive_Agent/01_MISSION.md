# Project 21 — Company Deep-Dive Agent

## Mission Briefing

A venture capitalist evaluating a potential investment does not just look at a stock chart. She wants the full picture: what does this company actually do, what products have they shipped recently, who is running it, what do their numbers look like, who are they fighting in the market, and what is the SWOT — the honest assessment of strengths, weaknesses, opportunities, and threats.

Assembling that picture for one company currently takes a junior analyst four to six hours: running searches, pulling financial filings, reading press releases, mapping competitors, and writing the summary.

This project automates that workflow using a multi-agent system. Three specialist agents work in parallel: one searches the web for company news, products, and leadership; one pulls financial data for public companies; one identifies competitors and fetches their key metrics. A synthesis agent — Claude — receives all three agents' outputs and writes the full intelligence report.

The result: you type a company name or ticker, and within 90 seconds you have a comprehensive company brief.

---

## What You Will Build

A Python multi-agent system with four distinct agents:

| Agent | Responsibility | Data source |
|---|---|---|
| Web Research Agent | Company news, products, leadership, recent events | DuckDuckGo search |
| Financial Agent | Stock data, revenue, margins, debt if public | yfinance |
| Competitor Agent | Top 3 competitors, their basic financials | yfinance + DuckDuckGo |
| Claude Synthesis Agent | Full structured intelligence report | Anthropic API |

**Output sections Claude generates:**

1. Company Overview — products, business model, revenue streams
2. Recent News and Sentiment — last 30 days, overall tone
3. Financial Health — revenue trend, margins, debt (public companies only)
4. Competitive Position — how the company stands vs its identified competitors
5. SWOT Analysis — Claude-generated, grounded in the collected data
6. Key Risks

**Output file:** `{company_name}_deep_dive.md`

---

## Supported Input Formats

The agent accepts either format:

- Company name: `"Apple"`, `"Reliance Industries"`, `"OpenAI"`
- Ticker symbol: `"AAPL"`, `"RELIANCE.NS"`, `"TCS.NS"`

For private companies (no ticker), the financial agent gracefully skips and the report notes the limitation.

---

## Difficulty

Advanced — you are designing the interface between three agents, each with their own failure modes, and funneling their outputs into a single coherent synthesis prompt. The DuckDuckGo search result parsing requires care. The competitor identification step is a particularly interesting challenge: you must first ask Claude to identify competitors, then fetch data for those competitors.

---

## Tech Stack

| Library | Purpose |
|---|---|
| `anthropic` | Claude synthesis agent + competitor identification + SWOT |
| `yfinance` | Stock data and fundamentals for public companies |
| `duckduckgo-search` | Web search without an API key (`DDGS` class) |
| `requests` | HTTP utilities |
| `python-dotenv` | API key management |

---

## Prerequisites

- Completed Project 20 (Stock Market Analysis Agent) — the yfinance patterns carry over
- Comfortable with class-based Python (agents as classes is cleaner for this project)
- Understand that DuckDuckGo search returns snippets, not full page content — you are summarizing headlines and snippets, not scraping articles

---

## Environment Setup

```bash
pip install anthropic yfinance duckduckgo-search requests python-dotenv
```

Create a `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
```

No other API keys required. DuckDuckGo search is free with no key.

---

## Expected Output

```
Company Deep-Dive Agent
========================
Target: Apple (AAPL)

[Web Research Agent]   Searching company news and profile...   done (12 results)
[Financial Agent]      Fetching financial data...              done (public company)
[Competitor Agent]     Identifying and researching competitors...
    Claude identified: MSFT, GOOGL, META, AMZN
    Fetching MSFT...  done
    Fetching GOOGL... done
    Fetching META...  done  (AMZN skipped — rate limit)
[Synthesis Agent]      Building intelligence report...         done

Report saved: output/apple_deep_dive.md
```

---

## Extension Challenges

1. Add a Leadership Research sub-agent: search for CEO/CFO names and recent statements
2. Support batch mode: `python solution.py Apple Microsoft Google` — generate three reports in sequence
3. Add a "confidence score" to each report section based on how much data was available
4. Build a Streamlit UI that shows each agent's status as it runs
5. Cache DuckDuckGo results in a local SQLite database to avoid re-searching the same company within 24 hours
6. Add an "Executive Brief" mode: Claude produces a 150-word TL;DR at the top of the report

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| 📄 **01_MISSION.md** | Mission briefing — what and why |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and agent communication |
| [📄 03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [📄 src/starter.py](./src/starter.py) | Starter scaffold |
| [📄 src/solution.py](./src/solution.py) | Complete working solution |
| [📄 04_RECAP.md](./04_RECAP.md) | What you built and what is next |

⬅️ **Prev:** [Project 20 — Stock Market Analysis Agent](../20_Stock_Market_Analysis_Agent/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [22_Capstone_Projects README](../../README.md)
