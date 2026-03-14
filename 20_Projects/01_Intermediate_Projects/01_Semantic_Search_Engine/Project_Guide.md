# Project 1 — Semantic Search Engine

## Why This Project Matters

Picture a developer at a mid-size startup. The engineering team has accumulated three years of internal documentation: architecture decisions, post-mortems, onboarding guides, API references. All of it lives in a shared drive. When a new engineer joins and asks "how do we handle database migrations?", the answer exists — somewhere — buried in 400 documents. Keyword search returns 60 results. Nobody reads them. The new engineer asks a senior who then loses 30 minutes re-explaining something already written down.

This is not a storage problem. It is a retrieval problem. And the reason keyword search fails is that meaning is not in the words — it is in the space between them. "Database migration" and "schema change rollout" mean the same thing. A keyword index does not know that. An embedding model does.

This project builds the core technology behind every AI search product: you embed documents into a vector space where meaning corresponds to geometry, then find the nearest neighbors to any query. Once you understand this, you understand the foundation of every RAG system, every AI assistant, and every semantic search product shipped in the last three years.

---

## What You Will Build

A semantic search engine over a collection of plain-text articles. Given a natural language query, the system:

1. Embeds all documents at load time using the Anthropic (or OpenAI) Embeddings API
2. Stores embeddings in a numpy matrix (no external vector database)
3. Embeds the incoming query using the same model
4. Computes cosine similarity between the query vector and every document vector
5. Returns the top-5 most relevant documents with their similarity scores

The final product is a command-line tool that takes a query and prints ranked results with document titles and short excerpts.

---

## Learning Objectives

By completing this project you will be able to:

- Call an embeddings API and understand what the response contains
- Explain why cosine similarity works for comparing embeddings
- Build a nearest-neighbor search without any external library
- Describe the relationship between embedding dimensionality and search quality
- Articulate the difference between semantic and lexical search

---

## Topics Covered

| Phase | Topic | Theory File |
|---|---|---|
| Phase 2 | Tool Calling | `08_LLM_Applications/02_Tool_Calling/Theory.md` |
| Phase 2 | Vector Databases | `08_LLM_Applications/05_Vector_Databases/Theory.md` |
| Phase 2 | Semantic Search | `08_LLM_Applications/06_Semantic_Search/Theory.md` |
| Phase 5 | Embeddings (PEFT context) | `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/Theory.md` |

---

## Prerequisites

- Completed the Beginner Path or equivalent
- Comfortable with Python classes and functions
- API key for Anthropic or OpenAI
- Understanding of what a vector/array is (numpy basics)

---

## Difficulty

Easy (2 / 5 stars)

This project has one external dependency (the embeddings API) and uses only numpy for the math. There is no database, no server, no orchestration framework. The concepts are new but the implementation is straightforward.

---

## Expected Output

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

## Key Concepts You Will Learn

**Embeddings**: A numerical vector (e.g., 1536 numbers) that represents the meaning of a piece of text. Two texts with similar meanings will have vectors that point in similar directions in high-dimensional space.

**Cosine Similarity**: Measures the angle between two vectors. A score of 1.0 means identical direction (same meaning), 0.0 means perpendicular (unrelated), -1.0 means opposite. We use the cosine (not Euclidean distance) because it is scale-invariant — a short document and a long document can express the same idea.

**Nearest Neighbor Search**: Given a query vector, find the k vectors in your collection that are closest (most similar). With numpy, this is a matrix multiplication followed by an argsort.

**Vector Space Model**: The fundamental insight that meaning can be geometry. Documents cluster by topic. Queries land near relevant documents. This is the mathematical heart of modern AI search.

---

## Project Structure

```
01_Semantic_Search_Engine/
├── Project_Guide.md         ← you are here
├── Step_by_Step.md          ← build instructions
├── Starter_Code.md          ← code with TODOs
├── Architecture_Blueprint.md ← system diagram
├── documents/               ← your test corpus (you create this)
│   ├── article_01.txt
│   ├── article_02.txt
│   └── ...
└── semantic_search.py       ← your implementation
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| Project_Guide.md | ← you are here |
| [Step_by_Step.md](./Step_by_Step.md) | Build instructions |
| [Starter_Code.md](./Starter_Code.md) | Code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

**Projects:**
⬅️ No previous project &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 — Personal Knowledge Base RAG](../02_Personal_Knowledge_Base_RAG/Project_Guide.md)
