# Using Vision APIs — Cheatsheet

## Image Input Methods

| Method | When to use | Code pattern |
|--------|------------|--------------|
| **Base64** | Local files, reliability critical | Read file → `base64.encode()` → embed in payload |
| **URL** | Public images, save bandwidth | Include URL string directly in payload |
| **File upload** (some APIs) | Large files, reuse across calls | Upload once, reference by ID |

---

## Claude Vision — Minimal Example

```python
import anthropic, base64

client = anthropic.Anthropic()

with open("image.jpg", "rb") as f:
    b64 = base64.standard_b64encode(f.read()).decode()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}},
            {"type": "text", "text": "What is in this image?"}
        ]
    }]
)
print(response.content[0].text)
```

---

## OpenAI Vision — Minimal Example

```python
from openai import OpenAI
import base64

client = OpenAI()

with open("image.jpg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "auto"}},
            {"type": "text", "text": "What is in this image?"}
        ]
    }]
)
print(response.choices[0].message.content)
```

---

## Supported Media Types

| Format | MIME type | Notes |
|--------|----------|-------|
| JPEG | `image/jpeg` | Most common, lossy compression |
| PNG | `image/png` | Lossless, supports transparency |
| GIF | `image/gif` | Static only (first frame used) |
| WebP | `image/webp` | Modern format, good compression |

---

## Token / Cost Quick Reference

| Provider | Resolution | Approx. tokens | Approx. cost |
|----------|-----------|---------------|-------------|
| Claude Haiku | 1000×1000 | ~1,600 | ~$0.002 |
| Claude Sonnet | 1000×1000 | ~1,600 | ~$0.006 |
| GPT-4o (auto) | 1024×768 | ~765 | ~$0.004 |
| Gemini Flash | any | billed by MP | ~$0.0001 |

---

## Resolution Cheat Sheet

| Task | Use resolution |
|------|--------------|
| General Q&A, scene description | 512–800px (resize before sending) |
| Reading printed text / labels | 1024px+ |
| Document parsing | 1200–2000px |
| Handwriting | 1500px+ |
| Chart reading | 800px+ |
| Defect detection | Depends on defect size |

Resize command (Python):
```python
from PIL import Image

img = Image.open("large.jpg")
img.thumbnail((1024, 1024), Image.LANCZOS)  # max 1024px on longest side
img.save("resized.jpg", quality=85)
```

---

## Prompt Templates

**General description:**
```
Describe what you see in this image. Be specific about objects, people, text, colors, and setting.
```

**Structured extraction:**
```
Extract [fields] from this image as JSON:
{"field1": null, "field2": null}
Return ONLY valid JSON.
```

**Binary decision:**
```
Look at this image and answer with only: YES or NO.
Question: [your question]
```

**Step-by-step reasoning:**
```
Step 1: Describe what you see.
Step 2: Based on what you see, answer: [your question]
```

---

## Error Handling Template

```python
import time
from anthropic import RateLimitError, APIError

def vision_call_with_retry(image_b64, question, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.messages.create(...)
            return response.content[0].text
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # exponential backoff
            else:
                raise
        except APIError as e:
            raise  # non-retriable errors
```

---

## Golden Rules

1. Always resize images before sending — most tasks don't need full resolution
2. Use base64 for production; URLs only for prototyping
3. Validate + parse structured output before using it (never trust raw JSON)
4. Add retry logic with exponential backoff for rate limits
5. Monitor image token usage separately from text token usage

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Send image to Claude Vision API |
| [📄 Code_Cookbook.md](./Code_Cookbook.md) | 10 vision use cases |

⬅️ **Prev:** [03 — Image Understanding](../03_Image_Understanding/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Audio and Speech AI](../05_Audio_and_Speech_AI/Theory.md)
