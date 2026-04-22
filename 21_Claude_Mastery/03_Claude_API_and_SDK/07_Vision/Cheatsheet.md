# Vision — Cheatsheet

## Image Content Block — base64

```python
import base64
from pathlib import Path

image_data = base64.standard_b64encode(Path("image.jpg").read_bytes()).decode("utf-8")

image_block = {
    "type": "image",
    "source": {
        "type": "base64",
        "media_type": "image/jpeg",   # must match actual format
        "data": image_data,
    }
}
```

## Image Content Block — URL

```python
image_block = {
    "type": "image",
    "source": {
        "type": "url",
        "url": "https://example.com/image.png"
    }
}
```

---

## Supported Formats

| Format | media_type |
|---|---|
| JPEG | `image/jpeg` |
| PNG | `image/png` |
| GIF | `image/gif` (first frame only) |
| WebP | `image/webp` |

---

## Size Limits

| Limit | Value |
|---|---|
| Max file size | 5 MB per image |
| Max dimensions | 8000 × 8000 px |
| Max images per request | 20 |
| Recommended longest side | ~1568 px |

---

## Full Vision Request

```python
import anthropic, base64
from pathlib import Path

client = anthropic.Anthropic()

data = base64.standard_b64encode(Path("chart.png").read_bytes()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": data}
            },
            {"type": "text", "text": "Describe this chart."}
        ]
    }]
)
print(response.content[0].text)
```

---

## Helper: Load Image from Path

```python
import base64
from pathlib import Path

EXT_MAP = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"
}

def image_block(path: str) -> dict:
    p = Path(path)
    data = base64.standard_b64encode(p.read_bytes()).decode("utf-8")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": EXT_MAP[p.suffix.lower()],
            "data": data
        }
    }
```

---

## Multiple Images

```python
content = [
    image_block("before.png"),
    {"type": "text", "text": "BEFORE"},
    image_block("after.png"),
    {"type": "text", "text": "AFTER. What changed?"}
]
```

---

## Token Cost (Approximate)

```
tiles = ceil(width/512) × ceil(height/512)
tokens ≈ tiles × 170 + 85

Examples:
- 512×512  → 1 tile  → 255 tokens
- 1024×768 → 2×2=4   → 765 tokens
- 1568×1568 → 3×3=9  → 1,615 tokens
```

Resize large images before sending to save tokens.

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Wrong `media_type` | Match extension exactly to `media_type` |
| URL behind authentication | Use base64 for private images |
| Content as string with image | Content must be array when using images |
| Expecting animated GIF | Only first frame is analyzed |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Streaming](../06_Streaming/Cheatsheet.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Prompt Engineering](../08_Prompt_Engineering/Cheatsheet.md)
