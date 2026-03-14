# Multimodal Embeddings — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Multimodal embedding** | Vector where images and text share the same space |
| **Cross-modal retrieval** | Using one modality to search for another (text → image) |
| **CLIP** | OpenAI model that creates this shared space via contrastive training |
| **Cosine similarity** | Angle-based similarity between vectors; 1 = identical direction |
| **L2 normalization** | Scale a vector to length 1 (unit vector); required before cosine similarity |
| **ANN** | Approximate Nearest Neighbor; fast similarity search at scale |
| **FAISS** | Facebook's library for fast ANN search (CPU and GPU) |
| **Zero-shot classification** | Classify an image using text labels, no training needed |

---

## CLIP Encoding Quick Start

```python
# pip install transformers torch pillow
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Encode an image
image = Image.open("photo.jpg")
inputs = processor(images=image, return_tensors="pt")
with torch.no_grad():
    image_features = model.get_image_features(**inputs)
    image_features = image_features / image_features.norm(dim=-1, keepdim=True)  # L2 normalize

# Encode text
texts = ["a photo of a cat", "a photo of a dog", "a sunny beach"]
inputs = processor(text=texts, return_tensors="pt", padding=True)
with torch.no_grad():
    text_features = model.get_text_features(**inputs)
    text_features = text_features / text_features.norm(dim=-1, keepdim=True)

# Similarity: image vs all text labels
similarity = (image_features @ text_features.T).squeeze()
print(similarity)  # [0.87, 0.12, 0.03] → "cat" matches best
```

---

## Via sentence-transformers (Simpler API)

```python
# pip install sentence-transformers
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("clip-ViT-B-32")

# Encode image
image_embedding = model.encode(Image.open("photo.jpg"))

# Encode text
text_embedding = model.encode("a photo of a cat")

# Similarity
from sentence_transformers.util import cos_sim
score = cos_sim(image_embedding, text_embedding)
```

---

## CLIP Model Variants

| Model | Embedding dim | Quality | Speed |
|-------|--------------|---------|-------|
| ViT-B/32 | 512 | Good | Fastest |
| ViT-B/16 | 512 | Better | Fast |
| ViT-L/14 | 768 | Best | Slower |
| ViT-L/14@336px | 768 | Best+detail | Slowest |

Always use the same variant for both indexing and querying.

---

## Cross-Modal Retrieval Pattern

```
1. Build index:
   - Encode all images → store (image_path, embedding) in vector DB

2. Query by text:
   - Encode query text → text embedding
   - Search vector DB for nearest image embeddings
   - Return top-k image paths

3. Query by image:
   - Encode query image → image embedding
   - Same search, returns similar images
```

---

## Vector Database Options for Multimodal

| DB | Open source | Hosted | CLIP built-in |
|----|------------|--------|--------------|
| **FAISS** | Yes | No | No (bring your own embeddings) |
| **Chroma** | Yes | No | No |
| **Weaviate** | Yes | Yes | Yes (img2vec-neural module) |
| **Qdrant** | Yes | Yes | No (bring embeddings) |
| **Pinecone** | No | Yes | No (bring embeddings) |

---

## Common Tasks and Which CLIP Handles

| Task | CLIP good? | Notes |
|------|-----------|-------|
| General image search by description | Excellent | Core use case |
| Zero-shot classification (common categories) | Excellent | |
| Fine-grained classification (dog breeds) | Poor | Needs fine-tuning |
| Detecting duplicate/near-duplicate images | Good | Image-image similarity |
| Specialized domains (medical, satellite) | Poor | Needs domain fine-tuning |
| Counting or spatial relationships | Poor | Architectural limitation |

---

## Golden Rules

1. Always L2-normalize embeddings before computing cosine similarity
2. Use the exact same CLIP variant for building the index and querying
3. Text queries should be descriptive ("a photo of X") not just label words ("X")
4. For fine-grained tasks, fine-tune CLIP on domain data rather than using base model
5. FAISS for millions of vectors locally; Weaviate/Qdrant/Pinecone for managed hosted

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | CLIP image search system |

⬅️ **Prev:** [05 — Audio and Speech AI](../05_Audio_and_Speech_AI/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 — Multimodal Agents](../07_Multimodal_Agents/Theory.md)
