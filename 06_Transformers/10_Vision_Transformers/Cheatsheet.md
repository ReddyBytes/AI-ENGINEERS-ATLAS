# Vision Transformers — Cheatsheet

**One-liner:** ViT splits images into fixed-size patches, embeds them as tokens, adds positional encoding, and processes them through a standard transformer encoder — applying NLP's most powerful architecture to computer vision.

---

## Key Terms

| Term | Definition |
|---|---|
| Patch | A fixed-size region of an image (e.g., 16×16 pixels) treated as one token |
| Patch embedding | Linear projection of a flattened patch to d_model dimensions |
| [CLS] token | Learnable token prepended to the sequence; its output is used for classification |
| Positional embedding | Learned 1D position embeddings for each patch (and [CLS]) |
| ViT | Vision Transformer — the base model applying transformers to images |
| Inductive bias | Prior assumptions baked into architecture (CNNs have locality bias; ViT has none) |
| CLIP | Contrastive Language-Image Pretraining — aligns images and text in shared embedding space |

---

## ViT architecture pipeline

```
224×224 image
  ↓ split into 16×16 patches
196 patches (each 768 dims = 16×16×3 flattened)
  ↓ linear projection
196 patch embeddings (d_model dims)
  ↓ prepend [CLS] token
197 tokens total
  ↓ add positional embeddings
  ↓ transformer encoder (L layers)
197 output vectors
  ↓ take [CLS] output
1 vector (d_model dims)
  ↓ linear classification head
Class probabilities
```

---

## Common ViT variants

| Model | Patch size | Layers | d_model | Heads | Params |
|---|---|---|---|---|---|
| ViT-Base/16 | 16×16 | 12 | 768 | 12 | 86M |
| ViT-Large/16 | 16×16 | 24 | 1024 | 16 | 307M |
| ViT-Huge/14 | 14×14 | 32 | 1280 | 16 | 632M |

Notation: ViT-Base/16 = Base size, 16×16 patches.

---

## ViT vs CNN

| | CNN | ViT |
|---|---|---|
| Local relationships | Built-in | Learned |
| Global relationships | Hard | Easy |
| Small data | Good | Needs pretraining |
| Scale behavior | Diminishing returns | Scales well |
| State of art (large scale) | Competitive | Often better |

---

## Multimodal connection

| System | Image representation | Text representation | Combined with |
|---|---|---|---|
| CLIP | ViT encoder | Text transformer | Contrastive pretraining |
| DALL-E | Patch tokens | Text tokens | Transformer decoder |
| GPT-4V | ViT encoder | GPT decoder | Cross-attention / concatenation |
| LLaVA | ViT (CLIP) | LLaMA | Projection + concatenation |

---

## Golden Rules

1. ViT needs large datasets or pretraining — without it, CNNs outperform it on small datasets.
2. Patch size controls the sequence length: smaller patches = more tokens = more compute = more detail.
3. The [CLS] token serves the same role as in BERT — sentence-level (image-level) representation.
4. Positional encoding matters — without it, ViT can't tell where a patch is in the image.
5. ViT is the backbone of all modern multimodal models — understanding it unlocks CLIP, DALL-E, and GPT-4V.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [09 GPT](../09_GPT/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 LLM Fundamentals](../../07_Large_Language_Models/01_LLM_Fundamentals/Theory.md)