# Data Flow Diagram
## Design Case 02: RAG Document Search System

Two completely separate flows: the asynchronous ingestion pipeline (triggered by document uploads) and the real-time query pipeline (triggered by user questions).

---

## Flow 1: Document Ingestion Pipeline

This flow runs asynchronously in the background. It is triggered by an S3 upload event and can take seconds to minutes depending on document size.

```mermaid
sequenceDiagram
    actor Admin as Admin / User
    participant S3
    participant SQS as SQS Queue
    participant Worker as Ingestion Worker
    participant Tika as Text Extractor
    participant Splitter as Chunking Service
    participant OpenAI as OpenAI Embeddings
    participant Pinecone
    participant Postgres

    Admin->>S3: PUT document.pdf
    S3->>SQS: S3 Event Notification (key, bucket, size)
    SQS->>Worker: Poll: new document to process

    Worker->>Postgres: INSERT document (status=indexing)
    Worker->>S3: GET document.pdf (raw bytes)

    Worker->>Tika: Extract text from PDF
    Tika-->>Worker: Raw text string (~50,000 chars)

    Worker->>Worker: Clean text (remove headers, normalize whitespace)
    Worker->>Splitter: Split into chunks (512 tokens, 50 overlap)
    Splitter-->>Worker: [chunk_1, chunk_2, ..., chunk_N] (~100 chunks)

    Worker->>OpenAI: POST /embeddings (batch of 100 chunks)
    OpenAI-->>Worker: [embedding_1, ..., embedding_100] (1536 dims each)

    Worker->>Pinecone: upsert(vectors, metadata)
    Note over Worker,Pinecone: Each vector: ID, embedding, {doc_id, chunk_index, content_preview, access_groups}

    Worker->>Postgres: UPDATE document (status=indexed, chunk_count=100, indexed_at=NOW())
    Worker->>SQS: Delete message (acknowledge)

    Note over Admin: Admin gets webhook/email: "Document indexed successfully (100 chunks)"
```

**Error handling in the ingestion pipeline:**
- Text extraction fails (corrupt PDF): Update status to `failed_extraction`, dead-letter queue for manual review
- Embedding API fails: Retry with exponential backoff (3 attempts), then DLQ
- Pinecone upsert fails: Retry, then mark status `failed_indexing`
- On retry: delete any partially-upserted vectors first to avoid duplicates

---

## Flow 2: Query Pipeline (Happy Path)

This flow runs in real-time on every user search. Target: P99 < 3 seconds.

```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI
    participant Auth as Auth Service
    participant Postgres as PostgreSQL
    participant Redis
    participant QueryEmbed as Query Embedder
    participant Pinecone
    participant ES as Elasticsearch (BM25)
    participant Merger as Hybrid Search Merger
    participant Reranker as Cohere Rerank
    participant LLM as Claude 3.5 Sonnet

    User->>API: POST /search { query: "What is the refund policy?", filters: {doc_type: "policy"} }
    API->>Auth: Validate JWT → get user_id, user_groups

    par Parallel: Permission check + Cache check
        Auth->>Postgres: SELECT allowed_doc_ids WHERE access_groups && user_groups
        Postgres-->>Auth: [doc_id_1, doc_id_2, ..., doc_id_847]
    and
        API->>Redis: GET cache:{semantic_hash(query + user_groups)}
        Redis-->>API: null (cache miss)
    end

    Note over API: Build Pinecone filter: {doc_id: {$in: [...847 IDs...], doc_type: "policy"}}

    par Parallel: Dense + BM25 Search
        API->>QueryEmbed: Embed user query
        QueryEmbed-->>API: query_vector [1536 floats] (~50ms)
        API->>Pinecone: query(vector, top_k=10, filter)
        Pinecone-->>API: [chunk_1..chunk_10] with scores (~30ms)
    and
        API->>ES: match query on content field (filtered to allowed docs)
        ES-->>API: [chunk_a..chunk_j] BM25 ranked (~20ms)
    end

    API->>Merger: RRF merge(dense_results, bm25_results)
    Merger-->>API: [merged_top_10] reranked by RRF score

    API->>Reranker: POST rerank(query, [10 chunks])
    Reranker-->>API: [top_3_chunks] reranked by cross-encoder score (~200ms)

    API->>LLM: Generate answer from top_3_chunks
    Note over API,LLM: System: "Answer only from docs. Cite sources."\nDocs: [chunk1, chunk2, chunk3]\nQuestion: user_query
    LLM-->>API: { answer: "...", sources: ["Policy Doc p.3", "HR Update 2024"] } (~800ms)

    API->>Redis: SET cache:{hash} {answer, sources} EX 3600
    API->>Postgres: INSERT search_audit_log (user_id, query_hash, doc_ids_used)

    API-->>User: { answer: "...", sources: [...], latency_ms: 1200 }
```

---

## Latency Budget Analysis

```mermaid
gantt
    title Query Pipeline Latency Budget (1200ms total target)
    dateFormat X
    axisFormat %Lms

    section Auth
    JWT validate + permission lookup   :0, 50

    section Search (Parallel)
    Query embedding                    :50, 100
    Pinecone dense search              :50, 80
    Elasticsearch BM25 search          :50, 70

    section Reranking
    Wait for both search results       :100, 110
    Cohere Rerank API                  :110, 310

    section Generation
    LLM synthesis (Claude streaming)   :310, 1100

    section Overhead
    Cache check + response write       :1100, 1200
```

**Bottleneck analysis:**
- **LLM inference** dominates: 800ms of the 1200ms total
- **Mitigation:** Stream the response — user sees first tokens at ~300ms even though full response takes 1.1s
- **Reranking:** 200ms is the second largest cost — worth it for quality but can be skipped for simple queries
- **Dense + BM25 search run in parallel** — the combined retrieval phase only costs ~100ms (max of the two, not sum)

---

## Document Update Flow

When an existing document is modified (e.g., policy updated), we need to re-index it without leaving stale chunks.

```mermaid
flowchart TD
    A["New document version uploaded\nSame document name / ID"] --> B
    B["Worker detects existing doc_id in Postgres"] --> C
    C["Delete all Pinecone vectors\nfilter: doc_id = existing_id"] --> D
    D["Delete from Elasticsearch\ndoc_id filter"] --> E
    E["Run full ingestion pipeline\non new document version"] --> F
    F["Update Postgres: new chunk_count, indexed_at"] --> G
    G["Invalidate Redis cache\nfor entries that used this doc_id"] --> H
    H["Notify: re-indexing complete"]
```

**Why delete first?** If you upsert without deleting, you get orphan chunks from the old version mixed with chunks from the new version. The LLM will find contradictory information in the same document.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| 📄 **Data_Flow_Diagram.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [01 Customer Support Agent](../01_Customer_Support_Agent/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md)
