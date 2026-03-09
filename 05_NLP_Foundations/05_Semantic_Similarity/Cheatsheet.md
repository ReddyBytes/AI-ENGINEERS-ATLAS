# Semantic Similarity — Cheatsheet

**One-liner:** Semantic similarity measures how close two texts are in meaning by comparing their vector representations — not just their shared words.

---

## Key Terms

| Term | Definition |
|---|---|
| Semantic similarity | How similar two texts are in meaning (0 = unrelated, 1 = identical) |
| Sentence embedding | A single vector representing the full meaning of a sentence |
| SBERT | Sentence BERT — a BERT model fine-tuned for sentence-level embeddings |
| Cosine similarity | Angle-based similarity between two vectors |
| Paraphrase | Different words, same meaning |
| Jaccard similarity | Ratio of shared words to total unique words |
| Semantic search | Search that matches by meaning, not keyword overlap |
| Cross-encoder | Slower but more accurate similarity: takes both sentences as joint input |
| Bi-encoder | Faster: encodes each sentence separately, then compares |

---

## Similarity score guide

| Score | What it means |
|---|---|
| 0.95 – 1.0 | Near-duplicate or exact paraphrase |
| 0.80 – 0.95 | Very similar |
| 0.60 – 0.80 | Related |
| 0.30 – 0.60 | Weakly related |
| 0.0 – 0.30 | Unrelated |

---

## Methods comparison

| Method | Captures Synonyms | Speed | When to use |
|---|---|---|---|
| Jaccard | No | Very fast | Quick prototype only |
| TF-IDF cosine | Partial | Fast | Keyword-based tasks |
| Word2Vec average | Some | Fast | Light semantic tasks |
| SBERT | Yes | Medium | Production semantic search |
| Cross-encoder | Yes | Slow | Re-ranking top results |

---

## Quick SBERT reference

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode sentences
embeddings = model.encode(["sentence 1", "sentence 2"])

# Pairwise similarity
score = util.cos_sim(embeddings[0], embeddings[1])

# All-pairs similarity matrix
scores = util.cos_sim(embeddings, embeddings)

# Top-k most similar from a corpus
hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=5)
```

---

## Use cases

| Application | Similarity use |
|---|---|
| Semantic search | Query vs documents |
| FAQ deduplication | Question vs question |
| Recommendation | Item description vs preferences |
| Plagiarism detection | Two documents |
| Chatbot NLU | User input vs intent templates |

---

## Golden Rules

1. Use SBERT (sentence-transformers) for any semantic similarity task — it's fast, accurate, and easy.
2. Never use keyword overlap alone for semantic tasks — synonyms will break it.
3. For high-volume production use, precompute embeddings and store them — don't re-encode at query time.
4. Cross-encoders are more accurate but too slow for large-scale retrieval — use bi-encoders for first-pass retrieval, cross-encoders for reranking.
5. Similarity thresholds are task-dependent — always tune them on your data.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [04 Word Embeddings](../04_Word_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Hidden Markov Models](../06_Hidden_Markov_Models/Theory.md)
