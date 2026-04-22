# Streaming — Interview Q&A

## Beginner Questions

**Q1: What is streaming in the context of the Anthropic API?**

A: Streaming is a mode where the API sends Claude's response incrementally as it's generated, rather than waiting for the full response to be ready. Each token (or small group of tokens) is delivered immediately as a Server-Sent Event (SSE). The result is a typewriter effect — users see the response appearing word by word rather than waiting for the whole answer at once.

---

**Q2: How do you enable streaming in the Python SDK?**

A: Use `client.messages.stream()` as a context manager instead of `client.messages.create()`. The `text_stream` property yields text fragments as they arrive:
```python
with client.messages.stream(model=..., max_tokens=..., messages=[...]) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

---

**Q3: Why do you need `flush=True` and `end=""` when printing streamed text?**

A: `end=""` prevents `print()` from adding a newline after each tiny token fragment (the default adds a newline, which would break the output into separate lines for each token). `flush=True` forces Python to immediately write the output buffer to the terminal — without it, Python buffers print calls and the typewriter effect disappears since tokens accumulate and print in batches.

---

**Q4: What is the SSE event type that carries the text tokens?**

A: `content_block_delta` with `delta.type == "text_delta"`. The actual text is in `delta.text`. Other delta types exist for tool arguments (`input_json_delta`), but `text_delta` is the one that carries conversational text.

---

## Intermediate Questions

**Q5: How do you get the stop reason and token usage from a streamed response?**

A: Call `stream.get_final_message()` after the `with` block ends. The stream context manager collects all events and assembles the final `Message` object, which has `.stop_reason` and `.usage` just like a non-streamed response:
```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        ...
final = stream.get_final_message()
print(final.stop_reason, final.usage)
```

---

**Q6: How does streaming work with FastAPI to push tokens to a browser?**

A: Use `StreamingResponse` with a generator function that yields SSE-formatted strings. The generator uses `client.messages.stream()` internally and yields each text fragment as a `data: {text}\n\n` SSE message. The browser's `EventSource` API or `fetch()` with streaming reads these as they arrive. Add `Cache-Control: no-cache` header to prevent proxy buffering.

---

**Q7: What happens when Claude calls a tool during a streaming response?**

A: The stream emits a `content_block_start` event with `"type": "tool_use"`, followed by `content_block_delta` events with `"type": "input_json_delta"` that stream the JSON arguments incrementally (as partial JSON fragments that you concatenate). The stream then emits `message_delta` with `stop_reason: "tool_use"`. At that point, you exit the stream, execute the tool, and make a new API call (streaming or not) with the tool result appended.

---

**Q8: Is streaming more expensive than non-streaming?**

A: No. Streaming has exactly the same per-token pricing as non-streaming. The tokens are identical — only the delivery mechanism differs (SSE vs batch HTTP response). The cost difference is zero. Streaming does keep the TCP connection open longer, but this has no billing impact.

---

## Advanced Questions

**Q9: How would you implement a streaming chat endpoint that also supports tool use?**

A: The architecture has two phases: (1) Start a streaming call for the initial user message. Stream text to the client in real time. When `stop_reason: "tool_use"` arrives, stop streaming and switch to non-streaming mode. (2) Execute tools synchronously, then send a new streaming call with tool results appended. Stream the final answer to the client. The client receives a seamless stream — the transition between the two API calls is invisible if you handle the handoff cleanly. For multi-tool scenarios, batch all tool results before sending the second call.

---

**Q10: Describe the full sequence of SSE events for a simple text response.**

A: In order: (1) `message_start` — contains the message ID, model, and initial usage (input_tokens set, output_tokens=1). (2) `content_block_start` — announces index 0, type "text", empty text. (3) One or more `ping` events — keep-alive signals, ignore. (4) Many `content_block_delta` events — each with `delta.type="text_delta"` and `delta.text` containing 1-10 tokens. (5) `content_block_stop` — block 0 is complete. (6) `message_delta` — contains `delta.stop_reason="end_turn"` and `usage.output_tokens` with final token count. (7) `message_stop` — stream is complete, connection closes.

---

**Q11: What backpressure and timeout considerations apply when streaming long responses?**

A: For long responses (2000+ tokens), the streaming connection stays open for potentially 30-60+ seconds. Production concerns: (1) Set an appropriate `httpx` timeout — the default may be too short. Use `timeout=httpx.Timeout(None, connect=10)` to set connect timeout but no read timeout. (2) Implement client-side backpressure — if the browser is slow, buffering too many tokens in memory can cause OOM. Use async generators with proper buffering. (3) Handle connection drops — if the client disconnects mid-stream, catch `GeneratorExit` or `asyncio.CancelledError` in your generator. (4) For serverless deployments (Lambda, Cloud Run), max response time limits may cut off long streams — use webhooks or long polling instead.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Tool Use](../05_Tool_Use/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Vision](../07_Vision/Interview_QA.md)
