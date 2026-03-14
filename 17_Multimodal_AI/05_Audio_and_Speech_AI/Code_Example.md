# Audio and Speech AI — Code Examples

## Example 1: Transcribe Audio with Whisper (Local)

```python
"""
whisper_local.py — Transcribe audio files using local Whisper model
pip install openai-whisper
"""
import whisper
from pathlib import Path

def transcribe_local(audio_path: str, model_size: str = "base") -> dict:
    """
    Transcribe audio using a local Whisper model.

    model_size: "tiny" | "base" | "small" | "medium" | "large"
    Returns dict with: text, language, segments (with timestamps)
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, word_timestamps=True)
    return result


def transcribe_with_timestamps(audio_path: str) -> list[dict]:
    """Return list of segments with start time, end time, and text."""
    result = transcribe_local(audio_path, model_size="base")
    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip(),
        })
    return segments


# Usage
if __name__ == "__main__":
    # Full transcription
    result = transcribe_local("meeting.mp3")
    print(f"Language detected: {result['language']}")
    print(f"Transcript:\n{result['text']}")

    print("\n--- Timestamped segments ---")
    segments = transcribe_with_timestamps("meeting.mp3")
    for seg in segments:
        print(f"[{seg['start']}s – {seg['end']}s] {seg['text']}")
```

---

## Example 2: Transcribe via OpenAI API (large-v3)

```python
"""
whisper_api.py — Transcribe using OpenAI Whisper API (large-v3 quality)
pip install openai
"""
from openai import OpenAI
from pathlib import Path

client = OpenAI()

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25MB limit


def transcribe_api(audio_path: str, language: str = None) -> str:
    """Transcribe audio using OpenAI Whisper API."""
    file_size = Path(audio_path).stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File too large ({file_size/1e6:.1f}MB). Max is 25MB. Split the audio first.")

    kwargs = {"model": "whisper-1", "response_format": "text"}
    if language:
        kwargs["language"] = language  # ISO 639-1 code, e.g., "en", "fr", "es"

    with open(audio_path, "rb") as f:
        return client.audio.transcriptions.create(file=f, **kwargs)


def transcribe_api_verbose(audio_path: str) -> dict:
    """Transcribe with full metadata including segments and timestamps."""
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment", "word"]
        )
    return result.model_dump()


def split_audio_and_transcribe(audio_path: str, chunk_duration_sec: int = 600) -> str:
    """Split a long audio file into chunks and transcribe each."""
    import subprocess
    import tempfile
    import os

    output_dir = tempfile.mkdtemp()
    chunks = []

    # Get audio duration using ffprobe
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True
    )
    duration = float(probe.stdout.strip())
    num_chunks = int(duration / chunk_duration_sec) + 1

    # Split into chunks
    for i in range(num_chunks):
        start = i * chunk_duration_sec
        output_path = os.path.join(output_dir, f"chunk_{i:04d}.mp3")
        subprocess.run([
            "ffmpeg", "-i", audio_path,
            "-ss", str(start), "-t", str(chunk_duration_sec),
            "-y", output_path
        ], capture_output=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            chunks.append(output_path)

    # Transcribe each chunk
    transcripts = []
    for chunk in chunks:
        text = transcribe_api(chunk)
        transcripts.append(text)

    return " ".join(transcripts)


# Usage
if __name__ == "__main__":
    # Simple transcription
    text = transcribe_api("audio.mp3")
    print(text)

    # With timestamps
    verbose = transcribe_api_verbose("audio.mp3")
    for segment in verbose.get("segments", []):
        print(f"[{segment['start']:.1f}s] {segment['text']}")
```

---

## Example 3: Text-to-Speech with OpenAI

```python
"""
openai_tts.py — Generate speech from text using OpenAI TTS
"""
from openai import OpenAI
from pathlib import Path

client = OpenAI()

VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]


def speak(text: str, output_path: str = "output.mp3", voice: str = "nova",
          model: str = "tts-1") -> str:
    """
    Convert text to speech and save to file.

    voice: alloy, echo, fable, onyx, nova, shimmer
    model: "tts-1" (fast) or "tts-1-hd" (higher quality)
    Returns: output file path
    """
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
    )
    response.stream_to_file(output_path)
    return output_path


def speak_streaming(text: str, output_path: str = "output.mp3") -> str:
    """Stream audio generation for lower latency on long texts."""
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="nova",
        input=text,
    ) as response:
        response.stream_to_file(output_path)
    return output_path


# Usage
if __name__ == "__main__":
    path = speak("Hello! This is a demonstration of text-to-speech using OpenAI's API.", voice="nova")
    print(f"Saved to: {path}")

    # Try all voices
    sample = "The quick brown fox jumps over the lazy dog."
    for voice in VOICES:
        out = speak(sample, output_path=f"voice_{voice}.mp3", voice=voice)
        print(f"Generated: {out}")
```

