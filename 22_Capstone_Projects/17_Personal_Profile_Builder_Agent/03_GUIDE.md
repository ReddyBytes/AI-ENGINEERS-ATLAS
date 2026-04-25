# 🔨 Build Guide — Personal Profile Builder Agent

## How to Use This Guide

This is a **Fully Guided** project. Every step has a complete explanation, complete working code, and `# ←` inline comments on non-obvious lines. Read each block, understand it, then paste it into your file. By Step 8 you will have a working CLI tool.

Estimated time: 2–3 hours.

---

## Step 1 — Project Setup

### What you are building
The skeleton: folder structure, `.env` file, and the `config.py` module that every other file imports.

### Why this matters
Centralising paths and API keys in one place means you only change them in one place when something moves. This is a standard pattern in production codebases.

### Complete code

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...       # optional — increases rate limit from 60 to 5000 req/hr
```

```python
# config.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()                              # ← reads .env file into os.environ

BASE_DIR        = Path(__file__).parent    # ← folder containing config.py
OUTPUT_DIR      = BASE_DIR / "output"      # ← all generated files go here
TEMPLATES_DIR   = BASE_DIR / "templates"  # ← Jinja2 templates

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN      = os.environ.get("GITHUB_TOKEN", "")   # ← optional; empty = anonymous

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)             # ← create if missing
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
```

<details><summary>💡 Hint</summary>

`Path(__file__).parent` always gives the directory of the current file, not the working directory from which you run the script. This makes your code relocatable.

</details>

---

## Step 2 — GitHub Scraper

### What you are building
A function `scrape_github(username: str) -> dict` that returns all the data Claude needs: name, bio, location, top repos by stars, primary languages, and a recent commit count.

### Why this matters
Raw GitHub API data is verbose and nested. By normalising it into a flat dict here, you keep the Claude agent simple — it just reads a clean dictionary, not paginated API objects.

### Complete code

```python
# github_scraper.py
from github import Github, GithubException  # ← pip install PyGithub
from datetime import datetime, timedelta, timezone
from config import GITHUB_TOKEN

def scrape_github(username: str) -> dict:
    """
    Fetch public GitHub profile data for a given username.
    Returns a flat dict ready to pass to the Claude agent.
    """
    g    = Github(GITHUB_TOKEN or None)             # ← None = anonymous (60 req/hr limit)
    user = g.get_user(username)

    # --- Fetch repos sorted by stars (most popular first) ---
    all_repos = list(user.get_repos(type="owner", sort="updated"))
    top_repos = sorted(all_repos, key=lambda r: r.stargazers_count, reverse=True)[:5]

    repo_dicts = []
    for repo in top_repos:
        if repo.fork:                               # ← skip forks; show original work only
            continue
        repo_dicts.append({
            "name":        repo.name,
            "description": repo.description or "",
            "stars":       repo.stargazers_count,
            "language":    repo.language or "N/A",
            "url":         repo.html_url,
        })

    # --- Aggregate languages across all repos ---
    lang_counts: dict[str, int] = {}
    for repo in all_repos[:20]:                    # ← sample first 20 to stay within rate limits
        if repo.fork:
            continue
        try:
            for lang, bytes_count in repo.get_languages().items():
                lang_counts[lang] = lang_counts.get(lang, 0) + bytes_count
        except GithubException:
            pass
    top_languages = sorted(lang_counts, key=lang_counts.get, reverse=True)[:5]

    # --- Count recent commits (last 30 days) ---
    since = datetime.now(timezone.utc) - timedelta(days=30)
    recent_commits = 0
    for repo in all_repos[:10]:                    # ← check 10 most-recently-updated repos
        try:
            commits = repo.get_commits(since=since, author=username)
            recent_commits += commits.totalCount
        except GithubException:
            pass

    return {
        "username":      username,
        "name":          user.name or username,
        "bio":           user.bio or "",
        "location":      user.location or "",
        "public_repos":  user.public_repos,
        "followers":     user.followers,
        "top_repos":     repo_dicts,
        "top_languages": top_languages,
        "recent_commits": recent_commits,
        "github_url":    user.html_url,
    }
