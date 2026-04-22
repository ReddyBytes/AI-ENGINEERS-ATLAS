# Messages API — Code Examples

## Example 1: Basic single-turn request (Python)

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "What are the three laws of thermodynamics?"}
    ]
)

print(response.content[0].text)
print(f"\nStop reason: {response.stop_reason}")
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
```

---

## Example 2: Multi-turn conversation

```python
import anthropic

client = anthropic.Anthropic()

# Simulate a conversation
conversation = [
    {"role": "user", "content": "I want to learn Python. Where should I start?"},
]

# First turn
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=conversation
)
print("Claude:", response.content[0].text)

# Append Claude's response to history
conversation.append({"role": "assistant", "content": response.content[0].text})

# Second turn
conversation.append({"role": "user", "content": "What about learning data structures?"})

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=conversation
)
print("Claude:", response.content[0].text)
```

---

## Example 3: Handling all content block types

```python
import anthropic

client = anthropic.Anthropic()

def process_response(response):
    """Handle any content block type in the response."""
    for block in response.content:
        if block.type == "text":
            print(f"[TEXT] {block.text}")
        elif block.type == "tool_use":
            print(f"[TOOL CALL] {block.name}({block.input})")
            print(f"  Tool ID: {block.id}")
    
    print(f"Stop reason: {response.stop_reason}")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": "Say hello in three languages"}]
)
process_response(response)
```

---

## Example 4: Multi-modal — text + image content block

```python
import anthropic
import base64
from pathlib import Path

client = anthropic.Anthropic()

# Load and encode image
image_data = base64.standard_b64encode(
    Path("chart.png").read_bytes()
).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe the trends shown in this chart."
                }
            ],
        }
    ]
)
print(response.content[0].text)
```

---

## Example 5: JavaScript SDK equivalent

```javascript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from process.env

// Single turn
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [
    { role: "user", content: "What is the capital of Japan?" }
  ],
});

console.log(response.content[0].text);
console.log("Stop reason:", response.stop_reason);
console.log("Usage:", response.usage);

// Multi-turn
const history = [];

async function chat(userMessage) {
  history.push({ role: "user", content: userMessage });
  
  const resp = await client.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 1024,
    messages: history,
  });
  
  const assistantText = resp.content[0].text;
  history.push({ role: "assistant", content: assistantText });
  return assistantText;
}
```

---

## Example 6: Detecting and handling stop reasons

```python
import anthropic

client = anthropic.Anthropic()

def safe_create(messages, max_tokens=2048, model="claude-sonnet-4-6"):
    """Wrapper that handles all stop reasons."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
    )
    
    match response.stop_reason:
        case "end_turn":
            # Normal — return text
            return {"status": "complete", "text": response.content[0].text}
        
        case "max_tokens":
            # Truncated — caller may want to continue
            return {
                "status": "truncated",
                "text": response.content[0].text,
                "message": "Response was truncated. Increase max_tokens or continue."
            }
        
        case "tool_use":
            # Tool call — caller must execute tools
            tool_calls = [b for b in response.content if b.type == "tool_use"]
            return {
                "status": "tool_use",
                "tool_calls": tool_calls,
                "full_content": response.content,
            }
        
        case "stop_sequence":
            return {"status": "stop_sequence", "text": response.content[0].text}
    
    return {"status": "unknown", "response": response}

result = safe_create(
    messages=[{"role": "user", "content": "Write a 10,000 word essay on AI."}],
    max_tokens=100  # intentionally small to trigger max_tokens
)
print(result["status"])  # "truncated"
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

⬅️ **Prev:** [API Basics](../01_API_Basics/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [First API Call](../03_First_API_Call/Code_Example.md)
