"""
Personal Profile Builder Agent — Starter Code
==============================================
This file gives you the function signatures and docstrings.
Implement each function by following the steps in 03_GUIDE.md.

Usage (once complete):
    python starter.py torvalds
    python starter.py priyasharma --linkedin https://linkedin.com/in/priya-example/
"""

import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Config — fill these paths in
# ---------------------------------------------------------------------------
BASE_DIR      = Path(__file__).parent.parent     # ← project root
OUTPUT_DIR    = BASE_DIR / "output"
TEMPLATES_DIR = BASE_DIR / "templates"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Step 2 — GitHub scraper
# ---------------------------------------------------------------------------
def scrape_github(username: str) -> dict:
    """
    Fetch public GitHub profile data.

    Returns dict with keys:
        username, name, bio, location, public_repos, followers,
        top_repos (list of dicts), top_languages (list), recent_commits, github_url
    """
    # TODO: use PyGithub to fetch user data, repos, and language stats
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 3 — LinkedIn scraper
# ---------------------------------------------------------------------------
def scrape_linkedin(url: str) -> dict:
    """
    Attempt to scrape public LinkedIn profile.

    Returns dict with keys:
        headline, summary, scraped (bool), note (optional error message)

    Must NEVER raise — always return a dict even on failure.
    """
    if not url:
        return {"headline": "", "summary": "", "scraped": False}
    # TODO: use httpx + BeautifulSoup to extract headline and summary
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 4 — Claude agent
# ---------------------------------------------------------------------------
def build_profile(github_data: dict, linkedin_data: dict) -> dict:
    """
    Send scraped data to Claude and return a structured profile dict.

    Returns dict with keys:
        summary, skills (list), projects (list of {name, highlight}),
        narrative, twitter_bio
    """
    # TODO: assemble context string, call Anthropic API, parse JSON response
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 5 + 6 — Output generator
# ---------------------------------------------------------------------------
def generate_outputs(github_data: dict, profile: dict) -> dict:
    """
    Merge github_data into profile and render three output files.

    Returns dict: {"readme": path, "twitter_bio": path, "html": path}
    """
    # TODO: use Jinja2 to render readme.md.j2 and index.html.j2
    # TODO: write twitter_bio.txt (max 160 chars)
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 7 — Orchestrator
# ---------------------------------------------------------------------------
def run(github_username: str, linkedin_url: str = "") -> dict:
    """Full pipeline: scrape -> synthesise -> generate outputs."""
    print(f"Fetching GitHub data for @{github_username} ...")
    github_data = scrape_github(github_username)

    print("Fetching LinkedIn data ...")
    linkedin_data = scrape_linkedin(linkedin_url)

    print("Calling Claude to build profile ...")
    profile = build_profile(github_data, linkedin_data)

    print("Generating output files ...")
    outputs = generate_outputs(github_data, profile)
    for name, path in outputs.items():
        print(f"  {name}: {path}")

    return outputs


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Personal Profile Builder Agent"
    )
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("--linkedin", default="", help="LinkedIn public URL (optional)")
    args = parser.parse_args()
    run(args.username, args.linkedin)
    print("\nDone. Check the output/ folder.")


if __name__ == "__main__":
    main()
