# Tech Stack
## Design Case 02: RAG Document Search System

Technology choices for every component in both the ingestion pipeline and the query pipeline.

---

## Full Stack Table

| Component | Technology Choice | Why This Choice | Alternatives | When to Switch |
|---|---|---|---|---|
| **Document Storage** | AWS S3 | Infinitely scalable object storage, versioning support, event notifications trigger ingestion, presigned URLs for secure upload/download | Google Cloud Storage, Azure Blob | Switch only if you're on a different cloud provider. Functionality is equivalent. |
| **Text Extraction — PDF** | PyMuPDF (`fitz`) | Fast (C extension), handles digital and scanned PDFs, good table extraction with pdfplumber complement | PDFMiner, Camelot (tables), AWS Textract | AWS Textract if you need enterprise-grade OCR for scanned documents ($0.0015/page). Camelot for table-heavy PDFs. |
| **Text Extraction — Word** | python-docx | Standard library for .docx, preserves heading structure, free | LibreOffice (headless), Tika | Apache Tika if you need one universal parser for 20+ file formats (REST API). |
| **Text Extraction — HTML** | BeautifulSoup + html2text | Strips tags, converts structure to markdown, lightweight | Trafilatura, Playwright | Trafilatura for better article extraction from news/blog pages. Playwright for JavaScript-rendered content. |
| **Chunking** | LangChain RecursiveCharacterTextSplitter | Best general-purpose chunker, respects semantic boundaries, configurable separators | Semantic chunking (embedding-based), fixed-size chunking | Semantic chunking (group sentences by embedding similarity) for higher quality at higher cost. Consider for legal/financial docs. |
| **Embedding Model** | OpenAI text-embedding-3-small | 1536 dims, best price/performance, $0.02/1M tokens, widely tested in production | text-embedding-3-large, Cohere embed-v3, multilingual-e5-large | Cohere embed-v3 for better multilingual performance. text-embedding-3-large for higher accuracy (3072 dims, 5x more expensive). multilingual-e5-large for self-hosted with no API cost. |
| **Vector Store** | Pinecone Managed | Managed service, no infra, excellent Python SDK, metadata filtering, auto-scaling, HNSW index | Weaviate (self-hosted), Qdrant, pgvector, Chroma | Weaviate/Qdrant for self-hosted requirement (data sovereignty). pgvector for < 5M chunks with Postgres simplification. |
| **BM25 / Keyword Search** | Elasticsearch | Industry standard, excellent for full-text search, BM25+ algorithm, metadata filtering, scalable cluster | OpenSearch (AWS), Typesense, Meilisearch | Typesense for simpler setup with good BM25 performance. OpenSearch if you're on AWS and want managed service. |
| **Hybrid Search Merger** | Custom RRF implementation (~30 lines Python) | Simple, no dependencies, mathematically sound, works with any retrieval sources | LlamaIndex hybrid retrieval, Weaviate native hybrid | Use Weaviate native hybrid if you consolidate to Weaviate (one less service to run). |
| **Reranker** | Cohere Rerank API | Best quality cross-encoder, simple API, $1/1K calls, no infrastructure | cross-encoder/ms-marco-MiniLM (HuggingFace), BGE-Reranker-v2-m3 | Self-host `cross-encoder/ms-marco-MiniLM-L-6-v2` if you need to keep data on-premise or want to eliminate API dependency. ~100ms on CPU. |
| **Document Metadata DB** | PostgreSQL | ACID, excellent for relational metadata (doc-to-user permissions), well-known, great tooling | MySQL, DynamoDB | DynamoDB for serverless/auto-scaling if you don't need relational queries on metadata. |
| **Query Cache** | Redis (ElastiCache) | Sub-ms reads, TTL per key, simple key-value, pub/sub for cache invalidation events | Memcached, DynamoDB DAX | Memcached for pure caching if you don't use Redis pub/sub. |
| **Task Queue (Ingestion)** | Celery + Redis broker | Python-native, easy setup, good for document processing workers, retry logic built in | AWS SQS + Lambda, Celery + RabbitMQ | SQS + Lambda for fully serverless. RabbitMQ for more sophisticated routing requirements. |
| **LLM (Synthesis)** | Claude 3.5 Sonnet | Strong instruction following ("only answer from provided docs"), good at synthesis and citation, 200K context, $3/1M input | GPT-4o, Gemini 1.5 Pro | GPT-4o for marginally higher reasoning quality. Both work well for synthesis. Benchmark on your document types. |
| **API Framework** | FastAPI (Python) | Async I/O, native Pydantic validation, auto-generated OpenAPI docs, excellent Python ML ecosystem | Django REST Framework, Node.js | Node.js for teams without Python expertise. DRF if you need batteries-included admin interface. |
| **Auth** | Auth0 / Okta + JWT | Enterprise SSO, group management, JWT claims carry group memberships, SAML/OIDC support for enterprise clients | AWS Cognito, custom JWT | Cognito if you're AWS-native. Custom JWT only for simple internal tools. |

