# Streaming Responses — Code Example

Streaming with the Anthropic API. Word-by-word output in terminal, collecting the full response, and timing TTFT.

```python
import anthropic
import time
import sys

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var


# ─────────────────────────────────────────────
# EXAMPLE 1: Basic streaming — words appear as generated
# ─────────────────────────────────────────────

print("=" * 50)
print("EXAMPLE 1: Basic streaming")
print("=" * 50)
print("Response: ", end="", flush=True)

with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Write a short haiku about programming."}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)  # end="" prevents newlines between tokens
                                          # flush=True forces immediate display

print("\n")  # newline after stream finishes


# ─────────────────────────────────────────────
# EXAMPLE 2: Measure Time to First Token (TTFT)
# TTFT is the key UX metric — how long until user sees something
# ─────────────────────────────────────────────

print("=" * 50)
print("EXAMPLE 2: Measuring TTFT")
print("=" * 50)

start_time = time.time()
first_token_time = None
token_count = 0

print("Response: ", end="", flush=True)

with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=300,
    messages=[
        {"role": "user", "content": "Explain what a neural network is in 3 sentences."}
    ]
) as stream:
    for text in stream.text_stream:
        if first_token_time is None:
            first_token_time = time.time()
        token_count += 1
        print(text, end="", flush=True)

end_time = time.time()

print(f"\n\n[Metrics]")
print(f"  Time to first token: {first_token_time - start_time:.3f}s")
print(f"  Total generation time: {end_time - start_time:.3f}s")
print(f"  Token chunks received: {token_count}")


# ─────────────────────────────────────────────
# EXAMPLE 3: Stream and collect the full response
# Sometimes you need both: display as it streams AND have the full text at the end
# ─────────────────────────────────────────────

print("\n" + "=" * 50)
print("EXAMPLE 3: Stream + collect full response")
print("=" * 50)

full_response = ""

print("Streaming: ", end="", flush=True)

with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "List 3 benefits of exercise."}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
        full_response += text  # accumulate the full text

print(f"\n\n[Full response collected — {len(full_response)} characters]")
print(f"Word count: {len(full_response.split())}")


# ─────────────────────────────────────────────
# EXAMPLE 4: Using get_final_message() for metadata
# After streaming, get token usage and stop reason
# ─────────────────────────────────────────────

print("\n" + "=" * 50)
print("EXAMPLE 4: Final message metadata")
print("=" * 50)

with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=150,
    messages=[
        {"role": "user", "content": "What is 2+2? Be brief."}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # After streaming completes, get the full message object
    final = stream.get_final_message()

print(f"\n\n[Message metadata]")
print(f"  Stop reason: {final.stop_reason}")
print(f"  Input tokens: {final.usage.input_tokens}")
print(f"  Output tokens: {final.usage.output_tokens}")
print(f"  Total tokens: {final.usage.input_tokens + final.usage.output_tokens}")


# ─────────────────────────────────────────────
# EXAMPLE 5: Streaming with system message
# Same pattern — system goes in the messages.create call
# ─────────────────────────────────────────────

print("\n" + "=" * 50)
print("EXAMPLE 5: Streaming with system message")
print("=" * 50)

print("Response: ", end="", flush=True)

with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=200,
    system="You are a pirate. Respond in character. Keep responses short.",
    messages=[
        {"role": "user", "content": "Tell me about machine learning."}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print("\n")


# ─────────────────────────────────────────────
# EXAMPLE 6: Non-streaming for comparison
# Run the same prompt without streaming to see the difference
# ─────────────────────────────────────────────

print("=" * 50)
print("EXAMPLE 6: Non-streaming (for comparison)")
print("=" * 50)

start = time.time()
print("Waiting for response", end="", flush=True)

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Write a haiku about programming."}
    ]
)

elapsed = time.time() - start
print(f"\n\n[Waited {elapsed:.2f}s before seeing anything]")
print(f"Response appeared all at once:\n{response.content[0].text}")
```

**Running this:**
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key"
python streaming_example.py
```

**Expected behavior:**
- Examples 1–5: words appear token by token, progressively
- Example 6: blank screen for several seconds, then full text appears at once

**Key patterns:**
- `stream.text_stream` — iterator over text deltas
- `print(text, end="", flush=True)` — essential for streaming display
- `stream.get_final_message()` — access token counts and stop reason after streaming
- Use `full_response += text` inside the loop to accumulate complete text

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [07 Memory Systems](../07_Memory_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 RAG Fundamentals](../../09_RAG_Systems/01_RAG_Fundamentals/Theory.md)
