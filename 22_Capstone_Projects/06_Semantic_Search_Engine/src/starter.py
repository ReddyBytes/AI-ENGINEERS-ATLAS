"""
Semantic Search Engine
======================
A vector-based search over a collection of plain-text documents.

Usage:
    python starter.py

Requirements:
    pip install openai numpy python-dotenv

Setup:
    Create a .env file with: OPENAI_API_KEY=sk-...
    Create a documents/ folder with at least 10 .txt files
"""

import os
import json
import time
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # ← reads .env file and sets environment variables

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOCUMENTS_DIR = Path("documents")           # ← folder containing .txt files
CACHE_FILE = Path("embeddings_cache.json")  # ← where we persist embeddings
EMBEDDING_MODEL = "text-embedding-3-small"  # ← 1536 dimensions, cheap, fast
TOP_K = 5                                   # ← number of results to return

# ---------------------------------------------------------------------------
# Client setup
# ---------------------------------------------------------------------------

client = OpenAI()  # ← reads OPENAI_API_KEY from environment automatically


# ---------------------------------------------------------------------------
# Step 1: Document loading
# ---------------------------------------------------------------------------

def load_documents(documents_dir: Path) -> list[dict]:
    """
    Load all .txt files from documents_dir.

    Returns a list of dicts:
        [{"title": "filename_without_extension", "content": "full text"}, ...]

    Why sort? The order of this list MUST stay consistent across runs
    because we match documents to embedding rows by index position.
    If a new document is added, it gets a new index at the end.
    """
    documents = []

    # TODO: Use documents_dir.glob("*.txt") to find all text files.
    # Sort them by name so the order is deterministic across runs.
    # For each file:
    #   - read its content with encoding="utf-8"
    #   - strip leading/trailing whitespace from content
    #   - append {"title": file.stem, "content": content}  ← file.stem = name without extension
    #
    # Example:
    # for filepath in sorted(documents_dir.glob("*.txt")):
    #     content = filepath.read_text(encoding="utf-8").strip()
    #     documents.append({"title": filepath.stem, "content": content})

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

    Critical: always use the same model for both documents AND queries.
    Mixing models produces garbage results with no error message.
    """
    # TODO: Call client.embeddings.create() with:
    #   model=EMBEDDING_MODEL
    #   input=text
    # Return response.data[0].embedding
    #
    # The response looks like:
    #   response.data[0].embedding  →  [0.0023, -0.0141, ...]  (1536 floats)
    pass  # TODO: replace with your implementation


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
    """Save embeddings cache to disk as JSON."""
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
    cache = load_cache(cache_file) or {}  # ← empty dict if no cache

    embeddings = []
    new_entries = 0

    for doc in documents:
        cache_key = doc["title"]  # ← use title as the cache key

        if cache_key in cache:
            # Cache hit — no API call needed
            embeddings.append(cache[cache_key])
        else:
            # TODO: Cache miss — call get_embedding(doc["content"]) to get the vector.
            # Append the vector to `embeddings`.
            # Store vector in cache[cache_key] so it gets saved.
            # Increment new_entries.
            # Add time.sleep(0.05) to stay within rate limits.
            pass  # TODO: replace with your implementation

    if new_entries > 0:
        print(f"Embedded {new_entries} new documents via API.")
        save_cache(cache_file, cache)
    else:
        print("All embeddings loaded from cache. No API calls made.")

    # TODO: Convert `embeddings` (a list of lists) to a numpy array.
    # Return ndarray of shape (num_documents, 1536).
    # Hint: np.array(embeddings, dtype=np.float32) does this.
    pass  # TODO: replace with your implementation


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
        query_vector:  Shape (D,)  ← 1 query
        corpus_matrix: Shape (N, D) ← N documents

    Returns:
        similarities: Shape (N,) — one score per document, range [-1, 1]

    Why vectorized? A Python loop calling cosine_similarity() once per document
    runs with Python overhead on every iteration. The matrix multiply
    corpus_matrix @ query_vector does all N dot products in a single C-level
    BLAS call — 10 to 100x faster.

    Formula: cosine(A, B) = (A · B) / (|A| × |B|)
    """
    # TODO: Implement vectorized cosine similarity. Do NOT use a Python loop.
    #
    # Steps:
    #   1. dots = corpus_matrix @ query_vector         → shape (N,)
    #   2. corpus_norms = np.linalg.norm(corpus_matrix, axis=1)  → shape (N,)
    #   3. query_norm = np.linalg.norm(query_vector)
    #   4. similarities = dots / (corpus_norms * query_norm + 1e-10)
    #      The + 1e-10 avoids division by zero for zero vectors.
    pass  # TODO: replace with your implementation


def search(
    query: str,
    documents: list[dict],
    corpus_matrix: np.ndarray,
    top_k: int = TOP_K,
) -> list[dict]:
    """
    Embed query, compute similarities, return top_k results.

    Args:
        query:         Natural language search query.
        documents:     List of document dicts (same order as corpus_matrix rows).
        corpus_matrix: Shape (N, embedding_dim).
        top_k:         How many results to return.

    Returns:
        List of result dicts, sorted by similarity descending:
        [{"rank": 1, "score": 0.91, "title": "...", "excerpt": "..."}, ...]
    """
    # TODO:
    #   1. Call get_embedding(query) to embed the query
    #   2. Convert result to np.array with dtype=np.float32
    #   3. Call cosine_similarity_batch() to get similarity scores
    #   4. Use np.argsort(similarities)[::-1][:top_k] to get top indices
    #      ← [::-1] reverses the sort to descending order
    #   5. Build and return a list of result dicts.
    #      Each dict: rank, score (round to 4 decimals), title, excerpt
    #      excerpt = first 200 characters of content
    pass  # TODO: replace with your implementation


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
    # TODO: Check if DOCUMENTS_DIR exists. If not, print a helpful message and exit.
    # Then call load_documents(DOCUMENTS_DIR).
    if not DOCUMENTS_DIR.exists():
        print(f"Error: '{DOCUMENTS_DIR}' folder not found.")
        print("Create a 'documents/' folder and add .txt files to it.")
        return

    documents = None  # TODO: documents = load_documents(DOCUMENTS_DIR)

    # Build or load corpus embeddings
    # TODO: Call build_corpus_embeddings(documents) to get corpus_matrix.
    corpus_matrix = None  # TODO: replace with your call

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
        # Call display_results(results).
        # Wrap in try/except to handle API errors gracefully.
        try:
            results = None  # TODO: search(query, documents, corpus_matrix)
            display_results(results)
        except Exception as e:
            print(f"[Error: {e}]")


if __name__ == "__main__":
    main()
