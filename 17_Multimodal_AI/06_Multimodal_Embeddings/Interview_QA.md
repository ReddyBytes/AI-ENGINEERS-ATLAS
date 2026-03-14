# Multimodal Embeddings — Interview Q&A

## Beginner Level

**Q1: What is a multimodal embedding?**
**A:** A multimodal embedding is a vector representation where different types of data — images and text — are mapped to the same shared vector space. This means an image and a text description of that image end up as vectors with high similarity (close together in the space), while an image and an unrelated text description end up far apart. CLIP is the most widely used model that creates these shared representations.

**Q2: What can you do with multimodal embeddings that you couldn't do with separate text and image embeddings?**
**A:** With separate embeddings, you can only compare text to text or image to image. With multimodal embeddings you can: search a photo library by typing a description (text → image retrieval), find images similar to an uploaded image (image → image), find text captions that match a photo (image → text retrieval), classify images using arbitrary text labels with no training (zero-shot classification), and build multimodal RAG systems that retrieve both documents and images.

**Q3: What is cross-modal retrieval?**
**A:** Cross-modal retrieval means using one type of input to search for results of a different type. The most common example: type a text description, retrieve matching images. Or show an image, retrieve matching text descriptions. CLIP embeddings make this possible because both types live in the same vector space — a text query vector and an image vector can be directly compared.

---

## Intermediate Level

**Q4: Why must CLIP vectors be L2-normalized before similarity computation?**
**A:** Cosine similarity measures the angle between two vectors, not their magnitude. The formula is `cos_sim(a,b) = (a·b)/(||a||·||b||)`. If vectors aren't normalized (||v|| ≠ 1), the magnitude affects the result — a longer vector would appear to have higher similarity to everything just because it's large, which is meaningless. L2 normalization sets ||v|| = 1 for all vectors, so `cos_sim(a,b) = a·b` (just the dot product), and similarity purely reflects directional alignment in semantic space.

**Q5: How do you build an image search system with CLIP?**
**A:** Three steps:
1. **Indexing**: For each image in your library, encode it with CLIP's visual encoder, L2-normalize the embedding, and store (image_path, embedding_vector) in a vector database
2. **Query encoding**: When a user types a query, encode it with CLIP's text encoder using the same CLIP variant used for indexing, L2-normalize
3. **Search**: Compute cosine similarity (dot product) between query vector and all stored image vectors, return top-k closest matches

For scale, use an ANN index (FAISS, HNSW) instead of brute-force search. For production, use a managed vector database like Qdrant or Weaviate.

**Q6: What are the limitations of base CLIP for specialized use cases?**
**A:** Base CLIP was trained on general internet images and their captions. Key limitations:
- **Fine-grained categories**: "Labrador vs Golden Retriever" both look like "dogs" to CLIP — it wasn't trained to distinguish fine-grained breeds reliably
- **Specialized domains**: Medical X-rays, satellite imagery, microscopy images — rare in training data, so embeddings are weak
- **Text in images**: CLIP doesn't specifically model text within images
- **Cultural specificity**: Concepts common in one culture but rare on English-language internet may embed poorly
Solution: fine-tune CLIP on domain-specific (image, text) pairs using the same contrastive loss.

---

## Advanced Level

**Q7: How would you fine-tune CLIP for a specialized domain like fashion product search?**
**A:** Process:
1. **Data collection**: Gather fashion product images with their text descriptions (product titles, descriptions, attributes)
2. **Architecture**: Start from pre-trained CLIP (ViT-B/32 or ViT-L/14) — don't train from scratch
3. **Training objective**: Same InfoNCE contrastive loss as original CLIP, but on your domain-specific pairs
4. **What to fine-tune**: Options: (a) fine-tune only the text encoder (cheaper, keeps visual representations), (b) fine-tune both encoders (better but needs more data), (c) add adapter layers without touching frozen weights (most efficient)
5. **Evaluation**: Build a held-out retrieval test set, measure Recall@k (does the correct image appear in the top-k results?)
6. **Negative mining**: Hard negatives (similar but not matching products) dramatically improve training efficiency — "black sneaker" vs "white sneaker" as negatives, not random unrelated items

**Q8: Explain how multimodal RAG differs from standard text-only RAG.**
**A:** Standard RAG retrieves text chunks relevant to a text query. Multimodal RAG extends this in two directions:
1. **Retrieval across modalities**: The retrieval step can return both text chunks and images, using multimodal embeddings (CLIP) to find relevant images based on a text query
2. **Multimodal context**: The retrieved items (images + text) are passed to a VLM that can process both
Architecture:
- Index: both text chunks (via text embeddings) and images (via CLIP image embeddings) in the same or separate vector stores
- Query: embed the user query with both a text embedder (for text retrieval) and CLIP text encoder (for image retrieval)
- Retrieve: merge and rerank text and image results by relevance
- Generate: pass both retrieved text and images to a VLM (Claude Vision, GPT-4V) for final answer generation
Use cases: QA over product catalogs with images, medical reports with scan images, technical documentation with diagrams.

**Q9: System design question: Build a Pinterest-style visual discovery system where users can upload an image and find visually similar items.**
**A:** Architecture:
1. **Ingest pipeline**: New items → CLIP ViT-L/14 encoding → L2 normalize → store in Qdrant with item metadata (price, category, URL)
2. **Query flow**: User uploads image → encode with same CLIP model → query Qdrant for top-k nearest neighbors (using HNSW index for sub-millisecond search at millions of items)
3. **Result reranking**: Apply category filters (user filtered for "shoes") → diversity sampling to avoid showing 20 identical black shoes → return top-20
4. **Scale**: CLIP encoding is 5ms/image on GPU → batch encoding at ingestion with queue; Qdrant handles 10M+ vectors efficiently
5. **Freshness**: New items ingested in real-time; deletions soft-delete with metadata filter
6. **Evaluation**: Precision@10 (are the retrieved items actually similar?), measured with human judges or click-through rate as proxy metric

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | CLIP image search system |

⬅️ **Prev:** [05 — Audio and Speech AI](../05_Audio_and_Speech_AI/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 — Multimodal Agents](../07_Multimodal_Agents/Theory.md)
