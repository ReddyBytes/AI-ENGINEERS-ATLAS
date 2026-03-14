# Research Agent — Architecture Blueprint

## High-Level Graph Architecture

```mermaid
flowchart TD
    START([START]) --> GQ[generate_queries]
    GQ --> SEARCH[search]
    SEARCH --> SYNTH[synthesize]
    SYNTH --> REF[reflect]
    REF -->|quality_score >= 0.8\nOR attempts >= max| FMT[format_output]
    REF -->|quality_score < 0.8\nAND attempts < max| GQ
    FMT --> END([END])

    style START fill:#2d6a4f,color:#fff
    style END fill:#c1121f,color:#fff
    style GQ fill:#023e8a,color:#fff
    style SEARCH fill:#0077b6,color:#fff
    style SYNTH fill:#0077b6,color:#fff
    style REF fill:#6d6875,color:#fff
    style FMT fill:#2d6a4f,color:#fff
```

---

## State Flow Across Iterations

```mermaid
sequenceDiagram
    participant S as State
    participant GQ as generate_queries
    participant SR as search
    participant SY as synthesize
    participant RF as reflect
    participant FO as format_output

    Note over S: Initial: {question: "...", attempts: 0, quality_score: 0.0, ...}

    GQ->>S: search_queries = ["q1", "q2"]
    SR->>S: raw_results += [result1, result2]\nsources += [src1, src2]
    SY->>S: current_answer = "Draft v1..."
    RF->>S: quality_score = 0.55\nquality_feedback = "Lacks examples"\nattempts = 1

    Note over S: Router: 0.55 < 0.8 AND 1 < 3 → loop back

    GQ->>S: search_queries = ["q3 (gap fill)"]
    SR->>S: raw_results += [result3]\nsources += [src3]
    SY->>S: current_answer = "Improved v2..."
    RF->>S: quality_score = 0.88\nattempts = 2

    Note over S: Router: 0.88 >= 0.8 → format_output

    FO->>S: final_answer = "Polished final..."

    Note over S: Final state has ALL accumulated results
```

---

## Node Detail: What Each Node Reads and Writes

```mermaid
graph LR
    subgraph State Fields
        Q[question]
        SQ[search_queries]
        RR[raw_results\nAnnotated-append]
        SRC[sources\nAnnotated-append]
        CA[current_answer]
        QS[quality_score]
        QF[quality_feedback]
        SH[score_history\nAnnotated-append]
        ATT[attempts]
        MAX[max_attempts]
        FA[final_answer]
    end

    subgraph generate_queries
        GQ_R[Reads: question, quality_feedback]
        GQ_W[Writes: search_queries]
    end

    subgraph search
        SR_R[Reads: search_queries]
        SR_W[Writes: raw_results, sources]
    end

    subgraph synthesize
        SY_R[Reads: raw_results, question, current_answer]
        SY_W[Writes: current_answer]
    end

    subgraph reflect
        RF_R[Reads: current_answer, question, attempts]
        RF_W[Writes: quality_score, quality_feedback, score_history, attempts]
    end

    subgraph format_output
        FO_R[Reads: current_answer, sources, score_history, attempts]
        FO_W[Writes: final_answer]
    end
```

---

## Loop Termination Logic

```mermaid
flowchart TD
    R{reflect\nrouter} --> A{attempts >= max_attempts?}
    A -->|Yes| FMT[format_output\nForced exit]
    A -->|No| B{quality_score >= 0.8?}
    B -->|Yes| FMT2[format_output\nSuccess exit]
    B -->|No| GQ[generate_queries\nLoop back for more research]

    style FMT fill:#2d6a4f,color:#fff
    style FMT2 fill:#2d6a4f,color:#fff
    style GQ fill:#023e8a,color:#fff
```

The two conditions serve different purposes:
- **Quality threshold** (`>= 0.8`): natural success exit — the answer is good enough
- **Max attempts** (`>= max_attempts`): safety exit — give up gracefully, return best answer found

---

## Data Accumulation Across Loop Iterations

The `raw_results` and `sources` fields use `Annotated[list, operator.add]` reducers. This means:

```
Iteration 1: raw_results = ["Result from q1", "Result from q2"]
             sources    = ["source.com/1", "source.com/2"]

Iteration 2: raw_results = ["Result from q1", "Result from q2",   ← iteration 1
                             "Result from q3"]                    ← iteration 2
             sources    = ["source.com/1", "source.com/2",        ← iteration 1
                           "source.com/3"]                        ← iteration 2
```

By iteration 3, the `synthesize` node has *all* results from *all* iterations to work with. This is why the answer quality improves: more information is available each time.

---

## Streaming Output Plan

When run with `.stream()`, you see:

```
[Node: generate_queries] → Generated queries: ["q1", "q2"]
[Node: search]           → Found 4 results
[Node: synthesize]       → Answer draft v1 (320 chars)
[Node: reflect]          → Score: 0.55 | Feedback: "Lacks examples"
[Node: generate_queries] → Generated queries: ["q3 (examples)"]  ← loop iteration 2
[Node: search]           → Found 2 results
[Node: synthesize]       → Answer draft v2 (480 chars)
[Node: reflect]          → Score: 0.88 | Success!
[Node: format_output]    → Final answer ready (520 chars)
```

---

## Checkpointing Plan

With `MemorySaver` or `SqliteSaver` attached:
- Every node execution is saved
- 3 loop iterations × 4 nodes per iteration = 12 checkpoints minimum (plus format_output)
- If the process crashes mid-research, you can resume from the last checkpoint
- Use `app.get_state_history(config)` to see all checkpoints

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Project_Guide.md](./Project_Guide.md) | Project overview and spec |
| 📄 **Architecture_Blueprint.md** | ← you are here |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Implementation guide |
| [📄 Troubleshooting.md](./Troubleshooting.md) | Debug help |

⬅️ **Prev:** [Streaming and Checkpointing](../07_Streaming_and_Checkpointing/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [LangGraph vs LangChain](../LangGraph_vs_LangChain.md)
