# Multi-Agent Architecture — Deep Dive

## Overview

This document provides a full architecture reference for multi-agent systems built with LangGraph, including detailed diagrams of the supervisor pattern and communication flows.

---

## Architecture 1: Simple Supervisor with 2 Specialists

The simplest multi-agent setup: one supervisor, two specialists, shared state.

```mermaid
flowchart TD
    START([START]) --> SUP[Supervisor\nAnalyze state, decide next step]

    SUP -->|next_agent = researcher| RES[Researcher\nSearch and gather information]
    SUP -->|next_agent = writer| WRI[Writer\nDraft content from research]
    SUP -->|next_agent = FINISH| END([END])

    RES -->|writes research_notes to state| SUP
    WRI -->|writes draft to state| SUP

    note1["Shared State:\n- task: str\n- next_agent: str\n- research_notes: str\n- draft: str\n- is_complete: bool"]
    SUP -.->|reads/writes| note1

    style START fill:#2d6a4f,color:#fff
    style END fill:#c1121f,color:#fff
    style SUP fill:#023e8a,color:#fff
    style RES fill:#0077b6,color:#fff
    style WRI fill:#0077b6,color:#fff
```

**Data flow:**
1. START → Supervisor (with empty state, only `task` set)
2. Supervisor → Researcher (no research yet)
3. Researcher → Supervisor (research_notes now populated)
4. Supervisor → Writer (research done, no draft yet)
5. Writer → Supervisor (draft now populated)
6. Supervisor → END (all tasks complete)

---

## Architecture 2: Supervisor with 3 Specialists + Review Loop

A more realistic pipeline where the supervisor can send work back to the writer if the reviewer is not satisfied.

```mermaid
flowchart TD
    START([START]) --> SUP[Supervisor\nOrchestrates the pipeline]

    SUP -->|task: research| RES[Researcher\nGather information]
    SUP -->|task: write| WRI[Writer\nCreate draft]
    SUP -->|task: review| REV[Reviewer\nCheck quality]
    SUP -->|all approved| END([END])

    RES --> SUP
    WRI --> SUP
    REV --> SUP

    SUP -->|review rejected:\nback to writer| WRI

    state1["State fields:\n- task: str\n- next_agent: str\n- research_notes: str\n- draft: str\n- review_feedback: str\n- revision_count: int\n- is_approved: bool"]
    state1 -.-> SUP

    style START fill:#2d6a4f,color:#fff
    style END fill:#c1121f,color:#fff
    style SUP fill:#023e8a,color:#fff
    style RES fill:#0077b6,color:#fff
    style WRI fill:#0077b6,color:#fff
    style REV fill:#6d6875,color:#fff
```

**Supervisor decision logic:**
```
if no research → research
if research but no draft → write
if draft but no review → review
if review rejected AND revisions < 3 → write again (with feedback)
if review approved OR revisions >= 3 → END
```

---

## Architecture 3: Subgraph Pattern (Each Agent is a Full Graph)

When specialists need their own internal complexity (their own loops, branching, tools).

```mermaid
flowchart TD
    subgraph Parent Graph
        START([START]) --> SUP[Supervisor Node]
        SUP -->|delegate| RES_NODE[Researcher Node]
        SUP -->|delegate| WRI_NODE[Writer Node]
        RES_NODE --> SUP
        WRI_NODE --> SUP
        SUP --> END([END])
    end

    subgraph Researcher Subgraph
        RS([START]) --> SEARCH[Search]
        SEARCH --> RERANK[Re-rank results]
        RERANK -->|not enough| SEARCH
        RERANK -->|sufficient| SYNTH[Synthesize]
        SYNTH --> RE([END])
    end

    subgraph Writer Subgraph
        WS([START]) --> DRAFT[Draft]
        DRAFT --> SELF_REVIEW[Self Review]
        SELF_REVIEW -->|needs improvement| DRAFT
        SELF_REVIEW -->|good enough| WE([END])
    end

    RES_NODE -.->|wraps| Researcher Subgraph
    WRI_NODE -.->|wraps| Writer Subgraph
```

**Code pattern for wrapping a subgraph:**

```python
# Each specialist is a compiled graph
researcher_app = build_researcher_graph().compile()
writer_app = build_writer_graph().compile()

# Wrap in a function that becomes a node
def researcher_node(state: TeamState) -> dict:
    sub_result = researcher_app.invoke({
        "query": state["task"],
        "max_results": 5
    })
    return {"research_notes": sub_result["synthesized_notes"]}

def writer_node(state: TeamState) -> dict:
    sub_result = writer_app.invoke({
        "task": state["task"],
        "notes": state["research_notes"]
    })
    return {"draft": sub_result["final_draft"]}
```

---

## Architecture 4: Parallel Fan-Out with Send API

When multiple agents can work simultaneously on independent subtasks.

