# Vision Transformers — Interview Q&A

## Beginner

**Q1. What is a Vision Transformer (ViT) and how does it process images?**

<details>
<summary>💡 Show Answer</summary>

ViT (Dosovitskiy et al., 2020) applies the standard transformer encoder architecture to images by treating image patches as tokens.

Process:
1. Split the input image (e.g., 224×224) into a grid of non-overlapping patches (e.g., 16×16 pixels each) → 196 patches
2. Flatten each patch and project it linearly to an embedding vector (patch embedding)
3. Prepend a learnable [CLS] token
4. Add learned positional embeddings to all 197 tokens
5. Process through a standard transformer encoder (L layers of multi-head self-attention + FFN)
6. Use the [CLS] token's output for classification

Every patch can attend to every other patch through self-attention, enabling global context modeling from the very first layer.

</details>

---

<br>

**Q2. How is processing image patches different from processing words?**

<details>
<summary>💡 Show Answer</summary>

Words are discrete symbols from a finite vocabulary. You look them up in an embedding table.

Image patches are continuous data — 16×16×3 = 768 pixel values. There's no lookup table. Instead, each patch is linearly projected with a learned weight matrix: `patch_embedding = flatten(patch) × W_E`.

The key similarity: both result in a sequence of vectors that the transformer processes. The transformer doesn't need to know whether the tokens came from text or images — it just does attention between vectors.

</details>

---

<br>

**Q3. Why does ViT need positional encoding for images?**

<details>
<summary>💡 Show Answer</summary>

Self-attention is permutation-invariant — it doesn't care about the order of the input tokens. Without positional information, patch 1 (top-left corner) would look the same as patch 196 (bottom-right corner) to the model.

For images, position is crucial for understanding structure — the relationship between a person's head (top patches) and their feet (bottom patches) depends on knowing their relative positions.

ViT adds learned 1D positional embeddings to each patch position. Research shows the model learns that nearby patches have similar positions (spatially adjacent positions cluster in the embedding space).

</details>

---

## Intermediate

**Q4. What are the main differences between ViT and CNNs in terms of inductive biases?**

<details>
<summary>💡 Show Answer</summary>

CNNs have strong inductive biases baked into their architecture:
- **Locality:** Each filter looks at a small local region. This assumes nearby pixels are more related than distant ones.
- **Translation equivariance:** The same filter is applied everywhere. This assumes a dog in the corner is similar to a dog in the center.

These biases make CNNs very data-efficient — they need fewer examples to learn because the architecture already encodes the right priors for images.

ViT has essentially no inductive biases. Every patch attends to every other patch from the first layer — there's no built-in assumption about locality or translation.

Consequence: ViT needs much more data or pretraining to match CNN performance on small datasets. But at large scale (pretraining on millions of images), ViT matches or exceeds CNNs because global attention is more flexible.

</details>

---

<br>

**Q5. What is CLIP and how does it relate to ViT?**

<details>
<summary>💡 Show Answer</summary>

CLIP (Contrastive Language-Image Pretraining, OpenAI 2021) trains two encoders jointly:
- An image encoder (often ViT)
- A text encoder (transformer)

Training objective: for a batch of (image, caption) pairs, maximize similarity between matching pairs and minimize similarity between non-matching pairs.

After training, images and text live in the same embedding space. "A dog playing in snow" as text and a photo of a dog in snow have very similar embeddings.

Applications:
- Zero-shot image classification: embed the image, embed category names, find the closest
- Image-text retrieval: find images matching a text query
- Foundation for DALL-E, Stable Diffusion, GPT-4 Vision

CLIP essentially gave ViT its "language" — the ability to connect visual concepts to linguistic descriptions.

</details>

---

<br>

**Q6. How is patch size related to model performance and computational cost?**

<details>
<summary>💡 Show Answer</summary>

Patch size controls the sequence length:

```
Number of patches = (image_height / patch_size) × (image_width / patch_size)

224×224 with 16×16 patches → 14×14 = 196 patches
224×224 with 8×8 patches  → 28×28 = 784 patches
```

Smaller patches = more patches = finer-grained detail = more tokens = O(n²) more computation.

Trade-offs:
- 16×16 patches: standard, good balance of quality and efficiency
- 32×32 patches: faster, less fine-grained detail
- 8×8 patches: more detail, 4× more compute, used in some DALL-E variants

For tasks requiring fine-grained detail (medical imaging, text recognition in images), smaller patches help. For scene classification, larger patches often suffice.

</details>

---

## Advanced

**Q7. How do multimodal models like GPT-4V combine ViT and language models?**

<details>
<summary>💡 Show Answer</summary>

At a high level: encode the image with a ViT, encode the text with the LLM's tokenizer, merge both into a single sequence, and process through the LLM.

Common approaches:

1. **Prefix/concatenation (LLaVA-style):** Project ViT patch embeddings to the LLM's embedding dimension using a linear layer or MLP. Prepend the projected image tokens before the text tokens. The LLM processes the combined sequence.

2. **Cross-attention (Flamingo-style):** Keep image and text separate. Add cross-attention layers in the LLM where language tokens attend to image patch tokens. This is more parameter-efficient for very long image sequences.

3. **Joint training from scratch (Gemini-style):** Train a single model from scratch on text, images, audio, and video simultaneously, without separate encoders.

The key challenge: aligning the feature spaces. A ViT trained on image classification has a different representation space than an LLM trained on text. The projection layer (or fine-tuning) bridges this gap.

</details>

---

<br>

**Q8. What are the key weaknesses of ViT compared to CNNs?**

<details>
<summary>💡 Show Answer</summary>

1. **Data hunger:** ViT without pretraining underperforms CNNs on datasets with fewer than ~1M images. CNNs' inductive biases give them a head start on small datasets.

2. **Quadratic attention cost:** With 196 patches for 224×224, the attention matrix is 196×196 = ~38k calculations per head. For higher-resolution or video (many frames), this becomes expensive. Solutions: hierarchical ViT (like Swin Transformer), sparse attention.

3. **Patch boundary artifacts:** Splitting images into rigid patches can cut through objects at boundaries. Solutions: overlapping patches, shifted window attention (Swin).

4. **Positional embedding limitations:** ViT's 1D positional embeddings don't naturally encode 2D spatial structure. Images are 2D grids, not 1D sequences. Models like Swin Transformer use relative 2D attention biases to handle this better.

</details>

---

<br>

**Q9. What is the Swin Transformer and how does it address ViT's limitations?**

<details>
<summary>💡 Show Answer</summary>

Swin (Shifted Window Transformer, Liu et al., 2021) is a hierarchical vision transformer that addresses ViT's quadratic scaling and patch boundary issues.

Key innovations:

1. **Hierarchical features:** Unlike ViT's single-resolution token sequence, Swin merges neighboring patches across layers (like CNN pooling), building a feature pyramid. This enables multi-scale feature extraction for detection and segmentation.

2. **Local window attention:** Instead of attending globally across all patches, Swin applies attention within small local windows (e.g., 7×7 patches). O(n) complexity instead of O(n²).

3. **Shifted windows:** Alternating layers shift the window grid, allowing patches to attend to neighbors across window boundaries. This recovers cross-window information without global attention.

Impact: Swin became the dominant backbone for vision tasks requiring dense predictions (object detection, semantic segmentation) because it provides multi-scale features at linear computational cost. ViT-pure variants are better suited for classification tasks.


**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [09 GPT](../09_GPT/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 LLM Fundamentals](../../07_Large_Language_Models/01_LLM_Fundamentals/Theory.md)

</details>
