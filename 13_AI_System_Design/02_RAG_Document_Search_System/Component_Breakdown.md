# Component Breakdown
## Design Case 02: RAG Document Search System

Every component that makes this system work — and critically, why poor implementation of any one of them degrades the entire system.

---

## 1. Document Ingestion Pipeline

The ingestion pipeline is not glamorous but its quality determines the ceiling of your system's accuracy. Garbage in, garbage out. The LLM can only synthesize answers from what you gave it — if your chunks are broken, your answers will be broken.

**Text Extraction:**

Different document formats require different extractors:
- **PDF:** PyMuPDF (`fitz`) — handles most PDFs including scanned ones (with OCR fallback). Watch for multi-column layouts, headers/footers that inject noise, and tables that extract as garbled text.
- **Word (.docx):** `python-docx` — preserves headings, which are useful for metadata extraction.
- **HTML/web pages:** `BeautifulSoup` — strip all tags, keep semantic structure. Watch for JavaScript-rendered content (use Playwright/Selenium for that).
- **Confluence:** Confluence REST API — export page as storage format, parse with `BeautifulSoup`.

**Common extraction problems to solve:**
- **Page headers/footers:** "Page 3 of 47 — Confidential" appears in every chunk if not removed. Use regex to detect and strip repeated short phrases.
- **Tables:** Standard text extraction makes a mess of tables. Consider converting tables to Markdown or structured text: "| Column 1 | Column 2 | → Row 1: Column 1: value..."
- **Mathematical notation:** Equations become garbage text. Either use a LaTeX-aware parser or skip math-heavy documents.
- **Scanned PDFs:** No text layer — need OCR (Tesseract or AWS Textract). Quality is lower than digital PDFs.

**Chunking Strategy:**

`RecursiveCharacterTextSplitter` tries to split at natural boundaries in this priority order:
1. Double newlines (paragraph breaks) — ideal
2. Single newlines — acceptable
3. Periods followed by spaces — preserves sentences
4. Spaces — last resort, splits mid-phrase
5. Characters — never happens with 512 tokens unless your "text" is one long string

**Why 512 tokens with 50-token overlap?** See Architecture Blueprint. The key insight: overlap ensures that a sentence split at a chunk boundary appears fully in at least one chunk. Without overlap, "The refund policy applies to all purchases made within 30 days" might split into "The refund policy applies to all purchases" (chunk N) and "made within 30 days" (chunk N+1), making both useless.

---

## 2. Embedding Model

The embedding model converts text into a fixed-size vector that captures its semantic meaning. Two texts with similar meanings will have high cosine similarity between their vectors.

**Why the same model must be used for indexing and querying:**

The embedding space is model-specific. Vectors from `text-embedding-3-small` are not comparable to vectors from `text-embedding-ada-002`. If you index with one model and query with another, your search results will be random noise.

**Operational implication:** Pin your embedding model version in code. When OpenAI releases a new embedding model, **do not switch without re-indexing the entire knowledge base.** Schedule a re-indexing job, validate quality, then switch over atomically.

**Batching for efficiency:**
```python
# Bad: one API call per chunk (slow, expensive)
for chunk in chunks:
    embed(chunk)  # 1 API call each

# Good: batch 2048 chunks per call (OpenAI limit)
for batch in chunks_batches(chunks, size=2048):
    embed_batch(batch)  # 1 API call for 2048 chunks
```

Batching reduces embedding cost from ~100ms/chunk to ~1ms/chunk amortized.

---

## 3. Vector Store (Pinecone)

Pinecone stores your embeddings and enables fast approximate nearest neighbor (ANN) search. The "approximate" matters — it trades a small amount of accuracy for massive speed improvements.

**How HNSW works (simplified):**
HNSW (Hierarchical Navigable Small World) builds a graph where each node (vector) is connected to its closest neighbors. Searching starts at a random entry point in the highest layer (sparse connections, fast navigation), then descends to denser layers to find the nearest neighbors. At 500K vectors, a search takes ~20ms. At 50M vectors, ~100ms.

**Metadata filtering:**
Every vector in Pinecone has a metadata dictionary. When querying, you can filter by metadata fields before (or after, with `filter`) the ANN search.

```python
# With access control filter
results = index.query(
    vector=query_vector,
    top_k=10,
    filter={"doc_id": {"$in": allowed_doc_ids}},
    include_metadata=True
)
```

**Important:** Pinecone's metadata filter can become slow if `$in` list is very large (>1000 IDs). For large permission sets, use group-level filtering instead of individual document IDs.

**Pod sizing:**
- `s1` pod: optimized for storage (cheaper, slower)
- `p1` pod: balanced speed and storage
- `p2` pod: optimized for query speed — use for production with >100 QPS
- Rule of thumb: at 1M vectors with 1536 dimensions, start with one `p2.x1` pod.

---

## 4. Hybrid Search (Dense + BM25)

Dense vector search alone fails on a category of queries where exact term matching matters: product codes, model numbers, legal article references, names, acronyms.

**Why BM25 complements dense search:**