```mermaid
flowchart TD
    START([START]) --> DISPATCH[Dispatch Node\nFan-out to all agents]

    DISPATCH -->|Send| RES[Researcher\nBackground info]
    DISPATCH -->|Send| ANA[Analyst\nData and numbers]
    DISPATCH -->|Send| COM[Competitor Watch\nMarket context]

    RES -->|results merged| MERGE[Merge Node\nCombine all results]
    ANA -->|results merged| MERGE
    COM -->|results merged| MERGE

    MERGE --> WRI[Writer\nCreate final report]
    WRI --> END([END])

    note1["All three agents run\nSIMULTANEOUSLY\nResults merged via reducers"]
    DISPATCH -.-> note1

    style START fill:#2d6a4f,color:#fff
    style END fill:#c1121f,color:#fff
    style DISPATCH fill:#023e8a,color:#fff
    style MERGE fill:#023e8a,color:#fff
    style RES fill:#0077b6,color:#fff
    style ANA fill:#0077b6,color:#fff
    style COM fill:#0077b6,color:#fff
    style WRI fill:#2d6a4f,color:#fff
```

---

## Architecture 5: Full Production Multi-Agent System

A complete production-grade system combining supervisor, subgraphs, HITL, and checkpointing.

```mermaid
flowchart TD
    USER([User Request]) --> START([START])
    START --> SUP[Supervisor LLM\nPlan and orchestrate]

    SUP --> PLAN[Planner Node\nBreak task into subtasks]
    PLAN --> SUP

    SUP -->|delegate research| RES[Researcher Subgraph]
    SUP -->|delegate analysis| ANA[Analyst Subgraph]
    RES --> SUP
    ANA --> SUP

    SUP -->|draft ready| HITL{Human Review\ninterrupt_before}
    HITL -->|approved| PUB[Publisher Node\nFormat and deliver]
    HITL -->|needs changes| WRI[Writer Subgraph\nRevise with feedback]
    WRI --> SUP

    PUB --> END([END])

    CP[(Checkpointer\nAll state saved\nafter every node)] -.-> START
    CP -.-> SUP
    CP -.-> HITL

    style USER fill:#4a4e69,color:#fff
    style START fill:#2d6a4f,color:#fff
    style END fill:#c1121f,color:#fff
    style SUP fill:#023e8a,color:#fff
    style HITL fill:#e76f51,color:#fff
    style CP fill:#6d6875,color:#fff
```

---

## State Flow in a Multi-Agent System

```mermaid
sequenceDiagram
    participant S as State
    participant SUP as Supervisor
    participant RES as Researcher
    participant WRI as Writer
    participant REV as Reviewer

    Note over S: Initial: {task: "Write about LangGraph", next_agent: "", ...}

    SUP->>S: Read state
    SUP->>S: Write {next_agent: "researcher"}
    S->>RES: Passes full state

    RES->>S: Write {research_notes: "LangGraph is..."}
    S->>SUP: Passes updated state

    SUP->>S: Read state (sees research_notes filled)
    SUP->>S: Write {next_agent: "writer"}
    S->>WRI: Passes full state (including research_notes)

    WRI->>S: Write {draft: "LangGraph is a framework for..."}
    S->>SUP: Passes updated state

    SUP->>S: Read state (sees draft filled)
    SUP->>S: Write {next_agent: "reviewer"}
    S->>REV: Passes full state

    REV->>S: Write {review_feedback: "Looks good", is_approved: True}
    S->>SUP: Passes updated state

    SUP->>S: Read is_approved=True
    SUP->>S: Write {next_agent: "FINISH"}
    Note over S: Final state has all fields populated
```

---

## State Design for Multi-Agent Systems

The state TypedDict must include fields for every agent's inputs and outputs:

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class FullTeamState(TypedDict):
    # --- Input ---
    task: str                    # The original user request

    # --- Orchestration ---
    next_agent: str              # Supervisor's routing decision
    task_plan: list              # Planner's task breakdown
    iteration_count: int         # Safety: max supervisor loops

    # --- Researcher outputs ---
    research_notes: str          # Raw research from researcher
    sources: list                # URLs / citations

    # --- Writer outputs ---
    draft: str                   # Current draft content
    revision_count: int          # How many times writer has revised

    # --- Reviewer outputs ---
    review_feedback: str         # Reviewer's comments
    is_approved: bool            # Final approval flag

    # --- Conversation history ---
    messages: Annotated[list[BaseMessage], add_messages]

    # --- Final output ---
    final_output: str            # Published/delivered content
```

---

## 📂 Navigation

**In this folder:**

| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Architecture_Deep_Dive.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code example |

⬅️ **Prev:** [Human-in-the-Loop](../05_Human_in_the_Loop/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Streaming and Checkpointing](../07_Streaming_and_Checkpointing/Theory.md)
