# 04 Recap — Multi-Agent Research System

## What You Built

A multi-agent research pipeline that accepts a natural language research question and produces a cited, fact-checked Markdown report in under two minutes. The Supervisor agent decomposes the question into parallel tasks, dispatches a WebResearcher and DataAnalyst simultaneously using LangGraph's Send API, routes their findings to a Writer, then fact-checks the draft before synthesizing the final report. If any worker fails, the pipeline degrades gracefully and notes the limitation in the output.

---

## Concepts Applied

| Concept | How It Was Applied |
|---|---|
| Supervisor pattern | Built a Supervisor that plans, dispatches, and synthesizes — separating orchestration from execution. Each worker is specialized and knows only its role. |
| LangGraph Send API | Used `Send("node_name", state_copy)` to dispatch multiple workers in parallel from a single conditional edge. Each worker receives a full state copy plus its specific task. |
| State merge semantics | Defined `Annotated[list, operator.add]` on shared fields so parallel worker outputs append rather than overwrite. |
| Parallel execution | Both WebResearcher and DataAnalyst run simultaneously. LangGraph waits for all parallel branches before running the Writer. |
| Fault tolerance | Wrapped all workers in try/except. Failures return `{"worker_errors": [...]}` — the pipeline continues with partial data and reports limitations. |
| Specialization | Each agent does one thing: search, extract, write, or verify. No single agent tries to do all four — which would produce mediocre results on all four. |
| FactChecker as independent verification | The FactChecker re-reads raw sources, not the Writer's output alone. This catches hallucinated statistics before they reach the final report. |
| Task decomposition | The Supervisor converts a broad research question into specific, executable sub-tasks with typed schemas (web_search vs wiki_lookup). |

---

## Extension Ideas

**1. Streaming UI with live agent progress**
Build a Streamlit app that shows a live feed of agent messages as they are generated. Use LangGraph's streaming mode (`graph.stream()`) and display each agent's output as it arrives. This makes the system feel like watching a research team work in real time.

**2. Critic agent for gap analysis**
Add a fifth agent: Critic. After the Writer produces a draft, the Critic identifies questions that remain unanswered and gaps in the evidence. The Supervisor then dispatches a second round of targeted research to fill those gaps before synthesizing the final report.

**3. Citation Manager agent**
Add a CitationManager that receives all sources (URLs + Wikipedia pages) and formats them in APA style. Have the final report reference citations by number ([1], [2]) rather than task_id. The CitationManager also deduplicates sources and identifies when two workers found the same URL.

---

## Job Mapping

| Role | How This Project Demonstrates Fit |
|---|---|
| AI/ML Engineer | Built a non-trivial multi-agent system with parallel execution and fault tolerance. Understand LangGraph state machines at implementation depth. |
| AI Product Engineer | Designed agents with clear roles and boundaries. Understand why specialization outperforms "one agent does everything" at scale. |
| Research Engineer | Built automated research workflows — directly applicable to literature review, competitive intelligence, and document synthesis pipelines. |
| Senior Software Engineer | Implemented the supervisor-worker pattern in a novel domain. Understand how to design distributed systems where components fail gracefully. |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| **04_RECAP.md** | you are here |
