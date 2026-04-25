"""
Project 22 — AI Job Application Agent
Complete working solution.

Usage:
    python solution.py --jd "https://jobs.example.com/sr-ml-engineer" \
                       --resume resume.pdf \
                       --company "Acme Corp" \
                       --role "Senior ML Engineer"

    python solution.py --jd "paste job description here" \
                       --resume resume.md \
                       --company "Acme Corp" \
                       --role "Senior ML Engineer"

Requirements:
    pip install anthropic pdfplumber requests beautifulsoup4 python-dotenv
    ANTHROPIC_API_KEY in .env
"""

import os
import sys
import json
import csv
import argparse
from datetime import date
from typing import Optional
from dotenv import load_dotenv
import anthropic

# Optional imports — gracefully handled if not installed
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SUPPORT = True
except ImportError:
    WEB_SUPPORT = False

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-opus-4-5"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# INGESTION
# ---------------------------------------------------------------------------

def ingest_jd(source: str) -> str:
    """Fetch JD from URL or return pasted text. Truncated to 4000 chars."""
    if source.startswith("http"):
        if not WEB_SUPPORT:
            raise ImportError("requests and beautifulsoup4 are required for URL ingestion.")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(source, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove script/style noise
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            # Collapse multiple spaces
            import re
            text = re.sub(r"\s+", " ", text).strip()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch JD from URL: {e}")
    else:
        text = source.strip()

    if len(text) < 100:
        raise ValueError("JD text is too short. Check your source.")

    return text[:4000]


def ingest_resume(path: str) -> str:
    """Read a PDF or Markdown resume file. Returns raw text."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Resume not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        if not PDF_SUPPORT:
            raise ImportError("pdfplumber is required for PDF resumes: pip install pdfplumber")
        pages = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        return "\n\n".join(pages)

    elif ext in (".md", ".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError(f"Unsupported resume format: {ext}. Use .pdf, .md, or .txt")


# ---------------------------------------------------------------------------
# PARSING
# ---------------------------------------------------------------------------

def _call_claude_for_json(prompt: str, default: dict) -> dict:
    """Call Claude and parse JSON from the response. Return default on failure."""
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"      Warning: Claude returned non-JSON response ({e}). Using defaults.")
        return default
    except Exception as e:
        print(f"      Warning: API call failed ({e}). Using defaults.")
        return default


def parse_jd(jd_text: str) -> dict:
    """Extract structured data from a job description."""
    default = {
        "required_skills": [],
        "nice_to_have": [],
        "role_level": "Mid",
        "culture_signals": [],
        "summary": "Role information could not be parsed.",
    }

    prompt = f"""Analyze this job description and return ONLY valid JSON with these exact keys:
- required_skills: list of strings (technical and non-technical requirements marked as required/must-have)
- nice_to_have: list of strings (preferred/bonus skills)
- role_level: one of ["Junior", "Mid", "Senior", "Staff", "Principal", "Director"]
- culture_signals: list of up to 5 short strings that reveal company values or work style
- summary: 2-sentence plain English description of the role

<job_description>
{jd_text}
</job_description>

Return only the JSON object. No markdown code fences. No explanation."""

    return _call_claude_for_json(prompt, default)


def parse_resume(resume_text: str) -> dict:
    """Extract structured data from a resume."""
    default = {
        "skills": [],
        "current_role": "Unknown",
        "years_experience": 0,
        "roles": [],
        "projects": [],
        "summary": "",
    }

    prompt = f"""Analyze this resume and return ONLY valid JSON with these exact keys:
- skills: list of strings (every technical and soft skill mentioned anywhere)
- current_role: string (most recent job title)
- years_experience: integer (approximate total professional years)
- roles: list of objects, each with: title (string), company (string), duration (string), bullets (list of strings)
- projects: list of strings (project names or short descriptions)
- summary: the existing summary/objective paragraph text, or empty string if none exists

<resume>
{resume_text}
</resume>

Return only the JSON object. No markdown code fences. No explanation."""

    return _call_claude_for_json(prompt, default)


# ---------------------------------------------------------------------------
# GAP ANALYSIS
# ---------------------------------------------------------------------------

def gap_analysis(jd_parsed: dict, resume_parsed: dict) -> dict:
    """
    Compare JD requirements against resume. Pure Python — no Claude needed.

    Strategy: substring matching (case-insensitive) across all resume skills.
    "PyTorch" in JD matches "pytorch", "pytorch/tensorflow" etc in resume.
    """
    resume_skills_raw = resume_parsed.get("skills", [])
    # Also include project descriptions and role bullets as skill evidence
    resume_text_pool = " ".join(
        resume_skills_raw
        + resume_parsed.get("projects", [])
        + [
            bullet
            for role in resume_parsed.get("roles", [])
            for bullet in role.get("bullets", [])
        ]
    ).lower()

    gaps = []
    strengths = []
    for skill in jd_parsed.get("required_skills", []):
        if skill.lower() in resume_text_pool:
            strengths.append(skill)
        else:
            gaps.append(skill)

    nice_to_have_gaps = []
    for skill in jd_parsed.get("nice_to_have", []):
        if skill.lower() not in resume_text_pool:
            nice_to_have_gaps.append(skill)

    return {
        "gaps": gaps,
        "strengths": strengths,
        "nice_to_have_gaps": nice_to_have_gaps,
    }


# ---------------------------------------------------------------------------
# GENERATION
# ---------------------------------------------------------------------------

def rewrite_resume(original_resume: str, jd_parsed: dict, gaps: dict) -> str:
    """Rewrite the resume to target the JD. Returns Markdown."""
    required_str = ", ".join(jd_parsed.get("required_skills", []))
    nice_str = ", ".join(jd_parsed.get("nice_to_have", []))
    level = jd_parsed.get("role_level", "")
    culture = ", ".join(jd_parsed.get("culture_signals", []))
    gap_str = ", ".join(gaps.get("gaps", []))
    strength_str = ", ".join(gaps.get("strengths", []))

    prompt = f"""You are an expert resume writer and ATS optimization specialist.
Rewrite the following resume to target this specific role.

<original_resume>
{original_resume}
</original_resume>

<jd_analysis>
Required skills: {required_str}
Nice-to-have: {nice_str}
Role level: {level}
Culture signals: {culture}
</jd_analysis>

<gap_analysis>
Skills to emphasize (present in resume): {strength_str}
Gaps (not clearly demonstrated in resume): {gap_str}
</gap_analysis>

Rules — follow all of them:
1. Rewrite the summary/objective section to lead with the top 2 required skills
2. Rewrite each experience bullet to front-load an impact metric, then a JD keyword, then the action
3. Do not add skills, companies, projects, or technologies not present in the original resume
4. Keep all dates, company names, and job titles exactly as they appear
5. Move the Skills section immediately after the Summary
6. Where a gap exists, find the closest analogous skill in the resume and frame it as evidence
7. Output the complete rewritten resume in clean Markdown

Produce only the resume. No preamble, no explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


def write_cover_letter(company: str, role: str,
                       jd_parsed: dict, resume_parsed: dict,
                       gaps: dict) -> str:
    """Write a 3-paragraph personalized cover letter. Returns Markdown."""
    culture = jd_parsed.get("culture_signals", ["innovation"])
    required = jd_parsed.get("required_skills", [])
    strengths = gaps.get("strengths", [])
    current_role = resume_parsed.get("current_role", "engineer")
    summary = resume_parsed.get("summary", "")

    prompt = f"""You are a career coach who writes compelling, concise cover letters.
Write a cover letter for this application. Three paragraphs only.

<role>
Company: {company}
Title: {role}
</role>

<jd_requirements>
Required skills: {", ".join(required[:6])}
Culture signals: {", ".join(culture)}
</jd_requirements>

<candidate>
Current role: {current_role}
Resume summary: {summary}
Top matching skills: {", ".join(strengths[:5])}
</candidate>

Structure — follow exactly:
Paragraph 1 (Hook, 2-3 sentences):
  Open with the single most compelling reason this candidate matches the role.
  Reference one specific JD requirement by name.
  Do not start with "I am writing to" or "I am excited".

Paragraph 2 (Evidence, 3-4 sentences):
  Give two concrete examples from the candidate's experience that demonstrate
  the top two required skills. Include a specific metric or outcome in each example.

Paragraph 3 (Close, 2-3 sentences):
  State why this company specifically. Reference one culture signal.
  End with a clear, direct call to action.

Banned phrases: "I am excited", "I am passionate", "would be a great fit",
"opportunity to join", "I look forward to hearing from you"

Format the output as clean Markdown with a header line.
First line: # Cover Letter — {role} at {company}
Second line: **Date:** {date.today().isoformat()}
Then a blank line before Paragraph 1.

Produce only the cover letter. No explanation."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

def log_application(company: str, role: str, jd_source: str,
                    resume_output_path: str) -> None:
    """Append one row to applications.csv. Creates file with header if needed."""
    fieldnames = [
        "company", "role", "date_applied", "status",
        "jd_url", "tailored_resume_path", "notes"
    ]
    csv_path = "applications.csv"
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
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


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def run(jd_source: str, resume_path: str, company: str, role: str) -> None:
    print("\nJob Application Agent")
    print("=" * 40)

    print("[1/6] Ingesting job description...")
    jd_text = ingest_jd(jd_source)
    print(f"      {len(jd_text)} characters extracted.")

    print("[2/6] Ingesting resume...")
    resume_text = ingest_resume(resume_path)
    print(f"      {len(resume_text)} characters extracted.")

    print("[3/6] Parsing JD with Claude...")
    jd_parsed = parse_jd(jd_text)
    print(f"      Required skills: {', '.join(jd_parsed.get('required_skills', [])[:5])}")
    print(f"      Role level:       {jd_parsed.get('role_level', 'Unknown')}")
    print(f"      Culture signals:  {', '.join(jd_parsed.get('culture_signals', [])[:3])}")

    print("[4/6] Parsing resume with Claude...")
    resume_parsed = parse_resume(resume_text)
    print(f"      Skills found: {len(resume_parsed.get('skills', []))}")
    print(f"      Current role: {resume_parsed.get('current_role', 'Unknown')}")

    print("[5/6] Running gap analysis...")
    gaps = gap_analysis(jd_parsed, resume_parsed)
    print(f"      Gaps:      {gaps.get('gaps', [])}")
    print(f"      Strengths: {gaps.get('strengths', [])}")

    print("[6/6] Generating tailored resume and cover letter...")
    rewritten = rewrite_resume(resume_text, jd_parsed, gaps)
    company_slug = company.replace(" ", "_").lower()
    resume_out = os.path.join(OUTPUT_DIR, f"tailored_resume_{company_slug}.md")
    with open(resume_out, "w", encoding="utf-8") as f:
        f.write(rewritten)
    print(f"      tailored_resume written -> {resume_out}")

    letter = write_cover_letter(company, role, jd_parsed, resume_parsed, gaps)
    letter_out = os.path.join(OUTPUT_DIR, f"cover_letter_{company_slug}.md")
    with open(letter_out, "w", encoding="utf-8") as f:
        f.write(letter)
    print(f"      cover_letter written -> {letter_out}")

    log_application(company, role, jd_source, resume_out)
    print("      applications.csv updated.")

    print(f"\nDone. 3 files ready in ./{OUTPUT_DIR}/")


def main():
    parser = argparse.ArgumentParser(description="AI Job Application Agent")
    parser.add_argument("--jd", required=True,
                        help="Job description URL or pasted text (quote it)")
    parser.add_argument("--resume", required=True,
                        help="Path to your resume (.pdf, .md, or .txt)")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--role", required=True, help="Role title")
    args = parser.parse_args()

    try:
        run(args.jd, args.resume, args.company, args.role)
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
