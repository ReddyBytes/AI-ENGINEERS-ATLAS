# Project 19 — Research Paper to Podcast Agent

## The Briefing

Every week, thousands of research papers are published on arXiv. Most engineers never read them — not because they are uninterested, but because academic writing is dense and time is short.

The podcast format solves this. A good host takes a complex idea, finds the right analogy, strips away the jargon, and explains it in plain English while you are commuting or cooking. The listener gets the insight without needing a PhD.

This project automates that translation. You give the agent an arXiv URL or a local PDF path. It reads the paper, extracts the key content, and asks Claude to write a 5-minute podcast script — a host explaining the paper to a curious but non-specialist listener. Then it converts the script to audio using gTTS (Google Text-to-Speech).

The result: an `.mp3` file you can actually listen to, a `transcript.md` you can search, and a `key_points.md` with five sharp takeaways.

---

## What Success Looks Like

Running `python src/solution.py --url https://arxiv.org/abs/1706.03762` will:

1. Download and parse the paper (Attention Is All You Need in this case)
2. Extract the abstract and major sections
3. Ask Claude to generate a conversational 5-minute podcast script
4. Convert the script to audio using gTTS
5. Save three output files:
   - `podcast_summary.mp3` — the audio episode
   - `transcript.md` — the full podcast script
   - `key_points.md` — 5 bullet takeaways

---

## What You Will Learn

| Skill | Where it appears |
|---|---|
| PDF text extraction | pdfplumber parsing pipeline |
| arXiv paper fetching via URL | PDF download from arXiv |
| Structured LLM prompt design | Claude podcast script generation |
| Text-to-speech conversion | gTTS audio generation |
| Multi-file output generation | Three output files from one run |
| CLI argument handling | argparse for `--url` and `--pdf` |
| Batch processing (extension) | Process multiple papers at once |

---

## Learning Tier

**Intermediate.** This guide explains what to build at each step, provides partial code and structural hints, but leaves the implementation to you. Use the solution only after attempting each step yourself.

---

## Prerequisites

- Python 3.9+
- Anthropic API key
- `ffmpeg` installed (required by gTTS on some systems)

Install ffmpeg on macOS: `brew install ffmpeg`

---

## Tech Stack

| Library | Role |
|---|---|
| `anthropic` | Claude API — podcast script generation |
| `pdfplumber` | Extract text from PDF files |
| `requests` | Download arXiv PDFs |
| `gTTS` | Google Text-to-Speech (free, no API key) |
| `python-dotenv` | API key management |
| `argparse` | CLI interface (stdlib) |

---

## Output Files

| File | Contents |
|---|---|
| `podcast_summary.mp3` | Audio version of the podcast script (~5 minutes) |
| `transcript.md` | Full podcast script with host narration |
| `key_points.md` | 5 bullet takeaways from the paper |

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