---

## Example 4: Simple Voice Agent Pipeline

```python
"""
voice_agent.py — STT → LLM → TTS voice agent
pip install openai openai-whisper sounddevice soundfile
"""
import anthropic
import base64
import tempfile
import os
from openai import OpenAI

openai_client = OpenAI()
anthropic_client = anthropic.Anthropic()

CONVERSATION_HISTORY = []


def transcribe(audio_path: str) -> str:
    """Audio file → text via Whisper API."""
    with open(audio_path, "rb") as f:
        result = openai_client.audio.transcriptions.create(
            model="whisper-1", file=f, response_format="text"
        )
    return result.strip()


def generate_response(user_text: str, system_prompt: str = "You are a helpful voice assistant. Keep your responses concise and conversational.") -> str:
    """Text → LLM response via Claude."""
    CONVERSATION_HISTORY.append({"role": "user", "content": user_text})

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,  # Keep short for voice
        system=system_prompt,
        messages=CONVERSATION_HISTORY
    )

    assistant_text = response.content[0].text
    CONVERSATION_HISTORY.append({"role": "assistant", "content": assistant_text})
    return assistant_text


def text_to_speech(text: str, output_path: str = None) -> str:
    """Text → audio file via OpenAI TTS."""
    if output_path is None:
        output_path = tempfile.mktemp(suffix=".mp3")

    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    response.stream_to_file(output_path)
    return output_path


def voice_turn(input_audio_path: str) -> dict:
    """
    Process one turn of the voice conversation.

    Returns dict with:
        user_said: transcribed text
        agent_said: LLM response text
        audio_path: path to TTS audio file
    """
    # Step 1: Transcribe user speech
    user_text = transcribe(input_audio_path)
    print(f"User: {user_text}")

    # Step 2: Generate LLM response
    response_text = generate_response(user_text)
    print(f"Agent: {response_text}")

    # Step 3: Convert response to speech
    audio_path = text_to_speech(response_text)

    return {
        "user_said": user_text,
        "agent_said": response_text,
        "audio_path": audio_path
    }


# Simulate a voice conversation from pre-recorded audio files
if __name__ == "__main__":
    # In a real app, you'd record audio from the microphone
    # Here we simulate with files
    test_inputs = ["hello.wav", "question.wav"]

    for audio_file in test_inputs:
        if os.path.exists(audio_file):
            result = voice_turn(audio_file)
            print(f"Response audio saved to: {result['audio_path']}")
        else:
            print(f"Skipping {audio_file} (not found) — provide real audio files to test")
```

---

## Example 5: Meeting Transcription + Summarization

```python
"""
meeting_summarizer.py — Transcribe a meeting recording and generate structured notes
"""
from openai import OpenAI
import anthropic

openai_client = OpenAI()
anthropic_client = anthropic.Anthropic()


def transcribe_meeting(audio_path: str) -> str:
    """Transcribe meeting audio, handling files > 25MB by splitting."""
    import os
    file_size = os.path.getsize(audio_path)

    if file_size > 24 * 1024 * 1024:
        print("File > 24MB, consider splitting. Attempting direct transcription...")

    with open(audio_path, "rb") as f:
        result = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )

    # Format with timestamps
    lines = []
    for seg in result.segments:
        minutes = int(seg.start // 60)
        seconds = int(seg.start % 60)
        lines.append(f"[{minutes:02d}:{seconds:02d}] {seg.text.strip()}")

    return "\n".join(lines)


def generate_meeting_notes(transcript: str) -> str:
    """Generate structured meeting notes from transcript."""
    prompt = f"""Here is the transcript of a meeting:

{transcript}

Generate structured meeting notes with:

## Meeting Summary
[2-3 sentence overview]

## Key Discussion Points
[bullet points of main topics discussed]

## Decisions Made
[list any decisions reached]

## Action Items
[format: - [ ] Task description (Owner if mentioned, Due date if mentioned)]

## Questions Raised (Unresolved)
[questions that came up but weren't answered]"""

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


# Usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        print("Transcribing...")
        transcript = transcribe_meeting(audio_file)
        print("Generating notes...")
        notes = generate_meeting_notes(transcript)
        print("\n" + "="*50)
        print(notes)

        # Save to file
        with open("meeting_notes.md", "w") as f:
            f.write("# Transcript\n\n")
            f.write(transcript)
            f.write("\n\n---\n\n")
            f.write(notes)
        print("\nSaved to meeting_notes.md")
    else:
        print("Usage: python meeting_summarizer.py <audio_file>")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [04 — Using Vision APIs](../04_Using_Vision_APIs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 — Multimodal Embeddings](../06_Multimodal_Embeddings/Theory.md)
