# Project 22 — AI Job Application Agent: Build Guide

## Before You Start

Install dependencies:

```bash
pip install anthropic pdfplumber requests beautifulsoup4 python-dotenv
```

Create a `.env` file in the project folder:

```
ANTHROPIC_API_KEY=your_key_here
```

Prepare a test resume. A Markdown file works fine — you do not need a PDF to start. Prepare a sample job description (copy any JD from LinkedIn or Indeed).

---

## Step 1 — Project structure and config loading

Create `job_agent.py`. At the top, load your environment:

```python
import os
import json
import csv
from datetime import date
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-opus-4-5"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

**Checkpoint:** Running `python job_agent.py` should produce no errors.

---

## Step 2 — JD ingestor

Write `ingest_jd(source: str) -> str`.

- If `source` starts with `http`, use `requests.get()` to fetch the page. Parse the HTML with BeautifulSoup and return the body text: `soup.get_text(separator=" ", strip=True)`.
- Otherwise, treat `source` as the JD text itself and return it directly.

Limit the returned text to 4000 characters to avoid blowing the prompt budget. Use `text[:4000]`.

**Checkpoint:** Paste a JD URL and print the first 500 characters of the returned text.

---

## Step 3 — Resume ingestor

Write `ingest_resume(path: str) -> str`.

- If path ends in `.pdf`: use `pdfplumber.open(path)` and concatenate `page.extract_text()` for all pages.
- If path ends in `.md` or `.txt`: use `open(path).read()`.
- Raise `ValueError` for unsupported extensions.

**Checkpoint:** Print the first 200 characters of your parsed resume. Confirm the text is clean (no garbled PDF characters).

---

## Step 4 — Parse the JD with Claude

Write `parse_jd(jd_text: str) -> dict`.

Call Claude with the JD parsing prompt from the Architecture file. Use `claude-opus-4-5` or `claude-haiku-4-5` (faster and cheaper for parsing tasks).

The prompt asks Claude to return valid JSON. Extract the JSON from the response:

```python
response_text = response.content[0].text
parsed = json.loads(response_text)
```

Return the dict. If `json.loads` raises an exception, print a warning and return a safe default dict with empty lists.

**Checkpoint:** Print the parsed JD dict. You should see `required_skills`, `nice_to_have`, `role_level`, `culture_signals`, `summary`.

---

## Step 5 — Parse the resume with Claude

Write `parse_resume(resume_text: str) -> dict`.

Same pattern as Step 4 — call Claude with the resume parsing prompt, extract JSON, return dict.

Keys to expect: `skills`, `current_role`, `years_experience`, `roles`, `projects`, `summary`.

**Checkpoint:** Print the parsed resume dict. Confirm skills list matches what is on your resume.

---

## Step 6 — Gap analysis (pure Python, no Claude)

Write `gap_analysis(jd_parsed: dict, resume_parsed: dict) -> dict`.

This function does not call Claude. It compares two lists:

1. Build a set of your skills (lowercased): `resume_skills = {s.lower() for s in resume_parsed["skills"]}`
2. For each required skill in `jd_parsed["required_skills"]`, check if any resume skill contains it as a substring
3. Skills not found: `gaps`. Skills found: `strengths`.

Return:
```python
{
    "gaps": [...],        # JD required skills absent from resume
    "strengths": [...],   # JD required skills present in resume
    "nice_to_have_gaps": [...],  # nice-to-have skills also absent
}
```

**Checkpoint:** Print the gap analysis. The gaps should make intuitive sense given your resume vs the JD.

---

## Step 7 — Rewrite the resume

Write `rewrite_resume(original_resume: str, jd_parsed: dict, gap_analysis: dict) -> str`.

Call Claude with the resume rewrite prompt. This is the most important prompt in the pipeline. Feed it:
- The original resume text
- The JD analysis (required skills, nice-to-have, role level, culture signals)
- The gap analysis (what to emphasize, what to acknowledge)

The response is raw Markdown — no JSON parsing needed. Return `response.content[0].text`.

Save to file:

```python
output_path = os.path.join(OUTPUT_DIR, "tailored_resume.md")
with open(output_path, "w") as f:
    f.write(rewritten)
```

**Checkpoint:** Open `output/tailored_resume.md`. Read the summary section — it should open with language from the JD.

---

## Step 8 — Write the cover letter

Write `write_cover_letter(company: str, role: str, jd_parsed: dict, resume_parsed: dict, gap_analysis: dict) -> str`.

Call Claude with the cover letter prompt. Three paragraphs, no fluff.

Save to `output/cover_letter.md`.

**Checkpoint:** Read the cover letter. Paragraph 1 should reference a specific JD requirement. Paragraph 3 should reference a culture signal.

---

## Step 9 — Log the application and wire everything together

Write `log_application(company, role, jd_source, resume_output_path)`.

Append a row to `applications.csv`:

```python
fieldnames = ["company", "role", "date_applied", "status", "jd_url", "tailored_resume_path", "notes"]
file_exists = os.path.exists("applications.csv")
with open("applications.csv", "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if not file_exists:
        writer.writeheader()
    writer.writerow({
        "company": company,
        "role": role,
        "date_applied": date.today().isoformat(),
        "status": "Applied",
        "jd_url": jd_source if jd_source.startswith("http") else "pasted",
        "tailored_resume_path": resume_output_path,
        "notes": "",
    })
```

Write a `main()` function that accepts command-line arguments or prompts for:
- JD source (URL or paste)
- Resume path
- Company name
- Role title

Call each stage in order and print progress markers `[1/6]` through `[6/6]`.

**Checkpoint:** Run the full pipeline end-to-end. Check that all three output files exist and `applications.csv` has one row.

---

## Stretch Goals

- Add a `--dry-run` flag that runs gap analysis and prints results without calling Claude for rewrite/cover letter
- Add a `--model` flag to switch between `claude-haiku-4-5` (fast/cheap) and `claude-opus-4-5` (best quality)
- Add a `list` command that prints `applications.csv` as a formatted table
- Add `status update` command that updates the status field in `applications.csv` for a given company/role

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | What you'll build |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and data flow |
| 03_GUIDE.md | ← you are here |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [src/solution.py](./src/solution.py) | Complete working solution |
| [04_RECAP.md](./04_RECAP.md) | What you built and what's next |

⬅️ **Prev:** [21 — Claude Mastery](../../21_Claude_Mastery/Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [23 — Codebase Review Agent](../23_Codebase_Review_Agent/01_MISSION.md)