```

<details><summary>💡 Hint</summary>

The `totalCount` attribute on a PyGithub `PaginatedList` makes a lightweight API call to get the count without downloading every commit. This keeps your API usage low.

</details>

---

## Step 3 — LinkedIn Scraper

### What you are building
A function `scrape_linkedin(url: str) -> dict` that attempts to extract the public headline and summary from a LinkedIn public profile URL. LinkedIn aggressively rate-limits bots, so you include a graceful fallback.

### Why this matters
LinkedIn is the most common professional data source, but it blocks automated requests. Learning to handle this gracefully — returning partial data rather than crashing — is a real production skill.

### Complete code

```python
# linkedin_scraper.py
import httpx                              # ← pip install httpx
from bs4 import BeautifulSoup            # ← pip install beautifulsoup4

# LinkedIn serves different HTML depending on the User-Agent.
# A browser-like UA gets the public profile; a Python default gets a login wall.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_linkedin(url: str) -> dict:
    """
    Scrape public LinkedIn profile for headline and summary.
    Returns a dict with best-effort data; never raises on failure.
    """
    if not url:
        return {"headline": "", "summary": "", "scraped": False}

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            resp = client.get(url, headers=HEADERS)

        if resp.status_code != 200:
            return {
                "headline": "",
                "summary":  "",
                "scraped":  False,
                "note":     f"HTTP {resp.status_code} — LinkedIn may have blocked the request",
            }

        soup = BeautifulSoup(resp.text, "html.parser")

        # LinkedIn public profiles embed structured data in <script type="application/ld+json">
        # The h1 tag usually holds the full name; the .top-card__subline-item holds the headline.
        headline = ""
        for selector in [
            ".top-card-layout__headline",     # ← older public profile layout
            ".top-card__subline-item",
            "h2.top-card-layout__headline",
        ]:
            tag = soup.select_one(selector)
            if tag:
                headline = tag.get_text(strip=True)
                break

        # Summary / About section
        summary = ""
        for selector in [
            ".core-section-container__content p",
            ".summary__text",
            "section.summary p",
        ]:
            tag = soup.select_one(selector)
            if tag:
                summary = tag.get_text(strip=True)
                break

        return {
            "headline": headline,
            "summary":  summary,
            "scraped":  bool(headline or summary),
        }

    except (httpx.RequestError, Exception) as exc:
        # Always return a dict — never let a scrape failure crash the agent
        return {"headline": "", "summary": "", "scraped": False, "note": str(exc)}
```

<details><summary>💡 Hint</summary>

LinkedIn frequently changes its HTML class names. If the selectors above stop working, inspect the page source in your browser DevTools (`Ctrl+U`) and search for the text of the headline to find the current container class.

</details>

---

## Step 4 — Claude Agent

### What you are building
A function `build_profile(github_data: dict, linkedin_data: dict) -> dict` that sends all scraped data to Claude and receives a structured profile back.

### Why this matters
This is the heart of the agent. All the messy raw data — varying bio lengths, uneven repo descriptions, optional LinkedIn data — goes in, and clean, consistent, professional copy comes out. Claude handles the variation so your templates stay simple.

### Complete code

```python
# claude_agent.py
import json
import anthropic                           # ← pip install anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """
You are a professional technical writer and career coach.
Given raw GitHub and LinkedIn data about a software developer,
produce a JSON object with these exact keys:
  - summary:     3-5 sentence professional bio in third person
  - skills:      list of up to 10 skill tag strings (concise, e.g. "Python", "RAG Pipelines")
  - projects:    list of up to 4 objects with keys: name, highlight (1 sentence)
  - narrative:   2-3 sentence career story in first person (for personal website About section)
  - twitter_bio: ≤160 characters, first person, punchy, include 1-2 key skills and location if known

