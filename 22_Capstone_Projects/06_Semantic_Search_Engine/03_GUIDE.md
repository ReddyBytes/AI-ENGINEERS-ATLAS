# Project 6 — Build Guide

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
mkdir 06_Semantic_Search_Engine
cd 06_Semantic_Search_Engine
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### Step 2: Install dependencies

```bash
pip install openai numpy python-dotenv
```

### Step 3: Set up your API key

Create a `.env` file:
```
OPENAI_API_KEY=sk-...
```

Never commit this file. Add `.env` to your `.gitignore`.

### Step 4: Create a test corpus

Create a `documents/` folder and add at least 10 plain text files. Each file should be one article or topic summary (100 to 500 words). You can write your own or use content from the theory files in this repo.

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

<details><summary>💡 Hint — why does variety matter?</summary>

If all your documents are about the same topic, every query will return the same results and you cannot tell if semantic search is working correctly. A diverse corpus lets you verify that "attention mechanism" returns transformer documents and NOT Python decorator documents — which proves the embeddings are capturing meaning, not just keywords.

</details>

---

## Stage 2 — Embedding a Single Document

### Step 5: Understand the embedding API response

Open a Python REPL or a scratch file and call the embeddings API with one sentence:

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
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

<details><summary>💡 Hint — what do these 1536 numbers mean?</summary>

Each number is a coordinate in a 1536-dimensional space. The model learned to place texts with similar meanings at nearby coordinates during training. You cannot interpret individual numbers — the meaning lives in the pattern of all 1536 values together. Two texts with similar meanings will have similar patterns (high cosine similarity). Two unrelated texts will have dissimilar patterns (low cosine similarity).

</details>

### Step 6: Understand cosine similarity

Before writing more code, verify you understand the math. The formula:

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

<details><summary>✅ Answer — why cosine and not Euclidean distance?</summary>

Cosine similarity measures the angle between vectors, not the distance between their tips. This makes it scale-invariant: a short document and a long document that express the same idea will have vectors pointing in similar directions, even if one vector has a much larger magnitude. Euclidean distance would penalize the length difference and return misleading results.

</details>

---

## Stage 3 — Embed All Documents and Store Vectors

### Step 7: Load all documents from disk

Write a function that reads all `.txt` files from the `documents/` directory and returns a list of dicts: `[{"title": "filename", "content": "full text"}, ...]`

The order of this list must be consistent across runs because you match documents to embedding rows by index. Sort by filename.

### Step 8: Embed all documents

Write a function `build_corpus_embeddings(documents)` that:
- Calls the API for each document
- Returns a numpy array of shape `(num_documents, embedding_dim)`

```python
def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding
```

<details><summary>💡 Hint — what if you have many documents?</summary>

Add `time.sleep(0.1)` between API calls to avoid hitting rate limits. For large corpora (100+ documents), the OpenAI API also supports batched input — you can pass a list of strings to `input=` and get all embeddings in one call.

</details>

### Step 9: Save embeddings to disk (caching)

Calling the API for every document every time you run the script wastes money and time. Save your embeddings:

```python
import json

def save_cache(cache_file, data: dict) -> None:
    with open(cache_file, "w") as f:
        json.dump(data, f)

def load_cache(cache_file):
    if not cache_file.exists():
        return None
    with open(cache_file, "r") as f:
        return json.load(f)
```

Add logic: if the cache file exists, load it. Otherwise, call the API and save.

<details><summary>✅ Answer — the full corpus builder with caching</summary>

```python
def build_corpus_embeddings(documents, cache_file=CACHE_FILE):
    cache = load_cache(cache_file) or {}
    embeddings = []
    new_entries = 0

    for doc in documents:
        key = doc["title"]
        if key in cache:
            embeddings.append(cache[key])
        else:
            vector = get_embedding(doc["content"])
            embeddings.append(vector)
            cache[key] = vector
            new_entries += 1
            time.sleep(0.05)  # avoid rate limits

    if new_entries > 0:
        save_cache(cache_file, cache)
        print(f"Embedded {new_entries} new documents.")
    else:
        print("All embeddings loaded from cache.")

    return np.array(embeddings, dtype=np.float32)
```

