"""
Project 19 — Research Paper to Podcast Agent
Complete working solution.

Usage:
    python src/solution.py --url https://arxiv.org/abs/1706.03762
    python src/solution.py --pdf /path/to/paper.pdf

Required .env:
    ANTHROPIC_API_KEY   — Anthropic API key

Output files written to project root:
    podcast_summary.mp3 — audio episode
    transcript.md       — full podcast script
    key_points.md       — 5 key takeaways
"""

import os
import argparse
import io
import datetime
from pathlib import Path

import anthropic
import pdfplumber
import requests
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
BASE_DIR = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# PDF Fetcher
# ---------------------------------------------------------------------------

def fetch_pdf(url: str) -> bytes:
    """Download a PDF from arXiv or any direct PDF URL. Returns raw bytes."""
    # Convert arXiv abstract page to direct PDF URL
    if "/abs/" in url:
        url = url.replace("/abs/", "/pdf/")
    if not url.endswith(".pdf"):
        url = url + ".pdf"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; research-podcast-agent/1.0; "
            "+https://github.com/AI-ENGINEERS-ATLAS)"
        )
    }
    print(f"Downloading PDF: {url}")
    resp = requests.get(url, headers=headers, timeout=60)
    resp.raise_for_status()

    if "application/pdf" not in resp.headers.get("Content-Type", ""):
        # arXiv sometimes redirects — content is still valid, proceed anyway
        pass

    print(f"Downloaded {len(resp.content) / 1024:.1f} KB")
    return resp.content


# ---------------------------------------------------------------------------
# Text Extractor
# ---------------------------------------------------------------------------

def extract_text(pdf_bytes: bytes) -> dict:
    """Extract title, abstract, and body text from PDF bytes."""
    result = {"title": "", "abstract": "", "sections": ""}

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages_text = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        full_text = "\n".join(pages_text)

    if not full_text.strip():
        result["sections"] = "Could not extract text from this PDF."
        return result

    lines = full_text.split("\n")

    # Title: first non-empty, non-number line
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.isdigit() and len(stripped) > 10:
            result["title"] = stripped
            break

    # Abstract: extract between 'abstract' keyword and next section marker
    abstract_lines = []
    in_abstract = False
    for line in lines:
        lower = line.strip().lower()
        if lower in ("abstract", "abstract.") or lower.startswith("abstract—") or lower.startswith("abstract:"):
            in_abstract = True
            # If the keyword line contains content after it, capture it
            content_after = line.strip()
            for prefix in ["abstract—", "abstract:", "abstract."]:
                if content_after.lower().startswith(prefix):
                    content_after = content_after[len(prefix):].strip()
                    if content_after:
                        abstract_lines.append(content_after)
            continue
        if in_abstract:
            # Stop at next section header (numbered or all-caps short line)
            stripped = line.strip()
            if stripped and (
                (stripped[0].isdigit() and len(stripped.split()) <= 5)
                or (stripped.isupper() and len(stripped) < 40)
                or lower in ("introduction", "1 introduction", "1. introduction")
            ):
                break
            if stripped:
                abstract_lines.append(stripped)

    result["abstract"] = " ".join(abstract_lines)

    # Sections: everything after the abstract
    abstract_end_idx = 0
    if abstract_lines:
        for i, line in enumerate(lines):
            if abstract_lines[-1] in line:
                abstract_end_idx = i
                break

    remaining_lines = lines[abstract_end_idx + 1 :]
    result["sections"] = "\n".join(remaining_lines)

    return result


# ---------------------------------------------------------------------------
# Content Truncator
# ---------------------------------------------------------------------------

def prepare_content(extracted: dict, max_chars: int = 8000) -> str:
    """Format extracted paper content into a truncated string for Claude."""
    header = (
        f"TITLE: {extracted.get('title', 'Unknown Title')}\n\n"
        f"ABSTRACT:\n{extracted.get('abstract', 'No abstract found.')}\n\n"
        f"CONTENT:\n"
    )

    remaining_chars = max_chars - len(header)
    sections_text = extracted.get("sections", "")

    if len(sections_text) > remaining_chars:
        sections_text = sections_text[:remaining_chars] + "\n\n[... paper truncated for brevity ...]"

    return header + sections_text


# ---------------------------------------------------------------------------
# Podcast Script Generator
# ---------------------------------------------------------------------------

