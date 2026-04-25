"""
Project 18 — Daily Automation Agent
Starter skeleton — fill in the TODO sections to complete the project.

Run immediately (skip scheduler):
    python src/starter.py --now

Run with scheduler (fires at 7am daily):
    python src/starter.py
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
# Step 2 — Weather Module
# ---------------------------------------------------------------------------

def fetch_weather() -> dict:
    """
    Fetch current weather from OpenWeatherMap for CITY.

    Returns a dict with keys: city, temp, feels_like, description, humidity.
    Return a safe fallback dict if anything fails.

    API endpoint: https://api.openweathermap.org/data/2.5/weather
    Required params: q (city), appid (key), units (use 'metric')

    TODO: implement this function
    """
    # TODO: check if OWM_API_KEY is set; return error dict if not
    # TODO: call the OWM API with requests.get()
    # TODO: parse and return the relevant fields
    # TODO: wrap in try/except and return fallback dict on failure
    pass


# ---------------------------------------------------------------------------
# Step 3 — News Module
# ---------------------------------------------------------------------------

def fetch_news() -> list:
    """
    Return up to 5 news headlines as a list of strings.
    Try NewsAPI first; fall back to BBC RSS if not configured.

    NewsAPI endpoint: https://newsapi.org/v2/top-headlines
    BBC RSS: https://feeds.bbci.co.uk/news/rss.xml

    TODO: implement this function
    """
    # TODO: try NewsAPI if NEWS_API_KEY is set
    # TODO: fall back to feedparser.parse(bbc_rss_url)
    # TODO: return list of headline strings
    pass


# ---------------------------------------------------------------------------
# Step 4 — Calendar and Task Modules
# ---------------------------------------------------------------------------

def load_calendar() -> list:
    """
    Load today's events from events.yaml.
    Expected format:
        events:
          - "09:00 — Team standup"
          - "14:00 — Design review"

    TODO: implement this function
    """
    # TODO: check if EVENTS_FILE exists
    # TODO: yaml.safe_load() the file
    # TODO: return the events list
    pass


def load_tasks() -> list:
    """
    Load open tasks from todo.txt.
    Only return lines that start with '[ ]' (uncompleted tasks).

    TODO: implement this function
    """
    # TODO: check if TODO_FILE exists
    # TODO: read lines and filter for '[ ]' prefix
    pass


# ---------------------------------------------------------------------------
# Step 5 — Market Module
# ---------------------------------------------------------------------------

def fetch_market() -> dict:
    """
    Fetch Nifty 50 index price and top 3 movers by absolute % change.

    Nifty 50 ticker: "^NSEI"
    Sample constituents: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, ICICIBANK.NS

    Use yf.Ticker(symbol).fast_info for speed.

    TODO: implement this function
    """
    # TODO: fetch Nifty 50 index price and daily % change
    # TODO: loop through constituent tickers, compute % change for each
    # TODO: sort by abs(pct_change) and return top 3
    # TODO: return fallback dict on failure
    pass


# ---------------------------------------------------------------------------
# Step 6 — Context Assembler and Claude Briefing
# ---------------------------------------------------------------------------

def assemble_context(weather: dict, news: list, events: list, tasks: list, market: dict) -> str:
    """
    Format all module outputs into a single structured string for Claude.

    Include: today's date, weather, headlines, calendar, tasks, market data.

    TODO: implement this function
    """
    # TODO: format today's date
    # TODO: build news_block, events_block, tasks_block, movers_block strings
    # TODO: assemble into one multi-line string and return it
    pass


def generate_briefing(context: str) -> str:
    """
    Send the context to Claude and return a 200-word narrative morning briefing.

    Use model: claude-haiku-4-5
    System prompt should ask for: calm, direct, 200-word narrative, practical closing advice.

    TODO: implement this function
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # TODO: write a system prompt defining the briefing persona
    # TODO: call client.messages.create() with the context as user message
    # TODO: return message.content[0].text
    pass


# ---------------------------------------------------------------------------
# Step 7 — Delivery Module
# ---------------------------------------------------------------------------

def deliver(briefing: str, context: str) -> None:
    """
    1. Always write the digest to DIGEST_FILE as markdown.
    2. Optionally send via email if EMAIL_FROM/TO/PASSWORD are set.
    3. Optionally post to Slack if SLACK_WEBHOOK_URL is set.

    TODO: implement this function
    """
    # TODO: format markdown content with date, briefing, raw data
    # TODO: write to DIGEST_FILE
    # TODO: if email env vars are set, send via smtplib SMTP_SSL
    # TODO: if SLACK_WEBHOOK_URL is set, POST json payload with requests
    pass


# ---------------------------------------------------------------------------
# Step 8 — Orchestrator and Scheduler
# ---------------------------------------------------------------------------

def run_briefing() -> None:
    """
    Orchestrate all modules: fetch → assemble → generate → deliver.

    TODO: call each module in order, print progress, then deliver.
    """
    print(f"\n--- Running morning briefing at {datetime.datetime.now()} ---")
    # TODO: call fetch_weather(), fetch_news(), load_calendar(), load_tasks(), fetch_market()
    # TODO: call assemble_context() with all results
    # TODO: call generate_briefing() with context
    # TODO: print the briefing
    # TODO: call deliver()
    pass


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
        run_briefing()
    else:
        run_scheduler()
