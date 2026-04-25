"""
Project 19 — Research Paper to Podcast Agent
Starter skeleton — fill in the TODO sections to complete the project.

Usage:
    python src/starter.py --url https://arxiv.org/abs/1706.03762
    python src/starter.py --pdf /path/to/paper.pdf
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
# Step 2 — PDF Fetcher
# ---------------------------------------------------------------------------

def fetch_pdf(url: str) -> bytes:
    """
    Download a PDF from a URL and return raw bytes.

    - Convert arXiv abstract URLs (/abs/) to PDF URLs (/pdf/)
    - Add a User-Agent header (arXiv blocks plain requests)
    - Raise a clear error if download fails

    TODO: implement this function
    """
    # TODO: convert /abs/ to /pdf/ in the URL
    # TODO: add .pdf extension if missing
    # TODO: use requests.get() with headers={"User-Agent": "..."} and timeout=30
    # TODO: raise_for_status() and return response.content
    pass


# ---------------------------------------------------------------------------
# Step 3 — Text Extractor
# ---------------------------------------------------------------------------

def extract_text(pdf_bytes: bytes) -> dict:
    """
    Extract title, abstract, and body text from a PDF.

    Returns:
        {
            "title": str,
            "abstract": str,
            "sections": str   # remaining body text
        }

    Use pdfplumber.open(io.BytesIO(pdf_bytes)) to open the PDF.

    TODO: implement this function
    """
    result = {"title": "", "abstract": "", "sections": ""}
    # TODO: open PDF with pdfplumber, extract text page by page
    # TODO: attempt to extract title from first non-empty line
    # TODO: extract abstract (text between 'Abstract' keyword and next section)
    # TODO: collect remaining text as sections
    return result


# ---------------------------------------------------------------------------
# Step 4 — Content Truncator
# ---------------------------------------------------------------------------

def prepare_content(extracted: dict, max_chars: int = 8000) -> str:
    """
    Format extracted text into a single string and truncate to max_chars.

    Format:
        TITLE: {title}

        ABSTRACT:
        {abstract}

        CONTENT:
        {sections — truncated to fit remaining chars}

    TODO: implement this function
    """
    # TODO: build header string with title and abstract
    # TODO: compute remaining chars for sections
    # TODO: truncate sections and assemble final string
    pass


# ---------------------------------------------------------------------------
# Step 5 — Podcast Script Generator
# ---------------------------------------------------------------------------

def generate_podcast_script(content: str, client: anthropic.Anthropic) -> str:
    """
    Call Claude to generate a 5-minute podcast script (700-850 words).

    System prompt should ask for:
    - Hook, background, approach, findings, implications, closing
    - Conversational prose (no bullet points)
    - Analogies for technical concepts
    - Direct address to listener ("you", "imagine")

    Use model: claude-haiku-4-5, max_tokens=1200

    TODO: implement this function
    """
    # TODO: write system prompt
    # TODO: call client.messages.create()
    # TODO: return message.content[0].text
    pass


# ---------------------------------------------------------------------------
# Step 6 — Key Points Generator
# ---------------------------------------------------------------------------

def generate_key_points(content: str, client: anthropic.Anthropic) -> str:
    """
    Call Claude to generate 5 key takeaways from the paper.

    Each point: **Bold term**: 1-2 sentence plain English explanation.
    Focus on: core contribution, key finding, method, limitation, implication.

    Use model: claude-haiku-4-5, max_tokens=600

    TODO: implement this function
    """
    # TODO: write focused system prompt for key points extraction
    # TODO: call client.messages.create()
    # TODO: return the text
    pass


# ---------------------------------------------------------------------------
# Step 7 — TTS Converter
# ---------------------------------------------------------------------------

def convert_to_audio(script: str, output_path: Path) -> None:
    """
    Convert the podcast script to an mp3 file using gTTS.

    TODO: implement this function
    """
    # TODO: create gTTS(text=script, lang="en", slow=False)
    # TODO: call tts.save(str(output_path))
    # TODO: print confirmation
    pass


# ---------------------------------------------------------------------------
# Step 8 — Output Writers
# ---------------------------------------------------------------------------

def write_outputs(script: str, key_points: str, audio_path: Path, output_dir: Path) -> None:
    """
    Write transcript.md and key_points.md to output_dir.

    Both files should include a generation timestamp.

    TODO: implement this function
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # TODO: write transcript.md with script content
    # TODO: write key_points.md with key points content
    # TODO: print paths of all written files
    pass


# ---------------------------------------------------------------------------
# Step 9 — Main Orchestrator
# ---------------------------------------------------------------------------

def main(args) -> None:
    """
    Orchestrate the full pipeline:
    1. Get PDF bytes (from URL or local file)
    2. Extract and prepare content
    3. Generate podcast script and key points via Claude
    4. Convert script to audio
    5. Write all output files

    TODO: implement this function
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # TODO: handle args.url vs args.pdf to get pdf_bytes
    # TODO: call extract_text() then prepare_content()
    # TODO: call generate_podcast_script() and generate_key_points()
    # TODO: call convert_to_audio() and write_outputs()
    pass


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
