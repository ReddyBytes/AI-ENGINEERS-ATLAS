# Project 21 — Recap

## What You Built

You built a multi-agent company intelligence system. Three specialist agents each handle one domain of research — web, financials, competitive landscape — and hand their findings to Claude for synthesis. The result is a structured intelligence brief that would take a junior analyst four to six hours to produce manually.

This is qualitatively different from Project 20. In Project 20, you had one agent and one Claude call at the end. Here you have an orchestrated pipeline where agents are loosely coupled, where Claude is called twice (once for competitor identification, once for synthesis), and where the system gracefully handles the fundamental difference between public and private companies.

---

## Skills You Applied

| Skill | Where you used it |
|---|---|
| Agent class design | Each agent is a self-contained class with a single `run()` method |
| DuckDuckGo integration | Real-time web search without an API key using the `DDGS` class |
| Two-phase agent design | Competitor Agent: Claude identifies, then yfinance fetches |
| Graceful private-company handling | FinancialAgent returns a structured flag, not an exception |
| Briefing design | Assembling heterogeneous data sources into a scannable prompt |
| Structured Claude calls | Claude for identification (JSON output) and for synthesis (prose output) — two different prompting modes |

---

## Key Patterns to Remember

### Agents Are Not Magic — They Are Functions With a Contract

Each agent has exactly one job and returns exactly one type of output. `WebResearchAgent.run()` returns `{news, products, leadership}`. `FinancialAgent.run()` returns either a financial dict or a private-company flag. The orchestrator does not need to know how either agent works — it just calls them and passes their output downstream. This is what makes the system testable and replaceable.

### Two-Phase Competitor Discovery

You cannot pre-program competitor lists. Industries change. The solution: ask Claude for competitor tickers, then fetch data for those tickers. This is a general pattern for any agent task where the set of objects to process is not known in advance. Claude becomes the planning layer; yfinance (or any data source) becomes the execution layer.

### Private vs Public Is Not an Error

A private company returning no financial data is not a bug — it is valid information. The system encodes this with a structured return value (`{"is_public": False, "reason": "..."}`), not an exception. Claude knows how to handle it because the briefing explicitly labels the section. The report section says "private company, no public data" rather than crashing or fabricating numbers.

### DuckDuckGo Rate Limiting

The 1-second sleep between queries is not optional. DuckDuckGo will return HTTP 202 "Ratelimit" if you fire three requests in rapid succession. The sleep costs 2 seconds and prevents the entire web research step from returning empty. In production you would add exponential backoff with retry.

---

## Connecting the Two Projects

Projects 20 and 21 are natural complements:

- Use Project 21's competitor section to enrich Project 20's peer comparison
- A full workflow: run Project 21 first to get a company overview and identify peers, then run Project 20 on the ticker for deep technical and earnings analysis
- Together they form a lightweight research workflow you could run before any investment decision

---

## What to Build Next

1. Add a leadership sub-agent: search specifically for the CEO name, tenure, and recent public statements
2. Cache DuckDuckGo results in SQLite with a 24-hour TTL — avoid re-fetching the same company
3. Build a "portfolio brief": run both agents on a list of companies and output a comparative markdown table
4. Add Streamlit: show each agent's status in real time as a progress dashboard
5. Connect to a Slack webhook: post the Key Risks section to a channel as an alert

---

## Concepts to Study Next

- Section 10 — AI Agents: the ReAct pattern formalizes what you built here — the orchestrator's loop is a manual ReAct implementation
- Section 07 — Multi-Agent Systems: the orchestrator-worker pattern you used is one of three canonical multi-agent architectures
- Section 12 — Production AI: caching, rate limiting, and fault tolerance for agent pipelines at scale

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

⬅️ **Prev:** [03_GUIDE.md](./03_GUIDE.md) &nbsp;&nbsp;&nbsp; ➡️ **Back to:** [22_Capstone_Projects README](../../README.md)
