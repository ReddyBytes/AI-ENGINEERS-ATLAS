# 01 Mission — Multi-Agent Research System

## The Story

In late 2024, a policy research organization needed to produce a report on the economic impact of AI automation across five industry sectors. A solo analyst would need two weeks: searching academic literature, pulling labor statistics, synthesizing contradictions, and writing a coherent narrative.

A well-designed AI system could do a first draft in 20 minutes — not by having one model try to do everything at once, but by decomposing the problem and running specialists in parallel.

The insight is simple but powerful: the reason we have research teams instead of lone researchers is the same reason we need multi-agent systems instead of single-agent systems. Parallelism, specialization, and error checking through independent verification. One model trying to web-search, analyze data, write prose, and fact-check simultaneously will be mediocre at all four. Four specialized agents doing one thing each — and a supervisor ensuring they work toward a common goal — produces dramatically better output.

This project builds that system.

---

## What You Build

A multi-agent research pipeline using LangGraph's supervisor pattern:

1. **Supervisor Agent** — Decomposes the research question into sub-tasks, dispatches workers, collects results, and synthesizes a final report
2. **WebResearcher** — Searches the web using DuckDuckGo, returns summaries of relevant results
3. **DataAnalyst** — Fetches Wikipedia content and extracts structured facts, statistics, and key claims
4. **Writer** — Takes research findings and drafts coherent prose sections
5. **FactChecker** — Cross-references claims from the Writer against the raw research, flags contradictions

**Fault Tolerance:** If any worker fails (network error, API timeout, empty results), the Supervisor retries once then marks that sub-task as failed and continues with available data.

**Deliverable:** A runnable Python script that accepts a research question and produces a structured Markdown research report with citations.

---

## Concepts You Apply

| Topic | What You Apply |
|---|---|
| Multi-Agent with LangGraph | Supervisor pattern, parallel subgraphs |
| Planning and Reasoning | Task decomposition, research planning |
| Multi-Agent Systems | Orchestrator-worker, independent verification |
| LangGraph state management | Annotated list fields, operator.add merge semantics |

**Theory files to read first:**
- `15_LangGraph/06_Multi_Agent_with_LangGraph/Theory.md`
- `15_LangGraph/06_Multi_Agent_with_LangGraph/Architecture_Deep_Dive.md`
- `10_AI_Agents/07_Multi_Agent_Systems/Theory.md`
- `10_AI_Agents/05_Planning_and_Reasoning/Theory.md`

---

## Prerequisites

- Completed Project 2 (LangGraph Support Bot) — you need solid LangGraph foundations
- Python: basic async, list comprehensions, error handling
- Network access for DuckDuckGo and Wikipedia API calls

---

## Difficulty and Format

**Difficulty: 5 / 5 — Hard**

The supervisor pattern involves complex state management — workers return partial results that the supervisor must merge. LangGraph's `Send` API has a specific mental model that takes time to internalize. Debugging parallel node execution requires understanding graph traversal order.

**Learning format tier: Advanced**

The starter code gives you the full graph skeleton, state schema, and tool wrappers. You implement the logic inside each agent node by following the `# TODO:` markers. The graph wiring is pre-built; your job is to make each node do real work.

---

## Success Looks Like

```
Research Question: "What are the economic impacts of large-scale AI adoption on employment in manufacturing?"

[Supervisor] Decomposing question into 4 sub-tasks...
[WebResearcher] Searching: "AI manufacturing employment impact 2024"...
[DataAnalyst]   Fetching Wikipedia: "Automation and jobs", "Industry 4.0"...
  (running in parallel)

[WebResearcher] Found 8 relevant results, summarized to 3 key findings
[DataAnalyst]   Extracted 12 statistics from Wikipedia articles

[Writer]      Drafting report section (847 words)...
[FactChecker] Checking 6 claims against source data...
  Claim 3: Partially supported -- original source cited 23%, draft said 30%

[Supervisor] Synthesizing final report...
Report saved: research_output/report_20260314.md
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| **01_MISSION.md** | you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and component table |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |

⬅️ **Prev:** [13_Automated_Eval_Pipeline](../13_Automated_Eval_Pipeline/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [15_Fine_Tune_Evaluate_Deploy](../15_Fine_Tune_Evaluate_Deploy/01_MISSION.md)
