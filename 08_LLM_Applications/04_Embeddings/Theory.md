# Embeddings — Theory

Imagine every word, sentence, and document gets a unique address in a giant city of meaning. The city has thousands of streets. Similar things live near each other.

"Dog" and "puppy" are neighbors on the same block. "Dog" and "cat" are a few streets apart — same neighborhood (pets), different residents. "Dog" and "quantum physics" are across town in completely different districts.

Now imagine you can ask: "Show me everything within a 5-minute walk of 'dog'." Instantly you get: puppy, canine, wolf, Labrador, breed.

That's what embeddings do. They convert text into coordinates in a meaning-space city. Similar meanings live nearby. Different meanings live far away.

👉 This is why we need **Embeddings** — to turn text into numbers that capture meaning so we can do math on language: find similar content, measure distance between ideas, and enable semantic search.

---

## What Is an Embedding?

An embedding is a list of numbers (a vector) that represents the meaning of a piece of text.

```
"The dog barked loudly."  →  [0.23, -0.45, 0.11, 0.78, -0.33, ...]
                                        (1536 numbers)
```

Those 1536 numbers encode the meaning of that sentence. You can't read the numbers yourself — they don't individually mean anything. But their pattern together represents the semantic content.

---

## How It Works (Simplified)

```mermaid
flowchart LR
    A[Text Input] --> B[Embedding Model]
    B --> C[Vector: list of floats]
    C --> D[Similar texts = nearby vectors]
    C --> E[Different texts = distant vectors]
```

The embedding model was trained on billions of text examples. It learned to place similar meanings close together in vector space. The model is frozen — you just run your text through it and get the coordinates back.

---

## What Do the Dimensions Mean?

The dimensions don't have human-readable labels. But conceptually, you can imagine some might encode things like:
- Is this about animals? (0 to 1)
- Is this technical or casual?
- Is this a question or a statement?
- What domain is this from?

In practice, 1536 dimensions all blend together to capture subtle meaning. No single dimension is interpretable — the meaning is distributed across all of them together.

---

## Cosine Similarity: Measuring Meaning Distance

To compare two embeddings, you calculate cosine similarity. It measures the angle between two vectors.

- Score of **1.0** = identical meaning
- Score of **0.8+** = very similar
- Score of **0.5** = somewhat related
- Score near **0** = unrelated

```python
from numpy import dot
from numpy.linalg import norm

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))
```

This is the foundation of semantic search, recommendation systems, and duplicate detection.

---

## Dense vs Sparse Embeddings

| Type | What it is | Example | Best for |
|------|-----------|---------|---------|
| **Dense** | Compact vector (e.g. 1536 dims), all values non-zero | OpenAI embeddings, sentence-transformers | Semantic similarity, RAG |
| **Sparse** | Huge vector (50K+ dims), mostly zeros — one per vocabulary word | TF-IDF, BM25 | Keyword matching, exact terms |

Dense = captures meaning and context. Sparse = captures exact word matches.

In practice: combine both (hybrid search) for the best results.

---

## Popular Embedding Models

| Model | Dimensions | Context | Speed | Cost |
|-------|-----------|---------|-------|------|
| `text-embedding-3-small` (OpenAI) | 1536 | 8K tokens | Fast | Low |
| `text-embedding-3-large` (OpenAI) | 3072 | 8K tokens | Medium | Medium |
| `all-MiniLM-L6-v2` (sentence-transformers) | 384 | 256 tokens | Very fast | Free (local) |
| `all-mpnet-base-v2` (sentence-transformers) | 768 | 384 tokens | Medium | Free (local) |
| `embed-english-v3.0` (Cohere) | 1024 | 512 tokens | Fast | Low |

For most RAG applications: start with `text-embedding-3-small` (cost-effective) or `all-MiniLM-L6-v2` (free, local).

---

## What Embeddings Enable

- **Semantic search**: find documents by meaning, not keywords
- **Recommendation**: "if you liked this article, here are similar ones"
- **Clustering**: group similar documents automatically
- **Duplicate detection**: find near-identical content
- **RAG (Retrieval-Augmented Generation)**: retrieve relevant docs before generating an answer

---

✅ **What you just learned:** Embeddings convert text into fixed-size number vectors where similar meanings are mathematically close — enabling semantic search and comparison using cosine similarity.

🔨 **Build this now:** Embed three sentences: "I love my dog", "My puppy is adorable", and "Machine learning is complex". Use cosine similarity to show the first two are closer to each other than to the third.

➡️ **Next step:** Vector Databases → `08_LLM_Applications/05_Vector_Databases/Theory.md`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Structured Outputs](../03_Structured_Outputs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Vector Databases](../05_Vector_Databases/Theory.md)
