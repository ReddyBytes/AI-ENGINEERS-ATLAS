# 🎯 Mission Briefing — Personal Profile Builder Agent

## 🗺️ The Analogy

Imagine a career coach who has spent the weekend reading every repository you ever pushed to GitHub, skimmed your LinkedIn headline, and then — without you lifting a finger — drafted your GitHub profile README, your Twitter bio, and your personal website. That is exactly what this agent does. It scrapes what is already public, hands it to Claude for synthesis, and writes three polished output files ready to copy-paste.

---

## 🎯 What This Project Builds

An agent that accepts a **GitHub username** and an optional **LinkedIn public profile URL**, then:

1. Fetches public GitHub data via the PyGithub API: repositories, star counts, primary languages, recent commit activity, and your bio
2. Scrapes the LinkedIn public profile page for headline and summary (with graceful rate-limit handling)
3. Sends everything to Claude to generate:
   - A professional summary
   - A ranked skill tag list
   - Highlighted project descriptions
   - A career narrative
4. Writes three output files:
   - `profile_README.md` — GitHub-flavored profile README
   - `twitter_bio.txt` — 160-character Twitter/X bio
   - `index.html` — a simple dark-theme personal website

---

## 📋 Success Criteria

| Criterion | What "Done" Looks Like |
|-----------|----------------------|
| GitHub scraper | Bio, top 5 repos by stars, primary languages, and recent commit count fetched without errors |
| LinkedIn scraper | Headline extracted or graceful fallback if blocked |
| Claude synthesis | Professional summary is 3–5 sentences, coherent, and specific to the user |
| profile_README.md | Renders correctly on GitHub with badge, skill tags, and project table |
| twitter_bio.txt | Exactly ≤160 characters |
| index.html | Opens in browser, dark theme, no broken links |

---

## 🎓 Learning Tier

**Intermediate — Fully Guided**

This project assumes you are comfortable with:
- Basic Python (functions, classes, f-strings)
- Making HTTP requests with `requests` or similar
- Reading and writing files

Every step in `03_GUIDE.md` includes a full explanation, complete working code, and inline comments. There are no gaps to fill in — just read, understand, and run.

---

## 🌍 Why This Matters

Your GitHub profile README is the first thing a recruiter sees when they Google your GitHub username. Most developers either have a blank profile or a generic template. An agent-generated profile that reflects your *actual* projects and skills — written in professional English — immediately signals that you understand AI tooling at a practical level. This project is also a clear demonstration of multi-source data scraping, LLM synthesis, and multi-format output generation — core skills for any AI engineering role.

---

## 📂 Navigation

| | Link |
|---|---|
| Back to Capstone Index | [22_Capstone_Projects README](../README.md) |
| Previous Project | [16 — Budget Portfolio Agent](../16_Budget_Portfolio_Agent/01_MISSION.md) |
| Next File | [02 — Architecture](./02_ARCHITECTURE.md) |
