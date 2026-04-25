# Project 19 — Research Paper to Podcast Agent: Build Guide

**Format:** Partially Guided — each step explains what to build and how it fits. Partial code is provided for harder parts. Implement the gaps yourself before reading the solution.

**Time estimate:** 2–3 hours

---

## Before You Start

Create a `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
```

Install dependencies:

```bash
pip install anthropic pdfplumber requests gtts python-dotenv
```

Test gTTS works:

```python
from gtts import gTTS
tts = gTTS("Hello from the podcast agent.")
tts.save("test.mp3")
```

If `test.mp3` plays audio, you are ready.

---

## Step 1 — CLI and Configuration

**What to build:** An `argparse` CLI that accepts two mutually exclusive inputs:
- `--url` — an arXiv abstract or PDF URL
- `--pdf` — a local PDF file path

Also load your `ANTHROPIC_API_KEY` from `.env`.

The entry point should look like:

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a research paper to a podcast episode.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="arXiv URL (abstract or PDF)")
    group.add_argument("--pdf", help="Path to local PDF file")
    args = parser.parse_args()
    main(args)
```

**Your task:** Write the full import block and configuration loading. Make sure `main(args)` is called. You will implement `main()` in Step 9.

<details>
<summary>Hint: what imports does this project need?</summary>

```python
import os
import argparse
import io
from pathlib import Path

import anthropic
import pdfplumber
import requests
from gtts import gTTS
from dotenv import load_dotenv
```

</details>

---

## Step 2 — PDF Fetcher

**What to build:** A function `fetch_pdf(url: str) -> bytes` that downloads a PDF from a URL and returns raw bytes.

arXiv has a quirk: the abstract page URL (`/abs/`) does not serve a PDF. You need to convert it to `/pdf/`.

```python
def fetch_pdf(url: str) -> bytes:
    # If the URL is an abstract page, convert to PDF URL
    if "/abs/" in url:
        url = url.replace("/abs/", "/pdf/")
    if not url.endswith(".pdf"):
        url = url + ".pdf"
    # ...
```

**Your task:** Complete the function. Use `requests.get()` with a browser-like `User-Agent` header (arXiv rate-limits bots). Raise an informative error if the download fails. Return `response.content`.

<details>
<summary>Hint: arXiv rejects requests without a User-Agent</summary>

```python
headers = {"User-Agent": "Mozilla/5.0 (research-podcast-agent/1.0)"}
resp = requests.get(url, headers=headers, timeout=30)
resp.raise_for_status()
return resp.content
```

</details>

---

## Step 3 — Text Extractor

**What to build:** A function `extract_text(pdf_bytes: bytes) -> dict` that reads a PDF and returns a structured dict with `title`, `abstract`, and `sections`.

Use `pdfplumber` to extract text page by page. The key insight: the first page almost always contains the title and abstract. Section headers are usually short lines in ALL CAPS or followed by a number (e.g., `1 Introduction`).

```python
def extract_text(pdf_bytes: bytes) -> dict:
    result = {"title": "", "abstract": "", "sections": []}
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # TODO: extract title from first non-empty line
    # TODO: extract abstract (text between "Abstract" and next section header)
    # TODO: collect remaining text as sections
    return result
```

**Your task:** Implement the three extraction steps. You do not need perfect section parsing — a rough extraction of the first 8000 characters is sufficient for Claude to understand the paper.

<details>
<summary>Hint: simple abstract extraction</summary>

Look for the word "Abstract" in the text and take everything between it and the next empty line or section header:

```python
lines = full_text.split("\n")
abstract_lines = []
in_abstract = False
for line in lines:
    if "abstract" in line.lower():
        in_abstract = True
        continue
    if in_abstract:
        if line.strip() == "" and abstract_lines:
            break
        abstract_lines.append(line.strip())
result["abstract"] = " ".join(abstract_lines)
```

</details>

---

## Step 4 — Content Truncator

**What to build:** A function `prepare_content(extracted: dict, max_chars: int = 8000) -> str` that formats the extracted text into a single string and truncates it to fit Claude's context.

Why truncate? Long papers can have 30,000+ characters. Claude's context can handle it, but a 5-minute podcast script only needs the key ideas — abstract, introduction, conclusions. Truncating to 8000 characters keeps costs low and outputs focused.

**Your task:** Format the dict into:

```
TITLE: {title}

ABSTRACT:
{abstract}

