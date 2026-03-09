# Streaming Responses — Cheatsheet

**One-liner:** Streaming sends LLM output to the client token by token as it's generated — so users see words appearing immediately instead of waiting for the full response.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Streaming** | Sending output incrementally as tokens are generated, not all at once |
| **SSE** | Server-Sent Events — HTTP mechanism for server to push data to client |
| **Token** | The smallest unit the LLM generates (~0.75 words) |
| **Stream event** | A single data packet containing one or more tokens |
| **TTFT** | Time to First Token — how long until the user sees the first word |
| **Flush** | Force the buffer to send immediately (needed for print streaming) |
| **Context manager** | `with client.messages.stream(...) as stream:` pattern in Python |
| **text_stream** | Iterator yielding text deltas from Anthropic streaming API |

---

## Streaming vs Non-Streaming

| | Non-Streaming | Streaming |
|--|---------------|----------|
| User experience | Blank → full response appears | Words appear immediately |
| Time to first token | Same as full response time | ~0.5–1 second |
| Perceived wait | Long | Short |
| Code complexity | Simple | Slightly more complex |
| Works for JSON parsing | Yes | Requires accumulating full text first |
| Works for tool calling | Yes | Partial — need to complete before executing tool |

---

## Anthropic Streaming Quick Reference

```python
# Pattern 1: Print as it streams
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": "Write a haiku about coding."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Pattern 2: Collect full response
with client.messages.stream(...) as stream:
    full_response = stream.get_final_message()
    text = full_response.content[0].text

# Pattern 3: Accumulate manually
full_text = ""
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        full_text += text
```

---

## When to Use / Not Use

| Use streaming when... | Don't use streaming when... |
|-----------------------|-----------------------------|
| Chat interface (user is watching) | Batch processing in background |
| Long responses (> 2 seconds) | You need to parse JSON from the output |
| Any interactive UI | Short responses (< 2 seconds overhead not worth it) |
| Building a chatbot frontend | Tool calling (need complete response first) |

---

## Golden Rules

1. **Always use `flush=True`** when printing streamed text in a terminal — otherwise output buffers until newline.
2. **Accumulate text if you need it later** — the stream is consumed once. You can't re-iterate it.
3. **Handle stream errors** — network interruptions can cut streams. Wrap in try/except and handle partial responses.
4. **Don't stream to non-streaming consumers** — APIs calling your backend often don't handle SSE. Use regular responses for API-to-API calls.
5. **TTFT is the key UX metric** — users perceive time-to-first-token more than total generation time.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [07 Memory Systems](../07_Memory_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 RAG Fundamentals](../../09_RAG_Systems/01_RAG_Fundamentals/Theory.md)
