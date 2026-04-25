# Project 25 — Recap

## What You Built

A production-pattern multi-agent system where four AI specialists operate in a coordinated pipeline: two run in parallel, two run sequentially after them, and all communicate through a shared typed state object managed by LangGraph. The system produces a complete financial analysis report by synthesizing quantitative data with Claude's reasoning.

---

## Core Patterns You Now Own

### LangGraph StateGraph with TypedDict

Every agent in the system reads from and writes to a single `PortfolioState` TypedDict. This is not a convention — it is an enforced contract. LangGraph validates state keys at each edge transition. The benefit is that you can insert a new agent anywhere in the graph without changing any other agent's code, as long as it reads and writes the same state schema.

### Parallel Execution via Send API

The `Send` API is LangGraph's mechanism for true parallelism. When `fetch_data` returns `[Send("market_analyst", state), Send("fundamental_researcher", state)]`, LangGraph launches both nodes simultaneously in separate threads. The `Annotated[dict, operator.or_]` type annotation on `market_analysis` and `fundamental_analysis` tells LangGraph how to merge the two parallel outputs — dictionary union in this case.

Without the Send API, you would have to run the analysts sequentially, doubling the latency of the most expensive part of the pipeline.

### Separation of Computation and Reasoning

The system uses two distinct modes deliberately:

- `risk_manager` does pure computation (numpy, pandas) — no LLM involved
- `portfolio_advisor` does pure reasoning (Claude) — no computation involved

This is the right separation. LLMs are expensive and slow for arithmetic. Numpy is useless for generating prose with citations. The architecture keeps each tool in its domain.

### Structured Agent Outputs

Each specialist agent returns a Python dict with consistent keys and a `"summary"` field populated by Claude. The downstream `portfolio_advisor` can rely on these keys existing — it does not have to parse free-form text. Consistent schemas between agents are the difference between a demo and a maintainable system.

---

## What Could Break in Production

| Issue | Why | Fix |
|-------|-----|-----|
| yfinance rate limiting | Fetching 10+ tickers in rapid succession | Add `time.sleep(0.5)` between ticker fetches |
| Missing financials | Not all tickers have P/E or analyst ratings | Always handle `.get()` returning `None` |
| JSON decode failure | Claude occasionally returns non-JSON despite instructions | Wrap all `json.loads()` in try/except with fallback |
| Parallel state merge conflict | Two agents writing the same key | Use `Annotated[dict, operator.or_]` reducer |
| Graph compilation error | Invalid edge topology | Draw the graph on paper before coding |

---

## Career Framing

### AI Engineer

"Built a LangGraph multi-agent system with four specialist agents (technical analyst, fundamental researcher, risk manager, portfolio advisor) connected by a TypedDict state graph. Implemented parallel execution of the first two agents using LangGraph's Send API, reducing total pipeline latency. System generates a structured Markdown investment report."

This demonstrates: LangGraph, multi-agent architecture, state management, parallel execution, structured LLM output — all in one project.

### Quantitative Developer

The risk metrics node — Sharpe ratio, max drawdown, VaR, correlation matrix — are standard tools in any quant toolkit. You implemented them from scratch using pandas and numpy rather than a library, which means you understand the math, not just the API call. That distinction matters in interviews.

### Financial ML Engineer

The architecture of this system — ingesting market data, running multiple analytical passes, and synthesizing into a recommendation — mirrors how real quantitative research platforms work. The agents here use Claude for reasoning; in production they might use fine-tuned domain models or rules-based systems for some steps. The structure is identical.

---

## What to Build Next

- Add a backtesting node: given a recommended allocation, compute what the return would have been over the historical period
- Add a news agent: fetch recent news headlines per ticker using a news API and include sentiment analysis
- Replace yfinance with a real-time data provider (Polygon.io, Alpha Vantage) for live portfolio monitoring
- Add a `HumanInTheLoop` interrupt before `save_report` so the user can review and modify the recommendation before writing
- Add persistent state with LangGraph checkpointing so the graph can be paused and resumed

---

## 📂 Navigation

| File | |
|------|---|
| [01_MISSION.md](./01_MISSION.md) | Project brief |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | LangGraph state diagram |
| [03_GUIDE.md](./03_GUIDE.md) | Build guide + reference solution |
| [src/starter.py](./src/starter.py) | Starter scaffold |
| [src/solution.py](./src/solution.py) | Complete reference solution |
| **04_RECAP.md** | You are here |

**Section:** [22 Capstone Projects](../) &nbsp;&nbsp; **Prev:** [24 — Personal Knowledge Vault](../24_Personal_Knowledge_Vault/01_MISSION.md)
