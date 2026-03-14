# Vision API Code Cookbook — 10 Use Cases

Each recipe is self-contained. All use Claude Vision API. Adapt prompts and schemas for your use case.

---

## Setup (all recipes share this)

```python
import anthropic
import base64
import json
from pathlib import Path
from PIL import Image
import io

client = anthropic.Anthropic()

def encode_image(path: str, max_dim: int = 1200) -> tuple[str, str]:
    ext = Path(path).suffix.lower()
    mt_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".png": "image/png", ".webp": "image/webp"}
    mt = mt_map.get(ext, "image/jpeg")
    with Image.open(path) as img:
        if img.mode in ("RGBA", "P") and mt == "image/jpeg":
            img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG" if mt == "image/jpeg" else "PNG", quality=85)
        return base64.standard_b64encode(buf.getvalue()).decode(), mt

def vision(image_path: str, prompt: str, max_tokens: int = 2048) -> str:
    data, mt = encode_image(image_path)
    r = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": mt, "data": data}},
            {"type": "text", "text": prompt}
        ]}]
    )
    return r.content[0].text

def vision_json(image_path: str, prompt: str) -> dict:
    raw = vision(image_path, prompt, max_tokens=4096)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])
    return json.loads(raw)
```

---

## Recipe 1: Receipt / Invoice Parsing

Extract structured data from any receipt or invoice photo.

```python
def parse_receipt(image_path: str) -> dict:
    prompt = """Extract all information from this receipt/invoice as JSON:
{
  "vendor_name": null,
  "vendor_address": null,
  "date": null,
  "invoice_number": null,
  "line_items": [{"description": null, "quantity": null, "unit_price": null, "total": null}],
  "subtotal": null,
  "tax": null,
  "tax_rate_percent": null,
  "total": null,
  "payment_method": null
}
Use null for missing fields. All amounts as numbers without currency symbols. Return ONLY JSON."""
    return vision_json(image_path, prompt)

# Usage
receipt = parse_receipt("receipt.jpg")
print(f"Total: ${receipt['total']}")
print(f"Items: {len(receipt['line_items'])}")
```

---

## Recipe 2: Business Card Extraction

```python
def parse_business_card(image_path: str) -> dict:
    prompt = """Extract all contact information from this business card as JSON:
{
  "name": null,
  "title": null,
  "company": null,
  "email": null,
  "phone": null,
  "mobile": null,
  "website": null,
  "address": null,
  "linkedin": null,
  "other": null
}
Return ONLY the JSON object."""
    return vision_json(image_path, prompt)

card = parse_business_card("bizcard.jpg")
print(f"Contact: {card['name']} at {card['company']}")
```

---

## Recipe 3: Chart / Graph Data Reading

```python
def read_chart(image_path: str) -> dict:
    prompt = """Analyze this chart or graph and extract:
{
  "chart_type": "bar/line/pie/scatter/other",
  "title": null,
  "x_axis_label": null,
  "y_axis_label": null,
  "data_series": [
    {
      "series_name": null,
      "data_points": [{"label": null, "value": null}]
    }
  ],
  "key_insight": "one sentence summary of what the chart shows"
}
Be as accurate as possible reading values. Return ONLY JSON."""
    return vision_json(image_path, prompt)

chart_data = read_chart("quarterly_sales.png")
print(f"Chart: {chart_data['title']}")
for series in chart_data['data_series']:
    print(f"  {series['series_name']}: {series['data_points']}")
```

---

## Recipe 4: Product Damage Assessment (Insurance / QC)

```python
def assess_damage(image_path: str, product_type: str = "product") -> dict:
    prompt = f"""Inspect this image of a {product_type} for damage or defects.

Return your assessment as JSON:
{{
  "damage_detected": true/false,
  "damage_level": "none/minor/moderate/severe",
  "damage_locations": ["description of each damage location"],
  "damage_types": ["scratch/dent/crack/stain/tear/other"],
  "estimated_repair_needed": true/false,
  "confidence": "high/medium/low",
  "notes": "any additional observations"
}}
Return ONLY JSON."""
    return vision_json(image_path, prompt)

assessment = assess_damage("car_photo.jpg", "car bumper")
if assessment["damage_detected"]:
    print(f"Damage found: {assessment['damage_level']} severity")
    for loc in assessment["damage_locations"]:
        print(f"  - {loc}")
```

---

## Recipe 5: Automatic Alt-Text Generation (Accessibility)

```python
def generate_alt_text(image_path: str, context: str = "") -> dict:
    context_note = f"Context: this image appears in {context}. " if context else ""
    prompt = f"""{context_note}Generate accessibility alt text for this image.

Return as JSON:
{{
  "short_alt": "brief alt text under 125 characters for screen readers",
  "long_description": "detailed description for complex images (2-4 sentences)",
  "is_decorative": false,
  "contains_text": true/false,
  "text_content": "exact text if any is visible"
}}
Return ONLY JSON."""
    return vision_json(image_path, prompt)

alt = generate_alt_text("hero_banner.jpg", context="a marketing email")
print(f'Alt: {alt["short_alt"]}')
```

---

## Recipe 6: Screenshot → Code or Description

