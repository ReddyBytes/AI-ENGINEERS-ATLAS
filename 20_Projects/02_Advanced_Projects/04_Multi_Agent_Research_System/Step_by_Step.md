# Project 4: Step-by-Step Build Guide

## Overview

Build the research system in five phases. You'll have a working single-agent version by Phase 2, then upgrade to true multi-agent by Phase 4.

---

## Phase 0 — Environment Setup

### Step 1: Install dependencies

```bash
pip install langgraph langchain-anthropic anthropic \
    duckduckgo-search wikipedia-api
```

### Step 2: Test web search and Wikipedia tools independently

Before building agents, verify your tools work:

```python
# Test DuckDuckGo
from duckduckgo_search import DDGS
with DDGS() as ddgs:
    results = list(ddgs.text("AI manufacturing employment", max_results=5))
print(results[0])

# Test Wikipedia
import wikipediaapi
wiki = wikipediaapi.Wikipedia("ResearchBot/1.0", "en")
page = wiki.page("Automation")
print(page.summary[:300])
```

Tools that fail here will fail in agents too — fix them now.

### Step 3: Plan your state schema on paper

Before writing code, sketch the state schema. Each worker needs to:
- Know its assigned task
- Write its output somewhere the supervisor can read it

Key design question: How do worker results get merged back into shared state?

**Theory checkpoint:** Read `15_LangGraph/06_Multi_Agent_with_LangGraph/Architecture_Deep_Dive.md` — specifically the "Send API" section.

---

## Phase 1 — Define State and Supervisor

### Step 4: Define the research state

```python
from typing import TypedDict, Annotated
import operator

class ResearchState(TypedDict):
    research_question: str
    sub_tasks: list[dict]        # List of {"task_id", "type", "query", "assigned_to"}
    web_results: Annotated[list, operator.add]    # Accumulated across workers
    wiki_results: Annotated[list, operator.add]   # Accumulated across workers
    draft_sections: Annotated[list, operator.add] # Accumulated across workers
    fact_check_results: list[dict]
    final_report: str
    worker_errors: Annotated[list, operator.add]  # Track failures
```

Note the `Annotated[list, operator.add]` pattern — this is LangGraph's way of merging parallel worker outputs by appending rather than overwriting.

### Step 5: Build the Supervisor planning node

The supervisor's first job is task decomposition. Call Claude with:

```
You are a research supervisor. Given the question: "{research_question}"
Decompose this into exactly 2 research tasks:
1. A web search task (specific search query)
2. A Wikipedia lookup task (specific topic to look up)

Return JSON:
[
  {"task_id": "task_1", "type": "web_search", "query": "..."},
  {"task_id": "task_2", "type": "wiki_lookup", "topic": "..."}
]
```

Keep it to 2 parallel tasks initially — add more after the system works.

### Step 6: Test the supervisor in isolation

Call the supervisor function directly (not through LangGraph yet):
```python
state = {"research_question": "What is the economic impact of AI on manufacturing?"}
result = supervisor_plan_node(state)
print(result["sub_tasks"])
```

Verify you get well-formed sub-tasks before wiring into a graph.

**Theory checkpoint:** Read `10_AI_Agents/05_Planning_and_Reasoning/Theory.md` — the task decomposition section.

---

## Phase 2 — Build Individual Worker Agents

### Step 7: Build the WebResearcher worker

```python
def web_researcher_node(state: ResearchState) -> dict:
    # 1. Get the web search task from sub_tasks
    # 2. Run DuckDuckGo search with max_results=8
    # 3. Summarize results using Claude (extract key facts, deduplicate)
    # 4. Return {"web_results": [{"source": url, "summary": text, "task_id": ...}]}
    # 5. On error: return {"worker_errors": [{"worker": "web_researcher", "error": str(e)}]}
```

Keep the Claude summarization prompt tight: "Extract the 3 most important facts from these search results. Return as bullet points."

### Step 8: Build the DataAnalyst worker

```python
def data_analyst_node(state: ResearchState) -> dict:
    # 1. Get the wiki_lookup task from sub_tasks
    # 2. Fetch Wikipedia page(s) using wikipedia-api
    # 3. Use Claude to extract statistics and key claims as structured data
    # 4. Return {"wiki_results": [{"page": title, "facts": [...], "stats": [...]}]}
    # 5. On error: return {"worker_errors": [...]}
```

Use the Wikipedia summary (not the full text) for token efficiency.

### Step 9: Test both workers in sequence (no parallelism yet)

```python
state = {
    "research_question": "AI impact on manufacturing",
    "sub_tasks": [
        {"task_id": "t1", "type": "web_search", "query": "AI manufacturing employment 2024"},
        {"task_id": "t2", "type": "wiki_lookup", "topic": "Industry 4.0"},
    ],
    "web_results": [], "wiki_results": [], "draft_sections": [],
    "fact_check_results": [], "final_report": "", "worker_errors": []
}
web_out = web_researcher_node(state)
state.update(web_out)
wiki_out = data_analyst_node(state)
state.update(wiki_out)
print(state["web_results"])
print(state["wiki_results"])
```

**Theory checkpoint:** Read `10_AI_Agents/07_Multi_Agent_Systems/Theory.md`.

---

## Phase 3 — Build Writer and FactChecker

### Step 10: Build the Writer agent

The Writer receives the accumulated research and drafts a structured report section:

