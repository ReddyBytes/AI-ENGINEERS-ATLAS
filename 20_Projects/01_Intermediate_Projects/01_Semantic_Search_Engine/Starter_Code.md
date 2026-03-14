# Project 1 — Semantic Search Engine: Starter Code

## How to Use This File

Copy the code below into `semantic_search.py`. Every `# TODO:` comment marks something you must implement. Lines that are already written show you the correct structure — do not change function signatures.

Run the code after each TODO to make sure it works before moving to the next.

---

## Setup

```bash
pip install openai numpy python-dotenv
```

Create `.env`:
```
OPENAI_API_KEY=sk-...
```

---

## `semantic_search.py`

```python
"""
Semantic Search Engine
======================
A vector-based search over a collection of plain-text documents.

Usage:
    python semantic_search.py

Requirements:
    pip install openai numpy python-dotenv
"""

import os
import json
import time
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOCUMENTS_DIR = Path("documents")          # folder containing .txt files
CACHE_FILE = Path("embeddings_cache.json") # where we persist embeddings
EMBEDDING_MODEL = "text-embedding-3-small" # 1536 dimensions, cheap, fast
TOP_K = 5                                  # number of results to return

# ---------------------------------------------------------------------------
# Client setup
# ---------------------------------------------------------------------------

client = OpenAI()  # reads OPENAI_API_KEY from environment automatically


# ---------------------------------------------------------------------------
# Step 1: Document loading
# ---------------------------------------------------------------------------

def load_documents(documents_dir: Path) -> list[dict]:
    """
    Load all .txt files from documents_dir.

    Returns a list of dicts:
        [{"title": "filename_without_extension", "content": "full text"}, ...]

    The order of this list MUST stay consistent across runs because we
    match documents to embedding rows by index.
    """
    documents = []

    # TODO: Use Path.glob("*.txt") to find all text files.
    #       Sort them by name so the order is deterministic.
    #       For each file, read its content and append a dict with
    #       keys "title" (stem of filename) and "content" (file text).
    #       Strip leading/trailing whitespace from the content.

    if not documents:
        raise ValueError(
            f"No .txt files found in '{documents_dir}'. "
            "Create the folder and add some documents first."
        )

    print(f"Loaded {len(documents)} documents.")
    return documents


# ---------------------------------------------------------------------------
# Step 2: Embedding a single text
# ---------------------------------------------------------------------------

def get_embedding(text: str) -> list[float]:
    """
    Call the OpenAI Embeddings API and return a vector (list of floats).

    Args:
        text: The text to embed. Keep it under 8192 tokens.

    Returns:
        A list of 1536 floats representing the text in embedding space.
    """
    # TODO: Call client.embeddings.create() with:
    #         model=EMBEDDING_MODEL
    #         input=text
    #       Return response.data[0].embedding
    #
    # Hint: The response looks like:
    #   response.data[0].embedding  →  [0.0023, -0.0141, ...]
    pass


# ---------------------------------------------------------------------------
# Step 3: Build or load the embedding cache
# ---------------------------------------------------------------------------

def load_cache(cache_file: Path) -> dict | None:
    """Load embeddings cache from disk. Returns None if file does not exist."""
    if not cache_file.exists():
        return None
    with open(cache_file, "r") as f:
        return json.load(f)


def save_cache(cache_file: Path, data: dict) -> None:
    """Save embeddings cache to disk."""
    with open(cache_file, "w") as f:
        json.dump(data, f)
    print(f"Cache saved to {cache_file}")


def build_corpus_embeddings(
    documents: list[dict],
    cache_file: Path = CACHE_FILE,
) -> np.ndarray:
    """
    Return a numpy matrix of shape (num_documents, embedding_dim).

    If a valid cache exists and covers all current documents, load from disk.
    Otherwise, call the API for missing documents and save the updated cache.

    Args:
        documents: List of {"title": ..., "content": ...} dicts.
        cache_file: Path to the JSON cache file.

    Returns:
        np.ndarray of shape (N, 1536) where N = len(documents).
    """
    cache = load_cache(cache_file) or {}

    embeddings = []
    new_entries = 0

    for doc in documents:
        cache_key = doc["title"]

        if cache_key in cache:
            # Cache hit — no API call needed
            embeddings.append(cache[cache_key])
        else:
            # TODO: Call get_embedding(doc["content"]) to get the vector.
            #       Append the vector to `embeddings`.
            #       Store the vector in cache[cache_key] so it is saved.
            #       Increment new_entries.
            #       Add time.sleep(0.05) to avoid rate limits.
            pass

    if new_entries > 0:
        print(f"Embedded {new_entries} new documents via API.")
        save_cache(cache_file, cache)
    else:
        print("All embeddings loaded from cache. No API calls made.")

    # TODO: Convert `embeddings` (list of lists) to a numpy array.
    #       Return an ndarray of shape (num_documents, embedding_dim).
    #       Hint: np.array(embeddings) does this directly.
    pass


# ---------------------------------------------------------------------------
# Step 4: Cosine similarity search
# ---------------------------------------------------------------------------

def cosine_similarity_batch(
    query_vector: np.ndarray,
    corpus_matrix: np.ndarray,
) -> np.ndarray:
    """
    Compute cosine similarity between query_vector and every row of corpus_matrix.

    Args:
        query_vector: Shape (D,)
        corpus_matrix: Shape (N, D)

    Returns:
        similarities: Shape (N,) — one score per document, range [-1, 1]
    """
    # TODO: Implement vectorized cosine similarity. Do NOT use a Python loop.
    #
    # Steps:
    #   1. Compute dot products: corpus_matrix @ query_vector  →  shape (N,)
    #   2. Compute L2 norm of each corpus row: np.linalg.norm(corpus_matrix, axis=1)
    #   3. Compute L2 norm of query_vector: np.linalg.norm(query_vector)
    #   4. Divide dot products by (corpus_norms * query_norm)
    #
    # Edge case: if any norm is zero, the similarity is undefined.
    # Add a small epsilon (1e-10) to the denominator to avoid division by zero.
    pass


def search(
    query: str,
    documents: list[dict],
    corpus_matrix: np.ndarray,
    top_k: int = TOP_K,
) -> list[dict]:
    """
    Embed query, compute similarities, return top_k results.

    Args:
        query: Natural language search query.
        documents: List of document dicts (same order as corpus_matrix rows).
        corpus_matrix: Shape (N, embedding_dim).
        top_k: How many results to return.

    Returns:
        List of result dicts, sorted by similarity descending:
        [{"rank": 1, "score": 0.91, "title": "...", "excerpt": "..."}, ...]
    """
    # TODO:
    #   1. Call get_embedding(query) to embed the query.
    #   2. Convert result to np.array with dtype=np.float32.
    #   3. Call cosine_similarity_batch() to get similarity scores.
    #   4. Use np.argsort(similarities)[::-1][:top_k] to get top indices.
    #   5. Build and return a list of result dicts.
    #      Each dict should have: rank, score (float, 2 decimals), title, excerpt.
    #      excerpt = first 200 characters of content.
    pass


# ---------------------------------------------------------------------------
# Step 5: Display and main loop
# ---------------------------------------------------------------------------

def display_results(results: list[dict]) -> None:
    """Print search results in a readable format."""
    if not results:
        print("No results found.")
        return

    print()
    for r in results:
        print(f"  {r['rank']}. [{r['score']:.2f}] {r['title']}")
        print(f"     {r['excerpt'][:150]}...")
        print()


def main():
    """
    Main entry point: load documents, build/load embeddings, run search loop.
    """
    print("=" * 60)
    print("  Semantic Search Engine")
    print("=" * 60)

    # Load documents from disk
    # TODO: Call load_documents(DOCUMENTS_DIR).
    #       If documents_dir does not exist, print a helpful message and exit.
    documents = None  # replace with your call

    # Build or load corpus embeddings
    # TODO: Call build_corpus_embeddings(documents) to get corpus_matrix.
    corpus_matrix = None  # replace with your call

    print(f"\nIndex ready: {len(documents)} documents, "
          f"{corpus_matrix.shape[1]}-dimensional embeddings.\n")

    # Interactive search loop
    print("Type a query to search. Type 'quit' to exit.\n")
    while True:
        try:
            query = input("Search > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not query:
            continue
        if query.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        # TODO: Call search(query, documents, corpus_matrix) and store results.
        #       Call display_results(results).
        #       Wrap in try/except to handle API errors gracefully.


if __name__ == "__main__":
    main()
```

