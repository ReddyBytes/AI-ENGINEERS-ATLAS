# Image Understanding — Code Examples

## Setup

```python
import anthropic
import base64
import json
from pathlib import Path

client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var
```

---

## Example 1: Basic Visual Question Answering

```python
def vqa(image_path: str, question: str) -> str:
    """Ask any question about a local image."""

    # Read and encode the image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Detect media type from file extension
    ext = Path(image_path).suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_type_map.get(ext, "image/jpeg")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
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
                    {
                        "type": "text",
                        "text": question
                    }
                ],
            }
        ],
    )

    return response.content[0].text


# Usage
answer = vqa("photo.jpg", "What objects are visible in this image?")
print(answer)

answer = vqa("receipt.jpg", "What is the total amount on this receipt?")
print(answer)
```

---

## Example 2: Image Captioning

```python
def caption_image(image_path: str, detail_level: str = "standard") -> str:
    """Generate a caption for an image.

    detail_level: "brief" | "standard" | "detailed"
    """

    prompts = {
        "brief": "Describe this image in one sentence.",
        "standard": "Describe this image in 2-3 sentences. Include the main subjects, setting, and any notable details.",
        "detailed": """Describe this image in detail. Include:
- Main subjects and their actions
- Background and setting
- Colors, lighting, and atmosphere
- Any text visible in the image
- Overall mood or story of the scene"""
    }

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}
                },
                {
                    "type": "text",
                    "text": prompts[detail_level]
                }
            ]
        }]
    )

    return response.content[0].text


# Usage
print(caption_image("scene.jpg", "detailed"))
```

---

## Example 3: Document / Receipt Extraction

```python
from pydantic import BaseModel
from typing import Optional

class ReceiptItem(BaseModel):
    description: str
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total: float

class Receipt(BaseModel):
    vendor_name: Optional[str] = None
    date: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    items: list[ReceiptItem] = []


def extract_receipt(image_path: str) -> Receipt:
    """Extract structured data from a receipt image."""

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    prompt = """Extract all information from this receipt as JSON matching this exact schema:
{
  "vendor_name": "string or null",
  "date": "YYYY-MM-DD format or null",
  "subtotal": number or null,
  "tax": number or null,
  "total": number or null,
  "items": [
    {
      "description": "string",
      "quantity": number or null,
      "unit_price": number or null,
      "total": number
    }
  ]
}

Rules:
- Use null for any field not visible in the receipt
- All monetary values as numbers (no currency symbols)
- Return ONLY the JSON, no other text"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}
                },
                {"type": "text", "text": prompt}
            ]
        }]
    )

    raw_json = response.content[0].text.strip()

    # Remove markdown code blocks if present
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:]

    data = json.loads(raw_json)
    return Receipt(**data)


# Usage
try:
    receipt = extract_receipt("receipt.jpg")
    print(f"Vendor: {receipt.vendor_name}")
    print(f"Total: ${receipt.total}")
    print(f"Items: {len(receipt.items)}")
    for item in receipt.items:
        print(f"  - {item.description}: ${item.total}")
except json.JSONDecodeError as e:
    print(f"Failed to parse JSON: {e}")
except Exception as e:
    print(f"Extraction failed: {e}")
```

---

## Example 4: OCR — Extract All Text from Image

```python
def extract_text_from_image(image_path: str, preserve_structure: bool = True) -> str:
    """Extract all visible text from an image."""

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    if preserve_structure:
        prompt = """Extract all text visible in this image.
Preserve the original layout and structure as much as possible using spacing and line breaks.
Output only the extracted text, nothing else."""
    else:
        prompt = "Extract all text visible in this image. Output only the text, nothing else."

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}
                },
                {"type": "text", "text": prompt}
            ]
        }]
    )

    return response.content[0].text


# Usage
text = extract_text_from_image("document.png", preserve_structure=True)
print(text)
```

---

## Example 5: Multi-Image Comparison

```python
def compare_images(image_path_1: str, image_path_2: str, comparison_question: str) -> str:
    """Compare two images and answer a question about the comparison."""

    def load_image(path):
        with open(path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")

    img1 = load_image(image_path_1)
    img2 = load_image(image_path_2)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Image 1:"},
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img1}},
                {"type": "text", "text": "Image 2:"},
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img2}},
                {"type": "text", "text": comparison_question}
            ]
        }]
    )

    return response.content[0].text


# Usage examples
diff = compare_images(
    "before.jpg",
    "after.jpg",
    "What differences do you see between Image 1 (before) and Image 2 (after)?"
)
print(diff)

defect = compare_images(
    "reference_part.jpg",
    "inspection_part.jpg",
    "Compare these two machine parts. Does the second part have any defects compared to the reference?"
)
print(defect)
```

---

## Example 6: Batch Image Processing

```python
from pathlib import Path
import concurrent.futures
from typing import NamedTuple

class ImageResult(NamedTuple):
    path: str
    answer: str
    error: str | None = None


def batch_vqa(image_paths: list[str], question: str, max_workers: int = 5) -> list[ImageResult]:
    """Ask the same question about multiple images in parallel."""

    def process_one(path: str) -> ImageResult:
        try:
            answer = vqa(path, question)
            return ImageResult(path=path, answer=answer)
        except Exception as e:
            return ImageResult(path=path, answer="", error=str(e))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_one, image_paths))

    return results


# Usage: screen 100 product photos for quality issues
image_files = list(Path("product_photos/").glob("*.jpg"))
results = batch_vqa(
    [str(p) for p in image_files],
    question="Is this product in good condition? Answer with: PASS, FAIL, or UNCERTAIN. Then briefly explain."
)

for result in results:
    if result.error:
        print(f"ERROR {result.path}: {result.error}")
    else:
        print(f"{result.path}: {result.answer[:100]}")
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

⬅️ **Prev:** [02 — Vision Language Models](../02_Vision_Language_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — Using Vision APIs](../04_Using_Vision_APIs/Theory.md)
