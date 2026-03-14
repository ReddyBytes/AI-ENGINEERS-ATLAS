# Project 1 — Semantic Search Engine: Step-by-Step Guide

## Overview

You will build this in five stages. Each stage produces something runnable before you move on.

| Stage | What you build | Time estimate |
|---|---|---|
| 1 | Environment and test corpus | 20 min |
| 2 | Embedding a single document | 30 min |
| 3 | Embedding all documents + storing vectors | 30 min |
| 4 | Query embedding + cosine similarity search | 45 min |
| 5 | Polish: caching, CLI, scoring display | 30 min |

Total: approximately 2.5 hours

---

## Stage 1 — Environment Setup and Test Corpus

### Step 1: Create your project directory and virtual environment

```bash
mkdir 01_Semantic_Search_Engine
cd 01_Semantic_Search_Engine
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### Step 2: Install dependencies

```bash
pip install anthropic numpy python-dotenv
```

If you prefer OpenAI:
```bash
pip install openai numpy python-dotenv
```

### Step 3: Set up your API key

Create a `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Never commit this file. Add `.env` to your `.gitignore`.

### Step 4: Create a test corpus

Create a `documents/` folder and add at least 10 plain text files. Each file should be one article or topic summary (100–500 words). You can write your own or use content from the theory files in this repo.

Suggested topics to cover (variety helps you test that semantic search actually works):
- Attention mechanism in Transformers
- What is backpropagation
- How RAG systems work
- Gradient descent explained
- Python decorators
- What is a neural network
- Tokenization in NLP
- How git works
- REST API design
- Docker containers

**Theory connection:** Read `08_LLM_Applications/06_Semantic_Search/Theory.md` before continuing. Pay attention to the section on corpus construction and why diverse documents make better test cases.

---

## Stage 2 — Embedding a Single Document

### Step 5: Understand the embedding API response

Open a Python REPL or a scratch file and call the embeddings API with one sentence:

```python
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Anthropic uses the Messages API for embeddings differently.
# For embeddings, use the voyage API or OpenAI's text-embedding model.
# This project uses OpenAI embeddings for simplicity, or you can
# use a sentence-transformers model locally.
```

