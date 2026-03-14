# 🕸️ LangGraph

<div align="center">

⬅️ [14 Hugging Face Ecosystem](../14_Hugging_Face_Ecosystem/Readme.md) &nbsp;|&nbsp; [🏠 Home](../00_Learning_Guide/Readme.md) &nbsp;|&nbsp; [16 Diffusion Models ➡️](../16_Diffusion_Models/Readme.md)

</div>

> LangChain's graph-based framework for building stateful, multi-step AI agents — where nodes are actions, edges are decisions, and cycles are the engine of autonomous reasoning.

**[▶ Start here → LangGraph Fundamentals Theory](./01_LangGraph_Fundamentals/Theory.md)**

---

## At a Glance

| | |
|---|---|
| 📚 Topics | 8 topics |
| ⏱️ Est. Time | 8–10 hours |
| 📋 Prerequisites | [Hugging Face Ecosystem](../14_Hugging_Face_Ecosystem/Readme.md) |
| 🔓 Unlocks | [Diffusion Models](../16_Diffusion_Models/Readme.md) |

---

## What's in This Section

```mermaid
flowchart TD
    START(["▶ START"])
    NODE_A["🔵 Node A\nAgent / LLM Call"]
    NODE_B["🟢 Node B\nTool Execution"]
    NODE_C["🟡 Node C\nHuman Review"]
    END_NODE(["⏹ END"])
    STATE[["📦 Shared State\n(TypedDict)"]  ]

    START --> NODE_A
    NODE_A -->|"tool_call"| NODE_B
    NODE_A -->|"needs_review"| NODE_C
    NODE_B -->|"result → state"| STATE
    NODE_C -->|"approved"| NODE_A
    NODE_C -->|"rejected"| END_NODE
    STATE -.->|"read state"| NODE_A
    NODE_B -->|"done"| END_NODE

    style START fill:#2ECC71,color:#fff,stroke:#27AE60
    style END_NODE fill:#E74C3C,color:#fff,stroke:#C0392B
    style NODE_A fill:#3498DB,color:#fff,stroke:#2980B9
    style NODE_B fill:#27AE60,color:#fff,stroke:#1E8449
    style NODE_C fill:#F39C12,color:#fff,stroke:#D68910
    style STATE fill:#9B59B6,color:#fff,stroke:#8E44AD
```

**The state machine in action:** every node reads from shared state, writes updates back, and the graph router decides which node fires next — including cycling back for multi-step reasoning loops.

---

## Topics

| # | Topic | What You'll Learn | Files |
|---|---|---|---|
| 01 | [LangGraph Fundamentals](./01_LangGraph_Fundamentals/) | Why graph-based agent orchestration beats linear chains; the core mental model of nodes, edges, and state | [📖 Theory](./01_LangGraph_Fundamentals/Theory.md) · [⚡ Cheatsheet](./01_LangGraph_Fundamentals/Cheatsheet.md) · [🎯 Interview Q&A](./01_LangGraph_Fundamentals/Interview_QA.md) |
| 02 | [Nodes and Edges](./02_Nodes_and_Edges/) | How to define nodes as Python functions, connect them with normal and conditional edges, and build your first graph | [📖 Theory](./02_Nodes_and_Edges/Theory.md) · [⚡ Cheatsheet](./02_Nodes_and_Edges/Cheatsheet.md) · [🎯 Interview Q&A](./02_Nodes_and_Edges/Interview_QA.md) |
| 03 | [State Management](./03_State_Management/) | Designing `TypedDict` state schemas, how reducers merge partial updates, and strategies for keeping state clean across long runs | [📖 Theory](./03_State_Management/Theory.md) · [⚡ Cheatsheet](./03_State_Management/Cheatsheet.md) · [🎯 Interview Q&A](./03_State_Management/Interview_QA.md) |
| 04 | [Cycles and Loops](./04_Cycles_and_Loops/) | Building graphs with back-edges for iterative refinement, retry logic, and ReAct-style reasoning loops without infinite loops | [📖 Theory](./04_Cycles_and_Loops/Theory.md) · [⚡ Cheatsheet](./04_Cycles_and_Loops/Cheatsheet.md) · [🎯 Interview Q&A](./04_Cycles_and_Loops/Interview_QA.md) |
| 05 | [Human in the Loop](./05_Human_in_the_Loop/) | Using `interrupt_before` and `interrupt_after` to pause execution, collect human input, and resume — essential for high-stakes agent workflows | [📖 Theory](./05_Human_in_the_Loop/Theory.md) · [⚡ Cheatsheet](./05_Human_in_the_Loop/Cheatsheet.md) · [🎯 Interview Q&A](./05_Human_in_the_Loop/Interview_QA.md) |
| 06 | [Multi-Agent with LangGraph](./06_Multi_Agent_with_LangGraph/) | Orchestrating supervisor–subagent patterns: how a controller graph routes tasks to specialized agent subgraphs | [📖 Theory](./06_Multi_Agent_with_LangGraph/Theory.md) · [⚡ Cheatsheet](./06_Multi_Agent_with_LangGraph/Cheatsheet.md) · [🎯 Interview Q&A](./06_Multi_Agent_with_LangGraph/Interview_QA.md) |
| 07 | [Streaming and Checkpointing](./07_Streaming_and_Checkpointing/) | Streaming token-by-token output from graph nodes, persisting checkpoints with `MemorySaver` and `SqliteSaver`, and resuming interrupted runs | [📖 Theory](./07_Streaming_and_Checkpointing/Theory.md) · [⚡ Cheatsheet](./07_Streaming_and_Checkpointing/Cheatsheet.md) · [🎯 Interview Q&A](./07_Streaming_and_Checkpointing/Interview_QA.md) |
| 08 | [Build with LangGraph](./08_Build_with_LangGraph/) | A full hands-on project: building a research agent with tool use, memory, human approval steps, and streaming output | [📖 Theory](./08_Build_with_LangGraph/Theory.md) · [⚡ Cheatsheet](./08_Build_with_LangGraph/Cheatsheet.md) · [🎯 Interview Q&A](./08_Build_with_LangGraph/Interview_QA.md) |

---

## Key Concepts at a Glance

| Concept | What It Means |
|---|---|
| **A graph is a state machine** | Execution is not a linear chain of calls; it is a directed graph where each node reads the current state, performs work, writes updates, and the graph decides what runs next. |
| **Conditional edges are the decision points** | A function inspects the current state and returns the name of the next node to route to, enabling branching, retrying, or ending the run. |
| **State is the shared memory** | Every node communicates exclusively through a typed state dict; there are no direct node-to-node calls, which makes the flow composable and debuggable. |
| **Cycles enable true agency** | Unlike DAG-based chains, LangGraph allows cycles, which means an agent can observe a result, decide it's insufficient, and loop back to try again. |
| **Checkpointing makes agents resumable** | Persistence backends (SQLite, Redis, Postgres) save state after every step, enabling long-running workflows, human-in-the-loop pauses, and crash recovery. |

---

## Companion File

Wondering how LangGraph differs from plain LangChain? Read the [LangGraph vs LangChain](./LangGraph_vs_LangChain.md) comparison for a side-by-side breakdown of when to use which.

---

## 📂 Navigation

⬅️ **Prev:** [14 Hugging Face Ecosystem](../14_Hugging_Face_Ecosystem/Readme.md) &nbsp;&nbsp; ➡️ **Next:** [16 Diffusion Models](../16_Diffusion_Models/Readme.md)
