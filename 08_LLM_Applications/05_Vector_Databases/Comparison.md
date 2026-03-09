# Vector Database Comparison

Pinecone vs ChromaDB vs Weaviate vs pgvector — pick the right tool for your use case.

---

## Side-by-Side Comparison

| Feature | Pinecone | ChromaDB | Weaviate | pgvector |
|---------|----------|----------|----------|----------|
| **Type** | Fully managed cloud | Local / cloud hybrid | Self-hosted + cloud | PostgreSQL extension |
| **Free tier** | Yes (1 index, 100K vectors) | Yes (fully free, open-source) | Yes (open-source self-host) | Free (open-source) |
| **Setup time** | 5 min (API key only) | 2 min (pip install) | 15 min (Docker) | 10 min (if you have Postgres) |
| **Scale** | 100M+ vectors managed | 1M vectors easily | 10M+ with proper config | 1–5M vectors comfortably |
| **Latency** | ~10–50ms cloud | ~1–5ms local | ~5–20ms | ~5–30ms |
| **Metadata filtering** | Yes | Yes | Yes (rich GraphQL filters) | Yes (SQL WHERE) |
| **Hybrid search** | Yes (sparse+dense) | Basic | Yes (BM25 + vector) | Yes (with tsvector) |
| **SQL JOIN support** | No | No | No | Yes (native PostgreSQL) |
| **Multi-modal** | No | No | Yes (image, text, etc.) | No |
| **Infrastructure** | None (fully managed) | None (in-process) | Docker / Kubernetes | PostgreSQL server |
| **Data stays in-house** | No (cloud) | Yes | Yes (self-hosted) | Yes |
| **Pricing model** | Per pod / per vector | Free | Free (self-host) / Cloud pricing | Free (just Postgres cost) |

---

## When to Use Each

### Pinecone
**Best for:** Production SaaS applications where you don't want to manage infrastructure. Teams that want zero DevOps for the vector layer. Applications needing simple horizontal scale.

**Use when:**
- You're building a production app and want it to "just work"
- Your team doesn't have infrastructure bandwidth
- You're comfortable with cloud data residency
- Budget isn't your primary constraint

**Avoid when:**
- Data must stay on-premises (compliance requirements)
- You're on a tight budget
- You want to self-host everything

---

### ChromaDB
**Best for:** Local development, prototyping, research, and applications that don't need massive scale. Also great for embedded use (runs in the same process as your Python app).

**Use when:**
- You're building a proof of concept
- Your corpus is < 500K documents
- You want to get started in under 5 minutes
- You're running offline or air-gapped environments

**Avoid when:**
- You need high concurrent query throughput
- Corpus is growing to millions of documents
- You need enterprise features (access control, monitoring)

---

### Weaviate
**Best for:** Advanced use cases needing multi-modal search (images + text), hybrid search built-in, and GraphQL queries. Teams comfortable with Docker and Kubernetes.

**Use when:**
- You need hybrid search (semantic + keyword) out of the box
- You're doing multi-modal retrieval (text + images)
- You want self-hosted but production-grade
- You need fine-grained access control

**Avoid when:**
- You want a zero-config solution
- Your team isn't comfortable with infrastructure management

---

### pgvector
**Best for:** Teams already using PostgreSQL who want semantic search without adding a new system. Cases where you need to JOIN vector results with relational data.

**Use when:**
- You already have PostgreSQL in your stack
- You need to join vector results with your existing tables
- Corpus is < 3M vectors
- You want a single database system instead of two

**Avoid when:**
- Vector search is the primary workload at scale
- You need specialized vector DB features (namespacing, hybrid search at scale)
- Your corpus is 10M+ vectors with high QPS requirements

---

## Performance Ballpark

| Scenario | Recommended Tool |
|----------|-----------------|
| Local prototype, 10K docs | ChromaDB in-memory |
| Production app, 100K–1M docs, hosted | Pinecone starter |
| Self-hosted production, 1M docs | Weaviate or Qdrant |
| Existing PostgreSQL + < 2M docs | pgvector |
| Enterprise scale, 10M+ docs | Pinecone, Weaviate, or Qdrant |

---

## Pros and Cons Summary

| | Pros | Cons |
|--|------|------|
| **Pinecone** | Managed, scalable, fast setup | Cost, data in cloud, vendor lock-in |
| **ChromaDB** | Free, simple, local-first | Limited scale, no built-in auth |
| **Weaviate** | Feature-rich, hybrid search, multi-modal | Complex setup, steep learning curve |
| **pgvector** | SQL joins, existing stack, no new infra | Limited scale, PostgreSQL overhead |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [04 Embeddings](../04_Embeddings/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Semantic Search](../06_Semantic_Search/Theory.md)
