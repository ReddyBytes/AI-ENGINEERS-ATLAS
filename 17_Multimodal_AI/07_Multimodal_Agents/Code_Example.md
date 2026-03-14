# Multimodal Agents — Code Examples

## Example 1: Screen Reader Agent (Perception Only)

```python
"""
screen_reader.py — Use Claude to describe and analyze a screenshot
pip install anthropic pillow mss
"""
import anthropic
import base64
from PIL import Image
import io


client = anthropic.Anthropic()


def capture_screenshot(scale: float = 0.5) -> tuple[str, str]:
    """
    Capture the current screen and encode as base64.
    Scales down to reduce token cost.
    """
    try:
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # All screens
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    except ImportError:
        # Fallback: create a sample image for demo
        img = Image.new("RGB", (800, 600), color=(240, 240, 240))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.text((100, 100), "Sample Screen", fill="black")
        draw.rectangle([200, 200, 600, 400], outline="black")
        draw.text((250, 290), "Submit Form", fill="black")

    # Resize for cost reduction
    new_width = int(img.width * scale)
    new_height = int(img.height * scale)
    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Encode to base64
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.standard_b64encode(buf.getvalue()).decode()

    return b64, "image/jpeg"


def describe_screen(screenshot_b64: str, media_type: str = "image/jpeg") -> str:
    """Ask Claude what it sees on the screen."""
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": screenshot_b64}
                },
                {
                    "type": "text",
                    "text": """Describe everything visible on this screen:
1. What application or interface is shown
2. List all visible text content
3. List all interactive elements (buttons, inputs, links, menus)
4. Describe the current state (loading, error, success, form, etc.)
5. What would a user likely want to do next?"""
                }
            ]
        }]
    )
    return response.content[0].text


def identify_actions(screenshot_b64: str, task: str) -> dict:
    """
    Given a task and screenshot, identify the next action to take.
    Returns structured action dict.
    """
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": screenshot_b64}
                },
                {
                    "type": "text",
                    "text": f"""Task: {task}

Looking at this screenshot, determine the single next action to take.
Respond as JSON with exactly this structure:
{{
  "observation": "what I see on screen",
  "reasoning": "why this is the next action",
  "action": "click|type|scroll|key|done",
  "element_description": "describe the element to interact with",
  "value": "text to type or key to press (if applicable)",
  "task_complete": false
}}

If the task is already complete, set action to "done" and task_complete to true."""
                }
            ]
        }]
    )

    import json
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])

    return json.loads(raw)


# Demo
if __name__ == "__main__":
    print("Capturing screen...")
    b64, mt = capture_screenshot(scale=0.6)

    print("\nDescribing screen:")
    description = describe_screen(b64, mt)
    print(description)

    print("\nIdentifying next action for a sample task:")
    action = identify_actions(b64, "Find and click the main action button on the screen")
    import json
    print(json.dumps(action, indent=2))
```

---

## Example 2: Web Page Analyzer