**Important note on Anthropic embeddings:** As of early 2024, the Anthropic API does not expose a direct embeddings endpoint — you would use Voyage AI (Anthropic's embedding partner) or OpenAI. The starter code uses OpenAI's `text-embedding-3-small`. Swap in any provider you prefer.

```python
from openai import OpenAI
client = OpenAI()  # reads OPENAI_API_KEY from environment

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="The attention mechanism allows transformers to focus on relevant tokens"
)

vector = response.data[0].embedding
print(f"Dimensions: {len(vector)}")        # 1536
print(f"First 5 values: {vector[:5]}")
print(f"Type: {type(vector[0])}")          # float
```

Run this. Make sure you see a list of 1536 floats.

**Theory connection:** Read `08_LLM_Applications/05_Vector_Databases/Theory.md` — specifically the section explaining what embedding dimensions represent.

### Step 6: Understand what cosine similarity is

Before writing any more code, verify you understand the math. Open `08_LLM_Applications/06_Semantic_Search/Theory.md` and find the cosine similarity formula:

```
cosine_similarity(A, B) = (A · B) / (|A| × |B|)
```

Where `·` is dot product and `| |` is the vector magnitude (L2 norm). In numpy:

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

Test this with two identical vectors (should return 1.0) and two random vectors.

---

## Stage 3 — Embed All Documents and Store Vectors

### Step 7: Load all documents from disk

Write a function that:
- Reads all `.txt` files from the `documents/` directory
- Returns a list of dicts: `[{"title": "filename", "content": "full text"}, ...]`

### Step 8: Embed all documents

Write a function `embed_corpus(documents)` that:
- Calls the API for each document (or batches them — OpenAI supports batch input)
- Returns a numpy array of shape `(num_documents, embedding_dim)`
- Also returns the list of documents in the same order

**Rate limiting:** If you have many documents, add a `time.sleep(0.1)` between API calls to avoid hitting rate limits.

**Theory connection:** Read `09_RAG_Systems/04_Embedding_and_Indexing/Theory.md` — this covers why we embed at index time (not query time) and how the index is organized.

### Step 9: Save embeddings to disk (caching)

Calling the API for every document every time you run the script wastes money and time. Save your embeddings with numpy:

```python
# Save
np.save("embeddings_cache.npy", embedding_matrix)

# Load
embedding_matrix = np.load("embeddings_cache.npy")
```

Add logic: if `embeddings_cache.npy` exists, load it. Otherwise, call the API and save.

---

## Stage 4 — Query and Return Results

### Step 10: Embed the query

Write a function `embed_query(query_text)` that calls the same embedding model and returns a single vector of shape `(1536,)`.

Use the **exact same model** as you used for documents. Mixing models breaks search completely — a query embedded by model A cannot be meaningfully compared to documents embedded by model B.

### Step 11: Compute similarity against all documents

Write a function `search(query_vector, corpus_matrix, top_k=5)` that:
1. Computes cosine similarity between `query_vector` and every row of `corpus_matrix`
2. Returns the indices of the top-k highest scores, sorted descending

Efficient vectorized approach (do not loop):
```python
# corpus_matrix: shape (N, D)
# query_vector: shape (D,)

# Dot products — shape (N,)
dots = corpus_matrix @ query_vector

# Norms
corpus_norms = np.linalg.norm(corpus_matrix, axis=1)   # shape (N,)
query_norm = np.linalg.norm(query_vector)

# Cosine similarities — shape (N,)
similarities = dots / (corpus_norms * query_norm)

# Top k indices
top_indices = np.argsort(similarities)[::-1][:top_k]
```

### Step 12: Display results

Write a function `display_results(documents, similarities, top_indices)` that prints each result with:
- Rank (1–5)
- Similarity score (formatted to 2 decimal places)
- Document title
- First 150 characters of content as an excerpt

---

## Stage 5 — Polish

### Step 13: Add a CLI loop

Wrap everything in a `main()` function that:
1. Loads documents
2. Loads or builds the embedding cache
3. Enters a `while True` loop: prompt for query, display results, repeat
4. Exits cleanly on `quit` or `exit`

### Step 14: Handle edge cases

- What happens if the corpus is empty? Add a check.
- What if the query is blank? Skip it.
- What if the API call fails? Wrap in try/except with a helpful error message.

### Step 15: Test with semantically similar but lexically different queries

Try these query pairs — both should return overlapping results even though they use different words:

| Query A | Query B |
|---|---|
| "how does attention work" | "transformer focus mechanism" |
| "training a model" | "gradient descent optimization" |
| "splitting text into pieces" | "chunking documents for RAG" |

If your results diverge significantly between query pairs, your corpus may be too small. Add more documents.

---

## Extension Challenges

Once the core system works, try these:

1. **Batch embeddings**: Instead of one API call per document, send all documents in a single batched request. Measure the time difference.

2. **Re-ranking**: After getting top-10 by cosine similarity, send the query and top-10 excerpts to Claude and ask it to re-rank them by actual relevance. This is called LLM re-ranking and is used in production systems.

3. **Hybrid search**: Combine semantic similarity with BM25 keyword matching. Average the two scores. When does hybrid outperform pure semantic?

4. **Embedding visualization**: Use PCA or t-SNE to reduce your embeddings to 2D and plot them. Documents about similar topics should cluster together.

---

## Checklist Before Moving On

- [ ] Corpus has at least 10 documents on varied topics
- [ ] Embeddings are cached — running the script twice does not cost extra API calls
- [ ] Cosine similarity is vectorized (no Python loop over documents)
- [ ] Search returns top-5 with scores
- [ ] Semantically similar queries return overlapping results
- [ ] Code is in a single clean `.py` file

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | What you'll build |
| Step_by_Step.md | ← you are here |
| [Starter_Code.md](./Starter_Code.md) | Code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ No previous project &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 — Personal Knowledge Base RAG](../02_Personal_Knowledge_Base_RAG/Project_Guide.md)
