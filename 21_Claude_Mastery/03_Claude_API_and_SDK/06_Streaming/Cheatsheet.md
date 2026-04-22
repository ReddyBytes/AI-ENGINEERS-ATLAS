# Streaming — Cheatsheet

## Python — Stream Context Manager

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

final = stream.get_final_message()  # access after `with` block
```

---

## Python — Raw Event Stream

```python
with client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}],
    stream=True
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
        elif event.type == "message_stop":
            print()
```

---

## JavaScript — Streaming

```javascript
const stream = await client.messages.stream({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "..." }],
});

for await (const chunk of stream) {
  if (chunk.type === "content_block_delta" &&
      chunk.delta.type === "text_delta") {
    process.stdout.write(chunk.delta.text);
  }
}

// Or use the text helper
stream.on("text", (text) => process.stdout.write(text));

const final = await stream.finalMessage();
```

---

## SSE Event Types

| Event | When | Key fields |
|---|---|---|
| `message_start` | Once, start | `message.id`, `usage.input_tokens` |
| `content_block_start` | Per block | `index`, `content_block.type` |
| `content_block_delta` | Many times | `delta.text` (text) or `delta.partial_json` (tool) |
| `content_block_stop` | Per block | Block complete |
| `message_delta` | Once, near end | `delta.stop_reason`, `usage.output_tokens` |
| `message_stop` | Once, end | Stream done |
| `ping` | Periodic | Keep-alive, ignore |

---

## Getting Stop Reason from Stream

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

final = stream.get_final_message()
print(final.stop_reason)   # "end_turn"
print(final.usage)         # Usage(input_tokens=..., output_tokens=...)
```

---

## FastAPI Streaming Endpoint

```python
@app.post("/chat")
async def chat(request: dict):
    async def generate():
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": request["message"]}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `print(text)` adds newlines | Use `print(text, end="", flush=True)` |
| No flush → no output | Always `flush=True` for immediate printing |
| Sync client in async code | Use `anthropic.AsyncAnthropic()` |
| Accessing stream outside `with` | Get final message via `stream.get_final_message()` after block |

---

## Streaming vs Non-Streaming: When to Use

| Use streaming | Use non-streaming |
|---|---|
| Chat interfaces (typewriter effect) | Batch processing |
| Long responses (code, essays) | Simple lookups |
| Real-time feedback needed | When response order matters more than speed |
| User-facing applications | Background data pipelines |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Tool Use](../05_Tool_Use/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Vision](../07_Vision/Cheatsheet.md)
