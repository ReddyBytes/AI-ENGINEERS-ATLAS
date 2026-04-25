# Project 10 — Production RAG System: Architecture

## System Overview

The production RAG system wraps the core RAG pipeline from Project 2 with four orthogonal production layers. Each layer is independently testable. They integrate into a single query pipeline at the end.

---

## Full System Architecture

```mermaid
flowchart TD
    U["User query"] --> IG["Input Guardrails\ncheck_input()"]

    IG -- "BLOCKED" --> BLOCK1["Return rejection\nmessage + log"]

    IG -- "SAFE" --> EMBED["embed_query()\nOpenAI embeddings\nreturns vector + token count"]

    EMBED --> CACHE["Semantic Cache Lookup\nSemanticCache.lookup()"]

    CACHE -- "HIT (similarity >= 0.92)" --> CACHED["Return cached answer\nLog: cache_hit=True, cost=$0"]

    CACHE -- "MISS" --> RETRIEVE["retrieve_chunks()\nChromaDB query\ntop-5 chunks"]

    RETRIEVE --> ASSEMBLE["assemble_context()\nFormat SOURCE 1..5 block"]

    ASSEMBLE --> GENERATE["generate_answer()\nClaude API\nreturns text + token counts"]

    GENERATE --> OG["Output Guardrails\ncheck_output()"]

    OG -- "BLOCKED (PII)" --> BLOCK2["Return safety message\nLog: blocked=True"]

    OG -- "SOFT WARNING" --> WARN["Log warning\nContinue"]

    OG -- "SAFE" --> COST["Cost Calculation\ncalculate_cost(tokens)"]

    WARN --> COST

    COST --> CSTORE["Cache Store\ncache.store(query, embedding, answer)"]

    CSTORE --> LOG["Log Stats\nlog_query(db, tokens, cost, latency)"]

    LOG --> DISPLAY["Display answer + sources"]
```

---

## Semantic Cache Internals

```mermaid
flowchart LR
    subgraph LOOKUP["Cache Lookup"]
        Q["query_text"] --> E["embed(query)"]
        E --> QV["query_vector (1536d)"]
        QV --> SIM["cosine_similarity_batch(\nquery_vector,\nall_cached_vectors)"]
        DB["SQLite\nquery_cache table"] --> LOAD["Load all rows\njson.loads(embedding)"]
        LOAD --> MAT["cached_matrix\n(N x 1536)"]
        MAT --> SIM
        SIM --> MAX["max similarity\nand index"]
        MAX --> THRESH{"similarity\n>= 0.92?"}
        THRESH -- Yes --> HIT["Cache HIT\nReturn cached answer"]
        THRESH -- No --> MISS["Cache MISS\nProceed to RAG"]
    end

    subgraph STORE["Cache Store (after RAG)"]
        ANS["answer + sources"] --> INSERT["INSERT INTO query_cache\n(query, embedding JSON,\nanswer, sources)"]
        INSERT --> COMMIT["SQLite commit"]
    end
```

---

## SQLite Database Schema

```mermaid
erDiagram
    query_cache {
        INTEGER id PK
        TEXT query_text
        TEXT embedding "JSON array of 1536 floats"
        TEXT answer_text
        TEXT sources "JSON array of source strings"
        INTEGER hit_count
        REAL created_at "Unix timestamp"
    }

    query_stats {
        INTEGER id PK
        TEXT query_text
        INTEGER cache_hit "0 or 1"
        INTEGER embed_tokens
        INTEGER input_tokens
        INTEGER output_tokens
        REAL cost_usd
        INTEGER latency_ms
        INTEGER blocked "0 or 1"
        REAL created_at "Unix timestamp"
    }
```

Both tables share the same SQLite database file (`production_rag.db`). The cache's `hit_count` column increments each time a cached entry is served.

---

## Guardrails Decision Tree

```mermaid
flowchart TD
    INPUT["Incoming query"] --> L1{"Length check\n3 < len <= 1000?"}
    L1 -- Fail --> B1["BLOCK: length violation"]
    L1 -- Pass --> L2{"Injection pattern\nmatch?"}
    L2 -- Match --> B2["BLOCK: prompt injection"]
    L2 -- No match --> L3{"Excessive\nrepetition?"}
    L3 -- Yes --> B3["BLOCK: spam"]
    L3 -- No --> SAFE["SAFE: proceed"]

    OUTPUT["Generated response"] --> O1{"PII patterns\npresent?"}
    O1 -- Found --> OB1["BLOCK: PII in output"]
    O1 -- Not found --> O2{"Hallucination\nmarkers?"}
    O2 -- Found --> OW["SOFT WARNING: log only\nSAFE: return to user"]
    O2 -- Not found --> OS["SAFE: return to user"]
```

