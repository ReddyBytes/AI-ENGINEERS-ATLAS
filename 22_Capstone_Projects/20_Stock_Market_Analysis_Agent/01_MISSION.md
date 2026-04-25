# Project 20 — Stock Market Analysis Agent

## Mission Briefing

Imagine hiring a financial analyst on a Friday evening. By Monday morning, you want a full research report on a stock: price trends, fundamental health, what the news is saying, how earnings have trended, and how the company stacks up against its peers. Then — based on all that — a clear recommendation with reasoning.

This project builds that analyst. You feed it a ticker symbol. It fetches a year of price data, computes the standard technical indicators every professional uses, pulls fundamental ratios from the filings, scores the last ten news articles for sentiment, traces the earnings trend, benchmarks the company against competitors, and then hands all that context to Claude. Claude plays the role of equity analyst and writes a structured research report — executive summary, technical view, fundamental view, risks, and a Buy / Hold / Sell call with price target rationale.

The output is a markdown file you can open, read, and act on.

---

## What You Will Build

A Python agent that accepts a stock ticker and produces a complete equity research report.

**Data pipeline:**

| Layer | What it fetches | How |
|---|---|---|
| Price data | 1-year OHLCV, 50/200 DMA, RSI, MACD, Bollinger Bands | `yfinance` + `pandas` |
| Fundamentals | P/E, P/B, Debt/Equity, ROE, market cap | `yfinance .info` |
| News sentiment | Last 10 articles — Claude scores each bullish/bearish/neutral | NewsAPI |
| Earnings trend | Last 4 quarters revenue + net profit | `yfinance .quarterly_financials` |
| Competitor comparison | P/E and revenue growth for 2-3 peers | `yfinance` per peer ticker |

**Claude Analyst Agent generates:**

1. Executive Summary — one paragraph, what the key story is
2. Technical Analysis — what price action and indicators say
3. Fundamental Analysis — balance sheet health, valuation vs peers
4. Risk Factors — the three biggest threats to the thesis
5. Recommendation — Buy / Hold / Sell with a price target rationale

**Output:** `{TICKER}_analysis.md` + optional PDF via `reportlab`

---

## Supported Ticker Formats

- Indian markets (NSE/BSE): `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`
- US markets: `AAPL`, `NVDA`, `MSFT`, `GOOGL`

---

## Difficulty

Advanced — you are orchestrating multiple data sources, computing financial indicators without a dedicated TA library, feeding structured context to Claude, and formatting a professional-grade output document.

---

## Tech Stack

| Library | Purpose |
|---|---|
| `anthropic` | Claude analyst — reasoning over structured financial data |
| `yfinance` | Historical OHLCV, fundamentals, earnings, peer data |
| `requests` | NewsAPI HTTP calls |
| `pandas` | DataFrame operations, indicator computation |
| `numpy` | Rolling calculations (RSI, Bollinger Bands) |
| `reportlab` | Optional PDF output |
| `python-dotenv` | API key management |

---

## Prerequisites

- Comfortable with pandas DataFrames and rolling window calculations
- Understand what P/E, RSI, and MACD measure at a conceptual level
- Can make HTTP requests and parse JSON
- Have read the Claude API sections on structured prompting

---

## Environment Setup

```bash
pip install anthropic yfinance requests pandas numpy reportlab python-dotenv
```

Create a `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
NEWS_API_KEY=your_newsapi_key_here
```

Get a free NewsAPI key at https://newsapi.org (free tier: 100 req/day).

---

## Expected Output

```
Stock Market Analysis Agent
============================
Ticker: AAPL

[1/6] Fetching 1-year price data...       done  (252 trading days)
[2/6] Computing technical indicators...   done  (RSI: 58.3, MACD: +1.24)
[3/6] Fetching fundamentals...            done  (P/E: 28.4, ROE: 147%)
[4/6] Fetching and scoring news...        done  (7 bullish, 2 neutral, 1 bearish)
[5/6] Fetching earnings trend...          done  (4 quarters loaded)
[6/6] Fetching competitor data...         done  (MSFT, GOOGL, META)

Sending data to Claude analyst...

Report saved: AAPL_analysis.md
PDF saved:    AAPL_analysis.pdf  (optional)
```

---

## Extension Challenges

1. Add a Streamlit UI — ticker input, progress bar, rendered report
2. Backtest the RSI signal: did buying when RSI < 30 produce positive returns on this ticker?
3. Add options data: implied volatility, put/call ratio from yfinance
4. Schedule the agent to run weekly and email you the report
5. Support a portfolio: accept a list of tickers and generate a comparative ranking

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| 📄 **01_MISSION.md** | Mission briefing — what and why |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and data flow |
| [📄 03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [📄 src/starter.py](./src/starter.py) | Starter scaffold |
| [📄 src/solution.py](./src/solution.py) | Complete working solution |
| [📄 04_RECAP.md](./04_RECAP.md) | What you built and what's next |

⬅️ **Prev:** [Project 19 — Research Paper Podcast Agent](../19_Research_Paper_Podcast_Agent/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Project 21 — Company Deep-Dive Agent](../21_Company_Deep_Dive_Agent/01_MISSION.md)
