# First API Call — Code Examples

## Example 1: Absolute minimal call — Python

```python
# pip install anthropic
# export ANTHROPIC_API_KEY="sk-ant-..."

import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Say hello in 5 words."}]
)

print(message.content[0].text)
```

---

## Example 2: Absolute minimal call — JavaScript

```javascript
// npm install @anthropic-ai/sdk
// export ANTHROPIC_API_KEY="sk-ant-..."

import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Say hello in 5 words." }],
});

console.log(message.content[0].text);
```

---

## Example 3: Inspecting the full response object

```python
import anthropic
import json

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": "What is Python?"}]
)

print("=== Response Object ===")
print(f"ID:           {message.id}")
print(f"Type:         {message.type}")
print(f"Role:         {message.role}")
print(f"Stop reason:  {message.stop_reason}")
print(f"Model used:   {message.model}")
print(f"\n=== Content ===")
for i, block in enumerate(message.content):
    print(f"Block {i}: type={block.type}")
    if block.type == "text":
        print(f"  text: {block.text[:100]}...")
print(f"\n=== Usage ===")
print(f"Input tokens:  {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")
```

---

## Example 4: Python with error handling

```python
import anthropic
import sys

def ask_claude(question: str) -> str:
    client = anthropic.Anthropic()
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": question}]
        )
        
        if message.stop_reason == "max_tokens":
            print("Warning: response was truncated", file=sys.stderr)
        
        return message.content[0].text
    
    except anthropic.AuthenticationError:
        print("Error: invalid API key. Set ANTHROPIC_API_KEY.", file=sys.stderr)
        sys.exit(1)
    except anthropic.RateLimitError:
        print("Error: rate limit hit. Try again in a moment.", file=sys.stderr)
        raise
    except anthropic.APIConnectionError as e:
        print(f"Error: network problem: {e}", file=sys.stderr)
        raise
    except anthropic.APIStatusError as e:
        print(f"Error: API returned {e.status_code}", file=sys.stderr)
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ask.py 'your question here'")
        sys.exit(1)
    
    answer = ask_claude(sys.argv[1])
    print(answer)
```

Usage:
```bash
python ask.py "What is the speed of light?"
```

---

## Example 5: Async client (for FastAPI / asyncio)

```python
import asyncio
import anthropic

async def ask_async(question: str) -> str:
    # Use AsyncAnthropic for non-blocking calls
    client = anthropic.AsyncAnthropic()
    
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": question}]
    )
    
    return message.content[0].text

# FastAPI integration example
from fastapi import FastAPI

app = FastAPI()

@app.post("/ask")
async def ask_endpoint(question: str):
    answer = await ask_async(question)
    return {"answer": answer}

# Direct asyncio usage
if __name__ == "__main__":
    result = asyncio.run(ask_async("What is asyncio?"))
    print(result)
```

---

## Example 6: Side-by-side Python vs JS with token tracking

**Python:**
```python
import anthropic
import time

client = anthropic.Anthropic()

start = time.time()
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=512,
    messages=[{"role": "user", "content": "Explain decorators in Python"}]
)
elapsed = time.time() - start

print(message.content[0].text)
print(f"\n[{elapsed:.2f}s | in:{message.usage.input_tokens} out:{message.usage.output_tokens}]")
```

**JavaScript:**
```javascript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const start = Date.now();
const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 512,
  messages: [{ role: "user", content: "Explain decorators in Python" }],
});
const elapsed = (Date.now() - start) / 1000;

console.log(message.content[0].text);
console.log(`\n[${elapsed.toFixed(2)}s | in:${message.usage.input_tokens} out:${message.usage.output_tokens}]`);
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

⬅️ **Prev:** [Messages API](../02_Messages_API/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [System Prompts](../04_System_Prompts/Code_Example.md)