| Query Type | Dense Search | BM25 | Hybrid |
|---|---|---|---|
| "What is our parental leave policy?" | Excellent — finds semantically related content | Good | Excellent |
| "GDPR Article 17(1)(f)" | Poor — similar vectors for all GDPR articles | Excellent — exact term match | Excellent |
| "Error code E-4021" | Poor — no semantic meaning to error codes | Excellent | Excellent |
| "How does John Smith describe the onboarding process?" | Good | Good (name match) | Excellent |

**Reciprocal Rank Fusion in practice:**

RRF doesn't require score normalization (BM25 scores are not bounded like cosine similarity). It only uses rank position. A document ranked #1 by both systems gets a much higher combined score than one ranked #1 by one system and #5 by the other.

```
RRF score = 1/(k + rank_dense) + 1/(k + rank_bm25)

Where k=60 is a constant that smooths the effect of outliers.
A document ranked #1 by dense: 1/(60+1) = 0.016
A document ranked #1 by both: 0.016 + 0.016 = 0.033 → ranked first
A document ranked #1 dense, #20 bm25: 0.016 + 1/(60+20) = 0.016 + 0.012 = 0.028
```

---

## 5. Reranker (Cohere Rerank)

The reranker is a cross-encoder model: it takes (query, document) pairs and outputs a relevance score by processing them jointly (unlike bi-encoders that process them separately).

**Why this is more accurate:**
A bi-encoder encodes "What is the refund window?" into a single vector. It encodes "Refunds are processed within 14 days of purchase" into another vector. Cosine similarity between them is computed. The model never "sees" the query-document pair together.

A cross-encoder takes both texts concatenated as input: `[CLS] What is the refund window? [SEP] Refunds are processed within 14 days of purchase [SEP]`. It can attend to both simultaneously and model their interaction. Much more accurate. But too slow (100-500ms per pair) to run on all 500K chunks.

**The two-stage retrieval pattern:**
1. Stage 1 (fast): bi-encoder retrieves top-10 from 500K chunks in ~50ms
2. Stage 2 (accurate): cross-encoder reranks the 10 candidates in ~200ms
3. Return top-3 to LLM

**Cohere Rerank is the easiest path** — no infrastructure, $1/1K calls, top-quality model. Alternatives if you need self-hosted: `cross-encoder/ms-marco-MiniLM-L-6-v2` on HuggingFace (free, good quality, runs on a single CPU in ~100ms).

---

## 6. LLM Synthesis

The LLM receives the top-3 reranked chunks and generates a grounded answer with citations.

**Prompt structure for RAG synthesis:**

```
System: You are an enterprise document assistant. Answer questions based ONLY on
the provided documents. If the documents don't contain enough information to
answer the question, say so explicitly. Never speculate or use external knowledge.

Always end your answer with a "Sources:" section listing the document names you
used. If you cite a specific section, include the page or section reference.

Documents:
[DOCUMENT 1] Title: Employee Handbook, Section: Parental Leave Policy
Content: Employees are entitled to 16 weeks of paid parental leave...

[DOCUMENT 2] Title: HR Policy Update 2024-Q3
Content: Effective January 2025, parental leave has been extended to 20 weeks...

User question: How much parental leave am I entitled to?
```

**Critical design decisions:**
- **"ONLY on the provided documents"** — this is the key instruction that prevents hallucination. Without it, the LLM will blend its training knowledge with the retrieved content, producing plausible-sounding but potentially wrong answers.
- **Require citations** — makes the answer verifiable and builds user trust.
- **Explicit conflict handling** — when two documents contradict each other, the LLM should surface the conflict: "According to the Employee Handbook (2022), the policy is X. However, the HR Policy Update (2024-Q3) states Y. The more recent document supersedes the older one."

---

## 7. Query Cache (Redis)

For enterprise document search, many queries are repeated. "What is the expense reimbursement limit?" gets asked 50 times a week by different employees. Caching eliminates these redundant LLM calls.

**Cache key strategy:**
Don't cache on the exact query string (too precise — "what's the expense limit" and "what is the expense limit" are different strings but same query). Instead, embed the query, round the embedding values to 3 decimal places, and hash the result. This gives a "semantic hash" where similar queries hit the same cache entry.

```python
import hashlib, json, numpy as np

def semantic_cache_key(query: str, user_groups: list) -> str:
    embedding = embed(query)
    rounded = np.round(embedding, decimals=3).tolist()
    key_data = {"embedding": rounded, "groups": sorted(user_groups)}
    return "cache:" + hashlib.md5(json.dumps(key_data).encode()).hexdigest()
```

**TTL strategy:**
- FAQ-type queries: TTL 24 hours (policy questions don't change daily)
- Factual queries about specific documents: TTL 1 hour (documents can be updated)
- Queries about "latest" or "current": TTL 15 minutes (time-sensitive)

**Cache invalidation:** When a document is re-indexed (updated), clear all cache entries that involved that document. Store `doc_ids_used` in the cache value, and on re-index trigger a cache scan-and-delete.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| 📄 **Component_Breakdown.md** | ← you are here |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [01 Customer Support Agent](../01_Customer_Support_Agent/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md)