```python
def writer_node(state: ResearchState) -> dict:
    # 1. Collect all web_results and wiki_results from state
    # 2. Build a research brief: "Here is the research collected:..."
    # 3. Call Claude with a writing prompt:
    #    "Using ONLY the provided research, write a 400-600 word analysis
    #     of [research_question]. Use clear paragraphs, include statistics
    #     where available, and cite sources by task_id."
    # 4. Return {"draft_sections": [{"task_id": "draft_1", "content": text}]}
```

### Step 11: Build the FactChecker agent

The FactChecker verifies claims in the draft against raw sources:

```python
def fact_checker_node(state: ResearchState) -> dict:
    # 1. Get the latest draft from state["draft_sections"]
    # 2. Build a fact-checking prompt that includes both the draft AND the raw research
    # 3. Ask Claude to identify each claim in the draft and rate it:
    #    - VERIFIED: claim directly supported by source
    #    - PARTIALLY_SUPPORTED: claim is roughly right but details differ
    #    - UNSUPPORTED: claim not found in sources
    # 4. Return {"fact_check_results": [{"claim": ..., "verdict": ..., "source_ref": ...}]}
```

### Step 12: Build the Supervisor synthesis node

After workers complete, the supervisor synthesizes:
```python
def supervisor_synthesize_node(state: ResearchState) -> dict:
    # 1. Check for worker_errors — log which workers failed
    # 2. Get the latest draft
    # 3. Get fact_check_results — identify which claims need revision
    # 4. Call Claude to produce a final, fact-corrected report
    # 5. Format with headers, citations, and a "Research Notes" section
    #    listing any claims that were flagged by the FactChecker
    # 6. Return {"final_report": markdown_text}
```

---

## Phase 4 — Wire the Graph with Parallel Execution

### Step 13: Understand the Send API

LangGraph's `Send` API lets the supervisor dynamically dispatch to worker nodes:

```python
from langgraph.constants import Send

def dispatch_workers(state: ResearchState):
    """
    This function is used as a conditional edge source.
    It returns a list of Send objects, one per worker task.
    LangGraph executes them in parallel.
    """
    sends = []
    for task in state["sub_tasks"]:
        if task["type"] == "web_search":
            sends.append(Send("web_researcher", {**state, "current_task": task}))
        elif task["type"] == "wiki_lookup":
            sends.append(Send("data_analyst", {**state, "current_task": task}))
    return sends
```

### Step 14: Assemble the full graph

```python
builder = StateGraph(ResearchState)
builder.add_node("supervisor_plan", supervisor_plan_node)
builder.add_node("web_researcher", web_researcher_node)
builder.add_node("data_analyst", data_analyst_node)
builder.add_node("writer", writer_node)
builder.add_node("fact_checker", fact_checker_node)
builder.add_node("supervisor_synthesize", supervisor_synthesize_node)

builder.set_entry_point("supervisor_plan")

# After planning, dispatch workers in parallel using Send
builder.add_conditional_edges("supervisor_plan", dispatch_workers)

# After both workers finish, merge their outputs and run writer
# (LangGraph waits for all parallel branches to complete)
builder.add_edge("web_researcher", "writer")
builder.add_edge("data_analyst", "writer")
builder.add_edge("writer", "fact_checker")
builder.add_edge("fact_checker", "supervisor_synthesize")
builder.add_edge("supervisor_synthesize", END)
```

**Theory checkpoint:** Read `15_LangGraph/06_Multi_Agent_with_LangGraph/Theory.md` — the parallel execution section.

### Step 15: Test end-to-end

```python
graph = builder.compile()
result = graph.invoke({
    "research_question": "What are the main economic impacts of AI on manufacturing employment?",
    "sub_tasks": [], "web_results": [], "wiki_results": [],
    "draft_sections": [], "fact_check_results": [], "final_report": "", "worker_errors": []
})
print(result["final_report"])
```

---

## Phase 5 — Fault Tolerance

### Step 16: Add try/except to all workers

Wrap each worker's core logic in try/except:
```python
try:
    # ... worker logic ...
except Exception as e:
    print(f"[{worker_name}] Error: {e}")
    return {"worker_errors": [{"worker": worker_name, "error": str(e), "task_id": task_id}]}
```

### Step 17: Make the supervisor resilient

In `supervisor_synthesize_node`, check `state["worker_errors"]`:
- If web_researcher failed: note in report that web research was unavailable
- If data_analyst failed: continue with only web results
- If writer failed: fall back to raw research summary (no synthesis)
- If fact_checker failed: include unverified draft with warning

### Step 18: Test failure modes

Temporarily break each worker (raise Exception at the start) and confirm the pipeline completes with graceful degradation instead of crashing.

---

## Testing Checklist

- [ ] DuckDuckGo search returns results for test queries
- [ ] Wikipedia lookup returns page summaries
- [ ] Supervisor decomposes question into valid sub-tasks
- [ ] Both workers run in parallel (check log timestamps)
- [ ] Writer produces a coherent 400+ word section
- [ ] FactChecker identifies at least one verified and one flagged claim
- [ ] Final report contains citations back to task IDs
- [ ] Killing web_researcher with an exception doesn't crash the pipeline
- [ ] Killing data_analyst with an exception doesn't crash the pipeline
- [ ] worker_errors list populated correctly on failures