---

## Architecture Variants for Different Scales

### Small Scale: < 100K Documents, < 100 QPS

Skip Elasticsearch entirely. Use Pinecone's dense search only. The hybrid search complexity isn't worth it at this scale.

```
Stack: FastAPI + Pinecone + OpenAI Embeddings + Claude + PostgreSQL
No: Elasticsearch, Redis cache, Celery
Ingestion: Synchronous (process on upload, return when done)
Cost: ~$200/month
```

### Medium Scale: 100K–5M Documents, 100–1,000 QPS

Add hybrid search (Elasticsearch), query caching (Redis), and async ingestion (Celery).

```
Stack: FastAPI + Pinecone + Elasticsearch + OpenAI Embeddings + Claude + PostgreSQL + Redis + Celery
Ingestion: Async via SQS or Celery
Cost: ~$2,000–5,000/month
```

### Large Scale: > 5M Documents, > 1,000 QPS

Switch vector store to Weaviate or Qdrant (self-hosted, better cost at scale). Add quantization to reduce storage. Use self-hosted embedding model for ingestion throughput.

```
Stack: FastAPI + Weaviate (k8s) + Elasticsearch + BGE Embeddings (self-hosted) + Claude + PostgreSQL (RDS) + Redis Cluster + Celery (50 workers)
Cost: ~$15,000–50,000/month (dominated by GPU for embeddings + Weaviate infra)
```

---

## Decision: Why Cohere Rerank Over Self-Hosted?

The Cohere Rerank API is $1 per 1,000 reranking calls. At 100K queries/day = 100 API calls = $0.10/day = **$3/month**. This is negligibly cheap.

A self-hosted cross-encoder (`ms-marco-MiniLM-L-6-v2` on a c5.xlarge AWS instance) costs ~$150/month fixed + ~100ms latency on CPU.

**At < 10M queries/day, use the Cohere API.** The break-even point (API cost > self-hosted cost) is at roughly 50M reranking calls/day. Very few production systems hit this. Self-hosting only makes sense if you have strict data privacy requirements (no data leaving your network) or are at extreme scale.

---

## Embedding Model Comparison

| Model | Dimensions | Quality (MTEB) | Cost | Speed | Best For |
|---|---|---|---|---|---|
| text-embedding-3-small | 1536 | 62.3 | $0.02/1M tokens | Fast (API) | Default choice, best cost/quality |
| text-embedding-3-large | 3072 | 64.6 | $0.13/1M tokens | Fast (API) | Higher accuracy needed, 6.5x price |
| text-embedding-ada-002 | 1536 | 61.0 | $0.10/1M tokens | Fast (API) | Legacy, superseded by 3-small |
| Cohere embed-v3 | 1024 | 64.5 | $0.10/1M tokens | Fast (API) | Better multilingual, similar price to ada |
| multilingual-e5-large | 1024 | 63.2 | $0 (self-hosted) | Slow (CPU) / Fast (GPU) | Multilingual, self-hosted requirement |
| BGE-M3 | 1024 | 66.0 | $0 (self-hosted) | Medium (GPU needed) | Best open-source quality as of 2025 |

**Rule:** Start with `text-embedding-3-small`. Only switch after benchmarking on your specific document types and query distribution.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Tech_Stack.md** | ← you are here |

⬅️ **Prev:** [01 Customer Support Agent](../01_Customer_Support_Agent/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md)
