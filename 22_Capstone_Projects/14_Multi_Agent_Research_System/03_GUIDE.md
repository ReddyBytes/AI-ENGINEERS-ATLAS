# 03 Guide — Multi-Agent Research System

## Overview

Build the research system in five phases. You will have a working single-agent version by Phase 2, then upgrade to true multi-agent by Phase 4.

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

<details><summary>💡 Hint</summary>

DuckDuckGo rate-limits aggressively. If you get `RatelimitException`, add a `time.sleep(2)` between calls during development. Wikipedia requires a `user_agent` string — `"ResearchBot/1.0 (educational project)"` works.

</details>

### Step 3: Plan your state schema on paper

Before writing code, sketch the state schema. Each worker needs to:
- Know its assigned task
- Write its output somewhere the supervisor can read it

Key design question: how do worker results get merged back into shared state?

Read `15_LangGraph/06_Multi_Agent_with_LangGraph/Architecture_Deep_Dive.md` — specifically the "Send API" section.

---

## Phase 1 — Define State and Supervisor

### Step 4: Understand the state schema

The `ResearchState` in the starter code uses `Annotated[list, operator.add]` for shared fields. This means LangGraph appends (not overwrites) when multiple parallel workers both return values for the same key.

```python
class ResearchState(TypedDict):
    research_question: str
    sub_tasks: list[dict]
    current_task: Optional[dict]            # Set by Send API per worker
    web_results: Annotated[list, operator.add]
    wiki_results: Annotated[list, operator.add]
    draft_sections: Annotated[list, operator.add]
    fact_check_results: list[dict]
    final_report: str
    worker_errors: Annotated[list, operator.add]
```

### Step 5: Implement the Supervisor planning node

The supervisor's first job is task decomposition. Call Claude with a prompt asking it to split the research question into exactly 2 tasks: one web search and one Wikipedia lookup. Request JSON output.

<details><summary>💡 Hint</summary>

Ask Claude to return JSON in this exact format:
```json
[
  {"task_id": "t1", "type": "web_search", "query": "specific search query"},
  {"task_id": "t2", "type": "wiki_lookup", "topic": "Wikipedia article title"}
]
```

Include an example in your prompt. Wrap the Claude call in a try/except and fall back to constructing tasks from the raw research question if parsing fails.

</details>

<details><summary>✅ Answer</summary>

```python
def supervisor_plan_node(state: ResearchState) -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    question = state["research_question"]
    prompt = (
        f'Decompose this research question into exactly 2 tasks.\n'
        f'Question: "{question}"\n\n'
        f'Return JSON array:\n'
        f'[{{"task_id": "t1", "type": "web_search", "query": "..."}},\n'
        f' {{"task_id": "t2", "type": "wiki_lookup", "topic": "..."}}]'
    )
    response = client.messages.create(
        model=MODEL, max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        # Extract JSON from response text
        text = response.content[0].text
        start = text.index("[")
        end = text.rindex("]") + 1
        tasks = json.loads(text[start:end])
    except (json.JSONDecodeError, ValueError):
        tasks = [
            {"task_id": "t1", "type": "web_search", "query": f"{question} 2024"},
            {"task_id": "t2", "type": "wiki_lookup", "topic": question.split()[0]},
        ]
    return {"sub_tasks": tasks}
```

</details>

### Step 6: Test the supervisor in isolation

Call the supervisor function directly (not through LangGraph yet):
```python
state = {"research_question": "What is the economic impact of AI on manufacturing?"}
result = supervisor_plan_node(state)
print(result["sub_tasks"])
```

Verify you get well-formed sub-tasks before wiring into a graph.

---

## Phase 2 — Build Individual Worker Agents

### Step 7: Implement the WebResearcher worker

The worker calls `web_search(query)`, then uses Claude to summarize the top results into 3 key facts.

<details><summary>💡 Hint</summary>

Format raw search results as:
```
Title: ...
URL: ...
Excerpt: ...
```
Then ask Claude: "Extract the 3 most important facts relevant to [query]. Return JSON: [{"fact": "...", "source_url": "..."}]"

The error handling pattern is already shown in the starter code: `except Exception as e: return {"worker_errors": [...]}`.

</details>

### Step 8: Implement the DataAnalyst worker

Fetch the Wikipedia page for the assigned topic. Use Claude to extract statistics and key claims as structured data.

<details><summary>💡 Hint</summary>

Use `wiki_data["summary"][:2000]` — the full article is too long. Ask Claude:
"Extract from this Wikipedia text: (1) key statistics with numbers, (2) important claims. Return JSON: {"facts": [...], "stats": [...]}."

</details>

### Step 9: Test both workers in sequence

Before enabling parallelism, run both workers in sequence with a hand-crafted state to verify they produce real data:

