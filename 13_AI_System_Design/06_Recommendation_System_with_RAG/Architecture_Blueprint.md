# Architecture Blueprint
## Design Case 06: Recommendation System with RAG

A hybrid product recommendation engine that combines **collaborative filtering** (what similar users bought) with **RAG over product descriptions** (semantic understanding of what a product actually is). The result is a system that can recommend both "users like you bought this" and "this product is semantically similar to what you're browsing" — and blend both signals intelligently.

---

## System Overview

```mermaid
graph TB
    User["User / Mobile App / Web"]
    APIGateway["API Gateway\nAuth, Rate Limiting\nRequest routing"]

    subgraph RecommendationEngine["Recommendation Engine"]
        ReqHandler["Request Handler\nUser ID + context\n(current item, page, search query)"]
        CFEngine["Collaborative Filtering Engine\nUser embedding lookup\nItem-item similarity"]
        RAGEngine["RAG Engine\nProduct description search\nSemantic similarity"]
        HybridScorer["Hybrid Scorer\nCF score × α + Semantic score × β\nRe-rank + filter"]
        ABRouter["A/B Test Router\nRoute to experiment variant\nLog assignment"]
    end

    subgraph EmbeddingLayer["Embedding Layer"]
        UserEmbedStore[("User Embedding Store\nFAISS / Pinecone\n~10M user vectors")]
        ProductVectorIndex[("Product Vector Index\nPinecone\n~500K product chunks")]
        CFModelStore[("CF Model Store\nMatrix factorization weights\nItem-item similarity matrix")]
    end

    subgraph BatchPipeline["Batch Update Pipeline (Nightly)"]
        EventIngestion["Event Ingestion\nClickstream, purchases, ratings"]
        CFTrainer["CF Model Trainer\nALS / Neural CF\nIncremental updates"]
        EmbeddingRefresher["Product Embedding Refresher\nRe-embed changed products"]
    end

    subgraph RealTimePipeline["Real-Time Pipeline"]
        StreamProcessor["Stream Processor\nKafka + Flink\nUpdate user state on interaction"]
        RealtimeUserUpdate["Real-Time User Embedding\nSession-level signal injection"]
    end

    subgraph Storage["Storage"]
        ProductDB[("PostgreSQL\nProduct catalog\nMetadata, pricing, inventory")]
        UserDB[("PostgreSQL\nUser profiles\nInteraction history")]
        Redis[("Redis\nRecommendation cache\nTTL: 5 min per user")]
        EventLog[("S3 / Data Lake\nAll user events\nFor batch training")]
    end

    subgraph Observability["Observability"]
        ABDashboard["A/B Test Dashboard\nCTR, conversion, revenue lift"]
        RecommendationMetrics["Recommendation Metrics\nCoverage, diversity, novelty"]
    end

    User --> APIGateway
    APIGateway --> ReqHandler
    ReqHandler --> Redis
    Redis -->|Cache miss| ABRouter
    ABRouter --> CFEngine
    ABRouter --> RAGEngine
    CFEngine --> UserEmbedStore
    CFEngine --> CFModelStore
    RAGEngine --> ProductVectorIndex
    CFEngine --> HybridScorer
    RAGEngine --> HybridScorer
    HybridScorer --> ProductDB
    ProductDB --> User

    EventIngestion --> EventLog
    EventLog --> CFTrainer
    CFTrainer --> CFModelStore
    CFTrainer --> UserEmbedStore
    EmbeddingRefresher --> ProductVectorIndex

    StreamProcessor --> RealtimeUserUpdate
    RealtimeUserUpdate --> UserEmbedStore
```

---

## Hybrid Scoring Architecture

The critical design decision: how to blend collaborative filtering scores with semantic similarity scores from RAG.

