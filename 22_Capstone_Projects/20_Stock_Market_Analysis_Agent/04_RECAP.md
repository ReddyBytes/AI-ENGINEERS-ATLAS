# Project 20 — Recap

## What You Built

You built a financial research agent that operates exactly like a buy-side analyst preparing a morning brief. The agent accepts a ticker, gathers data from four independent sources simultaneously in concept (price data, fundamentals, news, peers), computes the indicators a professional would look at, and hands a fully structured briefing to Claude to produce a written report with a stated recommendation.

This is not a toy. The output is a document you could share at a team meeting.

---

## Skills You Applied

| Skill | Where you used it |
|---|---|
| Financial indicator math | Step 3 — RSI, MACD, Bollinger Bands in pure pandas |
| Multi-source data integration | Combining yfinance, NewsAPI, and peer fetches into one coherent briefing |
| Structured prompting | Briefing packager format + analyst system prompt design |
| Graceful degradation | Every data source can fail independently without crashing the agent |
| Context window management | Fitting all data into a clean, scannable briefing under ~2K tokens |
| PDF generation | Mapping markdown structure to reportlab paragraph styles |

---

## Key Patterns to Remember

### The Briefing Packager is the Real Work

Calling Claude is three lines. Building the briefing that Claude receives is the entire project. The cleaner and more structured your briefing, the sharper Claude's analysis. Every time you build an agent that reasons over external data, 80% of the engineering is in the data gathering and formatting layer.

### Fail Fast, Degrade Gracefully

Each data source wraps its fetch in a try/except. If NewsAPI is down, the report says "news data unavailable" and continues. If a peer ticker has no P/E, it shows N/A. The agent never crashes on real-world messiness. This is production thinking — data sources fail; good systems handle it.

### RSI and MACD Without a Library

You computed RSI using `clip(lower=0)` and `clip(upper=0)` on the daily delta series, then applied rolling means. You computed MACD using `ewm(span=N, adjust=False)`. No `ta` library, no `pandas_ta` — just numpy and pandas. This matters because it forces you to understand what these indicators actually measure, not just call a function.

---

## What the Numbers Mean

| Indicator | What it tells you |
|---|---|
| RSI > 70 | Recent gains are outsized relative to history — price may be stretched |
| RSI < 30 | Recent losses are outsized — potential oversold bounce |
| MACD crossing above signal | Short-term momentum turning positive — often a buy signal |
| Price above 200 DMA | Long-term uptrend — institutional money is net long |
| P/E vs peers | If the stock trades at a premium, earnings growth must justify it |
| Debt/Equity > 2.0 | Worth flagging as a risk in any credit environment |

---

## What to Build Next

This agent is a strong foundation. The natural extensions:

1. Add a Streamlit UI so the report renders in a browser as Claude streams it
2. Build a portfolio mode: pass 5 tickers, get a ranked table comparing all of them
3. Add options data from yfinance (implied volatility is a key risk signal)
4. Schedule with `cron` or Airflow to run every Monday morning on a watchlist
5. Connect to Project 21 (Company Deep-Dive Agent) — use the deep-dive for the competitor analysis section

---

## Concepts to Study Next

- Section 10 — AI Agents: how the ReAct loop generalizes what this agent does manually
- Section 13 — AI System Design: how you would productionize this with a queue and a database backing the reports
- Section 12 — Production AI: caching the yfinance and NewsAPI calls to avoid redundant fetches

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 01_MISSION.md](./01_MISSION.md) | Mission briefing |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| [📄 03_GUIDE.md](./03_GUIDE.md) | Step-by-step guide |
| [📄 src/starter.py](./src/starter.py) | Starter scaffold |
| [📄 src/solution.py](./src/solution.py) | Complete solution |
| 📄 **04_RECAP.md** | ← you are here |

⬅️ **Prev:** [03_GUIDE.md](./03_GUIDE.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Project 21 — Company Deep-Dive Agent](../21_Company_Deep_Dive_Agent/01_MISSION.md)
