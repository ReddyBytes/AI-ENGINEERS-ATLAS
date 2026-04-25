# Project 6 — Semantic Search Engine

## The Story

Picture a developer at a mid-size startup. The engineering team has accumulated three years of internal documentation: architecture decisions, post-mortems, onboarding guides, API references. All of it lives in a shared drive. When a new engineer joins and asks "how do we handle database migrations?", the answer exists — somewhere — buried in 400 documents. Keyword search returns 60 results. Nobody reads them. The new engineer asks a senior who then loses 30 minutes re-explaining something already written down.

This is not a storage problem. It is a retrieval problem. And the reason keyword search fails is that meaning is not in the words — it is in the space between them. "Database migration" and "schema change rollout" mean the same thing. A keyword index does not know that. An embedding model does.

This project builds the core technology behind every AI search product. You embed documents into a vector space where meaning corresponds to geometry, then find the nearest neighbors to any query. Once you understand this, you understand the foundation of every RAG system, every AI assistant, and every semantic search product shipped in the last three years.

---

## What You Build

A semantic search engine over a collection of plain-text articles. Given a natural language query, the system:

1. Embeds all documents at load time using an Embeddings API (OpenAI `text-embedding-3-small`)
2. Stores embeddings in a numpy matrix — no external vector database needed
3. Embeds the incoming query using the same model
4. Computes cosine similarity between the query vector and every document vector
5. Returns the top-5 most relevant documents with similarity scores and excerpts

---

## Concepts Covered

| Phase | Topic | Theory File |
|---|---|---|
| Phase 2 | Vector Databases | `08_LLM_Applications/05_Vector_Databases/Theory.md` |
| Phase 2 | Semantic Search | `08_LLM_Applications/06_Semantic_Search/Theory.md` |
| Phase 2 | Embeddings | `08_LLM_Applications/04_Embeddings/Theory.md` |
| Phase 5 | Embedding and Indexing | `09_RAG_Systems/04_Embedding_and_Indexing/Theory.md` |

---

## Prerequisites

- Completed the Beginner Path or equivalent
- Comfortable with Python classes and functions
- API key for OpenAI (or Anthropic / Voyage AI)
- Understanding of what a vector/array is (numpy basics)

---

## What Success Looks Like

```
Query: "how do transformers handle long sequences?"

Results:
1. [0.91] Positional Encoding in Transformers
   "Transformers use positional encodings to give the model a sense of token order..."

2. [0.87] Attention Mechanism Deep Dive
   "The self-attention operation computes relationships between every pair of tokens..."

3. [0.84] Context Window Limitations
   "As sequence length grows, the quadratic cost of attention becomes a bottleneck..."

4. [0.79] BERT vs GPT Architectures
   "Both BERT and GPT are built on the Transformer backbone, differing in..."

5. [0.71] Tokenization Strategies
   "Before a Transformer sees text, it must be converted to token IDs..."
```

---

## Learning Format

**Difficulty:** Easy — 2.5 hours

**Format:** One external dependency (the embeddings API) and numpy for the math. No database, no server, no orchestration framework. The concepts are new but the implementation is straightforward. Build in 5 stages, each independently runnable.

---

## Key Terms

- **Embeddings**: A numerical vector (e.g., 1536 numbers) representing the meaning of a piece of text. Two texts with similar meanings will have vectors that point in similar directions.
- **Cosine Similarity**: Measures the angle between two vectors. A score of 1.0 means identical direction (same meaning), 0.0 means unrelated, -1.0 means opposite. Scale-invariant — a short and long document expressing the same idea score the same.
- **Nearest Neighbor Search**: Given a query vector, find the k vectors in your collection that are closest. With numpy, this is a matrix multiplication followed by an argsort.
- **Vector Space Model**: The fundamental insight that meaning can be geometry. Documents cluster by topic. Queries land near relevant documents.
- **Embedding cache**: Storing computed embeddings to disk so you do not re-pay API costs on every run.

---

## 📂 Navigation

| File | |
|---|---|
| **01_MISSION.md** | You are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [04_RECAP.md](./04_RECAP.md) | What you built and what comes next |

**Project Series:** Project 1 of 5 — Intermediate Projects
⬅️ No previous project
➡️ **Next:** [02 — Personal Knowledge Base RAG](../07_Personal_Knowledge_Base_RAG/01_MISSION.md)
