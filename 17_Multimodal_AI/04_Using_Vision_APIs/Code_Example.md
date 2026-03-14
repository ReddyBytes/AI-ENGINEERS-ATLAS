# Using Vision APIs — Code Example

## Complete Vision API Helper

This module provides a clean wrapper around Claude's vision API with error handling, resizing, and structured output support.

```python
"""
vision_api.py — Production-ready Claude Vision API helper
"""
import anthropic
import base64
import json
import time
from pathlib import Path
from typing import Any
from PIL import Image
import io


client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment


# ──────────────────────────────────────────────
# Core: encode and call
# ──────────────────────────────────────────────

def encode_image(image_path: str, max_dimension: int = 1024) -> tuple[str, str]:
    """
    Load and encode an image as base64.
    Optionally resize to reduce token cost.

    Returns: (base64_string, media_type)
    """
    ext = Path(image_path).suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_type_map.get(ext, "image/jpeg")

    # Open and optionally resize
    with Image.open(image_path) as img:
        # Convert RGBA to RGB for JPEG compatibility
        if img.mode in ("RGBA", "LA", "P") and media_type == "image/jpeg":
            img = img.convert("RGB")

        # Resize if needed (preserves aspect ratio)
        if max(img.width, img.height) > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

        # Encode to bytes
        buffer = io.BytesIO()
        save_format = "JPEG" if media_type == "image/jpeg" else "PNG"
        img.save(buffer, format=save_format, quality=85)
        buffer.seek(0)
        encoded = base64.standard_b64encode(buffer.read()).decode("utf-8")

    return encoded, media_type


def ask_about_image(
    image_path: str,
    question: str,
    model: str = "claude-opus-4-6",
    max_tokens: int = 1024,
    max_dimension: int = 1024,
    max_retries: int = 3,
) -> str:
    """
    Ask any question about a local image.

    Args:
        image_path: Path to local image file
        question: The question or instruction
        model: Claude model to use
        max_tokens: Maximum response length
        max_dimension: Max image dimension (for cost control)
        max_retries: Retry count for rate limit errors

    Returns: Model's text response
    """
    image_data, media_type = encode_image(image_path, max_dimension)

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {"type": "text", "text": question},
                        ],
                    }
                ],
            )
            return response.content[0].text

        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}...")
                time.sleep(wait)
            else:
                raise


# ──────────────────────────────────────────────
# Structured output: extract as JSON
# ──────────────────────────────────────────────

def extract_structured(
    image_path: str,
    schema_description: str,
    example_schema: dict,
    model: str = "claude-opus-4-6",
) -> dict:
    """
    Extract structured data from an image as a Python dict.

    Args:
        image_path: Path to image
        schema_description: What to extract
        example_schema: Dict with keys and null values as template

    Returns: Parsed dict matching the schema
    """
    schema_str = json.dumps(example_schema, indent=2)
    prompt = f"""Extract the following information from this image as JSON.
Schema to fill:
{schema_str}

Instructions:
- Use null for any field not visible or not applicable
- Return ONLY valid JSON, no explanation or markdown
- {schema_description}"""

    raw = ask_about_image(image_path, prompt, max_tokens=2048, max_dimension=1600)

    # Strip markdown code fences if present
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])  # remove first and last lines

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # One retry with explicit correction
        correction_prompt = f"""Your previous response was not valid JSON.
The schema is:
{schema_str}

Return ONLY the JSON object, nothing else. No markdown, no explanation."""
        raw2 = ask_about_image(image_path, correction_prompt, max_tokens=2048)
        raw2 = raw2.strip()
        if raw2.startswith("```"):
            lines = raw2.split("\n")
            raw2 = "\n".join(lines[1:-1])
        return json.loads(raw2)


# ──────────────────────────────────────────────
# Demo: run all examples
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python vision_api.py <image_path>")
        print("Using a sample test by creating a small test image...")

        # Create a test image with PIL for demo
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (400, 200), color="white")
        draw = ImageDraw.Draw(img)
        draw.text((20, 80), "Invoice #1234", fill="black")
        draw.text((20, 110), "Total: $99.99", fill="black")
        draw.text((20, 140), "Date: 2024-01-15", fill="black")
        img.save("/tmp/test_invoice.jpg")
        test_image = "/tmp/test_invoice.jpg"
    else:
        test_image = sys.argv[1]

    print("=" * 50)
    print("Example 1: General description")
    print("=" * 50)
    description = ask_about_image(test_image, "Describe what you see in this image.")
    print(description)

    print("\n" + "=" * 50)
    print("Example 2: Specific question")
    print("=" * 50)
    answer = ask_about_image(
        test_image,
        "Is there any text visible in this image? If yes, list all text you can read."
    )
    print(answer)

    print("\n" + "=" * 50)
    print("Example 3: Structured extraction")
    print("=" * 50)
    result = extract_structured(
        test_image,
        schema_description="Extract invoice/receipt information",
        example_schema={
            "invoice_number": None,
            "date": None,
            "total_amount": None,
            "vendor": None
        }
    )
    print(json.dumps(result, indent=2))
```

---

## Using a URL Instead of Local File

```python
def ask_about_url(image_url: str, question: str, model: str = "claude-opus-4-6") -> str:
    """Ask about an image hosted at a public URL."""
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "url",
                        "url": image_url,
                    }
                },
                {"type": "text", "text": question}
            ]
        }]
    )
    return response.content[0].text


# Usage
result = ask_about_url(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png",
    "What is shown in this image?"
)
print(result)
```

---

## Comparing Two Images

```python
def compare_two_images(path1: str, path2: str, question: str) -> str:
    """Compare two local images."""
    data1, mt1 = encode_image(path1)
    data2, mt2 = encode_image(path2)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Image 1:"},
                {"type": "image", "source": {"type": "base64", "media_type": mt1, "data": data1}},
                {"type": "text", "text": "Image 2:"},
                {"type": "image", "source": {"type": "base64", "media_type": mt2, "data": data2}},
                {"type": "text", "text": question}
            ]
        }]
    )
    return response.content[0].text
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Code_Cookbook.md](./Code_Cookbook.md) | 10 vision use cases |

⬅️ **Prev:** [03 — Image Understanding](../03_Image_Understanding/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Audio and Speech AI](../05_Audio_and_Speech_AI/Theory.md)
