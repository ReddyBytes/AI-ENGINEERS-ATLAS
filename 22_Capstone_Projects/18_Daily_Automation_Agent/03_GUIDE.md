# Project 18 — Daily Automation Agent: Build Guide

**Format:** Fully Guided — every step includes complete, runnable code and a plain-English explanation.

**Time estimate:** 90–120 minutes

---

## Before You Start

Create a `.env` file in the project root with:

```
ANTHROPIC_API_KEY=your_key_here
OWM_API_KEY=your_openweathermap_key_here
NEWS_API_KEY=your_newsapi_key_here        # optional — RSS fallback works without it
CITY=Mumbai                               # or any city name
EMAIL_FROM=you@gmail.com                  # optional
EMAIL_TO=you@gmail.com                    # optional
EMAIL_PASSWORD=your_app_password          # Gmail app password
SLACK_WEBHOOK_URL=https://hooks.slack.com/...  # optional
```

Install dependencies:

```bash
pip install anthropic requests feedparser yfinance apscheduler python-dotenv pyyaml
```

---

## Step 1 — Project Skeleton

**What you are building:** The file structure and import block. Getting everything wired up before writing logic.

Analogy: this is setting out all your ingredients and tools before cooking. Nothing works yet, but nothing is missing either.

```python
# src/solution.py
import os
import smtplib
import datetime
from email.mime.text import MIMEText
from pathlib import Path

import anthropic
import feedparser
import requests
import yaml
import yfinance as yf
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()

# Configuration — reads from .env
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OWM_API_KEY = os.getenv("OWM_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
CITY = os.getenv("CITY", "Mumbai")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

BASE_DIR = Path(__file__).parent.parent
EVENTS_FILE = BASE_DIR / "events.yaml"
TODO_FILE = BASE_DIR / "todo.txt"
DIGEST_FILE = BASE_DIR / "daily_digest.md"
```

**Why `Path(__file__).parent.parent`?** Because `solution.py` lives in `src/`, so `.parent` is `src/` and `.parent.parent` is the project root where your data files live.

---

## Step 2 — Weather Module

**What you are building:** A function that calls OpenWeatherMap and returns a clean weather summary dict.

Analogy: calling your local weather app's internal API. It speaks JSON; you just need to know which keys to read.

```python
def fetch_weather() -> dict:
    """Fetch current weather for the configured city."""
    if not OWM_API_KEY:
        return {"error": "No OWM_API_KEY set", "temp": "N/A", "description": "unavailable", "humidity": "N/A"}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": CITY,
        "appid": OWM_API_KEY,
        "units": "metric",  # Celsius
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            "city": CITY,
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
        }
    except Exception as e:
        return {"error": str(e), "temp": "N/A", "description": "unavailable", "humidity": "N/A"}
```

**Key points:**
- Always pass `timeout=10` to prevent hanging indefinitely
- Return a fallback dict on error — downstream code should never crash because weather failed
- `units=metric` gives Celsius; use `imperial` for Fahrenheit

---

## Step 3 — News Module

**What you are building:** A function that returns 5 headlines. It tries NewsAPI first, falls back to BBC RSS.

Analogy: you have a preferred newspaper but also keep a backup on the shelf. Same headlines; different source.

```python
def fetch_news() -> list[str]:
    """Return up to 5 news headlines. NewsAPI → RSS fallback."""
    # Try NewsAPI first
    if NEWS_API_KEY:
        url = "https://newsapi.org/v2/top-headlines"
        params = {"language": "en", "pageSize": 5, "apiKey": NEWS_API_KEY}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
            return [a["title"] for a in articles[:5]]
        except Exception:
            pass  # Fall through to RSS

    # RSS fallback — no API key needed
    feed_url = "https://feeds.bbci.co.uk/news/rss.xml"
    try:
        feed = feedparser.parse(feed_url)
        return [entry.title for entry in feed.entries[:5]]
    except Exception as e:
        return [f"News unavailable: {e}"]
```

**Why feedparser?** It handles every quirk of RSS/Atom formatting. You pass it a URL; it returns a parsed object with `.entries`. No XML parsing needed.

---

## Step 4 — Calendar and Task Modules

**What you are building:** Two simple file readers. The calendar reads a YAML config; the task list reads a plain text file.

First, create your data files in the project root:

`events.yaml`:
```yaml
events:
  - "09:00 — Team standup"
  - "14:00 — Design review with product team"
  - "17:30 — 1:1 with manager"
```

`todo.txt`:
```
[ ] Finish quarterly report
[ ] Review pull request #142
[ ] Reply to vendor email
[ ] Book travel for offsite
```

Now the reader functions:

