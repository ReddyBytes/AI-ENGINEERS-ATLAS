# API Basics — Code Examples

## Example 1: Minimal curl request

```bash
#!/bin/bash
# Requires: ANTHROPIC_API_KEY exported in environment

curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-sonnet-4-6",
    "max_tokens": 256,
    "messages": [
      {"role": "user", "content": "What is 2 + 2?"}
    ]
  }'
```

Expected output:
```json
{
  "id": "msg_01...",
  "type": "message",
  "role": "assistant",
  "content": [{"type": "text", "text": "4"}],
  "model": "claude-sonnet-4-6-20250219",
  "stop_reason": "end_turn",
  "usage": {"input_tokens": 14, "output_tokens": 1}
}
```

---

## Example 2: Python SDK — basic call

```python
import anthropic

# Client reads ANTHROPIC_API_KEY from environment automatically
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain REST APIs in one paragraph."}
    ]
)

print(message.content[0].text)
print(f"Stop reason: {message.stop_reason}")
print(f"Input tokens: {message.usage.input_tokens}")
print(f"Output tokens: {message.usage.output_tokens}")
```

---

## Example 3: Environment variable setup with python-dotenv

```python
# requirements: pip install anthropic python-dotenv

from dotenv import load_dotenv
import os

# Load .env file from project root
load_dotenv()

import anthropic

# Explicit key extraction (for clarity)
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set in environment")

client = anthropic.Anthropic(api_key=api_key)

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.content[0].text)
```

---

## Example 4: JavaScript / Node.js SDK

```javascript
// npm install @anthropic-ai/sdk

import Anthropic from "@anthropic-ai/sdk";

// Reads ANTHROPIC_API_KEY from process.env
const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "What is the Anthropic API?" }],
});

console.log(message.content[0].text);
console.log("Stop reason:", message.stop_reason);
console.log("Tokens used:", message.usage);
```

---

## Example 5: Checking HTTP status before parsing

```python
import httpx
import json
import os

def call_api_raw(prompt: str) -> dict:
    """Direct HTTP call without the SDK — useful for debugging."""
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}],
    }
    
    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=body,
        timeout=30.0,
    )
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        retry_after = response.headers.get("retry-after", "unknown")
        raise Exception(f"Rate limited. Retry after {retry_after}s")
    elif response.status_code == 401:
        raise Exception("Invalid API key")
    else:
        raise Exception(f"API error {response.status_code}: {response.text}")

result = call_api_raw("What is 1+1?")
print(result["content"][0]["text"])
```

---

## Example 6: Multiple environments with key isolation

```python
import os
import anthropic
from enum import Enum

class Environment(Enum):
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"

def get_client(env: Environment) -> anthropic.Anthropic:
    """Return a client configured for the given environment."""
    key_map = {
        Environment.DEV: "ANTHROPIC_API_KEY_DEV",
        Environment.STAGING: "ANTHROPIC_API_KEY_STAGING",
        Environment.PROD: "ANTHROPIC_API_KEY_PROD",
    }
    
    env_var = key_map[env]
    api_key = os.environ.get(env_var)
    
    if not api_key:
        raise ValueError(f"Missing environment variable: {env_var}")
    
    return anthropic.Anthropic(api_key=api_key)

# Usage
client = get_client(Environment.DEV)
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

⬅️ **Prev:** [Track 3 Overview](../README.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Messages API](../02_Messages_API/Code_Example.md)