---

## RAGAS Evaluation Pipeline

```mermaid
flowchart TD
    subgraph FAITHFULNESS["Faithfulness Score"]
        A["Generated answer"] --> D["Claude: decompose_answer()\nBreak into atomic claims"]
        D --> CL["claim_1, claim_2, ... claim_N"]
        CL --> C{"For each claim:\ncheck_claim_supported(claim, context)"}
        CTX["Retrieved context\n(SOURCE 1..5 text)"] --> C
        C --> SUPPORTED["List of True/False"]
        SUPPORTED --> FS["faithfulness = supported / total"]
    end

    subgraph RELEVANCY["Answer Relevancy Score"]
        ANS["Generated answer"] --> GQ["Claude: generate_hypothetical_questions()\n3 questions this answer addresses"]
        GQ --> HQ["q1, q2, q3"]
        ORIG["Original question"] --> EMB["Embed: [original, q1, q2, q3]"]
        HQ --> EMB
        EMB --> COS["cosine_similarity(original, q_i)\nfor each i"]
        COS --> RS["relevancy = mean similarity"]
    end
```

---

## Component Table

| Component | File | Key Function | Output |
|---|---|---|---|
| Input Guardrails | `guardrails.py` | `check_input(query)` | `GuardrailResult(is_safe, reason, category)` |
| Output Guardrails | `guardrails.py` | `check_output(response)` | `GuardrailResult` |
| Embedding | `production_rag.py` | `embed_query(query)` | `(vector, token_count)` |
| Semantic Cache | `cache.py` | `SemanticCache.lookup()` | `dict` or `None` |
| Cache Store | `cache.py` | `SemanticCache.store()` | None (side effect: SQLite write) |
| Retrieval | `production_rag.py` | `retrieve_chunks(embedding)` | List of chunk dicts |
| Context Assembly | `production_rag.py` | `assemble_context(chunks)` | Formatted context string |
| Generation | `production_rag.py` | `generate_answer(q, context)` | `(answer, input_tokens, output_tokens)` |
| Cost Calculation | `cost_tracker.py` | `calculate_cost(tokens...)` | USD float |
| Stats Logging | `cost_tracker.py` | `log_query(conn, ...)` | None (side effect: SQLite write) |
| Faithfulness | `evaluator.py` | `compute_faithfulness(answer, context)` | Float [0, 1] |
| Answer Relevancy | `evaluator.py` | `compute_answer_relevancy(q, answer)` | Float [0, 1] |
| Stats Display | `cost_tracker.py` | `format_stats(stats_dict)` | Formatted string |

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| Vector store | ChromaDB (from Project 2) | Document retrieval |
| Embeddings | OpenAI `text-embedding-3-small` | Query and cache vectors |
| Generation | Anthropic Claude | Answer synthesis |
| Cache storage | SQLite | Persistent query cache and stats log |
| Evaluation | RAGAS-style LLM judge (Claude) | Faithfulness and relevancy scoring |
| Runtime | Python 3.11+ | All components |

---

## Cost Model

```
Cache HIT:
  Cost = $0.00 (no API calls)
  Latency ~50ms

Cache MISS (full pipeline):
  embed_query:      ~50 tokens  x $0.02/1M  = $0.000001
  generate_answer:
    input:  ~2000 tokens x $15/1M   = $0.000030
    output:  ~300 tokens x $75/1M   = $0.0000225
  Total per query: ~$0.000054

At 100 queries/day:
  Without cache: $0.0054/day -> $1.62/month
  With 40% cache hit rate: $0.00324/day -> $0.97/month
  Cache saves: ~40% on API spend
```

---

## RAGAS Score Interpretation

| Faithfulness | Meaning | Action |
|---|---|---|
| > 0.85 | Excellent — answers are grounded | Ship it |
| 0.70–0.85 | Good — minor hallucination | Review low-scoring answers |
| 0.50–0.70 | Moderate | Improve chunking or retrieval |
| < 0.50 | Poor — significant hallucination | Fix retrieval before shipping |

| Answer Relevancy | Meaning | Action |
|---|---|---|
| > 0.80 | Excellent | Ship it |
| 0.65–0.80 | Good — mostly on-topic | Tune generation prompt |
| 0.50–0.65 | Moderate | Improve context assembly |
| < 0.50 | Poor — answers miss the point | Check retrieval quality |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Project context and motivation |
| 02_ARCHITECTURE.md | you are here |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable Python skeleton |
| [04_RECAP.md](./04_RECAP.md) | What you learned, extensions, job mapping |

⬅️ **Prev:** [09 — Build a RAG App](../09_Custom_LoRA_Fine_Tuning/01_MISSION.md)