```python
def load_calendar() -> list[str]:
    """Load today's calendar events from events.yaml."""
    if not EVENTS_FILE.exists():
        return ["No events.yaml found — add your schedule"]
    try:
        with open(EVENTS_FILE) as f:
            data = yaml.safe_load(f)
        return data.get("events", [])
    except Exception as e:
        return [f"Calendar load error: {e}"]


def load_tasks() -> list[str]:
    """Load open tasks from todo.txt (lines starting with [ ])."""
    if not TODO_FILE.exists():
        return ["No todo.txt found — add your tasks"]
    try:
        with open(TODO_FILE) as f:
            lines = f.readlines()
        # Only return uncompleted tasks
        return [line.strip() for line in lines if line.strip().startswith("[ ]")]
    except Exception as e:
        return [f"Task load error: {e}"]
```

**Why filter for `[ ]`?** This gives you a real GTD-style task list where completed tasks (marked `[x]`) are silently dropped from the briefing. You own the format.

---

## Step 5 — Market Module

**What you are building:** A function that fetches the Nifty 50 index price and the top 3 movers using yfinance.

Analogy: asking a Bloomberg terminal the three questions you actually care about — where is the index, and who moved the most today?

```python
def fetch_market() -> dict:
    """Fetch Nifty 50 index and top 3 large-cap movers."""
    try:
        # Nifty 50 index
        nifty = yf.Ticker("^NSEI")
        nifty_info = nifty.fast_info
        nifty_price = round(nifty_info.last_price, 2)
        nifty_change = round(
            (nifty_info.last_price - nifty_info.previous_close) / nifty_info.previous_close * 100, 2
        )

        # Sample Nifty 50 constituents for movers
        tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
                   "HINDUNILVR.NS", "ITC.NS", "WIPRO.NS", "AXISBANK.NS", "BAJFINANCE.NS"]

        movers = []
        for symbol in tickers:
            try:
                t = yf.Ticker(symbol)
                info = t.fast_info
                pct = round(
                    (info.last_price - info.previous_close) / info.previous_close * 100, 2
                )
                movers.append((symbol.replace(".NS", ""), pct))
            except Exception:
                continue

        # Sort by absolute % change, take top 3
        movers.sort(key=lambda x: abs(x[1]), reverse=True)
        top_3 = movers[:3]

        return {
            "nifty_price": nifty_price,
            "nifty_change_pct": nifty_change,
            "top_movers": top_3,
        }
    except Exception as e:
        return {"error": str(e), "nifty_price": "N/A", "nifty_change_pct": "N/A", "top_movers": []}
```

**Why `fast_info` instead of `.info`?** The `.info` property makes many HTTP requests and is slow. `.fast_info` is a lightweight version that returns the key price fields quickly.

---

## Step 6 — Context Assembler and Claude Briefing

**What you are building:** The function that formats all module data into a structured prompt, and the function that sends it to Claude.

This is the core of the agent. Think of `assemble_context()` as writing the brief for the columnist — everything they need, nothing they don't.

```python
def assemble_context(weather: dict, news: list, events: list, tasks: list, market: dict) -> str:
    """Build the structured context string for Claude."""
    today = datetime.date.today().strftime("%A, %B %d, %Y")

    news_block = "\n".join(f"- {h}" for h in news)
    events_block = "\n".join(f"- {e}" for e in events) if events else "- No events scheduled"
    tasks_block = "\n".join(f"- {t}" for t in tasks) if tasks else "- No open tasks"

    movers_block = ""
    if market.get("top_movers"):
        movers_block = "\n".join(
            f"  - {name}: {pct:+.2f}%" for name, pct in market["top_movers"]
        )

    context = f"""Today is {today}.

WEATHER — {weather.get('city', CITY)}:
  Temperature: {weather.get('temp')}°C (feels like {weather.get('feels_like')}°C)
  Conditions: {weather.get('description')}
  Humidity: {weather.get('humidity')}%

TOP NEWS HEADLINES:
{news_block}

TODAY'S CALENDAR:
{events_block}

OPEN TASKS:
{tasks_block}

MARKETS — Nifty 50:
  Index: {market.get('nifty_price')} ({market.get('nifty_change_pct'):+}% today)
  Top movers:
{movers_block}
"""
    return context


def generate_briefing(context: str) -> str:
    """Send the context to Claude and return a 200-word narrative briefing."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = (
        "You are a personal morning briefing assistant. "
        "You receive structured daily data and write a calm, clear 200-word narrative digest. "
        "Weave together the weather, news, schedule, tasks, and market conditions into a coherent paragraph. "
        "Speak directly to the reader ('you'). Be informative, not dramatic. "
        "End with one sentence of practical advice for the day ahead."
    )

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Please generate my morning briefing from this data:\n\n{context}"}
        ],
    )
    return message.content[0].text
```

