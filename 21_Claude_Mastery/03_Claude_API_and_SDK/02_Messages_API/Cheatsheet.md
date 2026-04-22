# Messages API — Cheatsheet

## Endpoint

```
POST https://api.anthropic.com/v1/messages
```

---

## Minimal Request

```json
{
  "model": "claude-sonnet-4-6",
  "max_tokens": 1024,
  "messages": [
    {"role": "user", "content": "Your question here"}
  ]
}
```

---

## Full Request Schema

```python
client.messages.create(
    model="claude-sonnet-4-6",        # REQUIRED
    max_tokens=4096,                    # REQUIRED
    system="You are helpful.",          # optional
    messages=[...],                     # REQUIRED
    temperature=0.7,                    # optional, 0.0–1.0
    top_p=0.9,                          # optional
    top_k=40,                           # optional
    stream=False,                       # optional
    tools=[...],                        # optional
    tool_choice={"type": "auto"},       # optional
    metadata={"user_id": "abc"},        # optional
    stop_sequences=["<END>"],           # optional
)
```

---

## Message Roles

| Role | Used in | Purpose |
|---|---|---|
| `"user"` | messages array | Human turn, or tool_result |
| `"assistant"` | messages array | Claude's turn |

Rules: must alternate, last message must be user.

---

## Content Block Types

```json
// Text block
{"type": "text", "text": "Hello"}

// Image — base64
{
  "type": "image",
  "source": {"type": "base64", "media_type": "image/jpeg", "data": "..."}
}

// Image — URL
{
  "type": "image",
  "source": {"type": "url", "url": "https://..."}
}

// Tool use (in assistant message)
{"type": "tool_use", "id": "toolu_01...", "name": "fn", "input": {...}}

// Tool result (in user message)
{"type": "tool_result", "tool_use_id": "toolu_01...", "content": "result"}
```

---

## Response Structure

```python
response = client.messages.create(...)

response.id              # "msg_01..."
response.type            # "message"
response.role            # "assistant"
response.content         # list of content blocks
response.content[0].text # extract text (most common)
response.model           # "claude-sonnet-4-6-20250219"
response.stop_reason     # "end_turn" | "max_tokens" | "tool_use" | "stop_sequence"
response.usage.input_tokens
response.usage.output_tokens
```

---

## Stop Reasons — What to Do

| stop_reason | Meaning | Action |
|---|---|---|
| `"end_turn"` | Normal completion | Use response |
| `"max_tokens"` | Truncated | Increase max_tokens or continue |
| `"tool_use"` | Tool call needed | Execute tool, send result back |
| `"stop_sequence"` | Hit your stop string | Parse up to stop string |

---

## Multi-Turn Pattern

```python
history = []

def chat(user_msg):
    history.append({"role": "user", "content": user_msg})
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024, messages=history
    )
    history.append({"role": "assistant", "content": resp.content[0].text})
    return resp.content[0].text
```

---

## Content as String vs Array

```python
# Simple string (shorthand — only works for text-only)
{"role": "user", "content": "Hello"}

# Array of blocks (required for images, tools, caching)
{"role": "user", "content": [{"type": "text", "text": "Hello"}]}
```

---

## Golden Rules

1. `content` is an array — always index with `[0].text` for plain text
2. Check `stop_reason` before assuming the response is complete
3. Roles must alternate: user → assistant → user → assistant
4. Always set `max_tokens` — do not rely on defaults
5. Maintain your own conversation history — the API is stateless

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [API Basics](../01_API_Basics/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [First API Call](../03_First_API_Call/Cheatsheet.md)
