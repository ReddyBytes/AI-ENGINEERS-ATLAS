# Project 4: Multi-Agent Research System

## Why This Project Matters

In late 2024, a policy research organization needed to produce a report on the economic impact of AI automation across five industry sectors. A solo analyst would need two weeks: searching academic literature, pulling labor statistics, interviewing domain experts, synthesizing contradictions, and writing a coherent narrative.

A well-designed AI system could do a first draft in 20 minutes — not by having one model try to do everything at once, but by decomposing the problem and running specialists in parallel.

The insight is simple but powerful: the reason we have research teams instead of lone researchers is the same reason we need multi-agent systems instead of single-agent systems. Parallelism, specialization, and error checking through independent verification. One model trying to web-search, analyze data, write prose, and fact-check simultaneously will be mediocre at all four. Four specialized agents doing one thing each — and a supervisor ensuring they work toward a common goal — produces dramatically better output.

This project builds that system.

---

## What You'll Build

A multi-agent research pipeline using LangGraph's supervisor pattern:

1. **Supervisor Agent** — Decomposes the research question into sub-tasks, dispatches to workers, collects results, and synthesizes a structured report
2. **WebResearcher** — Searches the web using DuckDuckGo, returns summaries of relevant results
3. **DataAnalyst** — Fetches Wikipedia content and extracts structured facts, statistics, and key claims
4. **Writer** — Takes research findings and drafts coherent prose sections
5. **FactChecker** — Cross-references claims from the Writer against the raw research, flags contradictions

**Fault Tolerance:** If any worker fails (network error, API timeout, empty results), the Supervisor retries once then marks that sub-task as failed and continues with available data.

**Deliverable:** A runnable Python script that accepts a research question and produces a structured HTML/markdown research report with citations.

---

## Learning Objectives

By completing this project, you will:

- Implement the supervisor-worker pattern in LangGraph
- Use LangGraph's `Send` API to dispatch to workers dynamically
- Run workers in parallel using LangGraph's native parallel execution
- Build a fault-tolerant system that handles worker failures gracefully
- Understand the difference between sequential chaining and true multi-agent systems
- Design prompts for specialized agents that know their role and stay in scope

---

## Topics Covered

| Advanced Path Topic | What You Apply Here |
|---|---|
| Topic 15 — Multi-Agent with LangGraph | Supervisor pattern, parallel subgraphs |
| Topic 16 — Planning & Reasoning | Task decomposition, research planning |
| Topic 17 — Multi-Agent Systems | Orchestrator-worker, independent verification |
| Topic 18 — LangGraph vs LangChain | When parallel state matters |

---

## Prerequisites

- Completed Project 2 (LangGraph Support Bot) — you need solid LangGraph foundations
- Python: async basics, list comprehensions
- Comfortable with API calls that might fail (requests, error handling)
- Network access for DuckDuckGo and Wikipedia API calls

---

## Difficulty

**5 / 5 — Hard**

The supervisor pattern involves complex state management — workers return partial results that the supervisor must merge. LangGraph's `Send` API has a specific mental model that takes time to internalize. Debugging parallel node execution requires understanding graph traversal order.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `langgraph` | StateGraph, Send API, parallel execution |
| `anthropic` | Claude for all agent reasoning |
| `duckduckgo-search` | Web search without API key |
| `wikipedia-api` | Wikipedia content retrieval |
| `langchain-anthropic` | Claude integration |

---

## Expected Output

```
Research Question: "What are the economic impacts of large-scale AI adoption on employment in manufacturing?"

[Supervisor] Decomposing question into 4 sub-tasks...
  Task 1: Search for recent studies on AI impact on manufacturing employment
  Task 2: Find statistics on manufacturing job displacement rates
  Task 3: Draft economic impact summary
  Task 4: Fact-check claims against source data

[WebResearcher] Searching: "AI manufacturing employment impact 2024"...
[DataAnalyst]   Fetching Wikipedia: "Automation and jobs", "Industry 4.0"...
  (running in parallel)

[WebResearcher] Found 8 relevant results, summarized to 3 key findings
[DataAnalyst]   Extracted 12 statistics from Wikipedia articles

[Writer]    Drafting report section (847 words)...
[FactChecker] Checking 6 claims against source data...
  ✓ Claim 1: Verified
  ⚠ Claim 3: Partially supported — original source cited 23%, draft said 30%
  ✓ Claims 2,4,5,6: Verified

[Supervisor] Synthesizing final report...

Report saved: research_output/report_20260314.md
```

---

## Extension Challenges

1. Add a `CitationManager` worker that formats all sources in APA style
2. Implement a `Critic` agent that identifies gaps in the research
3. Add a second round: Supervisor reads Critic's feedback and dispatches additional research
4. Build a streaming UI with Streamlit that shows live worker progress
5. Add rate limiting so workers don't hammer APIs simultaneously
6. Implement worker timeout: if a worker takes > 30 seconds, skip it

---

## Theory Files to Read First

Before coding, read:
- `15_LangGraph/06_Multi_Agent_with_LangGraph/Theory.md`
- `15_LangGraph/06_Multi_Agent_with_LangGraph/Architecture_Deep_Dive.md`
- `10_AI_Agents/07_Multi_Agent_Systems/Theory.md`
- `10_AI_Agents/07_Multi_Agent_Systems/Architecture_Deep_Dive.md`
- `10_AI_Agents/05_Planning_and_Reasoning/Theory.md`
