# 02 Architecture — Multi-Agent Research System

## Full System Flowchart

```mermaid
flowchart TD
    Q([Research Question]) --> SP[Supervisor\nPlan Node\nDecomposes question]

    SP -->|Send task_1| WR[WebResearcher\nDuckDuckGo search\n+ Claude summarize]
    SP -->|Send task_2| DA[DataAnalyst\nWikipedia fetch\n+ Claude extract]

    WR -->|web_results appended| WRT[Writer Agent\nClaude drafts 400-600 words]
    DA -->|wiki_results appended| WRT

    WRT -->|draft_sections| FC[FactChecker Agent\nVerifies claims vs sources]
    FC -->|fact_check_results| SS[Supervisor\nSynthesize Node\nFinal corrected report]

    SS --> OUT([Final Markdown Report\nresearch_output/report.md])

    ERR[(worker_errors\nlist)] -.- WR
    ERR -.- DA
    ERR --> SS

    PARALLEL{{"Parallel Execution\n(LangGraph Send API)"}} -.->|executes| WR
    PARALLEL -.->|executes| DA

    style Q fill:#4A90D9,color:#fff
    style OUT fill:#27AE60,color:#fff
    style SS fill:#16213e,color:#fff
    style SP fill:#16213e,color:#fff
    style PARALLEL fill:#E67E22,color:#fff
    style ERR fill:#E74C3C,color:#fff
```

---

## Component Table

| Agent / Node | Role | Tools | Input from State | Output to State |
|---|---|---|---|---|
| Supervisor (Plan) | Decompose question into sub-tasks | Claude claude-sonnet-4-6 | `research_question` | `sub_tasks` (list of task dicts) |
| WebResearcher | Search web, extract key facts | DuckDuckGo + Claude | `current_task.query` | `web_results` (appended) |
| DataAnalyst | Fetch Wikipedia, extract stats | Wikipedia API + Claude | `current_task.topic` | `wiki_results` (appended) |
| Writer | Draft coherent prose from research | Claude claude-sonnet-4-6 | `web_results`, `wiki_results` | `draft_sections` (appended) |
| FactChecker | Verify claims vs sources | Claude claude-sonnet-4-6 | `draft_sections`, `web_results`, `wiki_results` | `fact_check_results` |
| Supervisor (Synthesize) | Final corrected report | Claude claude-sonnet-4-6 | All state fields | `final_report` |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| `langgraph` | StateGraph, Send API, parallel execution |
| `anthropic` | Claude for all agent reasoning |
| `duckduckgo-search` | Web search without API key |
| `wikipedia-api` | Wikipedia content retrieval |
| `langchain-anthropic` | Claude integration for LangGraph |

---

## State Merge Semantics

```mermaid
flowchart LR
    WR["WebResearcher\nreturns:\n{web_results: [fact1, fact2]}"] --> MERGE
    DA["DataAnalyst\nreturns:\n{wiki_results: [stat1, stat2]}"] --> MERGE
    MERGE["LangGraph State Merge\noperator.add for list fields"] --> STATE
    STATE["Merged State:\n{web_results: [fact1, fact2],\n wiki_results: [stat1, stat2]}"]
    STATE --> WRT[Writer sees\nall accumulated results]
```

| Field | Merge Strategy | Reason |
|---|---|---|
| `web_results` | `operator.add` (append) | Multiple workers may contribute; all results needed |
| `wiki_results` | `operator.add` (append) | Same |
| `draft_sections` | `operator.add` (append) | Multiple drafts possible in extended pipelines |
| `worker_errors` | `operator.add` (append) | Collect all errors without overwriting |
| `sub_tasks` | Overwrite | Only supervisor writes this |
| `final_report` | Overwrite | Only synthesizer writes this |
| `fact_check_results` | Overwrite | Only fact checker writes this |

---

## Supervisor Pattern — Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant S as Supervisor
    participant WR as WebResearcher
    participant DA as DataAnalyst
    participant W as Writer
    participant FC as FactChecker

    U->>S: research_question
    S->>S: Decompose into sub-tasks
    par Parallel Execution
        S->>WR: Send(task_1: web_search)
        S->>DA: Send(task_2: wiki_lookup)
    end
    WR-->>W: web_results (merged into state)
    DA-->>W: wiki_results (merged into state)
    Note over W: LangGraph waits for both branches
    W->>W: Draft 400-600 word analysis
    W->>FC: draft_sections
    FC->>FC: Verify each claim vs sources
    FC-->>S: fact_check_results
    S->>S: Produce corrected final report
    S-->>U: final_report (Markdown)
```

---

## Fault Tolerance Architecture

```mermaid
flowchart TD
    TRY[Worker tries tool call] --> OK{Success?}
    OK -->|Yes| RESULT[Return data in results field]
    OK -->|No| ERR[Return worker_errors entry]
    ERR --> CONTINUE[Pipeline continues\nwith partial data]

    SS[Supervisor Synthesize] --> CHECK{worker_errors\nnon-empty?}
    CHECK -->|Yes| WARN[Add Research Notes section\nwith limitation warnings]
    CHECK -->|No| CLEAN[Full report\nno warnings]
    WARN --> REPORT[Final Report]
    CLEAN --> REPORT
```

| Worker Failure | System Behavior |
|---|---|
| WebResearcher fails | Report uses only Wikipedia data; notes web research unavailable |
| DataAnalyst fails | Report uses only web data; notes Wikipedia data unavailable |
| Writer fails | Supervisor uses raw research summary instead of polished draft |
| FactChecker fails | Report uses unverified draft; notes fact-checking was skipped |

---

## Send API Mechanics

```mermaid
flowchart LR
    EDGE["conditional_edges\ndispatch_workers()"] --> SEND1["Send('web_researcher',\n{...state, current_task: t1})"]
    EDGE --> SEND2["Send('data_analyst',\n{...state, current_task: t2})"]
    SEND1 -->|"node receives\nfull state copy"| WR[web_researcher node]
    SEND2 -->|"node receives\nfull state copy"| DA[data_analyst node]
    WR -->|"returns partial state\n{web_results: [...]}"| MERGE[LangGraph\nmerges both returns]
    DA -->|"returns partial state\n{wiki_results: [...]}"| MERGE
```

Key insight: each `Send` gives the worker a copy of the full state plus the specific task. Workers return partial state updates (only the fields they modify). LangGraph merges these using the field-level merge strategies defined with `Annotated[list, operator.add]`.

---

## File Structure

```
14_Multi_Agent_Research_System/
├── 01_MISSION.md
├── 02_ARCHITECTURE.md
├── 03_GUIDE.md
├── 04_RECAP.md
├── src/
│   └── starter.py          # Main system (research_system.py)
└── research_output/        # Generated reports (auto-created)
    └── report_YYYYMMDD_HHMMSS.md
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| **02_ARCHITECTURE.md** | you are here |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |
