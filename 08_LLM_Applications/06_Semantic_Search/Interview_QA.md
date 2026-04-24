# Semantic Search — Interview Q&A

## Beginner

**Q1: What is the difference between keyword search and semantic search?**

<details>
<summary>💡 Show Answer</summary>

Keyword search finds documents that contain the exact words you typed. It uses an inverted index — a lookup table mapping each word to the documents containing it. BM25 is the classic algorithm. It's fast and great for exact matches: searching "Python tutorial" finds documents with those words.

Semantic search finds documents that have similar meaning to your query. It converts both the query and documents to embedding vectors, then finds vectors that are closest. Searching "how to learn Python" semantically might find documents titled "beginner's guide to programming in Python" — zero keyword overlap, but same meaning.

In practice: keyword search wins for exact terms, product codes, and proper nouns. Semantic search wins for natural language questions and concept-based retrieval. Hybrid search combines both.

</details>

---

**Q2: What does "embedding" a query mean, and why does it need to use the same model as the documents?**

<details>
<summary>💡 Show Answer</summary>

Embedding a query means passing it through an embedding model to get a vector (list of numbers). This puts the query in the same "semantic space" as the indexed documents.

The "same model" requirement exists because different embedding models create different vector spaces. Model A places "cat" at coordinates [0.3, -0.7, 0.5, ...]. Model B places "cat" at completely different coordinates. If your documents were embedded with Model A and you search with a query vector from Model B, the similarity scores are meaningless — you're comparing addresses from two different cities. Always use the same model (and same version) for both indexing and querying.

</details>

---

**Q3: What is hybrid search and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

Hybrid search combines semantic (embedding-based) search with keyword (BM25) search. You run both searches, get two ranked result lists, then fuse them into one combined ranking using Reciprocal Rank Fusion (RRF) or a weighted score.

Use hybrid search for most real-world applications. Example: an e-commerce search where customers sometimes search by product name ("Nike Air Max 270" — keyword wins), and sometimes by description ("comfortable running shoes for wide feet" — semantic wins). A pure semantic search might miss the exact product code; pure keyword misses the natural language query. Hybrid handles both.

</details>

---

## Intermediate

**Q4: Explain Reciprocal Rank Fusion (RRF) and why it works well for merging search results.**

<details>
<summary>💡 Show Answer</summary>

RRF is a simple formula for combining ranked lists from multiple retrieval methods: `score = 1/(k + rank)` where k is a constant (typically 60) and rank is the document's position in that list (1 = first result).

You sum the RRF scores across all lists. Documents that appear near the top of multiple lists get high combined scores.

Why it works well: it's rank-based, not score-based. Cosine similarity scores and BM25 scores are on completely different scales (0–1 vs. 0–10+) and can't be directly compared. RRF normalizes everything to rank positions. A document ranked #1 by BM25 and #3 by semantic search will score higher than a document that's #1 in only one list. It's robust and requires no tuning of weights between the two methods.

</details>

---

**Q5: What is re-ranking and how does it differ from the initial retrieval step?**

<details>
<summary>💡 Show Answer</summary>

Initial retrieval (first stage): embed query, search vector DB, return top-K candidates. This uses a bi-encoder — query and documents are encoded independently. Fast enough to search millions of documents in milliseconds. But cosine similarity between independently-encoded vectors is imprecise.

Re-ranking (second stage): take the top-K candidates and score them more carefully. A cross-encoder model takes the (query, document) pair together — it can see both at once and model their relationship. This is much more accurate than cosine similarity but much slower (can't run on millions, only top-K).

The two-stage pipeline: retrieval finds 20–50 plausible candidates quickly, re-ranking orders them accurately. You return only the top-5 to the user. This is how all serious production search systems work — Google, Bing, and enterprise search all use this pattern.

</details>

---

**Q6: How do you evaluate whether your semantic search system is working well?**

<details>
<summary>💡 Show Answer</summary>

Build an evaluation dataset: a set of (query, relevant_document_ids) pairs. At minimum 100–200 examples across different query types. This is your ground truth.

Key metrics:

**Recall@K**: of all relevant documents, what fraction appear in the top-K results? Most important for RAG — if the right doc isn't retrieved, the answer will be wrong. Target: Recall@5 > 0.85 for good RAG systems.

**MRR (Mean Reciprocal Rank)**: average of 1/rank of the first relevant result. Measures whether the right doc appears near the top.

**NDCG (Normalized Discounted Cumulative Gain)**: grades results by position — finding the relevant doc at rank 1 is better than rank 5.

Run evaluation before and after any change (new embedding model, chunking strategy, adding hybrid search). Never ship search changes without measuring the delta.

</details>

---

## Advanced

**Q7: How do you handle long documents in semantic search? What strategies exist?**

<details>
<summary>💡 Show Answer</summary>

Problem: embedding models have context limits (256–8192 tokens). A 50-page PDF can't be embedded as a whole — the embedding would represent too many different topics, making it poor at matching specific queries.

Strategies:

**Chunking**: split documents into smaller passages before embedding. Most common. But you lose context at chunk boundaries.

**Sliding window**: chunks with overlap (e.g., 512 tokens with 64-token overlap). Mitigates boundary cuts.

**Parent-child chunking**: embed small chunks for retrieval, but return the parent section (larger context) to the LLM. Small chunks match queries precisely; the LLM gets enough context.

**Late interaction (ColBERT)**: embed every token in the document separately. At query time, compute token-level interaction scores. Very accurate but storage-intensive.

For most production RAG: recursive splitting into 256–512 token chunks with 10–20% overlap is the standard starting point.

</details>

---

**Q8: What is ColBERT and how does it differ from standard bi-encoder and cross-encoder models?**

<details>
<summary>💡 Show Answer</summary>

Standard bi-encoder: one vector per document, one per query. Cosine similarity. Fast but loses fine-grained token interactions.

Cross-encoder: processes (query, document) pair together. Very accurate but O(n) cost for n documents — can't scale to retrieval.

ColBERT (Contextualized Late Interaction over BERT): a hybrid. It produces multiple embeddings per document — one per token. At query time, it computes the maximum inner product score between each query token and all document tokens, then sums. This allows fine-grained interaction without processing pairs — you precompute document token embeddings at index time.

ColBERT is significantly more accurate than bi-encoders and much faster than cross-encoders for retrieval. The tradeoff: 10–100x more storage (you store a vector per token instead of one per document). Used in high-accuracy search systems where storage is acceptable.

</details>

---

**Q9: How would you build a multi-lingual semantic search system?**

<details>
<summary>💡 Show Answer</summary>

Option 1: Multilingual embedding model. Use models like `multilingual-e5-large` or `text-embedding-3-large` (which supports 100+ languages). They embed text from different languages into a shared space — so a Spanish query can match an English document.

Option 2: Translation + monolingual model. Translate all queries and documents to English, embed with a high-quality English model. Better quality for languages with good translation, worse for low-resource languages.

Option 3: Per-language index. Maintain a separate collection for each language. Route queries to the right language index based on language detection. Best quality, highest operational complexity.

For most applications: start with multilingual-e5-large. Test with your specific language pairs — recall varies significantly. High-resource language pairs (EN-FR, EN-DE, EN-ES) will be good; low-resource pairs may need translation as a fallback.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [05 Vector Databases](../05_Vector_Databases/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Memory Systems](../07_Memory_Systems/Theory.md)
