# Vision — Code Examples

## Example 1: Analyze a local image file

```python
import anthropic
import base64
from pathlib import Path

client = anthropic.Anthropic()

def analyze_image(image_path: str, question: str) -> str:
    """Analyze a local image file with a question."""
    path = Path(image_path)
    
    # Map extension to media_type
    media_types = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"
    }
    media_type = media_types.get(path.suffix.lower())
    if not media_type:
        raise ValueError(f"Unsupported image format: {path.suffix}")
    
    # Encode image
    image_data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_data,
                    }
                },
                {"type": "text", "text": question}
            ]
        }]
    )
    
    return response.content[0].text

# Usage
description = analyze_image("chart.png", "What trend does this chart show?")
print(description)
```

---

## Example 2: Analyze image from URL

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "url",
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
                }
            },
            {"type": "text", "text": "Describe what you see in this image."}
        ]
    }]
)

print(response.content[0].text)
```

---

## Example 3: OCR — extract text from image

```python
import anthropic
import base64
from pathlib import Path

client = anthropic.Anthropic()

def extract_text_from_image(image_path: str) -> str:
    """Extract all text from an image using Claude's vision."""
    image_data = base64.standard_b64encode(
        Path(image_path).read_bytes()
    ).decode("utf-8")
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="You are an OCR engine. Extract ALL text from images exactly as it appears. Preserve line breaks and structure. Return only the extracted text, no commentary.",
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {"type": "text", "text": "Extract all text from this image."}
            ]
        }]
    )
    
    return response.content[0].text

# Usage
text = extract_text_from_image("receipt.jpg")
print(text)
```

---

## Example 4: Structured data extraction from image

```python
import anthropic
import base64
import json
from pathlib import Path

client = anthropic.Anthropic()

def extract_receipt_data(image_path: str) -> dict:
    """Extract structured data from a receipt image."""
    image_data = base64.standard_b64encode(
        Path(image_path).read_bytes()
    ).decode("utf-8")
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system='Extract receipt data as JSON. Return ONLY valid JSON, no other text.',
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": 'Extract: {"merchant": str, "date": str, "total": float, "items": [{"name": str, "price": float}], "tax": float}'
                }
            ]
        }]
    )
    
    return json.loads(response.content[0].text)

data = extract_receipt_data("receipt.jpg")
print(f"Merchant: {data['merchant']}")
print(f"Total: ${data['total']:.2f}")
```

---

## Example 5: Multiple image comparison

```python
import anthropic
import base64
from pathlib import Path

client = anthropic.Anthropic()

def compare_images(image_paths: list[str], question: str) -> str:
    """Compare multiple images and answer a question about them."""
    content = []
    
    for i, path in enumerate(image_paths, 1):
        # Label each image
        content.append({
            "type": "text",
            "text": f"Image {i}:"
        })
        
        # Add image block
        ext = Path(path).suffix.lower()
        media_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                       ".png": "image/png", ".webp": "image/webp"}
        
        data = base64.standard_b64encode(Path(path).read_bytes()).decode("utf-8")
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_types.get(ext, "image/jpeg"),
                "data": data
            }
        })
    
    # Add the final question
    content.append({"type": "text", "text": question})
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": content}]
    )
    
    return response.content[0].text

result = compare_images(
    ["screenshot_v1.png", "screenshot_v2.png"],
    "What UI changes were made between version 1 and version 2?"
)
print(result)
```

---

## Example 6: Resize image before sending (cost optimization)

```python
import anthropic
import base64
from pathlib import Path
from PIL import Image  # pip install Pillow
from io import BytesIO

client = anthropic.Anthropic()

def prepare_image(image_path: str, max_size: int = 1568) -> tuple[str, str]:
    """
    Resize image to max_size on longest side, return (base64_data, media_type).
    Reduces token cost for large images.
    """
    img = Image.open(image_path)
    
    # Resize if needed
    width, height = img.size
    if max(width, height) > max_size:
        ratio = max_size / max(width, height)
        new_size = (int(width * ratio), int(height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        print(f"Resized: {width}×{height} → {new_size[0]}×{new_size[1]}")
    
    # Convert to bytes
    buffer = BytesIO()
    fmt = "JPEG" if image_path.lower().endswith((".jpg", ".jpeg")) else "PNG"
    img.save(buffer, format=fmt, quality=85 if fmt == "JPEG" else None)
    
    data = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")
    media_type = "image/jpeg" if fmt == "JPEG" else "image/png"
    
    return data, media_type

def analyze_with_resize(image_path: str, question: str) -> str:
    data, media_type = prepare_image(image_path)
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": data}
                },
                {"type": "text", "text": question}
            ]
        }]
    )
    
    return response.content[0].text

answer = analyze_with_resize("large_diagram.png", "Summarize this architecture diagram.")
print(answer)
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

⬅️ **Prev:** [Streaming](../06_Streaming/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Prompt Engineering](../08_Prompt_Engineering/Code_Example.md)