---

## Testing Your Implementation

Once all TODOs are filled in, test with these queries against your corpus:

```python
# Quick unit test — run before the full CLI
import numpy as np

# Test cosine_similarity_batch
a = np.array([1.0, 0.0, 0.0])
b = np.array([[1.0, 0.0, 0.0],   # identical to a → should be 1.0
              [0.0, 1.0, 0.0],   # perpendicular → should be 0.0
              [-1.0, 0.0, 0.0]]) # opposite → should be -1.0

scores = cosine_similarity_batch(a, b)
print(scores)  # Expected: [1.0, 0.0, -1.0]
assert abs(scores[0] - 1.0) < 1e-6
assert abs(scores[1] - 0.0) < 1e-6
assert abs(scores[2] - (-1.0)) < 1e-6
print("All assertions passed.")
```

---

## Common Mistakes

**Wrong model for query vs documents:** Always use the same `EMBEDDING_MODEL` for both. Mismatched models give garbage results with no error.

**Not normalizing:** The cosine similarity formula handles normalization internally. Do not pre-normalize vectors unless you specifically want dot product = cosine similarity.

**Loading cache in wrong order:** If documents are loaded in different order across runs, the cached embedding matrix rows will not match the document list. The sort in `load_documents()` prevents this.

**Passing content vs title to embed:** Embed the `content`, not the `title`. The title is just metadata for display.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | What you'll build |
| [Step_by_Step.md](./Step_by_Step.md) | Build instructions |
| Starter_Code.md | ← you are here |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ No previous project &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 — Personal Knowledge Base RAG](../02_Personal_Knowledge_Base_RAG/Project_Guide.md)
