# First API Call — Cheatsheet

## Install SDK

```bash
pip install anthropic          # Python
npm install @anthropic-ai/sdk  # JavaScript
```

---

## Client Setup

```python
import anthropic

# Reads ANTHROPIC_API_KEY from environment (preferred)
client = anthropic.Anthropic()

# Explicit key
client = anthropic.Anthropic(api_key="sk-ant-api03-...")

# With timeout
client = anthropic.Anthropic(timeout=30.0)
```

---

## Minimal Working Call — Python

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)

print(message.content[0].text)
```

---

## Minimal Working Call — JavaScript

```javascript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();  // reads ANTHROPIC_API_KEY from process.env

const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello!" }],
});

console.log(message.content[0].text);
```

---

## Reading the Response

```python
message.id                  # "msg_01..."
message.type                # "message"
message.role                # "assistant"
message.content             # [TextBlock(type='text', text='...')]
message.content[0].type     # "text"
message.content[0].text     # The actual text ← this is what you want
message.model               # "claude-sonnet-4-6-20250219"
message.stop_reason         # "end_turn"
message.usage.input_tokens  # 14
message.usage.output_tokens # 87
```

---

## Basic Error Handling Template

```python
import anthropic

client = anthropic.Anthropic()

try:
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print(msg.content[0].text)

except anthropic.AuthenticationError:
    print("Bad API key")
except anthropic.RateLimitError:
    print("Rate limited — back off")
except anthropic.APIConnectionError:
    print("Network error")
except anthropic.APIStatusError as e:
    print(f"Error {e.status_code}: {e.message}")
```

---

## Python vs JavaScript Comparison

| | Python | JavaScript |
|---|---|---|
| Install | `pip install anthropic` | `npm install @anthropic-ai/sdk` |
| Import | `import anthropic` | `import Anthropic from '@anthropic-ai/sdk'` |
| Client | `anthropic.Anthropic()` | `new Anthropic()` |
| Call | synchronous | `await client.messages.create(...)` |
| Response | `message.content[0].text` | `message.content[0].text` |

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `message.content` instead of `message.content[0].text` | Always index into content array |
| Missing `await` in JS | All SDK calls are async in JS |
| `ANTHROPIC_API_KEY` not set | `export ANTHROPIC_API_KEY=sk-ant-...` |
| Missing `max_tokens` | Always include — required field |
| Missing `model` | Always include — required field |

---

## Environment Verification

```bash
# Check key is set
echo $ANTHROPIC_API_KEY

# Test installation
python -c "import anthropic; print(anthropic.__version__)"
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Messages API](../02_Messages_API/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [System Prompts](../04_System_Prompts/Cheatsheet.md)