```python
"""
web_analyzer.py — Capture and analyze a web page using Playwright + Claude Vision
pip install playwright anthropic pillow
playwright install chromium
"""
import asyncio
import anthropic
import base64
import json
from pathlib import Path


client = anthropic.Anthropic()


async def capture_page(url: str, output_path: str = "/tmp/page.jpg") -> str:
    """Capture a screenshot of a web page using Playwright."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(url, wait_until="networkidle")
        await page.screenshot(path=output_path, type="jpeg", quality=80)
        await browser.close()

    return output_path


def analyze_page(screenshot_path: str, question: str) -> str:
    """Ask Claude a specific question about a captured web page."""
    with open(screenshot_path, "rb") as f:
        b64 = base64.standard_b64encode(f.read()).decode()

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": question}
            ]
        }]
    )
    return response.content[0].text


def extract_page_structure(screenshot_path: str) -> dict:
    """Extract structured data about a page's UI elements."""
    with open(screenshot_path, "rb") as f:
        b64 = base64.standard_b64encode(f.read()).decode()

    prompt = """Analyze this web page screenshot and extract its structure as JSON:
{
  "page_title": null,
  "main_heading": null,
  "navigation_items": [],
  "primary_cta": null,
  "form_fields": [],
  "main_content_summary": null,
  "visible_errors_or_warnings": []
}
Return ONLY the JSON."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
                {"type": "text", "text": prompt}
            ]
        }]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])
    return json.loads(raw)


# Usage
async def main():
    url = "https://example.com"
    print(f"Capturing: {url}")
    screenshot = await capture_page(url)

    print("\nAnalyzing page...")
    analysis = analyze_page(screenshot, "What is the main purpose of this page and what can a user do here?")
    print(analysis)

    print("\nExtracting structure...")
    structure = extract_page_structure(screenshot)
    print(json.dumps(structure, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Example 3: Minimal Voice Agent

```python
"""
voice_agent_minimal.py — Minimal STT → LLM → TTS voice loop
pip install openai anthropic sounddevice soundfile numpy
"""
import os
import tempfile
import time
from openai import OpenAI
import anthropic

openai_client = OpenAI()
anthropic_client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a helpful voice assistant.
Keep responses concise (2-3 sentences max) and conversational.
You're being accessed via voice interface, so avoid using markdown, lists, or formatting."""

conversation_history = []


def transcribe(audio_bytes: bytes, format: str = "wav") -> str:
    """Convert audio bytes to text using Whisper."""
    with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as f:
        f.write(audio_bytes)
        temp_path = f.name

    try:
        with open(temp_path, "rb") as f:
            result = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        return str(result).strip()
    finally:
        os.unlink(temp_path)


def generate_response(user_text: str) -> str:
    """Generate LLM response maintaining conversation history."""
    conversation_history.append({"role": "user", "content": user_text})

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=conversation_history
    )

    assistant_text = response.content[0].text
    conversation_history.append({"role": "assistant", "content": assistant_text})

    # Keep history manageable (last 10 turns)
    if len(conversation_history) > 20:
        conversation_history[:] = conversation_history[-20:]

    return assistant_text


def text_to_speech(text: str) -> bytes:
    """Convert text to audio bytes using OpenAI TTS."""
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    return response.content


def voice_turn(audio_bytes: bytes) -> dict:
    """Process one turn: audio in → audio out."""
    start = time.time()

    # STT
    user_text = transcribe(audio_bytes)
    stt_time = time.time() - start
    print(f"User ({stt_time:.1f}s): {user_text}")

    if not user_text or user_text.lower() in ("", "you", "thank you", "bye"):
        return {"user_said": user_text, "agent_said": None, "audio": None}

    # LLM
    t2 = time.time()
    response_text = generate_response(user_text)
    llm_time = time.time() - t2
    print(f"Agent ({llm_time:.1f}s): {response_text}")

    # TTS
    t3 = time.time()
    audio_response = text_to_speech(response_text)
    tts_time = time.time() - t3

    total = time.time() - start
    print(f"Total latency: {total:.1f}s (STT={stt_time:.1f}s LLM={llm_time:.1f}s TTS={tts_time:.1f}s)")

    return {
        "user_said": user_text,
        "agent_said": response_text,
        "audio": audio_response,
        "latency_total": total
    }


# Demo with a pre-recorded audio file
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f:
            audio = f.read()
        result = voice_turn(audio)
        if result["audio"]:
            with open("response.mp3", "wb") as f:
                f.write(result["audio"])
            print(f"Response audio saved to response.mp3")
    else:
        print("Usage: python voice_agent_minimal.py <audio_file.wav>")
        print("Provide a .wav or .mp3 file as input for the voice agent to process.")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Architecture diagrams |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [06 — Multimodal Embeddings](../06_Multimodal_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Section 18 — AI Evaluation](../../18_AI_Evaluation/01_Evaluation_Fundamentals/Theory.md)
