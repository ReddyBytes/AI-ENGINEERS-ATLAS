# Image Understanding — Interview Q&A

## Beginner Level

**Q1: What is Visual Question Answering (VQA)?**
**A:** VQA is a task where an AI system is given an image and a natural-language question about that image, and must return a natural-language answer. For example: image of a kitchen + "How many apples are on the counter?" → "There are 3 apples." Modern VQA uses vision-language models that process the image and question together and generate the answer using a language model decoder.

**Q2: What is visual grounding?**
**A:** Visual grounding is the task of locating a specific object or region in an image given a text description. Input: an image and a phrase like "the person wearing the blue jacket on the right." Output: bounding box coordinates identifying where that person is in the image. It's harder than simple object detection because it requires understanding attributes, relationships, and disambiguation.

**Q3: How is AI-based OCR different from traditional OCR?**
**A:** Traditional OCR (like Tesseract) extracts characters by pattern matching — it reads text but doesn't understand context or structure. AI-based document understanding goes further: it understands layout (this label applies to that value), handles varied formats without configuration, can extract structured data (return JSON with specific fields), and handles degraded documents better. It reads text *and* understands what the text means in context.

---

## Intermediate Level

**Q4: How does modern VQA work mechanically?**
**A:** Modern VQA is implemented as conditional text generation using a VLM:
1. Encode the image through a visual encoder (ViT) → patch embeddings
2. Project visual embeddings to LLM token space via projection layer
3. Concatenate visual tokens + tokenized question
4. Feed the combined sequence to an LLM decoder
5. The decoder generates the answer token by token, attending to both visual and text tokens at each step
The question effectively serves as attention guidance — "how many chairs?" makes the model focus on sitting objects in the image.

**Q5: What are the main approaches to document understanding?**
**A:** Three main approaches:
1. **Traditional OCR + NLP**: Extract text with Tesseract, then parse/extract with NLP. Fast but loses layout information.
2. **Layout-aware models** (LayoutLM, DocFormer): Encode text positions as additional features alongside text tokens. Better for form understanding.
3. **End-to-end VLMs** (GPT-4V, Claude Vision, Donut): Process the document as an image, extract structure and content in one step. Most flexible but higher cost.
For most production use cases, approach 3 is now preferred due to flexibility and accuracy, despite higher cost per call.

**Q6: What is image captioning and how does it differ from VQA?**
**A:** Image captioning generates a descriptive text summary of the whole image — it's VQA with the implicit question "describe this image." The key differences:
- **VQA**: specific question → focused answer, often short
- **Captioning**: comprehensive coverage of the whole scene
- **Captioning** must decide what's important to mention (saliency selection)
- **VQA** focuses on answering precisely
In practice, with modern VLMs you implement both by prompting: "Describe this image" for captioning vs your specific question for VQA.

---

## Advanced Level

**Q7: What are the main failure modes of vision models for document understanding in production?**
**A:** Key failure modes:
1. **Hallucinated field values**: The model fills in a field it can't see with a plausible-sounding value. Mitigation: validate outputs, include "return null if not present" in prompts, check for values that appear in no image region.
2. **Layout confusion**: On complex multi-column forms, the model assigns values to wrong labels. Mitigation: pre-process to clean layout, crop into sections.
3. **Rare document types**: Models trained on common formats (invoices, receipts) may perform poorly on unusual formats. Mitigation: few-shot examples in prompt.
4. **Low-quality scans**: Skewed, blurry, or low-contrast documents degrade accuracy significantly. Mitigation: preprocessing pipeline (deskew, denoise, contrast enhancement).
5. **Structured output format failures**: Malformed JSON, missing brackets. Mitigation: always wrap in try/except, retry with correction prompt.

**Q8: How would you build a production-grade receipt extraction system?**
**A:** Architecture:
1. **Input validation**: Check image is legible (resolution, not corrupted)
2. **Preprocessing**: Deskew if rotated, auto-crop to remove borders, normalize contrast
3. **VLM call**: Send to Claude/GPT-4V with strict JSON schema prompt: `{"vendor": null, "date": null, "total": null, "items": [{"description": null, "amount": null}]}`
4. **Output validation**: Parse JSON, validate with Pydantic schema, check for nulls vs expected non-nulls
5. **Retry logic**: On parse failure, retry with "Your previous response was invalid JSON. Return only valid JSON: " + previous response + "Fix it."
6. **Confidence signaling**: Return extracted data + flag fields where the model said "not visible" vs fields that are null
7. **Human review queue**: Route low-confidence extractions to human review
8. **Cost monitoring**: Track per-call cost, batch process overnight for non-urgent receipts

**Q9: Why are VLMs still unreliable for spatial reasoning tasks?**
**A:** Spatial reasoning ("is A to the left of B?", "is A above B?") is difficult for several reasons:
1. **Training data imbalance**: Most image-caption training data describes *what* is in images, not *where* things are relative to each other
2. **Coordinate-free architecture**: Standard VLMs don't represent absolute positions explicitly — they use attention over patch tokens which is permutation-sensitive but not spatially grounded
3. **Reference frame ambiguity**: "left" could mean the viewer's left or the subject's left
4. **Occlusion and perspective**: 3D relationships projected onto 2D images lose depth information
Specialized grounding models (like Florence-2, SAM) or adding explicit coordinate tokens (like Paligemma's approach) help but don't fully solve the problem.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | VQA with vision model API |

⬅️ **Prev:** [02 — Vision Language Models](../02_Vision_Language_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — Using Vision APIs](../04_Using_Vision_APIs/Theory.md)