CONTENT:
{sections text — truncated to remaining chars}
```

Truncate the sections portion so the total does not exceed `max_chars`.

---

## Step 5 — Podcast Script Generator

**What to build:** A function `generate_podcast_script(content: str, client: anthropic.Anthropic) -> str` that calls Claude and returns a podcast script.

The script should sound like a real podcast host. The key prompt elements:
- Persona: enthusiastic science communicator (think Lex Fridman or 99% Invisible)
- Target length: 5 minutes of speaking = roughly 700–850 words
- Style: conversational, uses analogies, explains jargon, speaks directly to listener
- Structure: hook → background → what the paper does → key findings → why it matters → closing

```python
def generate_podcast_script(content: str, client: anthropic.Anthropic) -> str:
    system_prompt = """You are an engaging science podcast host who explains research to curious non-specialists.
Write a 5-minute podcast episode script (700-850 words) based on the paper content provided.

Structure:
1. Hook (1-2 sentences that make the listener curious)
2. Background (what problem does this solve?)
3. The paper's approach (what did the researchers do?)
4. Key findings (what did they discover?)
5. Why it matters (real-world implications)
6. Closing (one memorable takeaway)

Rules:
- Use analogies to explain technical concepts
- No bullet points — flowing prose only
- Speak directly to the listener ("you", "imagine")
- Define any jargon in plain English immediately after using it
- Keep sentences short and conversational"""

    # TODO: call client.messages.create() and return the script text
    pass
```

**Your task:** Complete the function. Use `claude-haiku-4-5` with `max_tokens=1200`.

---

## Step 6 — Key Points Generator

**What to build:** A function `generate_key_points(content: str, client: anthropic.Anthropic) -> str` that returns 5 concise bullet takeaways.

This is a second, separate Claude call. The prompt should ask for:
- Exactly 5 bullet points
- Each bullet: one bold term + 1–2 sentence explanation
- Written for an engineer who skimmed the abstract

**Your task:** Write the full function. Use the same model. Target `max_tokens=600`.

<details>
<summary>Hint: system prompt structure</summary>

```python
system_prompt = """You are a research analyst. Extract exactly 5 key takeaways from this paper.

Format each as:
- **[Key term or concept]**: [1-2 sentence plain English explanation of why it matters]

Focus on: core contribution, key finding, method, limitation, and practical implication."""
```

</details>

---

## Step 7 — TTS Converter

**What to build:** A function `convert_to_audio(script: str, output_path: Path) -> None` that takes the podcast script and saves it as an `.mp3`.

gTTS is simple: pass text and a language code, call `.save(path)`.

```python
from gtts import gTTS

def convert_to_audio(script: str, output_path: Path) -> None:
    # TODO: create a gTTS object with lang="en"
    # TODO: save to output_path
    # TODO: print a confirmation message
    pass
```

**Practical note:** gTTS has a soft limit on text length per request. For long scripts (>2000 chars), split by sentences and concatenate with `pydub`. For this project, a single gTTS call works fine for 800-word scripts.

<details>
<summary>Hint: gTTS has a character limit per request</summary>

If you hit gTTS errors on long text, split by paragraph:

```python
from gtts import gTTS
import io

def convert_to_audio(script: str, output_path: Path) -> None:
    tts = gTTS(text=script, lang="en", slow=False)
    tts.save(str(output_path))
```

For most 800-word scripts, a single call is fine.

</details>

---

## Step 8 — Output Writers

**What to build:** A function `write_outputs(script: str, key_points: str, audio_path: Path, output_dir: Path) -> None` that writes:
- `transcript.md` — the podcast script formatted as markdown
- `key_points.md` — the key points formatted as markdown

Both files should include the generation timestamp and the paper source.

**Your task:** Write this function. Use `pathlib.Path` for clean file writing.

---

## Step 9 — Main Orchestrator

**What to build:** The `main(args)` function that wires together all previous functions in order.

The flow is:

```
args.url → fetch_pdf() → extract_text() → prepare_content()
args.pdf → read bytes  ↗                       ↓
                               generate_podcast_script()  → convert_to_audio()
                               generate_key_points()      → key_points.md
                                                           → transcript.md
```

Handle the two input modes (URL vs local file) in a single `if/else` block at the start.

<details>
<summary>Hint: reading a local PDF into bytes</summary>

```python
if args.pdf:
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"File not found: {args.pdf}")
        return
    pdf_bytes = pdf_path.read_bytes()
else:
    print(f"Downloading: {args.url}")
    pdf_bytes = fetch_pdf(args.url)
```

</details>

<details>
<summary>Hint: full orchestration order</summary>

```python
def main(args):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    output_dir = Path(__file__).parent.parent

    # 1. Get PDF bytes
    if args.pdf:
        pdf_bytes = Path(args.pdf).read_bytes()
    else:
        pdf_bytes = fetch_pdf(args.url)

    # 2. Extract text
    extracted = extract_text(pdf_bytes)
    content = prepare_content(extracted)

    # 3. Generate script and key points
    script = generate_podcast_script(content, client)
    key_points = generate_key_points(content, client)

    # 4. Convert to audio
    audio_path = output_dir / "podcast_summary.mp3"
    convert_to_audio(script, audio_path)

    # 5. Write text outputs
    write_outputs(script, key_points, audio_path, output_dir)
    print("Done.")
```

</details>

---

## Testing

```bash
# Test with a famous paper
python src/solution.py --url https://arxiv.org/abs/1706.03762

# Test with a local PDF
python src/solution.py --pdf /path/to/paper.pdf
```

Check the output directory for `podcast_summary.mp3`, `transcript.md`, and `key_points.md`.

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System diagram |
| **03_GUIDE.md** | ← you are here |
| [04_RECAP.md](./04_RECAP.md) | Recap and extensions |
