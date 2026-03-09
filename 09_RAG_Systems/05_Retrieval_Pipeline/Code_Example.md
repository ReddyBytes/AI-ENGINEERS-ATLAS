# Retrieval Pipeline — Code Example

Full retrieval step — embed query, search ChromaDB, return top-3 chunks with scores. Assumes the index from the embedding section.

```python
# pip install chromadb sentence-transformers
import chromadb
from chromadb.utils import embedding_functions

# ─────────────────────────────────────────────
# SETUP: Connect to existing index
# (Created in 04_Embedding_and_Indexing code example)
# ─────────────────────────────────────────────

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Connect to the persisted index
client = chromadb.PersistentClient(path="./rag_index")
collection = client.get_collection(
    name="company_policies",
    embedding_function=embedding_fn
)

print(f"Connected to index: {collection.count()} documents")


# ─────────────────────────────────────────────
# STEP 1: Basic retrieval function
# ─────────────────────────────────────────────

def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Retrieve top-K most relevant chunks for a query."""
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    # Package results into a clean format
    chunks = []
    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": text,
            "metadata": metadata,
            "similarity": round(1 - distance, 4),  # convert distance to similarity
            "source": metadata.get("source", "unknown"),
            "section": metadata.get("section", "unknown"),
        })

    return chunks


# ─────────────────────────────────────────────
# STEP 2: Test with sample queries
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("RETRIEVAL TEST: Basic queries")
print("=" * 60)

test_queries = [
    "how long do I have to return a product?",
    "what are the shipping delivery times?",
    "how do I reach customer support?",
    "can I change my payment method?",
    "what happens to damaged returned items?",  # specific detail
]

for query in test_queries:
    print(f"\nQuery: '{query}'")
    results = retrieve(query, top_k=3)
    for i, r in enumerate(results):
        print(f"  {i+1}. [{r['similarity']:.3f}] [{r['section']}] {r['text'][:70]}")


# ─────────────────────────────────────────────
# STEP 3: Retrieval with metadata filtering
# Scope search to specific section
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("FILTERED RETRIEVAL: Scope to specific sections")
print("=" * 60)

def retrieve_filtered(query: str, section: str, top_k: int = 3) -> list[dict]:
    """Retrieve chunks filtered by metadata section."""
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"section": section}  # metadata filter
    )

    chunks = []
    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": text,
            "metadata": metadata,
            "similarity": round(1 - distance, 4),
        })
    return chunks


# Only search within the "returns" section
results = retrieve_filtered("how do refunds work?", section="returns")
print(f"\nQuery: 'how do refunds work?' (filtered to returns section)")
for i, r in enumerate(results):
    print(f"  {i+1}. [{r['similarity']:.3f}] {r['text'][:80]}")


# ─────────────────────────────────────────────
# STEP 4: Show how similarity scores help assess quality
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("SIMILARITY SCORES: Relevance assessment")
print("=" * 60)

def retrieve_with_quality_check(query: str, top_k: int = 5,
                                  min_similarity: float = 0.6) -> list[dict]:
    """Retrieve and filter by minimum similarity threshold."""
    results = retrieve(query, top_k=top_k)
    # Filter out low-quality matches
    quality_results = [r for r in results if r["similarity"] >= min_similarity]

    if not quality_results:
        print(f"  WARNING: No results above {min_similarity} similarity threshold!")
        print(f"  Best match was {results[0]['similarity']:.3f} — may be irrelevant")

    return quality_results


# A question that has a good answer in the database
print("\nWell-matched query:")
results = retrieve_with_quality_check("when does free shipping apply?", min_similarity=0.6)
for r in results:
    print(f"  [{r['similarity']:.3f}] {r['text'][:80]}")

# A question that doesn't match well
print("\nPoorly-matched query (out-of-scope topic):")
results = retrieve_with_quality_check("what is the company's vacation policy?", min_similarity=0.6)
# Will likely warn and return no results, or very low-score results


# ─────────────────────────────────────────────
# STEP 5: Multiple query types comparison
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("QUERY VARIETY: Same intent, different phrasing")
print("=" * 60)

# These should all retrieve the same chunk
variant_queries = [
    "how many days to return something",          # direct
    "return window duration",                     # technical
    "can I send back a purchase after a month",   # conversational
    "product return deadline",                    # keyword-style
]

for query in variant_queries:
    results = retrieve(query, top_k=1)
    print(f"\n'{query}'")
    print(f"  Best match [{results[0]['similarity']:.3f}]: {results[0]['text'][:70]}")
```

**Expected output:**
```
Connected to index: 20 documents

RETRIEVAL TEST: Basic queries

Query: 'how long do I have to return a product?'
  1. [0.823] [returns] All product returns must be initiated within 30 days of the purchase date.
  2. [0.741] [returns] To request a refund, customers must provide the original order number...
  3. [0.634] [returns] Items returned in damaged condition are not eligible for a full refund.
```

**Running:**
```bash
# First run 04_Embedding_and_Indexing code to create the index
python embedding_indexing.py

# Then run retrieval
python retrieval_pipeline.py
```

**Key patterns:**
- `1 - distance` converts ChromaDB's cosine distance to similarity (0–1, higher = more similar)
- `where={"section": "..."}` scopes the search to specific metadata
- Use a minimum similarity threshold (e.g., 0.6) to detect out-of-scope queries
- The same semantic intent ("return deadline" vs "days to send back") retrieves the same chunk

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [04 Embedding and Indexing](../04_Embedding_and_Indexing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Context Assembly](../06_Context_Assembly/Theory.md)