```python
def screenshot_to_description(image_path: str, output_type: str = "description") -> str:
    if output_type == "html":
        prompt = """This is a UI screenshot. Generate HTML + CSS that recreates this layout.
Focus on structure and layout, not pixel-perfect styling.
Return only the HTML code."""
    elif output_type == "spec":
        prompt = """This is a UI/UX design. Write a technical specification describing:
1. Layout and structure
2. All UI components present
3. Colors and typography (approximate)
4. Interactive elements (buttons, forms, etc.)
5. Content hierarchy"""
    else:
        prompt = """Describe this screenshot in detail:
- What application or webpage is shown
- What content is visible
- What actions are available
- Current state (loading, error, success, etc.)"""

    return vision(image_path, prompt, max_tokens=4096)

desc = screenshot_to_description("app_screen.png", "spec")
print(desc)
```

---

## Recipe 7: Document Digitization (Forms, Tables)

```python
def digitize_form(image_path: str, form_fields: list[str]) -> dict:
    fields_schema = {field: None for field in form_fields}
    prompt = f"""Extract the values from this form or document.
Fields to extract (use null if not found):
{json.dumps(fields_schema, indent=2)}

Return ONLY the JSON object with the extracted values."""
    return vision_json(image_path, prompt)

# Example: digitize a patient intake form
patient_data = digitize_form("intake_form.jpg", [
    "patient_name", "date_of_birth", "insurance_id",
    "primary_complaint", "allergies", "current_medications"
])
print(patient_data)
```

---

## Recipe 8: Shelf / Planogram Compliance Checking

```python
def check_shelf_compliance(shelf_image: str, planogram_image: str) -> dict:
    data1, mt1 = encode_image(shelf_image)
    data2, mt2 = encode_image(planogram_image)

    r = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "Image 1 - Required planogram (correct shelf arrangement):"},
            {"type": "image", "source": {"type": "base64", "media_type": mt2, "data": data2}},
            {"type": "text", "text": "Image 2 - Current shelf state:"},
            {"type": "image", "source": {"type": "base64", "media_type": mt1, "data": data1}},
            {"type": "text", "text": """Compare the current shelf to the planogram. Return JSON:
{
  "compliant": true/false,
  "compliance_score": 0-100,
  "issues": ["description of each non-compliance"],
  "missing_products": [],
  "misplaced_products": [],
  "recommendation": "brief action needed"
}
Return ONLY JSON."""}
        ]}]
    )
    raw = r.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.split("\n")[1:-1])
    return json.loads(raw)
```

---

## Recipe 9: Medical / Technical Image Triage (Requires Appropriate Permissions)

```python
def triage_image(image_path: str, domain: str, checklist: list[str]) -> dict:
    """
    General-purpose visual checklist evaluation.
    Use for non-diagnostic purposes: routing, filtering, flagging for expert review.
    NEVER use vision AI output as a final medical diagnosis.
    """
    checklist_str = "\n".join(f"- {item}: null (true/false/uncertain)" for item in checklist)
    prompt = f"""Evaluate this {domain} image against the following checklist.
For each item, respond true, false, or uncertain.

Checklist:
{checklist_str}

Return as JSON where each checklist item is a key with value: true/false/uncertain.
Add a "flag_for_review" key: true if ANY item is true or uncertain.
Add a "notes" key with any observations.
Return ONLY JSON."""

    result = vision_json(image_path, prompt)
    return result

# Example: routing flag for review
flags = triage_image(
    "submission_photo.jpg",
    domain="product photo",
    checklist=[
        "image is blurry",
        "product is not centered",
        "background is not white",
        "watermark visible",
        "product is damaged"
    ]
)
if flags.get("flag_for_review"):
    print("NEEDS REVIEW:", [k for k, v in flags.items() if v is True and k not in ["flag_for_review"]])
```

---

## Recipe 10: Multi-Image Report Generator

```python
def generate_image_report(image_paths: list[str], report_topic: str) -> str:
    """Generate a structured report analyzing multiple images together."""

    content = []
    for i, path in enumerate(image_paths, 1):
        data, mt = encode_image(path, max_dim=800)
        content.append({"type": "text", "text": f"Image {i} ({Path(path).name}):"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": mt, "data": data}})

    content.append({"type": "text", "text": f"""Analyze all {len(image_paths)} images above and generate a report on: {report_topic}

Structure your report as:
## Executive Summary
[2-3 sentences]

## Key Findings
[bullet points, one per major observation]

## Image-by-Image Analysis
[brief note on each image numbered 1-{len(image_paths)}]

## Recommendations
[actionable next steps]"""})

    r = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": content}]
    )
    return r.content[0].text

# Usage: analyze 5 inspection photos
report = generate_image_report(
    ["inspection_1.jpg", "inspection_2.jpg", "inspection_3.jpg"],
    report_topic="equipment condition and maintenance needs"
)
print(report)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Core vision helper |
| 📄 **Code_Cookbook.md** | ← you are here |

⬅️ **Prev:** [03 — Image Understanding](../03_Image_Understanding/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Audio and Speech AI](../05_Audio_and_Speech_AI/Theory.md)
