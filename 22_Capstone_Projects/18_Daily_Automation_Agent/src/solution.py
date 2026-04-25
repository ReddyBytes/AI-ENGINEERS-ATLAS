"""
Project 18 — Daily Automation Agent
Complete working solution.

Run immediately (skip scheduler):
    python src/solution.py --now

Run with scheduler (fires at 7am daily):
    python src/solution.py

Required .env variables:
    ANTHROPIC_API_KEY   — Anthropic API key
    OWM_API_KEY         — OpenWeatherMap API key (free tier)
    CITY                — city name (default: Mumbai)
    NEWS_API_KEY        — optional; falls back to BBC RSS without it
    EMAIL_FROM          — optional Gmail address
    EMAIL_TO            — optional recipient
    EMAIL_PASSWORD      — optional Gmail app password
    SLACK_WEBHOOK_URL   — optional Slack incoming webhook URL
"""

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


# ---------------------------------------------------------------------------
# Weather Module
# ---------------------------------------------------------------------------

def fetch_weather() -> dict:
    """Fetch current weather for CITY from OpenWeatherMap."""
    if not OWM_API_KEY:
        return {
            "error": "No OWM_API_KEY set",
            "city": CITY,
            "temp": "N/A",
            "feels_like": "N/A",
            "description": "unavailable",
            "humidity": "N/A",
        }

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": CITY, "appid": OWM_API_KEY, "units": "metric"}
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
        return {
            "error": str(e),
            "city": CITY,
            "temp": "N/A",
            "feels_like": "N/A",
            "description": "unavailable",
            "humidity": "N/A",
        }


# ---------------------------------------------------------------------------
# News Module
# ---------------------------------------------------------------------------

def fetch_news() -> list:
    """Return up to 5 news headlines. NewsAPI first, BBC RSS fallback."""
    if NEWS_API_KEY:
        url = "https://newsapi.org/v2/top-headlines"
        params = {"language": "en", "pageSize": 5, "apiKey": NEWS_API_KEY}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            articles = resp.json().get("articles", [])
            headlines = [a["title"] for a in articles[:5] if a.get("title")]
            if headlines:
                return headlines
        except Exception:
            pass  # Fall through to RSS

    # RSS fallback
    feed_url = "https://feeds.bbci.co.uk/news/rss.xml"
    try:
        feed = feedparser.parse(feed_url)
        return [entry.title for entry in feed.entries[:5]]
    except Exception as e:
        return [f"News unavailable: {e}"]


# ---------------------------------------------------------------------------
# Calendar and Task Modules
# ---------------------------------------------------------------------------

def load_calendar() -> list:
    """Load today's events from events.yaml."""
    if not EVENTS_FILE.exists():
        return ["No events.yaml found — create one to see your schedule"]
    try:
        with open(EVENTS_FILE) as f:
            data = yaml.safe_load(f)
        return data.get("events", [])
    except Exception as e:
        return [f"Calendar load error: {e}"]


def load_tasks() -> list:
    """Load open tasks from todo.txt (lines starting with '[ ]')."""
    if not TODO_FILE.exists():
        return ["No todo.txt found — create one to track your tasks"]
    try:
        with open(TODO_FILE) as f:
            lines = f.readlines()
        open_tasks = [line.strip() for line in lines if line.strip().startswith("[ ]")]
        return open_tasks if open_tasks else ["No open tasks — you are clear!"]
    except Exception as e:
        return [f"Task load error: {e}"]


# ---------------------------------------------------------------------------
# Market Module
# ---------------------------------------------------------------------------

