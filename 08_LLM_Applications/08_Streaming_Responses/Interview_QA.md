# Streaming Responses — Interview Q&A

## Beginner

**Q1: What is streaming in the context of LLM APIs and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

Streaming means the LLM API sends tokens to your application as they're generated, rather than waiting for the complete response before sending anything. Without streaming, you make a request and wait until the entire response is finished — which could be 5–30 seconds for long responses. With streaming, the first token arrives in under a second and words appear progressively.

It matters primarily for user experience. People tolerate progressive loading much better than blank screens. Studies on web performance consistently show that perceived speed (how fast something feels) matters more than actual speed. Streaming makes LLM responses feel instant even when they take 15 seconds to complete.

</details>

---

<br>

**Q2: What is SSE (Server-Sent Events) and how does it work?**

<details>
<summary>💡 Show Answer</summary>

Server-Sent Events is an HTTP mechanism that keeps a connection open between server and client, allowing the server to push data at any time. It's one-directional (server to client only) and built on standard HTTP.

The HTTP response has `Content-Type: text/event-stream` and sends data lines formatted as `data: {payload}\n\n`. The client reads these as they arrive. Most LLM APIs use SSE for streaming: Anthropic, OpenAI, and others all send token events over SSE.

In Python, the `anthropic` SDK handles all the SSE details for you — you just use `client.messages.stream()` and iterate over the result. The alternative to SSE is WebSockets, which is bidirectional and useful for real-time bidirectional apps, but adds complexity for the purely server-to-client LLM streaming use case.

</details>

---

<br>

**Q3: How do you display streamed output in a Python terminal?**

<details>
<summary>💡 Show Answer</summary>

Use `print(text, end="", flush=True)`:
- `end=""` prevents print from adding a newline after each token
- `flush=True` forces the output buffer to send immediately (without this, output might buffer until a newline appears, defeating the purpose of streaming)

```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
print()  # final newline after stream completes
```

</details>

---

## Intermediate

**Q4: How do you handle streaming in a web application frontend?**

<details>
<summary>💡 Show Answer</summary>

The frontend needs to read an SSE stream. In JavaScript, use the `EventSource` API or `fetch` with a ReadableStream:

```javascript
// Using fetch for POST requests (EventSource only supports GET)
const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message: userInput }),
    headers: { 'Content-Type': 'application/json' }
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    // Parse SSE events and append to UI
    appendToUI(chunk);
}
```

Your backend proxies the Anthropic streaming API and forwards the SSE events. Frameworks like Next.js have built-in support for streaming API routes.

</details>

---

<br>

**Q5: Can you use streaming with tool calling? What are the complications?**

<details>
<summary>💡 Show Answer</summary>

Streaming and tool calling work together, but with a complication: tool execution must happen between streaming turns, not during them.

The flow: stream the model's response → the model includes a `tool_use` block in its response → streaming stops → you execute the tool → you start a new streaming request with the tool result → stream the final response.

You can stream the "thinking" text before the tool call and the "response" text after, but the tool execution itself is synchronous — you can't execute a tool mid-stream. Most production implementations handle this by detecting `stop_reason == "tool_use"` after the stream ends, then executing tools, then starting a new stream.

</details>

---

<br>

**Q6: How do you measure "time to first token" (TTFT) in code?**

<details>
<summary>💡 Show Answer</summary>

```python
import time

start = time.time()
first_token_time = None
full_text = ""

with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": "Write a poem about space."}]
) as stream:
    for text in stream.text_stream:
        if first_token_time is None:
            first_token_time = time.time()
            print(f"\n[TTFT: {first_token_time - start:.3f}s]")

        print(text, end="", flush=True)
        full_text += text

end = time.time()
print(f"\n[Total: {end - start:.3f}s]")
```

TTFT is typically 0.3–1.5 seconds depending on model and prompt length. Total generation time depends on output length and model speed (tokens per second). TTFT is what users feel most acutely.

</details>

---

## Advanced

**Q7: How would you implement streaming in a production FastAPI backend that proxies Anthropic?**

<details>
<summary>💡 Show Answer</summary>

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import anthropic

app = FastAPI()
client = anthropic.Anthropic()

@app.post("/chat")
async def chat(request: dict):
    async def generate():
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": request["message"]}]
        ) as stream:
            for text in stream.text_stream:
                # Format as SSE events
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
```

Key header: `X-Accel-Buffering: no` — tells Nginx not to buffer the response, which would defeat streaming. Also set `Cache-Control: no-cache`. Handle client disconnects to avoid wasting Anthropic API tokens when the user navigates away.

</details>

---

<br>

**Q8: What are the challenges of streaming responses in multi-tenant production systems?**

<details>
<summary>💡 Show Answer</summary>

Connection management: each streaming request holds an open HTTP connection. At high concurrency (thousands of simultaneous users), this consumes connection pool resources. Use async frameworks (FastAPI + asyncio) to handle many streams with minimal threads.

Backpressure: if the client reads slowly (slow browser, slow network), the stream buffers on the server. Set reasonable buffer limits. If a client disconnects mid-stream, detect it and cancel the upstream Anthropic request to avoid wasting tokens.

Cost tracking: with streaming, billing events arrive token by token. The `usage` object with total token counts is only available in the final `message_stop` event. Make sure you capture it for billing reconciliation.

Timeout handling: streams can hang if the network drops mid-connection. Set read timeouts and implement client-side reconnection with `last-event-id` tracking to resume from where the stream broke.

Rate limiting: streaming connections hold a slot for much longer than regular requests. Your rate limiter needs to account for concurrent connections, not just requests per minute.

</details>

---

<br>

**Q9: How does streaming interact with response caching? Can you cache a streamed response?**

<details>
<summary>💡 Show Answer</summary>

Direct caching conflicts with streaming: a cache stores a complete response and returns it immediately — but streaming sends it piece by piece. There are two approaches:

(1) Cache then stream: for prompts that appear frequently (e.g., the same question asked by many users), check the cache first. If cached, stream the cached response token by token at a controlled rate (simulating real generation). If not cached, stream from the API and simultaneously write to cache when the stream completes.

(2) Cache the complete response, stream on cache hit: store the full text in cache. On cache hit, return it as a simulated stream (chunk the cached text and send with small delays). Users get the streaming UX with zero API cost on repeated queries.

Semantic caching — cache by meaning similarity instead of exact prompt — can significantly increase cache hit rates for LLM applications. Tools like GPTCache implement this pattern.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [07 Memory Systems](../07_Memory_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 RAG Fundamentals](../../09_RAG_Systems/01_RAG_Fundamentals/Theory.md)
