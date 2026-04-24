# Using Vision APIs — Interview Q&A

## Beginner Level

**Q1: What is a vision API?**

<details>
<summary>💡 Show Answer</summary>

**A:** A vision API is an API endpoint where you send an image (plus a text prompt) and receive a text response from an AI model. The model is hosted by the provider — you don't need to run anything locally. Examples: Claude Vision API (Anthropic), GPT-4V (OpenAI), Gemini Vision (Google). They all follow the same pattern: image + question in, text answer out.

</details>

**Q2: What are the two main ways to send images to a vision API?**

<details>
<summary>💡 Show Answer</summary>

**A:** (1) **Base64 encoding**: Read the image file as bytes, encode to base64 string, embed in the JSON payload. Works for local files, more reliable for production. (2) **URL**: Include a public URL pointing to the image. The API provider fetches it. Simpler for hosted images but dependent on URL availability and access. For production systems, base64 is preferred.

</details>

**Q3: Why does image resolution affect API cost?**

<details>
<summary>💡 Show Answer</summary>

**A:** Vision APIs convert images into tokens — the same unit as text tokens. Larger images produce more tokens (more patches to encode), and cost is measured in tokens. A 2000×2000 image might cost 4x as much as a 1000×1000 image. Resizing images to the minimum resolution needed for the task is an easy cost optimization.

</details>

---

## Intermediate Level

**Q4: What media types do vision APIs typically support?**

<details>
<summary>💡 Show Answer</summary>

**A:** Most major APIs support JPEG, PNG, GIF (static, first frame only), and WebP. JPEG is the most common and efficient for photos. PNG for diagrams or images with text where lossless quality matters. Always check the specific API documentation, as limits and supported types vary by provider.

</details>

**Q5: How do you handle multiple images in a single vision API call?**

<details>
<summary>💡 Show Answer</summary>

**A:** Most vision APIs (Claude, GPT-4V, Gemini) accept multiple image content blocks in a single message. You interleave image and text blocks in the message content array. For example:
```json
"content": [
  {"type": "text", "text": "Image 1:"},
  {"type": "image", "source": {...}},
  {"type": "text", "text": "Image 2:"},
  {"type": "image", "source": {...}},
  {"type": "text", "text": "What differences do you see?"}
]
```
Label each image clearly in text so the model can reference them.

</details>

**Q6: What prompt engineering techniques work best for vision tasks?**

<details>
<summary>💡 Show Answer</summary>

**A:** Key techniques:
1. **Be specific about what to examine**: "Focus on the welds in the lower left corner" not "describe the image"
2. **Guide output format explicitly**: "Return JSON with keys: defect_found, location, severity"
3. **Binary questions for classification**: "Answer only YES or NO: Is the package sealed correctly?"
4. **Chain of thought for reasoning**: "First describe what you see, then assess whether it meets spec"
5. **Label multiple images**: "Image 1 (reference):" / "Image 2 (inspection):"
6. **Specify what NOT to include**: "Do not describe people, only the product"

</details>

**Q7: How do you implement robust error handling for vision API calls in production?**

<details>
<summary>💡 Show Answer</summary>

**A:** Three layers:
1. **API-level errors**: Rate limit errors → retry with exponential backoff. Content policy errors → log and skip. Image too large → resize and retry.
2. **Output parsing errors**: JSON parse failures → retry with correction prompt or log for human review.
3. **Business logic validation**: Validate extracted values against expected ranges (a total on a receipt shouldn't be negative, a date should parse correctly, etc.) using Pydantic or similar.
Always have a fallback path (human review queue) for failed cases.

</details>

---

## Advanced Level

**Q8: How would you design a cost-efficient vision pipeline for processing 10,000 product photos per day?**

<details>
<summary>💡 Show Answer</summary>

**A:** Cost optimization strategy:
1. **Resolution optimization**: Resize all images to 800px max dimension before sending. For most product classification tasks, this preserves sufficient detail.
2. **Model selection**: Use Claude Haiku or Gemini Flash for high-volume, simpler tasks (classification, presence detection). Reserve Sonnet/GPT-4o for complex extraction or reasoning.
3. **Two-stage pipeline**: Use cheap model for initial filtering ("does this image contain text?"), only send text-containing images to expensive OCR model.
4. **Caching**: Hash image content, cache results. If the same product photo appears multiple times (reprocessing), serve from cache.
5. **Batch timing**: Process non-urgent images during off-peak hours for potentially lower API costs.
6. **Result storage**: Store extraction results so images are never processed twice.
Estimated: at $0.002/image with Haiku = $20/day for 10,000 images. Acceptable for most use cases.

</details>

**Q9: What are the key differences between Claude Vision, GPT-4V, and Gemini for production use?**

<details>
<summary>💡 Show Answer</summary>

**A:** Trade-offs as of early 2025:
- **Claude Vision (Sonnet/Opus)**: Strongest for document understanding and following complex instructions. Good at structured extraction. Strong safety filtering.
- **GPT-4V / GPT-4o**: Strong visual reasoning, good at charts and diagrams, established API ecosystem. GPT-4o supports image generation too.
- **Gemini Flash**: Very fast, very cheap, best for high-volume simple tasks. Long context window (1M tokens) allows mixing many images with text.
- **Gemini Pro**: Best for video (long video understanding), strong multimodal reasoning.
For document parsing: Claude. For speed + cost: Gemini Flash. For visual reasoning: GPT-4o. Always benchmark on your specific task — capabilities evolve quickly.

</details>

**Q10: System design question: How would you build a real-time receipt processing API?**

<details>
<summary>💡 Show Answer</summary>

**A:** Architecture:
1. **Upload endpoint**: Accepts image file, validates format and size, uploads to S3 with unique ID
2. **Preprocessing step** (async): Resize to 1200px max, auto-rotate if EXIF data indicates rotation, convert to JPEG
3. **Vision API call**: Send to Claude Haiku (cost-efficient for receipts) with strict JSON extraction prompt, Pydantic schema for validation
4. **Retry and fallback**: If JSON parse fails → retry once with correction prompt → if still fails → queue for human review
5. **Result storage**: Store extracted JSON in database with image ID, model used, processing time, confidence indicator
6. **Response**: Return extracted JSON immediately if fast (<3s) or poll pattern if slow
Key metrics to monitor: success rate, average extraction accuracy (spot-check), p95 latency, cost per receipt.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Send image to Claude Vision API |
| [📄 Code_Cookbook.md](./Code_Cookbook.md) | 10 vision use cases |

⬅️ **Prev:** [03 — Image Understanding](../03_Image_Understanding/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Audio and Speech AI](../05_Audio_and_Speech_AI/Theory.md)