</details>

---

## Stage 4 — Query and Return Results

### Step 10: Embed the query

Write a function `embed_query(query_text)` that calls the same embedding model and returns a single vector of shape `(1536,)`.

Use the **exact same model** as you used for documents. Mixing models breaks search completely — a query embedded by model A cannot be meaningfully compared to documents embedded by model B.

### Step 11: Compute similarity against all documents

Write a `search()` function that:
1. Embeds the query
2. Computes cosine similarity between the query vector and every row of the corpus matrix
3. Returns the top-k highest scores

Efficient vectorized approach (do not use a Python loop):

```python
def cosine_similarity_batch(query_vector, corpus_matrix):
    dots = corpus_matrix @ query_vector                       # shape (N,)
    corpus_norms = np.linalg.norm(corpus_matrix, axis=1)     # shape (N,)
    query_norm = np.linalg.norm(query_vector)
    similarities = dots / (corpus_norms * query_norm + 1e-10)  # avoid div by zero
    return similarities
```

<details><summary>💡 Hint — why is the vectorized approach better?</summary>

A Python loop calling `cosine_similarity()` once per document runs in O(N) with Python overhead on every iteration. The matrix multiply `corpus_matrix @ query_vector` does the same work in a single C-level BLAS operation — 10 to 100x faster. At 1K documents, this difference is unnoticeable. At 100K documents, it is the difference between a 0.1 second response and a 10 second response.

</details>

### Step 12: Display results

Write a `display_results()` function that prints each result with:
- Rank (1 to 5)
- Similarity score (formatted to 2 decimal places)
- Document title
- First 150 characters of content as an excerpt

```python
def display_results(results: list[dict]) -> None:
    print()
    for r in results:
        print(f"  {r['rank']}. [{r['score']:.2f}] {r['title']}")
        print(f"     {r['excerpt'][:150]}...")
        print()
```

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
- What if the API call fails? Wrap in `try/except` with a helpful error message.

### Step 15: Test with semantically similar but lexically different queries

Try these query pairs — both should return overlapping results even though they use different words:

| Query A | Query B |
|---|---|
| "how does attention work" | "transformer focus mechanism" |
| "training a model" | "gradient descent optimization" |
| "splitting text into pieces" | "chunking documents for RAG" |

<details><summary>✅ Answer — what if my results diverge significantly?</summary>

If semantically similar queries return completely different results, your corpus is probably too small or too uniform. Add more documents covering diverse topics. With fewer than 10 documents, there is not enough signal for the nearest-neighbor search to distinguish meaningfully between semantic clusters.

</details>

---

## Checklist Before Moving On

- [ ] Corpus has at least 10 documents on varied topics
- [ ] Embeddings are cached — running the script twice does not cost extra API calls
- [ ] Cosine similarity is vectorized (no Python loop over documents)
- [ ] Search returns top-5 with scores
- [ ] Semantically similar queries return overlapping results
- [ ] Code is in a single clean `.py` file

---

## Extension Challenges

1. **Batch embeddings**: Send all documents in a single batched request instead of one call per document. Measure the time difference.

2. **Re-ranking**: After getting top-10 by cosine similarity, send the query and top-10 excerpts to Claude and ask it to re-rank them by actual relevance. This is called LLM re-ranking and is used in production systems.

3. **Hybrid search**: Combine semantic similarity with BM25 keyword matching. Average the two scores. When does hybrid outperform pure semantic?

4. **Embedding visualization**: Use PCA or t-SNE to reduce your embeddings to 2D and plot them. Documents about similar topics should cluster together.

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| **03_GUIDE.md** | You are here |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [04_RECAP.md](./04_RECAP.md) | What you built and what comes next |
