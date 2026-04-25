# Project 18 — Daily Automation Agent: Recap

## What You Built

A scheduled, multi-source morning briefing agent that:

- Fetches live data from four external sources (weather, news, markets, local files)
- Assembles structured context and sends it to Claude
- Receives a coherent 200-word narrative in return
- Delivers the result to a file, email, or Slack — automatically, every morning

This is not a toy. The pattern you applied here — gather, assemble, synthesize, deliver — is how production data digests, ops reports, and business intelligence summaries work at scale.

---

## Core Concepts Applied

| Concept | Where it appeared |
|---|---|
| External API integration | OpenWeatherMap, NewsAPI, yfinance |
| RSS feed parsing | feedparser news fallback |
| Structured prompting | `assemble_context()` → Claude |
| LLM synthesis | Claude haiku turning raw data into narrative |
| Cron scheduling | APScheduler `BlockingScheduler` |
| Graceful degradation | Every module returns a fallback dict on error |
| Secret management | python-dotenv + .env file |
| Multi-channel delivery | File + email + Slack from a single function |

---

## Patterns Worth Naming

**The gather-assemble-synthesize pattern.** Every data aggregation agent follows this shape:

```
fetch independently → normalize → assemble into prompt → LLM synthesizes → deliver
```

You will see this exact pattern in financial reporting pipelines, ops dashboards, and AI-powered newsletter generators.

**Graceful degradation.** Every module catches its own exceptions and returns a safe fallback. The agent never crashes because one data source is down. This is a production habit, not just a beginner courtesy.

**The `--now` escape hatch.** Always give your scheduled jobs a manual trigger. Testing a 7am job by waiting for 7am is painful.

---

## 3 Extensions to Try

**Extension 1 — Personalized weather advice.**
Add a second Claude call after the briefing that generates a one-sentence clothing recommendation based on today's weather data. Chain two Claude calls — briefing first, advice second.

**Extension 2 — Weekly trend summary.**
At the end of each week, read the last 5 `daily_digest.md` files and ask Claude to summarize recurring themes, overdue tasks, and notable market moves. One more APScheduler job: `cron(day_of_week='fri', hour=18)`.

**Extension 3 — Sentiment-filtered news.**
Before passing headlines to Claude, run a second Claude call that scores each headline from -2 (very negative) to +2 (positive). Filter out the two most alarming ones so your morning briefing stays calm. Teach yourself about prompt chaining and response parsing.

---

## Job Mapping

This project demonstrates skills that appear directly in real job descriptions:

| What you built | Job title that cares |
|---|---|
| External API integration + error handling | Backend Engineer, Data Engineer |
| LLM prompt design for structured synthesis | AI Engineer, Prompt Engineer |
| Scheduled jobs with APScheduler | Data Engineer, Platform Engineer |
| Multi-channel delivery (email, Slack) | DevOps Engineer, Automation Engineer |
| dotenv + config management | Any backend role |
| Graceful degradation patterns | Senior Engineer (all tracks) |

A system that runs autonomously, uses an LLM for synthesis, and delivers results via multiple channels is exactly the kind of project that stands out in an AI engineering portfolio.

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System diagram |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| **04_RECAP.md** | ← you are here |
| [src/starter.py](./src/starter.py) | Skeleton with TODO markers |
| [src/solution.py](./src/solution.py) | Complete working solution |
