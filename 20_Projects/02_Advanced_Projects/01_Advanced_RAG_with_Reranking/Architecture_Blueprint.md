# Project 1: Architecture Blueprint

## System Flowchart

```mermaid
flowchart TD
    A([User Question]) --> B[HyDE Generator]
    B -->|Hypothetical Answer| C[Sentence-Transformers Encoder]
    A -->|Original Question| D[BM25 Index]
    C -->|Dense Query Vector| E[ChromaDB Vector Search]
    D -->|Keyword Scores + Ranking| F[BM25 Top-10]
    E -->|Semantic Top-10| G[RRF Fusion]
    F --> G
    G -->|~20 Unique Candidates| H[Cross-Encoder Reranker]
    H -->|Top-5 Chunks + Scores| I[Answer Generator]
    A -->|Original Question| I
    I -->|Grounded Answer + Citations| J([Final Answer])
    J --> K[RAGAS Evaluator]
    K --> L[Faithfulness Score]
    K --> M[Answer Relevance Score]
    K --> N[Context Recall Score]

    style A fill:#4A90D9,color:#fff
    style J fill:#27AE60,color:#fff
    style H fill:#E74C3C,color:#fff
    style K fill:#8E44AD,color:#fff
```

---

## Component Table

| Component | Class / Function | Input | Output | Notes |
|---|---|---|---|---|
| HyDE Generator | `HyDEGenerator.generate()` | Raw question string | Hypothetical answer text (~150 words) | Calls Claude claude-sonnet-4-6; output used as query for vector search only |
| Sentence-Transformer Encoder | Built into ChromaDB's `SentenceTransformerEmbeddingFunction` | Text string | 384-dim float vector | Model: `all-MiniLM-L6-v2`; runs locally |
| ChromaDB Vector Search | `DocumentStore.vector_search()` | HyDE answer text | Top-10 `RetrievedChunk` objects with cosine score | Persistent on disk; L2 distance converted to similarity |
| BM25 Index | `DocumentStore.bm25_search()` | Original question | Top-10 `RetrievedChunk` objects with BM25 score | `BM25Okapi` from `rank_bm25`; tokenized at index time |
| RRF Fusion | `HybridRetriever._reciprocal_rank_fusion()` | Two ranked lists of chunks | ~20 deduplicated chunks sorted by RRF score | Formula: `1/(k + rank)` summed across lists; k=60 |
| Cross-Encoder Reranker | `Reranker.rerank()` | Question + 20 candidates | Top-5 `RetrievedChunk` objects with logit scores | Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`; runs locally |
| Answer Generator | `AnswerGenerator.generate()` | Question + Top-5 chunks | Answer text + list of cited source IDs | Grounded prompt; Claude refuses to answer beyond context |
| RAGAS Evaluator | `run_ragas_evaluation()` | Pipeline + golden dataset | Dict of metric scores | Uses LLM internally; requires golden ground-truth answers |

---

## Data Flow Detail

```mermaid
sequenceDiagram
    participant U as User
    participant P as Pipeline
    participant H as HyDE
    participant R as Retriever
    participant X as CrossEncoder
    participant G as Generator
    participant E as RAGAS

    U->>P: question = "What is RAG?"
    P->>H: generate(question)
    H-->>P: hypothetical = "RAG is a technique that..."
    P->>R: retrieve(question, hyde_query=hypothetical)
    R-->>P: 20 merged candidates
    P->>X: rerank(question, candidates, top_n=5)
    X-->>P: 5 reranked chunks
    P->>G: generate(question, 5 chunks)
    G-->>P: answer + cited_ids
    P-->>U: RAGResult object
    P->>E: evaluate(golden_dataset)
    E-->>P: {faithfulness: 0.91, ...}
```

---

## Retrieval Strategy Comparison

| Strategy | Strengths | Weaknesses | When It Dominates |
|---|---|---|---|
| BM25 only | Fast, exact-match, no GPU | Misses paraphrases, no semantic understanding | Keyword queries: "BM25 algorithm definition" |
| Vector only | Handles paraphrases, conceptual queries | Misses exact terms, sensitive to embedding model | Conceptual: "why do models make things up" |
| HyDE + Vector | Fills vocabulary gap between question and doc | HyDE adds LLM call cost; can hallucinate in hypothesis | Short questions without technical terms |
| Hybrid (BM25 + Vector) | Best of both worlds, robust | More complex, two indexes to maintain | Production default |
| + Cross-Encoder Rerank | Highest precision on final top-5 | Slower (full inference per candidate pair) | Whenever answer quality matters more than latency |

---

## RAGAS Metrics Explained

```mermaid
flowchart LR
    A[Generated Answer] --> B{Faithfulness}
    C[Retrieved Contexts] --> B
    B --> B1[Does answer contain ONLY claims supported by context?]

    A --> D{Answer Relevance}
    E[Question] --> D
    D --> D1[Does the answer address the question?]

    C --> F{Context Recall}
    G[Ground Truth Answer] --> F
    F --> F1[Do retrieved chunks cover the ground truth?]
```

| Metric | What It Catches | Target |
|---|---|---|
| Faithfulness | Hallucination — answer introduces facts not in context | > 0.85 |
| Answer Relevance | Vague or off-topic answers | > 0.80 |
| Context Recall | Retrieval failure — relevant chunks not in top-5 | > 0.80 |

---

## File Structure

```
01_Advanced_RAG_with_Reranking/
├── advanced_rag.py          # Main pipeline (from Starter_Code.md)
├── evaluate.py              # Standalone RAGAS runner
├── golden_dataset.py        # 20 Q&A pairs with ground-truth contexts
├── corpus/
│   └── sample_docs.txt      # Your document corpus (30+ paragraphs)
├── chroma_db/               # ChromaDB persistent storage (auto-created)
└── requirements.txt         # Pin your dependencies
```
