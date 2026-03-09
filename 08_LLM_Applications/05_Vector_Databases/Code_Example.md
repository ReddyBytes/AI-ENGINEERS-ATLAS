# Vector Databases — Code Example

ChromaDB: create a collection, add documents, query by semantic similarity. Full working example in ~20 lines of core code.

```python
# pip install chromadb sentence-transformers
import chromadb
from chromadb.utils import embedding_functions

# ─────────────────────────────────────────────
# SETUP: Create client and collection
# ─────────────────────────────────────────────

# In-memory client (great for dev/testing)
client = chromadb.Client()

# Use sentence-transformers for local embeddings (free, no API key needed)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create a named collection
collection = client.create_collection(
    name="ai_knowledge",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}  # use cosine similarity
)

print("Collection created:", collection.name)


# ─────────────────────────────────────────────
# ADD DOCUMENTS
# ChromaDB embeds them automatically using your embedding_fn
# ─────────────────────────────────────────────

documents = [
    "Python is a high-level programming language known for its simple syntax.",
    "Machine learning is a subset of artificial intelligence that learns from data.",
    "Neural networks are computing systems inspired by biological brain structures.",
    "Gradient descent is an optimization algorithm used to train neural networks.",
    "Natural language processing enables computers to understand human text.",
    "Vector databases store embeddings and enable semantic search at scale.",
    "The Python programming language was created by Guido van Rossum.",
    "Deep learning uses many layers of neural networks to learn complex patterns.",
]

metadata = [
    {"topic": "programming", "level": "beginner"},
    {"topic": "ml", "level": "beginner"},
    {"topic": "deep_learning", "level": "intermediate"},
    {"topic": "optimization", "level": "intermediate"},
    {"topic": "nlp", "level": "beginner"},
    {"topic": "infrastructure", "level": "intermediate"},
    {"topic": "programming", "level": "beginner"},
    {"topic": "deep_learning", "level": "advanced"},
]

ids = [f"doc_{i}" for i in range(len(documents))]

collection.add(
    documents=documents,
    metadatas=metadata,
    ids=ids
)

print(f"Added {collection.count()} documents to collection")


# ─────────────────────────────────────────────
# BASIC SEMANTIC SEARCH
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("BASIC SEMANTIC SEARCH")
print("=" * 60)

query = "how do computers learn?"

results = collection.query(
    query_texts=[query],
    n_results=3
)

print(f"\nQuery: '{query}'")
print("\nTop 3 results:")
for i, (doc, meta, distance) in enumerate(zip(
    results["documents"][0],
    results["metadatas"][0],
    results["distances"][0]
)):
    similarity = 1 - distance  # convert cosine distance to similarity
    print(f"\n{i+1}. [{similarity:.3f}] {doc}")
    print(f"   Topic: {meta['topic']}, Level: {meta['level']}")


# ─────────────────────────────────────────────
# METADATA-FILTERED SEARCH
# Only retrieve documents matching certain metadata
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("METADATA-FILTERED SEARCH")
print("=" * 60)

query2 = "how to build AI models"

# Only search within deep_learning documents
results_filtered = collection.query(
    query_texts=[query2],
    n_results=2,
    where={"topic": "deep_learning"}  # metadata filter
)

print(f"\nQuery: '{query2}' (filtered to topic=deep_learning)")
for i, (doc, meta) in enumerate(zip(
    results_filtered["documents"][0],
    results_filtered["metadatas"][0]
)):
    print(f"\n{i+1}. {doc}")
    print(f"   Level: {meta['level']}")


# ─────────────────────────────────────────────
# FETCH, UPDATE, DELETE
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("CRUD OPERATIONS")
print("=" * 60)

# Get a specific document by ID
result = collection.get(ids=["doc_0"])
print(f"\nFetched doc_0: {result['documents'][0][:60]}...")

# Update a document
collection.update(
    ids=["doc_0"],
    documents=["Python is a versatile, beginner-friendly programming language."],
    metadatas=[{"topic": "programming", "level": "beginner", "updated": True}]
)
print("Updated doc_0")

# Delete a document
collection.delete(ids=["doc_7"])
print(f"Deleted doc_7. New count: {collection.count()}")


# ─────────────────────────────────────────────
# PERSISTENT STORAGE
# Use PersistentClient to save data to disk
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("PERSISTENT STORAGE")
print("=" * 60)

# Saves data to disk — survives program restarts
persistent_client = chromadb.PersistentClient(path="./chroma_db")

persistent_collection = persistent_client.get_or_create_collection(
    name="persistent_docs",
    embedding_function=embedding_fn
)
persistent_collection.add(
    documents=["This document will survive program restarts."],
    ids=["persistent_1"]
)
print(f"Persistent collection has {persistent_collection.count()} docs")
print("Data saved to ./chroma_db/")
```

**Expected output:**
```
Collection created: ai_knowledge
Added 8 documents to collection

BASIC SEMANTIC SEARCH
Query: 'how do computers learn?'
Top 3 results:
1. [0.812] Machine learning is a subset of artificial intelligence...
   Topic: ml, Level: beginner
2. [0.789] Neural networks are computing systems inspired by...
   Topic: deep_learning, Level: intermediate
3. [0.731] Deep learning uses many layers of neural networks...
   Topic: deep_learning, Level: advanced
```

**Install and run:**
```bash
pip install chromadb sentence-transformers
python vector_db_example.py
```

**Key ChromaDB facts:**
- No embedding_function = you must pass raw vectors manually
- `distances` in results = cosine distance (0 = identical, 2 = opposite). Convert with `1 - distance` for similarity score.
- `PersistentClient` saves to disk. Regular `Client()` is in-memory only.
- Switch to cloud: `chromadb.HttpClient(host="...", port=8000)` for shared ChromaDB server.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Vector database comparison |

⬅️ **Prev:** [04 Embeddings](../04_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Semantic Search](../06_Semantic_Search/Theory.md)