```python
state = {
    "research_question": "AI impact on manufacturing",
    "sub_tasks": [
        {"task_id": "t1", "type": "web_search", "query": "AI manufacturing employment 2024"},
        {"task_id": "t2", "type": "wiki_lookup", "topic": "Industry 4.0"},
    ],
    "web_results": [], "wiki_results": [], ...
}
```

---

## Phase 3 — Build Writer and FactChecker

### Step 10: Implement the Writer agent

The Writer receives accumulated `web_results` and `wiki_results` from state and drafts a structured report section.

<details><summary>💡 Hint</summary>

Build a research brief by formatting each result with its `task_id` for citation. The Claude prompt should be explicit: "Using ONLY the provided research, write a 400–600 word analysis. Cite sources as [task_id]. Do not add information not in the research."

Handle the empty case: if both `web_results` and `wiki_results` are empty, return a draft noting that research data was unavailable.

</details>

### Step 11: Implement the FactChecker agent

The FactChecker gets the latest draft and all raw research. It asks Claude to identify each factual claim and rate it: `VERIFIED`, `PARTIALLY_SUPPORTED`, or `UNSUPPORTED`.

<details><summary>💡 Hint</summary>

Limit to the top 5 most specific claims to keep token usage manageable. The prompt structure:

```
Draft: {latest_draft}

Sources:
- [t1] {web_result_facts}
- [t2] {wiki_result_facts}

For each factual claim in the draft, check it against the sources.
Return JSON: [{"claim": "...", "verdict": "VERIFIED", "source_ref": "t1", "notes": "..."}]
```

</details>

### Step 12: Implement the Supervisor synthesis node

After workers complete, the supervisor reads the fact-check results and produces a final corrected report. Any `UNSUPPORTED` claims should be removed or hedged. Any `PARTIALLY_SUPPORTED` claims should be adjusted to match source numbers.

<details><summary>✅ Answer</summary>

Build the synthesis prompt with:
1. The latest draft
2. The fact-check results (which claims need fixing)
3. All source URLs from `web_results` and `wiki_results`

Ask Claude to produce a final Markdown report with:
- `## Research Report: [question]`
- Body sections
- `## Sources` with URLs
- `## Research Notes` listing limitations and failed workers

Then save to file and return `{"final_report": markdown_text}`.

</details>

---

## Phase 4 — Wire the Graph with Parallel Execution

### Step 13: Understand the Send API

LangGraph's `Send` API lets the supervisor dynamically dispatch to worker nodes. The `dispatch_workers` function in the starter code is already complete — it reads `sub_tasks` and creates a `Send` for each task type.

```python
from langgraph.constants import Send

def dispatch_workers(state: ResearchState):
    sends = []
    for task in state["sub_tasks"]:
        task_state = {**state, "current_task": task}
        if task["type"] == "web_search":
            sends.append(Send("web_researcher", task_state))
        elif task["type"] == "wiki_lookup":
            sends.append(Send("data_analyst", task_state))
    return sends
```

### Step 14: Assemble the full graph

The graph structure is pre-built in `build_research_graph()`. After you implement all node functions, it should work end-to-end without changes to the wiring.

### Step 15: Test end-to-end

```python
graph = build_research_graph()
result = graph.invoke(initial_state(
    "What are the main economic impacts of AI on manufacturing employment?"
))
print(result["final_report"])
```

<details><summary>💡 Hint</summary>

If the graph hangs after `[Dispatch]`, both workers are running in parallel. If it crashes with a KeyError on `current_task`, check that `dispatch_workers` passes `{**state, "current_task": task}` and that your worker nodes call `state.get("current_task", {})` defensively.

</details>

---

## Phase 5 — Fault Tolerance

### Step 16: Add try/except to all workers

Wrap each worker's core logic in try/except and return `{"worker_errors": [...]}` on failure. This is already shown as the error path in `web_researcher_node`.

### Step 17: Make the supervisor resilient

In `supervisor_synthesize_node`, check `state["worker_errors"]` and include a `## Research Notes` section in the final report listing any data gaps.

### Step 18: Test failure modes

Temporarily break each worker (add `raise Exception("test")` at the start) and confirm the pipeline completes with a report that notes the limitation.

---

## Testing Checklist

- [ ] DuckDuckGo search returns results for test queries
- [ ] Wikipedia lookup returns page summaries
- [ ] Supervisor decomposes question into valid sub-tasks
- [ ] Both workers run in parallel (check log timestamps)
- [ ] Writer produces a coherent 400+ word section
- [ ] FactChecker identifies at least one verified and one flagged claim
- [ ] Final report contains citations back to task IDs
- [ ] Killing web_researcher does not crash the pipeline
- [ ] Killing data_analyst does not crash the pipeline
- [ ] `worker_errors` list populated correctly on failures

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| **03_GUIDE.md** | you are here |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |
