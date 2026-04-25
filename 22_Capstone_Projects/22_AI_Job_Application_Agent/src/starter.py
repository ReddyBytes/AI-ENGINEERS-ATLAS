"""
Project 22 — AI Job Application Agent
Starter code with TODOs

Fill in every TODO block. Run: python starter.py
"""

import os
import json
import csv
from datetime import date
from dotenv import load_dotenv
import anthropic

load_dotenv()

# TODO 1: Initialize the Anthropic client using your API key from .env
client = None  # Replace with real client

MODEL = "claude-opus-4-5"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# INGESTION
# ---------------------------------------------------------------------------

def ingest_jd(source: str) -> str:
    """
    Accept a URL or raw text. Return the JD as a plain text string.

    TODO 2:
    - If source starts with "http", use requests.get() to fetch the page.
      Parse HTML with BeautifulSoup and extract body text.
    - Otherwise return source directly.
    - Truncate to 4000 chars.
    """
    # HINT: from bs4 import BeautifulSoup; import requests
    pass


def ingest_resume(path: str) -> str:
    """
    Read a PDF or Markdown resume and return its text content.

    TODO 3:
    - If path ends in .pdf, use pdfplumber to extract all pages.
    - If path ends in .md or .txt, read directly.
    - Raise ValueError for unsupported formats.
    """
    pass


# ---------------------------------------------------------------------------
# PARSING (Claude calls)
# ---------------------------------------------------------------------------

def parse_jd(jd_text: str) -> dict:
    """
    Use Claude to extract structured data from the JD.

    TODO 4:
    Return a dict with keys:
      required_skills, nice_to_have, role_level, culture_signals, summary

    Prompt Claude to return valid JSON. Parse with json.loads().
    Handle JSON parse errors gracefully — return a safe default dict.
    """
    prompt = f"""Analyze this job description and return ONLY valid JSON with these exact keys:
- required_skills: list of strings
- nice_to_have: list of strings
- role_level: one of ["Junior", "Mid", "Senior", "Staff", "Principal", "Director"]
- culture_signals: list of strings
- summary: 2-sentence plain English description

<job_description>
{jd_text}
</job_description>

Return only the JSON object. No markdown, no explanation."""

    # TODO: call client.messages.create() and return parsed dict
    pass


def parse_resume(resume_text: str) -> dict:
    """
    Use Claude to extract structured data from the resume.

    TODO 5:
    Return a dict with keys:
      skills, current_role, years_experience, roles, projects, summary

    Same pattern as parse_jd().
    """
    prompt = f"""Analyze this resume and return ONLY valid JSON with these exact keys:
- skills: list of strings (all technical and soft skills)
- current_role: string (most recent job title)
- years_experience: integer (approximate total years)
- roles: list of objects, each with: title, company, duration, bullets (list of strings)
- projects: list of strings
- summary: existing summary paragraph or empty string if none

<resume>
{resume_text}
</resume>

Return only the JSON object. No markdown, no explanation."""

    # TODO: call client.messages.create() and return parsed dict
    pass


# ---------------------------------------------------------------------------
# GAP ANALYSIS (pure Python, no Claude)
# ---------------------------------------------------------------------------

def gap_analysis(jd_parsed: dict, resume_parsed: dict) -> dict:
    """
    Compare JD requirements against resume skills.

    TODO 6:
    - Build a lowercased set of all resume skills.
    - For each required_skill in jd_parsed, check if any resume skill contains it
      as a substring (case-insensitive).
    - Separate into: gaps (missing), strengths (present).
    - Also check nice_to_have skills for gaps.

    Return:
      {"gaps": [...], "strengths": [...], "nice_to_have_gaps": [...]}
    """
    pass


# ---------------------------------------------------------------------------
# GENERATION (Claude calls)
# ---------------------------------------------------------------------------

def rewrite_resume(original_resume: str, jd_parsed: dict, gaps: dict) -> str:
    """
    Rewrite the resume to target the JD. Return Markdown string.

    TODO 7:
    Build a prompt that gives Claude:
    - The original resume
    - JD required skills, nice-to-have, role level, culture signals
    - Gaps and strengths from gap analysis

    Rules to include in the prompt:
    1. Rewrite the summary to lead with top 2 JD requirements
    2. Rewrite bullet points to front-load impact + JD keywords
    3. Do not fabricate skills, companies, or roles
    4. Keep all dates and company names unchanged
    5. Output complete resume in Markdown
    """
    pass


def write_cover_letter(company: str, role: str,
                       jd_parsed: dict, resume_parsed: dict,
                       gaps: dict) -> str:
    """
    Write a 3-paragraph personalized cover letter. Return Markdown string.

    TODO 8:
    Three paragraphs:
    - Paragraph 1 (Hook): Most compelling match, reference a specific JD requirement
    - Paragraph 2 (Evidence): Two concrete examples from experience
    - Paragraph 3 (Close): Why this company — reference a culture signal. CTA.

    Banned phrases: "I am excited", "I am passionate", "would be a great fit"
    """
    pass


# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

def log_application(company: str, role: str, jd_source: str,
                    resume_output_path: str) -> None:
    """
    Append one row to applications.csv.

    TODO 9:
    Fields: company, role, date_applied, status, jd_url, tailored_resume_path, notes
    Create the file with header if it does not exist.
    """
    pass


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
    print(f"      Role level: {jd_parsed.get('role_level', 'Unknown')}")

    print("[4/6] Parsing resume with Claude...")
    resume_parsed = parse_resume(resume_text)
    print(f"      Skills found: {len(resume_parsed.get('skills', []))}")

    print("[5/6] Running gap analysis...")
    gaps = gap_analysis(jd_parsed, resume_parsed)
    print(f"      Gaps: {gaps.get('gaps', [])}")
    print(f"      Strengths: {gaps.get('strengths', [])}")

    print("[6/6] Generating tailored resume and cover letter...")
    rewritten = rewrite_resume(resume_text, jd_parsed, gaps)
    resume_out = os.path.join(OUTPUT_DIR, f"tailored_resume_{company.replace(' ', '_').lower()}.md")
    with open(resume_out, "w") as f:
        f.write(rewritten)

    letter = write_cover_letter(company, role, jd_parsed, resume_parsed, gaps)
    letter_out = os.path.join(OUTPUT_DIR, f"cover_letter_{company.replace(' ', '_').lower()}.md")
    with open(letter_out, "w") as f:
        f.write(letter)

    log_application(company, role, jd_source, resume_out)

    print(f"\nDone. Files written to ./{OUTPUT_DIR}/")
    print(f"  - {resume_out}")
    print(f"  - {letter_out}")
    print("  - applications.csv (updated)")


if __name__ == "__main__":
    # Replace these with real paths before running
    JD_SOURCE = "paste your job description here or enter a URL"
    RESUME_PATH = "path/to/your/resume.pdf"  # or .md
    COMPANY = "Example Corp"
    ROLE = "Senior Engineer"

    run(JD_SOURCE, RESUME_PATH, COMPANY, ROLE)
