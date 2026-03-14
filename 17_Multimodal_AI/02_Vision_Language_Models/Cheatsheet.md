# Vision-Language Models — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **VLM** | Vision-Language Model: processes both images and text |
| **CLIP** | Contrastive Language-Image Pre-training; creates shared text-image embedding space |
| **LLaVA** | Large Language and Vision Assistant; CLIP encoder + projection + LLM |
| **ViT** | Vision Transformer: encodes images as sequences of 16×16 pixel patches |
| **Contrastive loss** | Training objective: push matching pairs together, non-matching apart |
| **Projection layer** | Small network that maps visual embeddings to LLM token dimension |
| **Zero-shot classification** | Classify an image using only text labels, no training examples needed |
| **Visual instruction tuning** | Fine-tune on instruction-following image-text data for practical use |
| **InfoNCE** | The contrastive loss formula CLIP uses; also called NT-Xent |
| **Patch embedding** | A 16×16 pixel image patch converted to a vector, CLIP's input unit |
| **[CLS] token** | Special token whose final embedding represents the whole image |
| **BLIP-2** | Alternative architecture using Q-Former instead of linear projection |

---

## CLIP at a Glance

```
Input:  (image, text) pairs
Output: similarity score — how well they match

Architecture:
  Image → ViT encoder → 512-dim vector
  Text  → Transformer encoder → 512-dim vector
  Trained so matching pairs have high cosine similarity

Zero-shot classification:
  1. Encode image → image_vec
  2. Encode "a photo of a {label}" for each candidate label
  3. Return argmax(cosine_similarity(image_vec, label_vecs))
```

---

## LLaVA Architecture

```
Image
  ↓ ViT (CLIP visual encoder — frozen)
Visual patch embeddings (256 × 1024-dim)
  ↓ Linear projection layer (trainable)
Visual tokens (matched to LLM embedding dim)
  ↓
LLM (Vicuna / LLaMA / Mistral)  ← also receives text tokens
  ↓
Text response
```

---

## Training Components — What Gets Updated?

| Component | LLaVA Stage 1 | LLaVA Stage 2 |
|-----------|--------------|--------------|
| Visual encoder (CLIP ViT) | Frozen | Frozen |
| Projection layer | Trained | Trained |
| LLM | Frozen | Fine-tuned (LoRA) |

---

## CLIP vs LLaVA Quick Comparison

| | CLIP | LLaVA |
|--|------|-------|
| Can generate text | No | Yes |
| Can answer questions | No (only scores) | Yes |
| Output | Similarity score | Text response |
| Use for | Retrieval, classification | Q&A, description, reasoning |
| Training data | Image-caption pairs | Image + instruction data |

---

## Key Numbers (CLIP ViT-B/32)

| Parameter | Value |
|-----------|-------|
| Image resolution | 224 × 224 |
| Patch size | 32 × 32 |
| Number of patches | 49 |
| Embedding dimension | 512 |
| Text context length | 77 tokens |
| Training pairs | 400 million |

---

## Golden Rules

1. CLIP = embedding + retrieval. LLaVA = understanding + generation.
2. The projection layer is the bridge — small but crucial.
3. Freeze the visual encoder; it already knows how to see.
4. Large batch sizes are essential for contrastive training (CLIP used 32,768).
5. Visual instruction tuning is what makes VLMs actually follow user instructions.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | CLIP + LLaVA diagrams |

⬅️ **Prev:** [01 — Multimodal Fundamentals](../01_Multimodal_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 — Image Understanding](../03_Image_Understanding/Theory.md)
