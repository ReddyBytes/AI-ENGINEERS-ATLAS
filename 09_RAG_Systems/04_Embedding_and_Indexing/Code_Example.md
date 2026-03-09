# Embedding and Indexing — Code Example

Embed 20 document chunks with OpenAI embeddings and store in ChromaDB. Full indexing pipeline ready for retrieval.

```python
# pip install chromadb openai sentence-transformers
import chromadb
from chromadb.utils import embedding_functions
import hashlib

# ─────────────────────────────────────────────
# 20 sample document chunks from a company policy manual
# ─────────────────────────────────────────────

chunks = [
    # Returns & Refunds
    "All product returns must be initiated within 30 days of the purchase date.",
    "To request a refund, customers must provide the original order number and reason for return.",
    "Refunds are processed within 5-7 business days after the returned item is received.",
    "Items returned in damaged condition are not eligible for a full refund.",
    "Digital products and downloadable software cannot be returned once accessed.",

    # Shipping
    "Standard shipping orders are delivered within 5-10 business days.",
    "Express shipping is available for an additional fee and delivers within 2-3 business days.",
    "Free shipping is offered on orders over $50 within the continental United States.",
    "International shipping is available to 45 countries with varying delivery timelines.",
    "Shipping confirmation emails are sent within 24 hours of dispatch.",

    # Customer Support
    "Customer support is available Monday through Friday, 9 AM to 6 PM EST.",
    "Support tickets are typically responded to within 24 hours on business days.",
    "Phone support is available for Premium subscribers at 1-800-SUPPORT.",
    "Live chat support is available on the website for quick questions.",
    "Email support requests should be sent to support@company.com.",

    # Account & Billing
    "Users can update payment methods in the Account Settings section.",
    "Subscriptions automatically renew unless cancelled 24 hours before renewal date.",
    "Annual subscriptions offer a 20% discount compared to monthly billing.",
    "Account passwords must be at least 8 characters and include one number.",
    "Two-factor authentication can be enabled in the Security section of account settings.",
]


# ─────────────────────────────────────────────
# OPTION A: ChromaDB with sentence-transformers (free, local)
# ─────────────────────────────────────────────

print("=" * 60)
print("Setting up ChromaDB with sentence-transformers")
print("=" * 60)

# Use sentence-transformers for free local embeddings
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Create client and collection
client = chromadb.PersistentClient(path="./rag_index")
collection = client.get_or_create_collection(
    name="company_policies",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)

# Generate deterministic IDs from chunk content (hash-based)
def make_chunk_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]

ids = [make_chunk_id(chunk) for chunk in chunks]

# Add metadata for each chunk
metadatas = []
for i, chunk in enumerate(chunks):
    if i < 5:
        section = "returns"
    elif i < 10:
        section = "shipping"
    elif i < 15:
        section = "support"
    else:
        section = "billing"

    metadatas.append({
        "source": "company_policy.pdf",
        "section": section,
        "chunk_index": i,
        "word_count": len(chunk.split())
    })

# Add all chunks to ChromaDB (it embeds them automatically)
collection.add(
    ids=ids,
    documents=chunks,
    metadatas=metadatas
)

print(f"Indexed {collection.count()} document chunks")
print(f"Stored in: ./rag_index/")
print(f"\nSample IDs: {ids[:3]}")


# ─────────────────────────────────────────────
# OPTION B: Using OpenAI API for embeddings (higher quality)
# Uncomment when you have OPENAI_API_KEY set
# ─────────────────────────────────────────────

def index_with_openai(chunks_list: list, collection_name: str):
    """Index chunks using OpenAI's embedding API."""
    from openai import OpenAI

    openai_client = OpenAI()

    # Get embeddings in one batch (up to 2048 items per call)
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks_list
    )

    # Extract vectors
    embeddings = [item.embedding for item in response.data]
    print(f"Generated {len(embeddings)} embeddings, dim={len(embeddings[0])}")

    # Store in ChromaDB (pass vectors directly, no embedding_function needed)
    openai_collection = client.get_or_create_collection("company_policies_openai")

    openai_collection.add(
        ids=[make_chunk_id(c) for c in chunks_list],
        documents=chunks_list,
        embeddings=embeddings,
        metadatas=[{"source": "policy.pdf"} for _ in chunks_list]
    )
    print(f"Indexed {openai_collection.count()} chunks with OpenAI embeddings")
    return openai_collection

# Uncomment to use OpenAI:
# openai_collection = index_with_openai(chunks, "company_policies_openai")


# ─────────────────────────────────────────────
# Verify the index — do some quick test queries
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("Verifying index with test queries")
print("=" * 60)

test_queries = [
    "how long do I have to return something?",
    "when will my order arrive?",
    "how do I contact customer service?",
    "can I change my credit card?",
]

for query in test_queries:
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    print(f"\nQuery: '{query}'")
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        similarity = 1 - dist
        print(f"  [{similarity:.3f}] [{meta['section']}] {doc[:70]}")


# ─────────────────────────────────────────────
# Section-filtered query
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("Metadata-filtered query (only returns section)")
print("=" * 60)

results = collection.query(
    query_texts=["product damage"],
    n_results=3,
    where={"section": "returns"}
)

print("Query: 'product damage' (filtered to returns section)")
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"  [{meta['section']}] {doc[:80]}")


# ─────────────────────────────────────────────
# Show index statistics
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("Index Statistics")
print("=" * 60)

print(f"Total documents: {collection.count()}")

# Show all unique sections
all_docs = collection.get()
sections = set(m["section"] for m in all_docs["metadatas"])
for section in sorted(sections):
    count = sum(1 for m in all_docs["metadatas"] if m["section"] == section)
    print(f"  {section}: {count} chunks")
```

**Expected output:**
```
Indexed 20 document chunks
Stored in: ./rag_index/

Verifying index with test queries

Query: 'how long do I have to return something?'
  [0.812] [returns] All product returns must be initiated within 30 days...
  [0.743] [returns] To request a refund, customers must provide the original...

Query: 'when will my order arrive?'
  [0.831] [shipping] Standard shipping orders are delivered within 5-10 business days.
  [0.789] [shipping] Express shipping is available for an additional fee...
```

**Install and run:**
```bash
pip install chromadb sentence-transformers
python embedding_indexing.py
```

**Key patterns:**
- Use `PersistentClient(path="./")` to save the index to disk
- `get_or_create_collection` is idempotent — safe to run multiple times
- Pass `embedding_function` to let ChromaDB auto-embed. Or pass raw `embeddings=` for pre-computed vectors
- Use `where={"section": "..."}` for metadata-filtered queries
- Generate chunk IDs deterministically (content hash) so re-running is idempotent

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [03 Chunking Strategies](../03_Chunking_Strategies/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Retrieval Pipeline](../05_Retrieval_Pipeline/Theory.md)