```mermaid
flowchart TD
    Input["User ID + Context\n(current item / query)"]

    Input --> CFScore["CF Signal\nTop-N similar items\nbased on user embedding\nscored 0.0–1.0"]
    Input --> SemanticScore["RAG Signal\nTop-N products\nby semantic similarity\nto current item/query\nscored 0.0–1.0"]

    CFScore --> Normalize["Normalize scores\nMin-max per signal"]
    SemanticScore --> Normalize

    Normalize --> Blend["Hybrid Blend\nfinal = α × CF_score + β × semantic_score\nα + β = 1.0\n(learned per user segment)"]

    Blend --> BusinessRules["Business Rule Filter\n- Remove out-of-stock\n- Remove already-purchased\n- Apply category caps\n- Apply diversity constraint"]

    BusinessRules --> Rerank["LLM Re-rank (optional, cold start)\nClaude Haiku: pick top-5 from top-20\nusing product description reasoning"]

    Rerank --> TopK["Return Top-K\n(K=10 for homepage, K=4 for PDP)"]
```

---

## Cold Start Architecture

New users have no purchase history. New products have no interaction data. Both require special handling:

```mermaid
flowchart LR
    NewUser{"Is this\na new user?"}

    NewUser -->|"No interaction data"| ColdStart["Cold Start Path"]
    NewUser -->|"Has history"| WarmPath["Standard CF + RAG path"]

    ColdStart --> Onboarding{"Onboarding\ndata available?"}
    Onboarding -->|"Yes (category prefs, quiz)"| ContentBased["Content-Based Bootstrap\nRAG over products matching\nstated preferences"]
    Onboarding -->|"No"| Popular["Popularity-Based Fallback\nTop-N bestsellers\n+ editorial picks\n+ trending"]

    ContentBased --> EarlyPersonalization["Early Personalization\nAfter 3+ interactions:\nSwitch to hybrid CF+RAG"]
    Popular --> EarlyPersonalization
```

---

## Component Table

| Component | Technology | Responsibility | Scales How |
|---|---|---|---|
| API Gateway | AWS API Gateway / Kong | Auth, rate limiting, routing | Horizontal, stateless |
| Request Handler | Python FastAPI | Validate request, check Redis cache, dispatch to engines | Horizontal with Redis shared state |
| Collaborative Filtering Engine | Custom Python service | Load user embedding, query FAISS for top-N similar items | Horizontal; FAISS index loaded in-memory per replica |
| RAG Engine | Python + Pinecone | Embed query/current item, retrieve semantically similar products | Horizontal; Pinecone scales independently |
| Hybrid Scorer | Stateless scoring service | Merge CF and semantic scores, apply business rules, filter inventory | Horizontal, stateless |
| A/B Test Router | Custom + LaunchDarkly | Route users to experiment variants, log assignments | Stateless, millisecond overhead |
| User Embedding Store | FAISS (in-memory) + S3 backup | 10M user vectors for CF nearest-neighbor | FAISS sharded across replicas; nightly rebuild from S3 |
| Product Vector Index | Pinecone | 500K product chunks embedded with text-embedding-3-small | Pinecone managed, auto-scales |
| CF Model Store | S3 + in-memory model | Trained CF model weights + item similarity matrix | Loaded at startup, refreshed nightly |
| Redis | AWS ElastiCache | Cache top-10 recommendations per user, TTL 5 min | Cluster mode |
| PostgreSQL | AWS RDS | Product catalog, user profiles, order history | Read replicas for catalog queries |
| Kafka + Flink | AWS MSK + Kinesis | Real-time event streaming for immediate user state updates | Kafka partitions scale horizontally |
| Batch Pipeline | Airflow + Spark on EMR | Nightly CF model retraining, embedding refreshes | EMR auto-scales with job size |

---

## Latency Budget

For a homepage recommendation load (user opens app):

```
Redis cache check:                     3ms
  Cache miss path only:
  CF engine (FAISS lookup):           12ms
  RAG engine (Pinecone query):        25ms  (runs parallel with CF)
  Hybrid scoring + business rules:     5ms
  Optional LLM rerank (Haiku):       120ms  (only for cold-start users)
─────────────────────────────────────────────────────────────────────
Warm path (cache hit):                 3ms
Cold path (no LLM rerank):            45ms
Cold start path (with Haiku rerank): 165ms
```

Target SLA: P99 < 200ms for warm users, P99 < 500ms for cold start.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Architecture_Blueprint.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component deep dive |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [05 Multi-Agent Workflow](../05_Multi_Agent_Workflow/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 AI Content Moderation Pipeline](../07_AI_Content_Moderation_Pipeline/Architecture_Blueprint.md)
