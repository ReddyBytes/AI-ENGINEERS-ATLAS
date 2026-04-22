# Streaming — Code Examples

## Example 1: Basic streaming — Python

```python
import anthropic

client = anthropic.Anthropic()

print("Claude: ", end="", flush=True)

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a short story about a robot."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()  # final newline
```

---

## Example 2: Streaming with token usage

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": "Explain quantum entanglement briefly."}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Access final message after streaming completes
final = stream.get_final_message()
print(f"\n\n[Stop: {final.stop_reason} | In: {final.usage.input_tokens} | Out: {final.usage.output_tokens}]")
```

---

## Example 3: Streaming CLI chat loop

```python
import anthropic

client = anthropic.Anthropic()
history = []

print("Chat with Claude (type 'quit' to exit)\n")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit"):
        break
    if not user_input:
        continue
    
    history.append({"role": "user", "content": user_input})
    
    print("Claude: ", end="", flush=True)
    collected_text = ""
    
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=history
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            collected_text += text
    
    print()
    history.append({"role": "assistant", "content": collected_text})
```

---

## Example 4: Raw event inspection

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=[{"role": "user", "content": "Count to 3."}],
    stream=True
) as stream:
    for event in stream:
        print(f"[{event.type}]", end=" ")
        
        if event.type == "message_start":
            print(f"id={event.message.id}")
        elif event.type == "content_block_start":
            print(f"index={event.index} type={event.content_block.type}")
        elif event.type == "content_block_delta":
            if event.delta.type == "text_delta":
                print(f"'{event.delta.text}'")
        elif event.type == "content_block_stop":
            print(f"index={event.index}")
        elif event.type == "message_delta":
            print(f"stop_reason={event.delta.stop_reason} output_tokens={event.usage.output_tokens}")
        elif event.type == "message_stop":
            print("STREAM COMPLETE")
        elif event.type == "ping":
            print("(keep-alive)")
```

---

## Example 5: JavaScript streaming

```javascript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

// Method 1: for-await loop
const stream = await client.messages.stream({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Write a haiku about streaming." }],
});

process.stdout.write("Claude: ");
for await (const chunk of stream) {
  if (
    chunk.type === "content_block_delta" &&
    chunk.delta.type === "text_delta"
  ) {
    process.stdout.write(chunk.delta.text);
  }
}

// Get final message after loop
const final = await stream.finalMessage();
console.log(`\n[${final.usage.input_tokens} in, ${final.usage.output_tokens} out]`);

// Method 2: event listener (simpler for text-only)
const stream2 = client.messages.stream({
  model: "claude-sonnet-4-6",
  max_tokens: 256,
  messages: [{ role: "user", content: "Hi!" }],
});

stream2.on("text", (text) => process.stdout.write(text));
await stream2.finalMessage();
```

---

## Example 6: FastAPI streaming endpoint

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import anthropic
import json

app = FastAPI()
client = anthropic.Anthropic()

@app.post("/stream")
async def stream_chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")
    history = body.get("history", [])
    
    if not user_message:
        return {"error": "No message provided"}
    
    messages = history + [{"role": "user", "content": user_message}]
    
    async def generate():
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=messages
        ) as stream:
            for text in stream.text_stream:
                # Send as SSE
                data = json.dumps({"text": text})
                yield f"data: {data}\n\n"
        
        # Send completion event with usage
        final = stream.get_final_message()
        done_data = json.dumps({
            "done": True,
            "stop_reason": final.stop_reason,
            "usage": {
                "input_tokens": final.usage.input_tokens,
                "output_tokens": final.usage.output_tokens,
            }
        })
        yield f"data: {done_data}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Tool Use](../05_Tool_Use/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Vision](../07_Vision/Code_Example.md)
