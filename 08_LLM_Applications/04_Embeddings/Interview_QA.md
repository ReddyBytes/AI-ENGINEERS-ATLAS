# Embeddings — Interview Q&A

## Beginner

**Q1: What is a text embedding and what does it represent?**

A text embedding is a fixed-length vector (a list of floating-point numbers) that represents the semantic meaning of a piece of text. For example, the sentence "The cat sat on the mat" might become a list of 1536 numbers. The specific values encode the meaning, context, and topic of the text in a form that a computer can do math on.

The key property: similar meanings produce similar vectors. "Dog" and "puppy" will have vectors that are close together (high cosine similarity). "Dog" and "nuclear physics" will have vectors far apart. This property enables semantic search — finding similar content without keyword matching.

---

**Q2: What is cosine similarity and how is it used with embeddings?**

Cosine similarity measures the angle between two vectors. It returns a score from -1 to 1, where 1 means the vectors point in the same direction (identical meaning), 0 means unrelated, and -1 means opposite meaning.

For text embeddings, cosine similarity is the standard metric because it's scale-invariant — it doesn't care about the magnitude of the vectors, only their direction. A short sentence and a long paragraph about the same topic can have high cosine similarity even if their vector magnitudes are very different. Formula: `dot(a, b) / (norm(a) * norm(b))`. In practice, you call it with numpy or scipy: `np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))`.

---

**Q3: What is the difference between dense and sparse embeddings?**

Dense embeddings are short vectors (typically 384–3072 dimensions) where nearly all values are non-zero. They're produced by neural networks and capture semantic meaning. "Dog" and "canine" will be close together even though they're different words.

Sparse embeddings are very long vectors (vocabulary size, typically 30K–100K dimensions) where most values are zero. Each position corresponds to a specific word. TF-IDF and BM25 are sparse methods. They're great at exact keyword matching but don't understand synonyms.

Dense embeddings capture meaning. Sparse embeddings capture exact words. Hybrid search combines both for the best of both worlds.

---

## Intermediate

**Q4: Why do embedding models have a context length limit? What happens if you exceed it?**

Embedding models, like language models, process text as tokens. They have a maximum sequence length (e.g., 8K tokens for text-embedding-3-small, 256 tokens for all-MiniLM-L6-v2). This limit exists because of the self-attention mechanism — attention is O(n²) in sequence length, so longer sequences need quadratically more compute.

If you exceed the limit, the API typically truncates the input at the limit and embeds only the first N tokens. This means the embedding only represents part of your document, and the ending might not be represented at all. The fix: chunk your document before embedding. Each chunk should be well within the context limit, ideally 100–400 tokens for good semantic specificity.

---

**Q5: How do you choose between different embedding models?**

Four factors: accuracy, speed, cost, and deployment.

For accuracy: larger models with more dimensions generally score better on retrieval benchmarks (MTEB leaderboard is the standard reference). text-embedding-3-large beats text-embedding-3-small but costs more.

For speed: local models like all-MiniLM-L6-v2 are very fast and free but require local GPU/CPU. API models have network latency but no infrastructure.

For cost: OpenAI text-embedding-3-small is very cheap (~$0.02 per 1M tokens). Local models are free after infrastructure.

Decision tree: Need to run locally and free? Use sentence-transformers. Production RAG with small corpus? text-embedding-3-small. Maximum accuracy? text-embedding-3-large or fine-tune a custom model.

---

**Q6: What is "embedding drift" and why does it matter in production systems?**

Embedding drift happens when you change the embedding model or its version. The vectors stored in your database were created with model version A. If you upgrade to model version B, the vector space changes — the same text produces different numbers. A query embedded with model B will not match correctly against documents embedded with model A.

This is a significant operational concern. In production: (1) Never mix embeddings from different models or versions in the same index. (2) When upgrading models, you must re-embed ALL your documents. (3) Version your embedding model alongside your vector database. (4) Some organizations maintain two indexes simultaneously during migration, then cut over.

---

## Advanced

**Q7: How are embedding models trained? What makes a good embedding?**

Most embedding models are trained using contrastive learning with a Siamese network architecture. The training data consists of (query, positive_passage, hard_negative_passage) triplets. The model learns to minimize distance between query and positive, and maximize distance to negatives.

Modern methods use in-batch negatives (treating other examples in the batch as negatives), hard negative mining (finding particularly tricky negatives), and knowledge distillation from larger teacher models. MTEB (Massive Text Embedding Benchmark) is the standard evaluation suite — it covers retrieval, clustering, classification, and semantic similarity tasks.

A good embedding model generalizes across domains, handles short queries vs long passages well (asymmetric retrieval), and maintains semantic relationships across languages.

---

**Q8: What is matryoshka representation learning (MRL) and why does text-embedding-3-small use it?**

Matryoshka representation learning allows a single model to produce embeddings at multiple effective dimensions. The first N dimensions of a 1536-dim embedding are themselves a valid, slightly lower-quality embedding. So you can use 256-dim versions of text-embedding-3-small if you want faster search and smaller storage — at a small accuracy cost.

Technically: during training, the loss is computed at multiple truncation points (e.g., 256, 512, 1024, 1536), and the model is trained to produce good representations at all scales simultaneously. This gives you a cost/quality tradeoff dial without needing to run different models. OpenAI exposes this with the `dimensions` parameter in their embeddings API.

---

**Q9: How do you handle multilingual embeddings? What are the tradeoffs?**

Options: (1) Use a multilingual model like multilingual-e5-large or text-embedding-3-large (which has strong multilingual support). These embed text from 100+ languages into a shared vector space — English "dog" and French "chien" will be near each other. (2) Use a language-specific model for each language. Better quality per language but complex operationally.

Tradeoffs: multilingual models trade some quality per language for cross-lingual search capability. A dedicated English model will typically outperform a multilingual model on English-only tasks. But if your users query in English and documents are in French, a multilingual model is the only option. Test on your specific language pairs — quality varies dramatically by language. Low-resource languages (rare languages) typically get poor quality even from multilingual models.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Structured Outputs](../03_Structured_Outputs/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Vector Databases](../05_Vector_Databases/Theory.md)