Return ONLY valid JSON. No markdown fences. No explanation.
""".strip()


def build_profile(github_data: dict, linkedin_data: dict) -> dict:
    """
    Send scraped data to Claude and return a structured profile dict.
    Falls back to safe defaults if the API call fails.
    """
    # Build a compact context string — only include non-empty fields
    context_lines = [
        f"GitHub username: {github_data.get('username', '')}",
        f"Name: {github_data.get('name', '')}",
        f"GitHub bio: {github_data.get('bio', '')}",
        f"Location: {github_data.get('location', '')}",
        f"Public repos: {github_data.get('public_repos', 0)}",
        f"Followers: {github_data.get('followers', 0)}",
        f"Top languages: {', '.join(github_data.get('top_languages', []))}",
        f"Recent commits (30 days): {github_data.get('recent_commits', 0)}",
        "",
        "Top repositories:",
    ]
    for repo in github_data.get("top_repos", []):
        context_lines.append(
            f"  - {repo['name']} ({repo['language']}, {repo['stars']} stars): "
            f"{repo['description']}"
        )

    if linkedin_data.get("headline"):
        context_lines += [
            "",
            f"LinkedIn headline: {linkedin_data['headline']}",
        ]
    if linkedin_data.get("summary"):
        context_lines.append(f"LinkedIn summary: {linkedin_data['summary']}")

    context = "\n".join(context_lines)

    try:
        resp = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,               # ← enough for a full profile JSON
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Build a professional profile for this developer:\n\n{context}",
            }],
        )
        raw = resp.content[0].text.strip()
        # Strip accidental markdown fences if Claude added them
        if raw.startswith("```"):
            raw = raw.split("```")[1]      # ← grab content between first pair of fences
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)

    except (json.JSONDecodeError, Exception) as exc:
        # Safe fallback so the rest of the pipeline still runs
        print(f"Claude agent error: {exc}")
        return {
            "summary":     f"{github_data.get('name', 'A developer')} builds software.",
            "skills":      github_data.get("top_languages", []),
            "projects":    [],
            "narrative":   "I build open-source software.",
            "twitter_bio": f"{github_data.get('bio', 'Software developer')} — GitHub: {github_data.get('username', '')}",
        }
```

<details><summary>💡 Hint</summary>

Asking Claude to return JSON is more reliable when you also tell it the exact keys. Adding "Return ONLY valid JSON" in the system prompt prevents Claude from wrapping the response in prose — but always write a `json.JSONDecodeError` fallback anyway, because no prompt guarantee is 100%.

</details>

---

## Step 5 — Jinja2 Templates

### What you are building
Two Jinja2 template files: `templates/readme.md.j2` and `templates/index.html.j2`. These are the "layout team" — they take the profile dict and render it into final file formats.

### Why this matters
Separating templates from logic is the Model-View principle. If a recruiter wants a different README style, you change the template, not the Python code.

### Complete code

Create `templates/readme.md.j2`:
```jinja
<!-- GitHub Profile README — generated by Personal Profile Builder Agent -->

# Hi, I'm {{ profile.name }} 👋

{{ profile.summary }}

## 🛠️ Skills

{% for skill in profile.skills -%}
![{{ skill }}](https://img.shields.io/badge/{{ skill | urlencode }}-informational?style=flat)
{% endfor %}

## 🚀 Highlighted Projects

| Project | Description |
|---------|-------------|
{% for proj in profile.projects -%}
| [{{ proj.name }}](https://github.com/{{ profile.github_username }}/{{ proj.name }}) | {{ proj.highlight }} |
{% endfor %}

## 📊 GitHub Stats

- Public repos: **{{ profile.public_repos }}**
- Followers: **{{ profile.followers }}**
- Recent commits (30 days): **{{ profile.recent_commits }}**

---

*Generated by [Personal Profile Builder Agent](https://github.com/{{ profile.github_username }})*
```

Create `templates/index.html.j2`:
```jinja
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ profile.name }}</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.6;
        }
        header {
            background: #161b22;
            border-bottom: 1px solid #30363d;
            padding: 2rem;
            text-align: center;
        }
        header h1  { font-size: 2rem; color: #f0f6fc; }
        header p   { color: #8b949e; margin-top: 0.5rem; }
        main       { max-width: 860px; margin: 2rem auto; padding: 0 1.5rem; }
        section    { margin-bottom: 2rem; }
        h2         { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 0.5rem; margin-bottom: 1rem; }
        .skills    { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .skill-tag {
            background: #1f6feb;
            color: #f0f6fc;
            padding: 0.25rem 0.75rem;
            border-radius: 2rem;
            font-size: 0.875rem;
        }
        .project   {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .project a { color: #58a6ff; text-decoration: none; font-weight: 600; }
        footer     { text-align: center; padding: 2rem; color: #8b949e; font-size: 0.875rem; }
    </style>
</head>
<body>
    <header>
        <h1>{{ profile.name }}</h1>
        <p>{{ profile.location }}</p>
        <p><a href="{{ profile.github_url }}" style="color:#58a6ff">GitHub</a></p>
    </header>

    <main>
        <section>
            <h2>About</h2>
            <p>{{ profile.narrative }}</p>
        </section>

        <section>
            <h2>Skills</h2>
            <div class="skills">
                {% for skill in profile.skills %}
                <span class="skill-tag">{{ skill }}</span>
                {% endfor %}
            </div>
        </section>

        <section>
            <h2>Projects</h2>
            {% for proj in profile.projects %}
            <div class="project">
                <a href="https://github.com/{{ profile.github_username }}/{{ proj.name }}">{{ proj.name }}</a>
                <p>{{ proj.highlight }}</p>
            </div>
            {% endfor %}
        </section>
    </main>

    <footer>Generated by Personal Profile Builder Agent</footer>
</body>
</html>
```

<details><summary>💡 Hint</summary>

The `| urlencode` filter in the Jinja2 README template converts spaces and special characters in skill names into URL-safe strings for the shields.io badge URLs. Jinja2 includes this filter by default.

</details>

---

## Step 6 — Output Generator

### What you are building
A function `generate_outputs(github_data: dict, profile: dict) -> dict` that takes the Claude profile dict, adds the raw GitHub data fields needed by templates, renders all three templates, and writes the output files.

### Why this matters
The output generator is a pure transformation step — no API calls, no side effects except writing files. Keeping it isolated makes it easy to test and easy to swap templates.

### Complete code

```python
# output_generator.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from config import OUTPUT_DIR, TEMPLATES_DIR


def generate_outputs(github_data: dict, profile: dict) -> dict:
    """
    Merge github_data into profile, render templates, write output files.
    Returns dict of {output_name: file_path}.
    """
    # Merge GitHub fields that templates need directly
    profile["github_username"] = github_data["username"]
    profile["github_url"]      = github_data["github_url"]
    profile["public_repos"]    = github_data["public_repos"]
    profile["followers"]       = github_data["followers"]
    profile["recent_commits"]  = github_data["recent_commits"]
    profile["location"]        = profile.get("location") or github_data.get("location", "")
    profile["name"]             = profile.get("name") or github_data.get("name", github_data["username"])

    env = Environment(
        loader=select_loader(TEMPLATES_DIR),
        autoescape=select_autoescape(disabled_extensions=("j2",)),  # ← disable HTML escaping in .md
    )

    outputs = {}

    # --- profile_README.md ---
    readme_template = env.get_template("readme.md.j2")
    readme_content  = readme_template.render(profile=profile)
    readme_path     = OUTPUT_DIR / "profile_README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    outputs["readme"] = str(readme_path)

    # --- twitter_bio.txt ---
    bio = profile.get("twitter_bio", "")
    bio = bio[:160]                                          # ← hard cap at 160 chars
    bio_path = OUTPUT_DIR / "twitter_bio.txt"
    bio_path.write_text(bio, encoding="utf-8")
    outputs["twitter_bio"] = str(bio_path)

    # --- index.html ---
    html_template = env.get_template("index.html.j2")
    html_content  = html_template.render(profile=profile)
    html_path     = OUTPUT_DIR / "index.html"
    html_path.write_text(html_content, encoding="utf-8")
    outputs["html"] = str(html_path)

    return outputs


def select_loader(templates_dir: Path):
    """Return a Jinja2 FileSystemLoader, creating a fallback template if directory is empty."""
    from jinja2 import FileSystemLoader
    return FileSystemLoader(str(templates_dir))
```

<details><summary>💡 Hint</summary>

`select_autoescape(disabled_extensions=("j2",))` disables HTML auto-escaping for all `.j2` templates. Without this, angle brackets in the README (e.g. `<img>` tags from shields.io) would be escaped to `&lt;img&gt;`.

</details>

---

## Step 7 — CLI Orchestrator

### What you are building
`main.py` — the entry point that wires every component together and exposes a clean command-line interface.

### Why this matters
A CLI makes your agent reusable without modifying code. Other tools can call it; you can alias it; teammates can use it. This is how most production ML tools are packaged before they get a UI.

### Complete code

```python
# main.py
import argparse
from github_scraper    import scrape_github
from linkedin_scraper  import scrape_linkedin
from claude_agent      import build_profile
from output_generator  import generate_outputs


def run(github_username: str, linkedin_url: str = "") -> dict:
    """
    Full pipeline: scrape → synthesise → generate outputs.
    Returns dict of {output_name: file_path}.
    """
    print(f"Fetching GitHub data for @{github_username} ...")
    github_data = scrape_github(github_username)
    print(f"  Found {github_data['public_repos']} repos, "
          f"top languages: {', '.join(github_data['top_languages'])}")

    print("Fetching LinkedIn data ...")
    linkedin_data = scrape_linkedin(linkedin_url)
    if linkedin_data["scraped"]:
        print(f"  Headline: {linkedin_data['headline']}")
    else:
        print("  LinkedIn not available — proceeding with GitHub data only")

    print("Calling Claude to build profile ...")
    profile = build_profile(github_data, linkedin_data)
    print(f"  Summary: {profile['summary'][:80]}...")

    print("Generating output files ...")
    outputs = generate_outputs(github_data, profile)
    for name, path in outputs.items():
        print(f"  {name}: {path}")

    return outputs


def main():
    parser = argparse.ArgumentParser(
        description="Personal Profile Builder Agent — generate README, bio, and website"
    )
    parser.add_argument(
        "username",
        help="GitHub username (e.g. torvalds)",
    )
    parser.add_argument(
        "--linkedin",
        default="",
        help="LinkedIn public profile URL (optional)",
    )
    args = parser.parse_args()
    run(args.username, args.linkedin)
    print("\nDone. Check the output/ folder.")


if __name__ == "__main__":
    main()
```

<details><summary>💡 Hint</summary>

Separating `run()` from `main()` means you can import and call `run()` programmatically from a Streamlit app or a test, without triggering `argparse`. This is a standard pattern for Python CLI tools.

</details>

---

## Step 8 — Run It

### What you are doing
Running the complete agent end-to-end.

### Complete instructions

```bash
# 1. Install dependencies
pip install anthropic PyGithub httpx beautifulsoup4 jinja2 python-dotenv

# 2. Set up your .env
echo 'ANTHROPIC_API_KEY=sk-ant-...' >> .env
echo 'GITHUB_TOKEN=ghp_...' >> .env   # optional but recommended

# 3. Run the agent
python main.py torvalds

# 4. With LinkedIn (optional)
python main.py priyasharma --linkedin https://www.linkedin.com/in/priya-sharma-example/

# 5. View outputs
ls output/
# profile_README.md   twitter_bio.txt   index.html

# Open the website
open output/index.html          # macOS
xdg-open output/index.html      # Linux
```

Expected output:
```
Fetching GitHub data for @torvalds ...
  Found 11 repos, top languages: C, Shell, Perl
Fetching LinkedIn data ...
  LinkedIn not available — proceeding with GitHub data only
Calling Claude to build profile ...
  Summary: Linus Torvalds is a Finnish-American software engineer ...
Generating output files ...
  readme: /path/to/output/profile_README.md
  twitter_bio: /path/to/output/twitter_bio.txt
  html: /path/to/output/index.html

Done. Check the output/ folder.
```

<details><summary>💡 Hint</summary>

If you get a rate-limit error from GitHub (HTTP 403), set a `GITHUB_TOKEN` in your `.env`. A personal access token with no extra scopes is enough — it just raises the limit from 60 to 5000 requests per hour. Create one at `github.com/settings/tokens`.

</details>

---

## 📂 Navigation

| | Link |
|---|---|
| Back to Capstone Index | [22_Capstone_Projects README](../README.md) |
| Previous File | [02 — Architecture](./02_ARCHITECTURE.md) |
| Next File | [04 — Recap](./04_RECAP.md) |
| Starter Code | [src/starter.py](./src/starter.py) |
| Solution | [src/solution.py](./src/solution.py) |
