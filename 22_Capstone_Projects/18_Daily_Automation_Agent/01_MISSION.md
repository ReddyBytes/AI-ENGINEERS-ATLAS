# Project 18 — Daily Automation Agent

## The Briefing

Imagine you have a personal assistant who wakes up before you do. By 7am, they have already checked the weather outside your window, skimmed the morning headlines, reviewed your calendar, pulled up your task list, and glanced at the markets. Then they distill all of it into a single calm paragraph that tells you exactly what kind of day you are walking into.

That is what this project builds. Not a chatbot you talk to. An agent that runs on a schedule, fetches real data from multiple sources, and uses Claude to synthesize it into a coherent narrative — then delivers it to you.

This is the pattern behind every real-world automation: weather apps, financial dashboards, operations digests, daily standup bots. You are building the version you control.

---

## What Success Looks Like

When the project is complete, running `python src/solution.py` will:

1. Fetch today's weather for a configured city
2. Pull 5 news headlines from an RSS feed or NewsAPI
3. Load upcoming calendar events from a local YAML file
4. Read your TODO list from a plain text file
5. Fetch the Nifty 50 index price and top movers via yfinance
6. Send all of that to Claude, which returns a 200-word narrative briefing
7. Deliver the briefing — saved to `daily_digest.md` and optionally emailed or posted to Slack

The scheduler runs this automatically at 7am each morning via APScheduler.

---

## What You Will Learn

| Skill | Where it appears |
|---|---|
| Calling external APIs (weather, news, markets) | Data gathering phase |
| Parsing RSS feeds | News module |
| Reading structured config files (YAML) | Calendar module |
| Claude prompt engineering with structured context | Briefing generation |
| APScheduler for cron-style job scheduling | Delivery phase |
| Email delivery with smtplib / Slack webhooks | Output options |
| Environment variable management with dotenv | Throughout |

---

## Learning Tier

**Beginner-Intermediate.** You do not need prior agent experience. Every step is fully explained with working code. The hardest parts — Claude prompt design and scheduler setup — are demonstrated in detail.

---

## Prerequisites

- Python 3.9+
- Anthropic API key
- OpenWeatherMap API key (free tier)
- NewsAPI key (free tier) OR internet access for RSS
- yfinance works without an API key

---

## Tech Stack

| Library | Role |
|---|---|
| `anthropic` | Claude API — briefing generation |
| `requests` | Weather and news HTTP calls |
| `feedparser` | RSS feed parsing |
| `yfinance` | Market data |
| `APScheduler` | Cron-style scheduling |
| `smtplib` | Email delivery (stdlib) |
| `python-dotenv` | API key management |
| `pyyaml` | Calendar YAML parsing |

---

## 📂 Navigation

| File | |
|---|---|
| **01_MISSION.md** | ← you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System diagram and component table |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |
| [src/starter.py](./src/starter.py) | Skeleton with TODO markers |
| [src/solution.py](./src/solution.py) | Complete working solution |