**Prompt design choices:**
- System prompt defines the persona and constraints (200 words, calm tone, direct address)
- The context is passed as a user message, not baked into the system prompt — this is the cleanest pattern
- `claude-haiku-4-5` is chosen for speed and cost; for richer prose use `claude-sonnet-4-5`

---

## Step 7 — Delivery Module

**What you are building:** Three delivery options — write to file (always), email (optional), Slack (optional).

The file write is the guaranteed fallback. Email and Slack only activate when their credentials are present in `.env`.

```python
def deliver(briefing: str, context: str) -> None:
    """Write digest to file and optionally send via email or Slack."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Always write to file
    content = f"# Daily Digest — {today}\n\n_Generated at {timestamp}_\n\n## Morning Briefing\n\n{briefing}\n\n---\n\n## Raw Data\n\n```\n{context}\n```\n"
    with open(DIGEST_FILE, "w") as f:
        f.write(content)
    print(f"Digest written to {DIGEST_FILE}")

    # Email delivery
    if EMAIL_FROM and EMAIL_TO and EMAIL_PASSWORD:
        try:
            msg = MIMEText(f"{briefing}\n\n---\nRaw data:\n{context}", "plain")
            msg["Subject"] = f"Morning Briefing — {today}"
            msg["From"] = EMAIL_FROM
            msg["To"] = EMAIL_TO

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.send_message(msg)
            print("Email sent.")
        except Exception as e:
            print(f"Email failed: {e}")

    # Slack delivery
    if SLACK_WEBHOOK_URL:
        try:
            payload = {"text": f"*Morning Briefing — {today}*\n\n{briefing}"}
            resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
            resp.raise_for_status()
            print("Slack message sent.")
        except Exception as e:
            print(f"Slack failed: {e}")
```

**Gmail note:** Gmail blocks password auth. You need an App Password. Go to Google Account → Security → 2-Step Verification → App passwords. Generate one and put it in `EMAIL_PASSWORD`.

---

## Step 8 — Scheduler and Main Entry Point

**What you are building:** The APScheduler setup that triggers the briefing at 7am daily, and a `run_briefing()` function that orchestrates all modules.

```python
def run_briefing() -> None:
    """Orchestrate all modules and deliver the briefing."""
    print(f"\n--- Running morning briefing at {datetime.datetime.now()} ---")

    print("Fetching weather...")
    weather = fetch_weather()

    print("Fetching news...")
    news = fetch_news()

    print("Loading calendar...")
    events = load_calendar()

    print("Loading tasks...")
    tasks = load_tasks()

    print("Fetching market data...")
    market = fetch_market()

    print("Assembling context...")
    context = assemble_context(weather, news, events, tasks, market)

    print("Generating Claude briefing...")
    briefing = generate_briefing(context)

    print("\n" + "="*60)
    print(briefing)
    print("="*60 + "\n")

    deliver(briefing, context)
    print("Done.\n")


def run_scheduler() -> None:
    """Start APScheduler to run briefing at 7:00 AM daily."""
    scheduler = BlockingScheduler()
    scheduler.add_job(run_briefing, "cron", hour=7, minute=0)
    print("Scheduler started. Next briefing at 07:00. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("Scheduler stopped.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # Run immediately for testing: python src/solution.py --now
        run_briefing()
    else:
        # Default: start the scheduler
        run_scheduler()
```

**Testing tip:** Run `python src/solution.py --now` to trigger the briefing immediately without waiting for 7am. The scheduler runs when you use `python src/solution.py` alone.

**APScheduler's `BlockingScheduler`** blocks the current thread. If you want it to run in the background alongside other code, use `BackgroundScheduler` instead.

---

## What to Try Next

<details>
<summary>Hint: How do I add a second city's weather?</summary>

Pass a list of cities to `fetch_weather()` and call it in a loop. Aggregate the results into a dict keyed by city name, then update `assemble_context()` to format multiple weather blocks.

</details>

<details>
<summary>Hint: How do I make Claude generate a haiku summary instead of prose?</summary>

Change the system prompt in `generate_briefing()` to request a haiku format. You can even pass the format as a parameter and switch between `prose` and `haiku` via a command-line flag.

</details>

<details>
<summary>Hint: How do I make this run as a background service on macOS?</summary>

Create a launchd plist file in `~/Library/LaunchAgents/`. Point it to run `python src/solution.py` at boot. The APScheduler inside will handle the 7am timing. Alternatively, use a simple `crontab` entry: `0 7 * * * cd /path/to/project && python src/solution.py --now`.

</details>

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System diagram |
| **03_GUIDE.md** | ← you are here |
| [04_RECAP.md](./04_RECAP.md) | Recap and extensions |
