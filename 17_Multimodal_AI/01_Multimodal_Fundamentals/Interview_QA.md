# Multimodal AI Fundamentals — Interview Q&A

## Beginner Level

**Q1: What does "multimodal" mean in AI?**

<details>
<summary>💡 Show Answer</summary>

**A:** Multimodal means the system works with more than one type of data (modality). The main modalities are text, images, audio, and video. A multimodal AI can accept, process, or generate across these types — for example, taking an image and a text question as input and returning a text answer.

</details>

<br>

**Q2: What is a modality?**

<details>
<summary>💡 Show Answer</summary>

**A:** A modality is a distinct type or channel of information. Text is one modality. Images are another. Audio is another. Each requires a different kind of encoder to convert it into a format the model can work with.

</details>

<br>

**Q3: Can you give examples of multimodal AI systems?**

<details>
<summary>💡 Show Answer</summary>

**A:** Yes:
- Claude 3 (Vision): accepts images and text, returns text
- Whisper: accepts audio, returns text
- DALL-E 3: accepts text, returns images
- GPT-4V: accepts images and text, returns text
- Gemini 1.5 Pro: accepts images, audio, video, and text, returns text

</details>

<br>

**Q4: Why is multimodal AI useful?**

<details>
<summary>💡 Show Answer</summary>

**A:** The real world is multimodal. A user asking about a product might upload a photo. A customer support bot might need to read a scanned form. A meeting assistant needs to process spoken audio. Limiting AI to one modality means it can't handle these naturally multimodal tasks.

</details>

---

## Intermediate Level

**Q5: What are the three main fusion strategies in multimodal AI?**

<details>
<summary>💡 Show Answer</summary>

**A:**
1. **Early fusion**: Combine raw inputs before encoding. Simple but loses modality-specific structure. Rarely used.
2. **Late fusion**: Each modality is processed completely separately, and only the final predictions are combined. Easy but modalities can't inform each other's understanding.
3. **Cross-attention fusion**: The dominant modern approach. Text tokens attend to image tokens (using the transformer attention mechanism). Each modality can influence how the other is interpreted.

</details>

<br>

**Q6: What is the "alignment problem" in multimodal AI?**

<details>
<summary>💡 Show Answer</summary>

**A:** When you train a text encoder and an image encoder separately, their embedding spaces are completely unrelated — the number vector for the word "dog" has no mathematical relationship to the number vector for a photo of a dog. To make multimodal reasoning work, these spaces must be aligned. You do this through joint training with contrastive loss, forcing matching pairs (image + its caption) to have similar embeddings.

</details>

<br>

**Q7: What is contrastive loss and why is it used?**

<details>
<summary>💡 Show Answer</summary>

**A:** Contrastive loss is a training objective that pulls matching pairs together in embedding space and pushes non-matching pairs apart. For a batch of image-text pairs: the correct pairing (image_i, text_i) should have high cosine similarity, while wrong pairings (image_i, text_j where i≠j) should have low similarity. This is how CLIP creates a shared embedding space where images and text with similar meaning end up near each other.

</details>

<br>

**Q8: What is a projection layer in a vision-language model?**

<details>
<summary>💡 Show Answer</summary>

**A:** A projection layer is a small neural network (usually a linear transformation or MLP) that maps from one embedding space to another. When you connect a pre-trained image encoder (like CLIP's visual encoder) to a pre-trained LLM, their embedding dimensions and learned representations don't match. The projection layer translates image embeddings into the token embedding space that the LLM understands — acting like a translator between two languages.

</details>

---

## Advanced Level

**Q9: How does cross-attention fusion work mechanically?**

<details>
<summary>💡 Show Answer</summary>

**A:** In cross-attention, one sequence provides queries (Q) and the other provides keys (K) and values (V). For vision-language models: text tokens become queries, image patch tokens become keys and values. Each text token computes attention weights over all image patches — determining how much each image region is relevant to that text token. The output is enriched text token representations that contain information drawn from relevant image regions. This lets the model reason like: "the word 'red' in the question should attend to the reddish patches in the image."

</details>

<br>

**Q10: What are the key cost and latency trade-offs when adding vision to an application?**

<details>
<summary>💡 Show Answer</summary>

**A:** Vision API calls are typically 3–10x more expensive than text-only calls. The cost scales with image resolution (more pixels = more tokens). Key trade-offs:
- High-resolution images: more tokens, higher cost, better detail
- Low-resolution or downsampled: cheaper but might miss important details
- Processing video as frames: costs multiply per frame (can be extremely expensive)
- Always calculate cost per call before building and set resolution appropriately for the task

</details>

<br>

**Q11: What limitations do current vision models still have?**

<details>
<summary>💡 Show Answer</summary>

**A:** Despite impressive capabilities, current models consistently struggle with:
- **Precise spatial reasoning**: "Is object A to the left or right of object B?" often fails
- **Small text in images**: Text smaller than ~12pt in a typical photo is unreliable
- **Exact counting**: Counting objects over ~10 in a cluttered image
- **Complex diagrams**: Technical schematics, circuit diagrams, complex charts
- **Subtle visual differences**: Distinguishing near-identical objects
Always test your specific use case empirically — don't assume vision models are universally capable.

</details>

<br>

**Q12: System design question: How would you build a multimodal customer support system that handles text questions, image uploads, and voice messages?**

<details>
<summary>💡 Show Answer</summary>

**A:** Architecture:
1. **Input routing**: Detect input type (text / image / audio) and route accordingly
2. **Audio processing**: Send voice messages to Whisper (or similar STT) → transcribed text
3. **Image processing**: Send images with question to Vision LLM (Claude/GPT-4V)
4. **Text processing**: Standard LLM call for text-only questions
5. **Unified context**: All processed inputs get merged into a single context string for the main LLM
6. **RAG layer**: Retrieve relevant support documents based on the combined context
7. **Response generation**: LLM generates final response
Key considerations: async processing for audio (latency), image size limits, cost monitoring per modality, graceful degradation if vision API is unavailable.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Section 16 — Deployment](../../16_Deployment/) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 — Vision Language Models](../02_Vision_Language_Models/Theory.md)
