# Project 6 — Architecture

## System Overview

The semantic search engine is a two-phase system: an offline **indexing phase** that embeds documents once and caches them to disk, and an online **query phase** that embeds the user's query and runs a vectorized nearest-neighbor search.

---

## Full System Diagram

```mermaid
flowchart TD
    subgraph OFFLINE["Indexing Phase (runs once)"]
        A[".txt files on disk"] --> B["load_documents()"]
        B --> C["Document list\n[title, content]"]
        C --> D{"Cache exists?"}
        D -- Yes --> E["Load from\nembeddings_cache.json"]
        D -- No --> F["Embeddings API\ntext-embedding-3-small"]
        F --> G["Save to\nembeddings_cache.json"]
        E --> H["corpus_matrix\nshape: (N, 1536)"]
        G --> H
    end

    subgraph ONLINE["Query Phase (runs per query)"]
        I["User query string"] --> J["get_embedding(query)"]
        J --> K["Embeddings API\ntext-embedding-3-small"]
        K --> L["query_vector\nshape: (1536,)"]
        L --> M["cosine_similarity_batch()"]
        H --> M
        M --> N["similarity scores\nshape: (N,)"]
        N --> O["np.argsort()[::-1][:5]"]
        O --> P["Top-5 indices"]
        P --> Q["Ranked results\nwith scores + excerpts"]
    end

    Q --> R["Display to user"]
```

---

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant App as semantic_search.py
    participant Disk as File System
    participant API as Embeddings API

    Note over App,Disk: Startup (indexing phase)
    App->>Disk: Read .txt files from documents/
    Disk-->>App: List of documents
    App->>Disk: Check embeddings_cache.json
    alt Cache miss
        App->>API: embed(document_1_content)
        API-->>App: vector [1536 floats]
        App->>API: embed(document_2_content)
        API-->>App: vector [1536 floats]
        App->>Disk: Save embeddings_cache.json
    else Cache hit
        Disk-->>App: corpus_matrix (N x 1536)
    end

    Note over User,App: Runtime (query phase)
    User->>App: "how does attention work?"
    App->>API: embed("how does attention work?")
    API-->>App: query_vector [1536 floats]
    App->>App: cosine_similarity_batch(query_vector, corpus_matrix)
    App->>App: argsort → top-5 indices
    App-->>User: Ranked results with scores
```

---

## Embedding Space Concept

```mermaid
graph LR
    subgraph "High-dimensional space (1536D, shown simplified)"
        Q(["Query:\n'attention mechanism'"])
        D1(["Doc 1:\nAttention in Transformers"])
        D2(["Doc 2:\nSelf-attention deep dive"])
        D3(["Doc 3:\nBackpropagation explained"])
        D4(["Doc 4:\nPython decorators"])
    end

    Q -.->|"cos sim: 0.91"| D1
    Q -.->|"cos sim: 0.87"| D2
    Q -.->|"cos sim: 0.21"| D3
    Q -.->|"cos sim: 0.09"| D4
```

Documents about similar topics cluster together in embedding space. The query lands closest to semantically related documents — regardless of exact word overlap.

---

## Component Table

| Component | File/Function | Purpose | Key Detail |
|---|---|---|---|
| Document Loader | `load_documents()` | Reads `.txt` files from disk | Sorted by name for consistent ordering |
| Embedding API Client | `get_embedding()` | Converts text to vector | Always use same model for docs and queries |
| Cache Manager | `load_cache()` / `save_cache()` | Persist embeddings to JSON | Keyed by document title; avoids re-embedding |
| Corpus Builder | `build_corpus_embeddings()` | Combines loader + cache + API | Returns numpy matrix `(N, 1536)` |
| Similarity Engine | `cosine_similarity_batch()` | Scores query against all docs | Vectorized numpy — no Python loop |
| Ranker | Inside `search()` | Sorts scores, picks top-k | `np.argsort(scores)[::-1][:k]` |
| Display | `display_results()` | Formats output for terminal | Shows rank, score, title, excerpt |
| Main Loop | `main()` | Ties everything together | Load once, query repeatedly |

---

## Key Data Structures

```
documents: list[dict]
    [
        {"title": "attention_mechanism", "content": "Transformers use..."},
        {"title": "backpropagation",     "content": "Backprop is..."},
        ...
    ]
    Length: N

corpus_matrix: np.ndarray
    Shape: (N, 1536)
    dtype: float32
    Row i corresponds to documents[i]

query_vector: np.ndarray
    Shape: (1536,)
    dtype: float32

similarities: np.ndarray
    Shape: (N,)
    Values: [-1.0, 1.0]
    Index i is the similarity to documents[i]
```

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Language | Python 3.9+ | Pathlib, type hints |
| Embeddings | OpenAI `text-embedding-3-small` | 1536 dims, cheap, fast |
| Math | `numpy` | Vectorized cosine similarity — no loops |
| Cache | `json` + `pathlib` | Persist embeddings to disk without a database |
| Config | `python-dotenv` | Load API key from `.env` file |

---

## How This Scales

| Scale | Approach |
|---|---|
| 1K documents | This numpy approach — fine |
| 10K documents | Add ChromaDB (see Project 2) |
| 1M+ documents | FAISS with IVF index or Pinecone |
| Multi-modal | Use CLIP embeddings for image+text |

---

## Cost and Performance

| Metric | Value | Notes |
|---|---|---|
| Embedding cost | ~$0.00002 per 1K tokens | `text-embedding-3-small` pricing |
| 10 docs x 300 words each | ~$0.0001 total | One-time at index time |
| Query cost | ~$0.000001 per query | Single embedding call |
| Search latency | < 1ms | Numpy matrix multiply on CPU |
| API latency | 100–300ms | Per call to embeddings API |

---

## 📂 Navigation

| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and objectives |
| **02_ARCHITECTURE.md** | You are here |
| [03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [src/starter.py](./src/starter.py) | Starter code with TODOs |
| [04_RECAP.md](./04_RECAP.md) | What you built and what comes next |
