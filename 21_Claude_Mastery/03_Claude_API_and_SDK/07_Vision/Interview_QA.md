# Vision — Interview Q&A

## Beginner Questions

**Q1: How do you send an image to Claude in the API?**

A: You include an `image` content block in the user message's `content` array. The block has a `type: "image"` field and a `source` field specifying either `base64` (the image data encoded as base64) or `url` (a public URL to the image). You also specify `media_type` matching the image format (e.g., `image/jpeg`, `image/png`).

---

**Q2: What image formats does Claude support?**

A: JPEG (`.jpg`/`.jpeg`), PNG (`.png`), GIF (`.gif`, first frame only), and WebP (`.webp`). Images up to 5MB per image and 8000×8000 pixels maximum. You can send up to 20 images in a single request.

---

**Q3: What is the difference between `base64` and `url` source types for images?**

A: With `base64`, you read the image file, encode its bytes as base64, and include the encoded string directly in the request body. With `url`, you provide a public HTTPS URL and Claude's servers fetch the image. Use base64 for local files, private/authenticated images, or when you want guaranteed delivery. Use URL for publicly accessible images to keep request payload size smaller.

---

**Q4: Can you send multiple images in a single request?**

A: Yes. Include multiple `image` content blocks in the `content` array, interleaved with `text` blocks for labels or questions. Claude can reason across all of them simultaneously. The maximum is 20 images per request.

---

## Intermediate Questions

**Q5: How does Claude's vision capability count tokens for images?**

A: Images are divided into 512×512 pixel tiles. Each tile costs approximately 170 tokens. There's also a base cost of 85 tokens per image. A 1568×1568 image requires a 3×3 grid of tiles (9 tiles), costing roughly 9×170+85 = 1,615 tokens. To minimize cost, resize images to ~1568px on the longest side before encoding — this captures enough detail for analysis while avoiding excessive tiling.

---

**Q6: What order should you put images and text in the content array?**

A: For single-image analysis, place the image block first, then the question text. This matches how humans naturally present visual information. For multi-image analysis, label each image with a descriptive text block immediately before it: "Image 1 — January sales:" followed by the image block. End with your final question after all images. This labeling helps Claude track which image is which during analysis.

---

**Q7: What are practical limitations of Claude's vision capability?**

A: (1) No video — only static images (or first frame of GIFs). (2) No image generation — Claude can only analyze, not create images. (3) URLs must be publicly accessible — authenticated URLs (signed S3, etc.) may not work reliably. (4) Very small text in images may not be accurately read if resolution is low. (5) Complex mathematical equations in images are better analyzed if you also provide the text version. (6) Extremely detailed diagrams with many overlapping elements may lose detail.

---

**Q8: How would you build an OCR pipeline using Claude's vision API?**

A: Send each document page as a base64-encoded image with a system prompt like "Extract all text from this image. Preserve formatting where possible. Return the text only, no commentary." Use PNG for best quality with text-heavy documents (lossless). Process pages sequentially or in small batches. For structured documents (forms, tables), add instructions like "Extract as JSON with field names and values." Post-process the output if you need clean formatting. For production, cache results to avoid re-extracting the same pages.

---

## Advanced Questions

**Q9: Design a production system that automatically analyzes uploaded product photos and generates descriptions for an e-commerce catalog.**

A: Architecture: (1) Image upload endpoint receives photo, validates format and size, stores in S3. (2) Async worker picks up the S3 key from a queue. (3) Worker downloads image, resizes to ≤1568px longest side (saves ~30-50% tokens), re-encodes as JPEG at 85% quality. (4) Sends to Claude with system prompt: "You are a product copywriter. Analyze this product image and write a 2-3 sentence description covering appearance, material (if visible), and use case." (5) Returns generated description and stores in database. (6) Monitoring: log image dimensions, token cost, latency, and output length per image. Budget alert at $X/day. For scale: batch multiple images using the Batches API at 50% cost reduction.

---

**Q10: How does vision interact with tool use? Describe a scenario where you'd combine both.**

A: Claude can analyze an image and decide to call tools based on what it sees. Example: a screenshot of a web page where Claude identifies a broken UI element, then calls a `create_bug_report(title, description, severity)` tool with the findings. Implementation: include both the image and tool definitions in the same request. Claude's visual reasoning produces the tool call arguments. In a chart-analysis agent: the image arrives, Claude reads the chart and calls `store_data_point(metric_name, value, timestamp)` for each data point visible in the graph, populating a database from visual data.

---

**Q11: What strategies reduce image token costs in a high-volume production system?**

A: (1) Resize before sending: downscale to ≤1568px longest side — maintains analysis quality, reduces tiles. (2) Format choice: JPEG at 85% quality is 3-5x smaller than PNG for photos (fewer bytes, but same tile count — matters for 5MB limit). PNG is better for screenshots and diagrams (lossless). (3) Use URL source for public images to reduce HTTP payload (but token cost is the same). (4) Cache results: if you analyze the same image repeatedly (e.g., a company logo in every ticket), cache Claude's description and skip re-sending. (5) Prompt caching: if your system prompt is large and repeated across many image requests, cache it. (6) Model routing: use Haiku for simple image tasks (label, yes/no classification) and Sonnet only for complex analysis.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Streaming](../06_Streaming/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Prompt Engineering](../08_Prompt_Engineering/Interview_QA.md)
