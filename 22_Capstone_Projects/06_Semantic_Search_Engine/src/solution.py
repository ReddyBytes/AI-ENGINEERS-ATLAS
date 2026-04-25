"""
Semantic Search Engine — SOLUTION
===================================
A vector-based search over a collection of plain-text documents.

Usage:
    python solution.py

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

    for filepath in sorted(documents_dir.glob("*.txt")):  # ← sorted() for deterministic order
        content = filepath.read_text(encoding="utf-8").strip()  # ← strip() removes leading/trailing whitespace
        documents.append({"title": filepath.stem, "content": content})  # ← .stem = filename without extension

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
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding  # ← the vector is at response.data[0].embedding


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
            # Cache miss — call the API
            vector = get_embedding(doc["content"])  # ← embed the document content
            embeddings.append(vector)
            cache[cache_key] = vector   # ← store in cache dict so it gets persisted
            new_entries += 1
            time.sleep(0.05)            # ← small delay to stay within rate limits

    if new_entries > 0:
        print(f"Embedded {new_entries} new documents via API.")
        save_cache(cache_file, cache)
    else:
        print("All embeddings loaded from cache. No API calls made.")

    return np.array(embeddings, dtype=np.float32)  # ← convert list-of-lists to (N, 1536) matrix


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
    dots = corpus_matrix @ query_vector                          # ← shape (N,): one dot product per row
    corpus_norms = np.linalg.norm(corpus_matrix, axis=1)        # ← shape (N,): magnitude of each document vector
    query_norm = np.linalg.norm(query_vector)                   # ← scalar: magnitude of query vector
    similarities = dots / (corpus_norms * query_norm + 1e-10)   # ← +1e-10 prevents division by zero on zero vectors
    return similarities


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
    # Embed the query using the same model as documents
    query_vector = np.array(get_embedding(query), dtype=np.float32)  # ← must match dtype of corpus_matrix

    # Compute similarity between query and every document
    similarities = cosine_similarity_batch(query_vector, corpus_matrix)

    # Get indices of top-k documents sorted by descending similarity
    top_indices = np.argsort(similarities)[::-1][:top_k]  # ← argsort ascending, [::-1] reverses to descending

    results = []
    for rank, idx in enumerate(top_indices, start=1):
        doc = documents[idx]
        results.append({
            "rank": rank,
            "score": round(float(similarities[idx]), 4),  # ← round to 4 decimal places
            "title": doc["title"],
            "excerpt": doc["content"][:200],              # ← first 200 characters as preview
        })

    return results


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

    # Check for documents folder before trying to load
    if not DOCUMENTS_DIR.exists():
        print(f"Error: '{DOCUMENTS_DIR}' folder not found.")
        print("Create a 'documents/' folder and add .txt files to it.")
        return

    # Load documents from disk
    documents = load_documents(DOCUMENTS_DIR)

    # Build or load corpus embeddings
    corpus_matrix = build_corpus_embeddings(documents)  # ← shape (N, 1536)

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

        try:
            results = search(query, documents, corpus_matrix)  # ← embed query + cosine similarity
            display_results(results)
        except Exception as e:
            print(f"[Error: {e}]")


# ---------------------------------------------------------------------------
# Demo block
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Demo: create sample documents and run a search if DOCUMENTS_DIR is missing
    if not DOCUMENTS_DIR.exists():
        print("Creating sample documents directory for demo...")
        DOCUMENTS_DIR.mkdir(exist_ok=True)

        sample_docs = {
            "attention_mechanism": (
                "The attention mechanism in Transformers allows the model to focus on "
                "different parts of the input sequence when computing representations. "
                "It computes query, key, and value matrices from the input embeddings. "
                "The dot product of queries and keys determines attention weights, "
                "which are then used to produce a weighted sum of value vectors. "
                "Multi-head attention runs this process in parallel across multiple heads."
            ),
            "gradient_descent": (
                "Gradient descent is an optimization algorithm used to minimize the loss "
                "function during neural network training. The algorithm computes the gradient "
                "of the loss with respect to model parameters and takes a small step in the "
                "opposite direction. The step size is controlled by the learning rate hyperparameter. "
                "Variants include SGD, Adam, and RMSProp."
            ),
            "rag_systems": (
                "Retrieval-Augmented Generation (RAG) combines a retrieval component with "
                "a language model. When a query arrives, the system retrieves relevant documents "
                "from a vector database using semantic search. The retrieved context is appended "
                "to the prompt before sending to the LLM, allowing the model to generate answers "
                "grounded in specific documents rather than relying solely on parametric knowledge."
            ),
            "tokenization": (
                "Tokenization is the process of splitting text into smaller units called tokens. "
                "Modern LLMs use subword tokenization methods like Byte-Pair Encoding (BPE) or "
                "SentencePiece. These methods handle rare words by breaking them into common "
                "subword pieces. The vocabulary typically contains 32K to 100K tokens. "
                "Each token is mapped to an integer ID and then to an embedding vector."
            ),
            "backpropagation": (
                "Backpropagation is the algorithm for computing gradients in neural networks. "
                "It applies the chain rule of calculus to propagate the loss gradient backward "
                "through the computational graph from output to input. Each layer receives the "
                "gradient from the layer above, computes how much it contributed to the error, "
                "and passes gradients further back. These gradients are then used by an optimizer "
                "to update the weights."
            ),
        }

        for title, content in sample_docs.items():
            (DOCUMENTS_DIR / f"{title}.txt").write_text(content, encoding="utf-8")

        print(f"Created {len(sample_docs)} sample documents in {DOCUMENTS_DIR}/\n")

    main()
