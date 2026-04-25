# Project 22 — AI Job Application Agent

## Mission Brief

You are a recruiter's worst nightmare and a job seeker's best friend.

Picture a surgical resident fresh out of training. She knows her skills cold: sutures, diagnostics, patient management. But she's applying to 30 different hospitals, each with a different culture — trauma center, academic research, rural generalist, pediatric specialist. Each application needs to sound like it was written specifically for that role. Writing 30 personalized cover letters and tailored resumes from scratch would take weeks. She can't afford that time. So she builds an assistant.

That assistant reads the job description, reads her resume, finds the gap between what they're asking for and what she has, then rewrites her resume summary and bullet points to speak that hospital's language — all without changing the facts. Then it writes a personalized cover letter that opens with exactly what that employer cares about. Then it logs the application to a tracker so nothing falls through the cracks.

This project is that assistant. You will build an **AI Job Application Agent** that automates the entire personalization layer of job applications.

---

## What You Will Build

An agent that accepts a job description (pasted text or a URL) and your resume (PDF or Markdown file) and produces:

1. **JD Analysis** — extracts required skills, nice-to-have skills, role level, and company culture signals
2. **Resume Analysis** — extracts your skills, experience timeline, and project highlights
3. **Gap Analysis** — what the JD requires that your resume does not clearly demonstrate
4. **Tailored Resume** — Claude rewrites your resume summary and experience bullets to match JD keywords and ATS scoring patterns
5. **Cover Letter** — Claude writes a 3-paragraph personalized cover letter (hook, evidence, close)
6. **Application Log** — appends a row to `applications.csv` with company, role, date, status, JD URL, and tailored resume path

---

## Output Files

| File | Description |
|---|---|
| `tailored_resume.md` | Your resume rewritten for this specific JD |
| `cover_letter.md` | Personalized 3-paragraph cover letter |
| `applications.csv` | Running tracker — one row per application |

---

## Tech Stack

| Library | Why |
|---|---|
| `anthropic` | Claude API — JD parsing, resume rewriting, cover letter generation |
| `pdfplumber` | Extract text from PDF resumes |
| `requests` | Fetch JD from URL |
| `beautifulsoup4` | Parse HTML from JD pages |
| `python-dotenv` | Load API key from `.env` |
| `csv` | Write and append to `applications.csv` |

---

## Format

**Partially Guided** — You get the data flow, function signatures, and key prompts outlined. Implementation details are left to you.

---

## Difficulty

Intermediate (3 / 5)

The Claude API calls are straightforward. The challenge is engineering prompts that produce structured, consistent output across wildly different job descriptions and resume styles. Expect to iterate on your prompts.

---

## Prerequisites

- Completed the LLM Chatbot or Document Analyzer project, or equivalent
- Anthropic API key set in `.env` as `ANTHROPIC_API_KEY`
- Python 3.10+
- Installed: `pip install anthropic pdfplumber requests beautifulsoup4 python-dotenv`

---

## Expected Output

```
Job Application Agent
=====================
JD source: URL (https://jobs.example.com/senior-ml-engineer)
Resume source: resume.pdf

[1/6] Fetching job description...
      Done. 847 words extracted.

[2/6] Parsing your resume...
      Done. 6 roles, 12 skills, 4 projects found.

[3/6] Analyzing JD requirements...
      Required skills:     Python, PyTorch, distributed training, MLOps
      Nice-to-have:        Kubernetes, Rust, TPU experience
      Role level:          Senior / Staff
      Culture signals:     fast-paced, ownership-driven, research-to-production

[4/6] Running gap analysis...
      Gaps identified:     distributed training (not mentioned), MLOps tooling (vague)
      Strong matches:      Python, PyTorch, ML research, model deployment

[5/6] Rewriting resume for this role...
      tailored_resume.md written.

[6/6] Writing cover letter...
      cover_letter.md written.

Application logged to applications.csv.

Done. 3 files ready in ./output/
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 01_MISSION.md | ← you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and data flow |
| [03_GUIDE.md](./03_GUIDE.md) | 9-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [src/solution.py](./src/solution.py) | Complete working solution |
| [04_RECAP.md](./04_RECAP.md) | What you built and what's next |

⬅️ **Prev:** [21 — Claude Mastery](../../21_Claude_Mastery/Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [23 — Codebase Review Agent](../23_Codebase_Review_Agent/01_MISSION.md)
