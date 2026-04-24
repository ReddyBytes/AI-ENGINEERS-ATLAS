# Vision-Language Models — Interview Q&A

## Beginner Level

**Q1: What is CLIP and what makes it special?**

<details>
<summary>💡 Show Answer</summary>

**A:** CLIP (Contrastive Language-Image Pre-training) is a model trained on 400 million image-caption pairs from the internet. It learns to map images and text into the same embedding space so that an image and its description end up close together mathematically. What makes it special is zero-shot transfer: it can classify images using arbitrary text labels it's never seen during training — no fine-tuning needed.

</details>

<br>

**Q2: What is LLaVA?**

<details>
<summary>💡 Show Answer</summary>

**A:** LLaVA (Large Language and Vision Assistant) is an open-source vision-language model that connects a visual encoder (CLIP's ViT) to a language model (originally Vicuna/LLaMA) via a projection layer. It can accept an image and a text question, and generate a text answer. It introduced visual instruction tuning — training on diverse instruction-following image-text data to make the model actually useful for real tasks.

</details>

<br>

**Q3: What is a Vision Transformer (ViT)?**

<details>
<summary>💡 Show Answer</summary>

**A:** ViT applies the transformer architecture to images. Instead of processing pixels directly, it splits the image into fixed-size patches (e.g., 16×16 pixels), flattens each patch into a vector, adds positional embeddings, and processes the resulting sequence through standard transformer layers. This lets the same self-attention mechanism used in language models work on visual content.

</details>

<br>

**Q4: What is zero-shot image classification with CLIP?**

<details>
<summary>💡 Show Answer</summary>

**A:** Zero-shot classification means classifying an image without any training examples for the target categories. With CLIP you: (1) encode the image into a vector, (2) encode each candidate label as "a photo of a {label}" into text vectors, (3) find which label vector is most similar (cosine similarity) to the image vector. No training needed — the shared embedding space handles it.

</details>

---

## Intermediate Level

**Q5: How does CLIP's contrastive training work?**

<details>
<summary>💡 Show Answer</summary>

**A:** CLIP trains on batches of (image, text) pairs. For each batch of N pairs, it computes an N×N similarity matrix between all image and text embeddings. The training objective (InfoNCE loss) maximizes the similarity of correct pairs (the diagonal) and minimizes the similarity of all incorrect pairings. With very large batches (CLIP used 32,768), each example has thousands of negatives, forcing the model to learn fine-grained distinctions. Temperature τ controls how sharp the similarity distribution is.

</details>

<br>

**Q6: What does the projection layer in LLaVA do and why is it needed?**

<details>
<summary>💡 Show Answer</summary>

**A:** The projection layer is a small trainable neural network (linear or MLP) that maps visual embeddings from the CLIP encoder's dimension to the LLM's token embedding dimension. It's needed because the visual encoder and the LLM were trained independently — their embedding spaces have different dimensions and different learned representations. The projection layer acts as a translator, converting visual representations into the "language" the LLM expects, so visual tokens can be processed alongside text tokens seamlessly.

</details>

<br>

**Q7: What is visual instruction tuning?**

<details>
<summary>💡 Show Answer</summary>

**A:** Visual instruction tuning is the training strategy where instead of only training on image-caption pairs (which teaches description), you train on diverse instruction-following data: "Describe this image in detail", "What is unusual about this scene?", "What text is visible?", "How many objects are there?", etc. This dramatically improves practical usefulness — the model learns to follow user instructions, not just caption images. LLaVA pioneered this approach.

</details>

<br>

**Q8: Why is CLIP's batch size so important for training quality?**

<details>
<summary>💡 Show Answer</summary>

**A:** Contrastive learning quality depends heavily on the number of negatives per example. With batch size N, each image has N-1 negative text examples to contrast against. Small batch sizes (e.g., 64) provide weak training signal — it's easy to distinguish "a photo of a cat" from "a photo of a car" using only 63 negatives. With 32,768 negatives, the model must learn very fine distinctions. This is why CLIP required enormous computational resources and why reproducing CLIP training at high quality is expensive.

</details>

---

## Advanced Level

**Q9: Compare CLIP and LLaVA architectures. When would you use each?**

<details>
<summary>💡 Show Answer</summary>

**A:**
- **CLIP**: Dual encoders, contrastive training, outputs similarity scores (not text). Best for: image-text retrieval, zero-shot classification, computing semantic similarity between images and text, building image search systems.
- **LLaVA**: CLIP encoder + projection + generative LLM. Outputs text. Best for: visual question answering, image description, instruction following about images, OCR, visual reasoning.
Rule of thumb: if you need a number/ranking → CLIP. If you need a text response → LLaVA-style VLM.

</details>

<br>

**Q10: What are the limitations of using CLIP for image understanding?**

<details>
<summary>💡 Show Answer</summary>

**A:** CLIP has several known limitations:
1. **No generation**: Can score similarity but cannot describe or explain
2. **Weak spatial reasoning**: "Object A is to the left of object B" is poorly captured
3. **Systematic biases**: Trained on internet data, inherits internet biases
4. **Poor on rare or specific categories**: Works on common internet concepts, struggles with specialized domains (medical imaging, technical diagrams)
5. **Short text context**: Only 77 tokens, can't handle long descriptions
6. **No counting ability**: Similarity score doesn't capture "three dogs" vs "one dog" reliably

</details>

<br>

**Q11: How would you fine-tune a VLM for a specialized domain like medical imaging?**

<details>
<summary>💡 Show Answer</summary>

**A:** Strategy depends on compute budget:
1. **Freeze everything, prompt engineer**: Cheapest. Use the base model with detailed system prompts. Works for general tasks but limited for specialized visual concepts.
2. **Fine-tune projection layer only**: Train only the projection layer on domain data (radiology images + reports). Fast, low compute, reasonable results.
3. **LoRA fine-tuning on LLM**: Keep visual encoder frozen, apply LoRA adapters to the LLM layers. Good balance of cost and capability.
4. **Full fine-tuning**: All components trained end-to-end. Best performance, highest cost.
5. **Domain-specific visual encoder**: Replace CLIP with a domain-specific encoder (e.g., a ViT pre-trained on medical images with RadBERT for text). Best for highly specialized domains.
Key data requirement: high-quality instruction-following data — not just image-label pairs but instruction-response pairs with domain expert annotations.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | CLIP + LLaVA diagrams |

⬅️ **Prev:** [01 — Multimodal Fundamentals](../01_Multimodal_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 — Image Understanding](../03_Image_Understanding/Theory.md)
