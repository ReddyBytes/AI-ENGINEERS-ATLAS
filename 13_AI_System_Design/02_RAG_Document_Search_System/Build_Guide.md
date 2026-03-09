# Build Guide
## Design Case 02: RAG Document Search System

Five phases from simple single-document Q&A to a full enterprise search system with access control. Each phase is independently useful — a well-built Phase 2 is more valuable than a half-built Phase 5.

---

## Phase 1: Single Document, Simple RAG (Week 1)

**Goal:** Upload one PDF, ask questions about it, get accurate answers.

**What you build:**
- Document upload endpoint: `POST /documents` (accepts file, stores in S3)
- Ingestion script: extract text → chunk → embed → upsert to Pinecone
- Query endpoint: `POST /search` (accepts question, returns answer + source)

**Implementation details:**

Document text extraction:
```python
import pymupdf  # fitz

def extract_text_from_pdf(file_path: str) -> str:
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text
```

Chunking:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    length_function=len,  # token count via tiktoken is better, but character count works for Phase 1
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_text(document_text)
```

Embedding + upserting (batch for efficiency):
```python
from openai import OpenAI
client = OpenAI()

def embed_and_upsert(chunks: list[str], doc_id: str, index):
    # Batch embedding (OpenAI allows 2048 texts per request)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )
    vectors = []
    for i, chunk in enumerate(chunks):
        vectors.append({
            "id": f"{doc_id}_chunk_{i}",
            "values": response.data[i].embedding,
            "metadata": {
                "doc_id": doc_id,
                "chunk_index": i,
                "content": chunk[:500],  # Store preview for debugging
                "chunk_text": chunk  # Store full text for retrieval
            }
        })
    index.upsert(vectors=vectors, batch_size=100)
```

**Success criteria:** Can answer 80% of questions about the uploaded document correctly.

---

## Phase 2: Multi-Document with Metadata Filtering (Week 2-3)

**Goal:** Handle 100+ documents. Users can filter by document type, author, date.

**What changes:**
- PostgreSQL table for document metadata
- Pinecone metadata includes: `doc_id`, `doc_type`, `author`, `created_date`, `title`
- Query endpoint accepts optional filters: `{ "question": "...", "filters": { "doc_type": "policy", "date_after": "2024-01-01" } }`

**Metadata filtering in Pinecone:**
```python
query_result = index.query(
    vector=query_embedding,
    top_k=10,
    filter={
        "doc_type": {"$eq": "policy"},
        "created_date": {"$gte": "2024-01-01"}
    },
    include_metadata=True
)
```

**Document status tracking (PostgreSQL):**
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    s3_key TEXT UNIQUE NOT NULL,
    doc_type TEXT,
    author TEXT,
    page_count INTEGER,
    chunk_count INTEGER,
    status TEXT DEFAULT 'pending',  -- pending, indexing, indexed, failed
    indexed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Async ingestion with SQS:**
When a file is uploaded to S3, it triggers an SQS message. A worker service polls SQS and processes documents asynchronously. This way, uploading 100 documents doesn't block the API.

**Success criteria:** Can accurately answer questions that require filtering to specific document types or time periods.

---

## Phase 3: Hybrid Search (BM25 + Dense) (Week 4)

**Goal:** Handle queries with specific product codes, model numbers, legal references, and acronyms — things that dense search misses.

**Why dense search fails on keywords:**

Dense vector search finds semantically similar content. "GDPR Article 17" and "right to be forgotten regulation" will have similar embeddings — that's good. But "GDPR Article 17 subsection (c)" and "GDPR Article 17 subsection (d)" may have nearly identical embeddings even though they have different legal meanings. For keyword-precise queries, BM25 wins.

**Implementing BM25 with Elasticsearch:**
```python
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Index a chunk
es.index(index="documents", id=chunk_id, body={
    "doc_id": doc_id,
    "content": chunk_text,
    "title": doc_title
})