def generate_podcast_script(content: str, client: anthropic.Anthropic) -> str:
    """Call Claude to generate a 5-minute conversational podcast script."""
    system_prompt = """You are an engaging science podcast host who explains research papers to curious non-specialists.
Think of yourself as Lex Fridman meets 99% Invisible — you find the human story in technical work.

Write a 5-minute podcast episode script (700-850 words) based on the paper content provided.

Structure your episode:
1. Hook (1-2 sentences that make the listener genuinely curious)
2. Background (what problem or gap does this paper address?)
3. The approach (what did the researchers do, explained with an analogy)
4. Key findings (what did they discover or prove?)
5. Why it matters (real-world implications or what changes because of this)
6. Closing (one memorable sentence the listener will remember)

Style rules:
- Write flowing prose, no bullet points or section headers in the script
- Use at least one strong analogy to explain the core technical concept
- Speak directly to the listener using "you" and "imagine"
- Define any technical jargon in plain English immediately after using it
- Keep sentences punchy and conversational
- Write as a monologue — one host speaking directly to the audience"""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1200,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Please write a podcast episode based on this paper:\n\n{content}",
            }
        ],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Key Points Generator
# ---------------------------------------------------------------------------

def generate_key_points(content: str, client: anthropic.Anthropic) -> str:
    """Call Claude to extract 5 key takeaways from the paper."""
    system_prompt = """You are a research analyst who reads papers and extracts the most important insights for engineers.

Extract exactly 5 key takeaways from this paper. Format each as:
- **[Key concept or term]**: [1-2 sentence plain English explanation of what it means and why it matters]

Cover these five angles:
1. Core contribution (what is new or different about this work)
2. Key technical finding (the main result or discovery)
3. Method or technique (how they achieved this)
4. Limitation (what this approach does not solve)
5. Practical implication (what engineers or practitioners can do with this knowledge)

Write for an engineer who skimmed the abstract and wants to know if they should read the full paper."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Extract 5 key takeaways from this paper:\n\n{content}",
            }
        ],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# TTS Converter
# ---------------------------------------------------------------------------

def convert_to_audio(script: str, output_path: Path) -> None:
    """Convert the podcast script to an mp3 file using gTTS."""
    print("Converting script to audio (gTTS)...")
    tts = gTTS(text=script, lang="en", slow=False)
    tts.save(str(output_path))
    size_kb = output_path.stat().st_size / 1024
    print(f"Audio saved: {output_path} ({size_kb:.1f} KB)")


# ---------------------------------------------------------------------------
# Output Writers
# ---------------------------------------------------------------------------

def write_outputs(
    script: str,
    key_points: str,
    title: str,
    audio_path: Path,
    output_dir: Path,
) -> None:
    """Write transcript.md and key_points.md to the output directory."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # transcript.md
    transcript_path = output_dir / "transcript.md"
    transcript_content = (
        f"# Podcast Transcript\n\n"
        f"**Paper:** {title}\n"
        f"**Generated:** {timestamp}\n\n"
        f"---\n\n"
        f"{script}\n"
    )
    with open(transcript_path, "w") as f:
        f.write(transcript_content)
    print(f"Transcript saved: {transcript_path}")

    # key_points.md
    key_points_path = output_dir / "key_points.md"
    key_points_content = (
        f"# Key Points\n\n"
        f"**Paper:** {title}\n"
        f"**Generated:** {timestamp}\n\n"
        f"---\n\n"
        f"{key_points}\n"
    )
    with open(key_points_path, "w") as f:
        f.write(key_points_content)
    print(f"Key points saved: {key_points_path}")


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------

def main(args) -> None:
    """Orchestrate the full paper-to-podcast pipeline."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Step 1: Get PDF bytes
    if args.pdf:
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            print(f"Error: File not found: {args.pdf}")
            return
        print(f"Reading local PDF: {pdf_path}")
        pdf_bytes = pdf_path.read_bytes()
    else:
        pdf_bytes = fetch_pdf(args.url)

    # Step 2: Extract and prepare content
    print("Extracting text from PDF...")
    extracted = extract_text(pdf_bytes)
    content = prepare_content(extracted)

    title = extracted.get("title", "Research Paper")
    print(f"Title detected: {title[:80]}...")
    print(f"Abstract length: {len(extracted.get('abstract', ''))} chars")
    print(f"Content prepared: {len(content)} chars (truncated to 8000)")

    # Step 3: Generate script and key points
    print("\nGenerating podcast script via Claude...")
    script = generate_podcast_script(content, client)
    print(f"Script generated: {len(script.split())} words")

    print("Generating key points via Claude...")
    key_points = generate_key_points(content, client)

    # Step 4: Convert to audio
    audio_path = BASE_DIR / "podcast_summary.mp3"
    convert_to_audio(script, audio_path)

    # Step 5: Write text outputs
    write_outputs(script, key_points, title, audio_path, BASE_DIR)

    print("\n--- Complete ---")
    print(f"  Audio:       {audio_path}")
    print(f"  Transcript:  {BASE_DIR / 'transcript.md'}")
    print(f"  Key points:  {BASE_DIR / 'key_points.md'}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a research paper to a podcast episode."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="arXiv URL (abstract or direct PDF link)")
    group.add_argument("--pdf", help="Path to a local PDF file")
    args = parser.parse_args()
    main(args)
