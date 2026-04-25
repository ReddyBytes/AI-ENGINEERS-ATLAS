# Project 25 — Multi-Agent Portfolio Manager

## The Hedge Fund Intern Problem

Imagine you have just joined a small hedge fund as a quantitative intern. Your manager walks in on Monday morning and drops a list of ten stocks on your desk: "Tell me whether we should rebalance by Thursday."

You have four days. You need to: pull price history and compute technical indicators for each position, dig into each company's latest earnings and P/E ratios, calculate how much risk the current portfolio is actually carrying, and synthesize all of that into a coherent recommendation with specific percentage allocations and the reasoning behind each number.

One person cannot do this well in four days. A real fund would split the work: one analyst owns the technical picture, one owns the fundamentals, one owns risk, and a senior PM synthesizes everything. Each specialist goes deep. The PM does not try to do their job — they read the outputs and decide.

This project builds that team. Not with humans — with four AI agents orchestrated by LangGraph.

---

## The Business Stakes

Portfolio rebalancing is a decision that compounds. A 1% improvement in Sharpe ratio over a decade transforms a $1M portfolio into a meaningfully different number. The analysts who used to spend three days pulling data now spend three hours interpreting it. The edge is not smarter math — it is faster synthesis of more information than any single analyst can hold in their head.

Multi-agent financial systems are already running at Citadel, Two Sigma, and every major quant shop. They are not AGI. They are specialized pipelines that route the right question to the right model at the right time. This project teaches you how they are built.

---

## What You Build

A LangGraph-orchestrated pipeline with four specialist agents:

**Market Analyst Agent** — fetches price history via yfinance, computes RSI (14-period), MACD (12/26/9), 50-day and 200-day moving averages, identifies the current trend (bullish/bearish/neutral) for each holding.

**Fundamental Research Agent** — fetches company financials, trailing P/E ratio, forward P/E, earnings per share, revenue growth, analyst consensus rating, and 12-month price targets from yfinance.

**Risk Manager Agent** — computes portfolio-level metrics from the combined data: annualized Sharpe ratio (using 4% risk-free rate), maximum drawdown over the period, Value-at-Risk at 95% confidence, pairwise correlation matrix between holdings.

**Portfolio Advisor Agent** — synthesizes all three agents' findings, reasons about the combined picture, and generates a concrete rebalancing recommendation: whether to buy/hold/trim each position and what percentage allocation each should carry.

The Market Analyst and Fundamental Research agents run in parallel. Risk Manager runs after both complete. Portfolio Advisor runs last.

**Output:** a markdown file `portfolio_report.md` with five sections: Current Portfolio State, Market Analysis, Fundamental Analysis, Risk Assessment, and Recommended Actions.

---

## Concepts Applied

| Section | Topic | Applied As |
|---------|-------|-----------|
| 15 LangGraph | StateGraph, TypedDict state | Shared portfolio state across agents |
| 15 LangGraph | Parallel execution via Send API | Market + Fundamental agents run simultaneously |
| 10 AI Agents | Multi-agent systems | Specialist agents with clear responsibilities |
| 10 AI Agents | Orchestrator pattern | LangGraph graph as the orchestrator |
| 08 LLM Applications | Structured outputs | Agents return JSON-formatted findings |
| 12 Production AI | Cost optimization | Parallel execution reduces total latency |

---

## Acceptance Criteria

Before considering this project complete, verify all four:

1. All four agents fire and produce non-empty output (check `state["findings"]` after each node)
2. Parallel execution is verified — Market Analyst and Fundamental Research agent start at the same time (check timestamps or use `asyncio` timing)
3. The final report contains all four sections: Market Analysis, Fundamental Analysis, Risk Assessment, Recommended Actions
4. Each recommendation includes a specific percentage allocation and written rationale citing data from the specialist agents

---

## Difficulty

**Expert.** This project requires understanding LangGraph's StateGraph, TypedDict-based state, the Send API for parallel dispatch, and how to structure agent outputs so downstream agents can consume them. It also requires debugging async execution, state mutation, and LLM-generated structured data that may occasionally be malformed.

---

## Tech Stack

```
anthropic                — Claude claude-sonnet-4-6, all four agent reasoning steps
langgraph                — StateGraph, Send API, parallel execution
langchain-anthropic      — ChatAnthropic for LangGraph node compatibility
yfinance                 — Price history, financials, earnings data
pandas                   — Time series processing, correlation matrix
numpy                    — Sharpe ratio, VaR, drawdown calculations
python-dotenv            — ANTHROPIC_API_KEY loading
```

---

## Prerequisites

- Python 3.11+
- Anthropic API key in `.env`
- `pip install anthropic langgraph langchain-anthropic yfinance pandas numpy python-dotenv`

---

## 📂 Navigation

| File | |
|------|---|
| **01_MISSION.md** | You are here — project brief |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | LangGraph state diagram and agent design |
| [03_GUIDE.md](./03_GUIDE.md) | Build-yourself spec + acceptance criteria + reference solution |
| [src/starter.py](./src/starter.py) | Starter scaffold |
| [src/solution.py](./src/solution.py) | Complete reference solution |
| [04_RECAP.md](./04_RECAP.md) | What you learned, career framing |

**Section:** [22 Capstone Projects](../) &nbsp;&nbsp; **Prev:** [24 — Personal Knowledge Vault](../24_Personal_Knowledge_Vault/01_MISSION.md)