def fetch_market() -> dict:
    """Fetch Nifty 50 index and top 3 movers by absolute % change."""
    try:
        nifty = yf.Ticker("^NSEI")
        nifty_info = nifty.fast_info
        nifty_price = round(float(nifty_info.last_price), 2)
        nifty_change = round(
            (float(nifty_info.last_price) - float(nifty_info.previous_close))
            / float(nifty_info.previous_close)
            * 100,
            2,
        )

        tickers = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "ITC.NS", "WIPRO.NS", "AXISBANK.NS", "BAJFINANCE.NS",
        ]

        movers = []
        for symbol in tickers:
            try:
                t = yf.Ticker(symbol)
                info = t.fast_info
                pct = round(
                    (float(info.last_price) - float(info.previous_close))
                    / float(info.previous_close)
                    * 100,
                    2,
                )
                movers.append((symbol.replace(".NS", ""), pct))
            except Exception:
                continue

        movers.sort(key=lambda x: abs(x[1]), reverse=True)
        return {
            "nifty_price": nifty_price,
            "nifty_change_pct": nifty_change,
            "top_movers": movers[:3],
        }
    except Exception as e:
        return {
            "error": str(e),
            "nifty_price": "N/A",
            "nifty_change_pct": "N/A",
            "top_movers": [],
        }


# ---------------------------------------------------------------------------
# Context Assembler
# ---------------------------------------------------------------------------

def assemble_context(weather: dict, news: list, events: list, tasks: list, market: dict) -> str:
    """Format all module outputs into a structured prompt context string."""
    today = datetime.date.today().strftime("%A, %B %d, %Y")

    news_block = "\n".join(f"- {h}" for h in news)
    events_block = "\n".join(f"- {e}" for e in events) if events else "- No events scheduled"
    tasks_block = "\n".join(f"- {t}" for t in tasks) if tasks else "- No open tasks"

    movers_block = "  (no data)"
    if market.get("top_movers"):
        movers_block = "\n".join(
            f"  - {name}: {pct:+.2f}%" for name, pct in market["top_movers"]
        )

    nifty_change = market.get("nifty_change_pct", "N/A")
    nifty_change_str = f"{nifty_change:+}" if isinstance(nifty_change, (int, float)) else str(nifty_change)

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
  Index: {market.get('nifty_price')} ({nifty_change_str}% today)
  Top movers:
{movers_block}
"""
    return context


# ---------------------------------------------------------------------------
# Claude Briefing Generator
# ---------------------------------------------------------------------------

def generate_briefing(context: str) -> str:
    """Send the context to Claude and return a 200-word narrative briefing."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = (
        "You are a personal morning briefing assistant. "
        "You receive structured daily data and write a calm, clear 200-word narrative digest. "
        "Weave together the weather, news, schedule, tasks, and market conditions into a coherent paragraph. "
        "Speak directly to the reader using 'you'. Be informative, not dramatic. "
        "End with one sentence of practical advice for the day ahead."
    )

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=400,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Please generate my morning briefing from this data:\n\n{context}",
            }
        ],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Delivery Module
# ---------------------------------------------------------------------------

def deliver(briefing: str, context: str) -> None:
    """Write digest to file and optionally deliver via email or Slack."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Always write to file
    content = (
        f"# Daily Digest — {today}\n\n"
        f"_Generated at {timestamp}_\n\n"
        f"## Morning Briefing\n\n{briefing}\n\n"
        f"---\n\n## Raw Data\n\n```\n{context}\n```\n"
    )
    with open(DIGEST_FILE, "w") as f:
        f.write(content)
    print(f"Digest written to {DIGEST_FILE}")

    # Email delivery
    if EMAIL_FROM and EMAIL_TO and EMAIL_PASSWORD:
        try:
            msg = MIMEText(f"{briefing}\n\n---\nRaw data:\n\n{context}", "plain")
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


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_briefing() -> None:
    """Orchestrate all modules: fetch → assemble → generate → deliver."""
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

    print("\n" + "=" * 60)
    print(briefing)
    print("=" * 60 + "\n")

    deliver(briefing, context)
    print("Done.\n")


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

def run_scheduler() -> None:
    """Start APScheduler to run briefing at 7:00 AM daily."""
    scheduler = BlockingScheduler()
    scheduler.add_job(run_briefing, "cron", hour=7, minute=0)
    print("Scheduler started. Briefing will run at 07:00 daily.")
    print("Press Ctrl+C to stop. Or run with --now to trigger immediately.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("Scheduler stopped.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        run_briefing()
    else:
        run_scheduler()