# BM25 search
bm25_results = es.search(
    index="documents",
    body={"query": {"match": {"content": user_query}}, "size": 10}
)
```

**Reciprocal Rank Fusion (RRF) to merge results:**
```python
def reciprocal_rank_fusion(dense_results: list, bm25_results: list, k: int = 60) -> list:
    scores = {}
    for rank, result in enumerate(dense_results):
        chunk_id = result["id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank + 1)
    for rank, result in enumerate(bm25_results):
        chunk_id = result["_id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + rank + 1)

    # Sort by combined score descending
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

**Success criteria:** Queries with product SKUs, legal article references, and proper nouns return correct documents. Measure: precision improvement on keyword-heavy test queries compared to dense-only.

---

## Phase 4: Reranking with Cohere (Week 5)

**Goal:** Take top-10 hybrid search results and select the best 3 for the LLM prompt.

**Why reranking matters:**

Your embedding model (bi-encoder) processes the query and document separately, then computes cosine similarity. Fast, but approximate. A cross-encoder processes the query and document together, allowing it to model their interaction. Much more accurate, but 10-100x slower (can't run on all 500K chunks).

The key insight: **run the fast bi-encoder over all chunks, then run the accurate cross-encoder on just the top-10 candidates.** This gives you the accuracy of cross-encoders at manageable cost.

**Cohere Rerank API call:**
```python
import cohere
co = cohere.Client(api_key="...")

reranked = co.rerank(
    model="rerank-english-v3.0",
    query=user_query,
    documents=[chunk["content"] for chunk in top_10_chunks],
    top_n=3
)

# reranked.results[0].index gives the index in your input list
top_3_chunks = [top_10_chunks[r.index] for r in reranked.results]
```

**Cost:** Cohere Rerank is $1/1,000 API calls. At 100K queries/day = $100/day. Cheap insurance against irrelevant chunks reaching the LLM.

**What reranking fixes:**
- The dense search returns a chunk that mentions the topic but doesn't actually answer the question — the reranker deprioritizes it
- Two chunks that look similar by embedding score but have very different relevance to the specific question — the reranker correctly orders them

**Success criteria:** Answer quality improves on ambiguous queries. Measure by LLM-as-judge scores before/after adding reranking.

---

## Phase 5: Access Control and Security (Week 6-7)

**Goal:** Ensure users only get answers from documents they have permission to access.

**Access control model (attribute-based):**

```python
# Document record has access_groups field
{
    "doc_id": "doc_abc",
    "name": "Q4 Financial Report",
    "access_groups": ["finance-team", "executives", "board"]
}

# User record has groups field (from your identity provider)
user_groups = ["finance-team", "all-staff"]  # from JWT claims

# Compute allowed doc IDs
allowed_docs = postgres.query(
    "SELECT id FROM documents WHERE access_groups && %s",
    [user_groups]  # PostgreSQL array overlap operator
)

# Pass allowed doc IDs to vector search
pinecone_filter = {"doc_id": {"$in": [str(id) for id in allowed_docs]}}
```

**Important: filter at the vector search layer, not after.** Never retrieve unauthorized chunks and then discard them in application code. That's a security risk — bugs could leak documents.

**For very large permission sets (user has access to 10,000 docs):** The metadata filter approach breaks down when the allowed_doc_ids list is too large (Pinecone filter has size limits). Alternative: group documents into collections, assign users to collections, filter on collection_id.

**Audit logging:**
```python
# Log every search to PostgreSQL
INSERT INTO search_audit_log (
    user_id, query_hash, doc_ids_accessed,
    timestamp, answer_generated
)
VALUES (%s, %s, %s, NOW(), %s)
```

**Why audit logs matter:** Enterprise customers require them for compliance (SOC2, HIPAA). When an employee leaves and their access is revoked, you need to know what they accessed.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| 📄 **Build_Guide.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [01 Customer Support Agent](../01_Customer_Support_Agent/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md)
