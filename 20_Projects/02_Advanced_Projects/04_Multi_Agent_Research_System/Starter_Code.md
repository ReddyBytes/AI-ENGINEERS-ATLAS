# Project 4: Starter Code

> Copy this into `research_system.py`. All `# TODO:` blocks are yours to implement.

```python
"""
Multi-Agent Research System with LangGraph Supervisor Pattern
Workers: WebResearcher, DataAnalyst, Writer, FactChecker
Supervisor: Decomposes, dispatches, synthesizes, handles failures
"""

import os
import json
import operator
from typing import TypedDict, Annotated, Optional
from datetime import datetime
import anthropic
from langgraph.graph import StateGraph, END
from langgraph.constants import Send

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"
MAX_SEARCH_RESULTS = 8
OUTPUT_DIR = "research_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# State Schema
# ─────────────────────────────────────────────

class ResearchState(TypedDict):
    """
    Shared state for the multi-agent research system.

    Annotated[list, operator.add] fields use LangGraph's merge-by-append
    semantics: when parallel workers both return a value for this key,
    LangGraph appends both lists rather than overwriting.
    """
    research_question: str
    sub_tasks: list[dict]
    current_task: Optional[dict]            # Set by Send API for each worker
    web_results: Annotated[list, operator.add]
    wiki_results: Annotated[list, operator.add]
    draft_sections: Annotated[list, operator.add]
    fact_check_results: list[dict]
    final_report: str
    worker_errors: Annotated[list, operator.add]


def initial_state(research_question: str) -> dict:
    return {
        "research_question": research_question,
        "sub_tasks": [],
        "current_task": None,
        "web_results": [],
        "wiki_results": [],
        "draft_sections": [],
        "fact_check_results": [],
        "final_report": "",
        "worker_errors": [],
    }


# ─────────────────────────────────────────────
# Tool Wrappers
# ─────────────────────────────────────────────

def web_search(query: str, max_results: int = MAX_SEARCH_RESULTS) -> list[dict]:
    """
    Search the web using DuckDuckGo.
    Returns list of {"title": ..., "href": ..., "body": ...} dicts.
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        raise RuntimeError(f"DuckDuckGo search failed: {e}")


def wikipedia_fetch(topic: str) -> dict:
    """
    Fetch Wikipedia page summary for a topic.
    Returns {"title": ..., "summary": ..., "url": ...}
    """
    try:
        import wikipediaapi
        wiki = wikipediaapi.Wikipedia(
            user_agent="MultiAgentResearchBot/1.0 (educational project)",
            language="en"
        )
        page = wiki.page(topic)
        if not page.exists():
            # Try a broader search
            return {"title": topic, "summary": f"No Wikipedia page found for '{topic}'", "url": ""}
        return {
            "title": page.title,
            "summary": page.summary[:2000],  # Limit for token budget
            "url": page.fullurl,
        }
    except Exception as e:
        raise RuntimeError(f"Wikipedia fetch failed: {e}")


# ─────────────────────────────────────────────
# Node: Supervisor — Plan
# ─────────────────────────────────────────────

def supervisor_plan_node(state: ResearchState) -> dict:
    """
    Decompose the research question into worker tasks.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    question = state["research_question"]

    print(f"\n[Supervisor] Planning research for: {question[:80]}...")

    # TODO: Implement task decomposition
    # Steps:
    #   1. Build a prompt asking Claude to decompose the question into:
    #      - One web_search task with a specific search query
    #      - One wiki_lookup task with a specific Wikipedia topic
    #   2. Request JSON output:
    #      [
    #        {"task_id": "t1", "type": "web_search", "query": "..."},
    #        {"task_id": "t2", "type": "wiki_lookup", "topic": "..."}
    #      ]
    #   3. Parse JSON and return {"sub_tasks": parsed_tasks}
    #
    # Tip: Include examples in your prompt to improve JSON formatting.
    # Handle JSON parse errors gracefully with a fallback set of tasks.

    # Placeholder tasks — replace with Claude-generated decomposition
    fallback_tasks = [
        {"task_id": "t1", "type": "web_search",
         "query": f"{question} research 2024"},
        {"task_id": "t2", "type": "wiki_lookup",
         "topic": question.split()[:3]},  # First 3 words as topic
    ]

    print(f"[Supervisor] Dispatching {len(fallback_tasks)} worker tasks")
    return {"sub_tasks": fallback_tasks}


# ─────────────────────────────────────────────
# Node: Worker Dispatcher (Conditional Edge Source)
# ─────────────────────────────────────────────

def dispatch_workers(state: ResearchState):
    """
    Called as a conditional edge from supervisor_plan.
    Returns a list of Send objects for parallel worker execution.

    TODO: Complete the dispatch logic.
    Steps:
      1. Iterate over state["sub_tasks"]
      2. For each task with type "web_search": Send to "web_researcher"
      3. For each task with type "wiki_lookup": Send to "data_analyst"
      4. Pass the full state PLUS the specific task as "current_task"
      5. Return the list of Send objects

    Note: LangGraph executes all Send objects in parallel.
    """
    sends = []
    for task in state["sub_tasks"]:
        # TODO: Add Send for each task type
        # Hint: Send("node_name", {**state, "current_task": task})
        task_state = {**state, "current_task": task}
        if task["type"] == "web_search":
            sends.append(Send("web_researcher", task_state))
        elif task["type"] == "wiki_lookup":
            sends.append(Send("data_analyst", task_state))

    print(f"[Dispatch] Sending {len(sends)} worker tasks (parallel)")
    return sends


# ─────────────────────────────────────────────
# Node: WebResearcher Worker
# ─────────────────────────────────────────────

def web_researcher_node(state: ResearchState) -> dict:
    """
    Search the web and summarize findings using Claude.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    task = state.get("current_task", {})
    query = task.get("query", state["research_question"])
    task_id = task.get("task_id", "t_web")

    print(f"\n[WebResearcher] Searching: '{query}'...")

    try:
        # Step 1: Fetch search results
        raw_results = web_search(query)
        print(f"[WebResearcher] Got {len(raw_results)} results")

        # TODO: Implement Claude-based summarization
        # Steps:
        #   1. Format raw_results into a readable string:
        #      "Title: ...\nURL: ...\nExcerpt: ...\n\n"
        #   2. Call Claude with:
        #      "You are a research assistant. Extract the 3 most important
        #       facts from these search results relevant to: [query].
        #       Return as JSON: [{"fact": "...", "source_url": "..."}, ...]"
        #   3. Parse JSON and return as web_results

        # Placeholder summarization (no Claude call yet)
        summaries = []
        for r in raw_results[:3]:
            summaries.append({
                "fact": r.get("body", "")[:200],
                "source_url": r.get("href", ""),
                "task_id": task_id,
            })

        print(f"[WebResearcher] Extracted {len(summaries)} key facts")
        return {"web_results": summaries}

    except Exception as e:
        print(f"[WebResearcher] ERROR: {e}")
        return {"worker_errors": [{"worker": "web_researcher", "error": str(e), "task_id": task_id}]}


# ─────────────────────────────────────────────
# Node: DataAnalyst Worker
# ─────────────────────────────────────────────

def data_analyst_node(state: ResearchState) -> dict:
    """
    Fetch Wikipedia content and extract structured facts.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    task = state.get("current_task", {})
    topic = task.get("topic", state["research_question"])
    task_id = task.get("task_id", "t_wiki")

    # Handle case where topic is a list (from our placeholder)
    if isinstance(topic, list):
        topic = " ".join(topic)

    print(f"\n[DataAnalyst] Fetching Wikipedia: '{topic}'...")

    try:
        # Step 1: Fetch Wikipedia content
        wiki_data = wikipedia_fetch(topic)
        print(f"[DataAnalyst] Fetched '{wiki_data['title']}' ({len(wiki_data['summary'])} chars)")

        # TODO: Implement Claude-based fact and statistic extraction
        # Steps:
        #   1. Build a prompt that extracts from wiki_data["summary"]:
        #      - Key statistics (numbers, percentages, dates)
        #      - Important claims and definitions
        #   2. Request JSON: {"facts": [...], "stats": [...], "definitions": [...]}
        #   3. Return as wiki_results

        # Placeholder — replace with Claude extraction
        result = {
            "page_title": wiki_data["title"],
            "summary_excerpt": wiki_data["summary"][:500],
            "url": wiki_data["url"],
            "facts": [],   # TODO: Populated by Claude extraction
            "stats": [],   # TODO: Populated by Claude extraction
            "task_id": task_id,
        }

        return {"wiki_results": [result]}

    except Exception as e:
        print(f"[DataAnalyst] ERROR: {e}")
        return {"worker_errors": [{"worker": "data_analyst", "error": str(e), "task_id": task_id}]}


# ─────────────────────────────────────────────
# Node: Writer Agent
# ─────────────────────────────────────────────

def writer_node(state: ResearchState) -> dict:
    """
    Synthesize research into a coherent draft report section.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print(f"\n[Writer] Drafting report section...")
    print(f"[Writer] Available: {len(state['web_results'])} web results, "
          f"{len(state['wiki_results'])} wiki results")

    # TODO: Implement writing with all available research
    # Steps:
    #   1. Build a research brief combining web_results and wiki_results
    #   2. Format each source with its task_id for citation
    #   3. Call Claude with a writing prompt:
    #      "You are a research writer. Using ONLY the provided research,
    #       write a 400-600 word analysis of: [research_question]
    #       - Use clear paragraphs with a logical flow
    #       - Include statistics where available (cite as [task_id])
    #       - Do not add information not present in the research
    #       - End with a 2-3 sentence conclusion"
    #   4. Return {"draft_sections": [{"content": text, "word_count": N}]}
    #
    # Fault handling: if both web_results and wiki_results are empty,
    # return a draft noting that research data was unavailable.

    if not state["web_results"] and not state["wiki_results"]:
        draft = ("Research data was unavailable due to worker failures. "
                 "A manual research pass is required.")
        return {"draft_sections": [{"content": draft, "word_count": len(draft.split())}]}

    # TODO: Replace placeholder with Claude writing call
    draft = f"[Draft placeholder for: {state['research_question'][:50]}...]\n"
    draft += f"Based on {len(state['web_results'])} web sources and "
    draft += f"{len(state['wiki_results'])} Wikipedia sources.\n"
    draft += "(Complete the writer_node TODO to generate real content)"

    return {"draft_sections": [{"content": draft, "word_count": len(draft.split())}]}


# ─────────────────────────────────────────────
# Node: FactChecker Agent
# ─────────────────────────────────────────────

def fact_checker_node(state: ResearchState) -> dict:
    """
    Cross-reference draft claims against raw research sources.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Get the latest draft
    if not state["draft_sections"]:
        return {"fact_check_results": [{"error": "No draft to fact-check"}]}

    latest_draft = state["draft_sections"][-1]["content"]
    print(f"\n[FactChecker] Checking draft ({len(latest_draft.split())} words)...")

    # TODO: Implement fact checking
    # Steps:
    #   1. Build a fact-checking prompt that includes:
    #      - The draft text
    #      - All raw research (web_results + wiki_results) as sources
    #   2. Ask Claude to:
    #      - Extract each factual claim from the draft
    #      - Check each claim against the sources
    #      - Rate each: VERIFIED, PARTIALLY_SUPPORTED, or UNSUPPORTED
    #   3. Request JSON:
    #      [{"claim": "...", "verdict": "VERIFIED", "source_ref": "t1", "notes": "..."}]
    #   4. Return {"fact_check_results": parsed_results}
    #
    # Tip: limit to the top 5 most specific claims to keep token usage manageable.

    # Placeholder
    fact_check = [{
        "claim": "Fact checking not yet implemented",
        "verdict": "UNSUPPORTED",
        "source_ref": "none",
        "notes": "Complete the fact_checker_node TODO",
    }]

    print(f"[FactChecker] Checked {len(fact_check)} claims")
    return {"fact_check_results": fact_check}


# ─────────────────────────────────────────────
# Node: Supervisor — Synthesize
# ─────────────────────────────────────────────

def supervisor_synthesize_node(state: ResearchState) -> dict:
    """
    Produce the final report, incorporating fact-check corrections.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print(f"\n[Supervisor] Synthesizing final report...")

    # Report failed workers
    if state["worker_errors"]:
        print(f"[Supervisor] ⚠ {len(state['worker_errors'])} worker error(s):")
        for err in state["worker_errors"]:
            print(f"   - {err['worker']}: {err['error']}")

    # TODO: Implement final synthesis
    # Steps:
    #   1. Get the latest draft from state["draft_sections"]
    #   2. Get fact_check_results — identify UNSUPPORTED and PARTIALLY_SUPPORTED claims
    #   3. Build a synthesis prompt:
    #      "Given this draft and fact-check results, produce a final, corrected report.
    #       - Fix any UNSUPPORTED claims (remove or hedge them)
    #       - Fix any PARTIALLY_SUPPORTED claims (adjust figures to match sources)
    #       - Keep VERIFIED claims unchanged
    #       - Add a 'Research Notes' section at the end listing any limitations"
    #   4. Format the final report in Markdown with:
    #      - Title: ## Research Report: [question]
    #      - Body sections
    #      - ## Sources section with URLs from web_results + wiki_results
    #      - ## Research Notes (limitations, failed workers, unverified claims)
    #   5. Save to file and return {"final_report": markdown_text}

    # Build basic report structure
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    draft = state["draft_sections"][-1]["content"] if state["draft_sections"] else "No content generated."

    # TODO: Replace with Claude-synthesized final report
    report_lines = [
        f"## Research Report: {state['research_question']}",
        f"*Generated: {timestamp}*",
        "",
        "### Findings",
        draft,
        "",
        "### Sources",
    ]

    for wr in state["web_results"]:
        if wr.get("source_url"):
            report_lines.append(f"- {wr.get('source_url', 'Unknown source')}")
    for wiki in state["wiki_results"]:
        if wiki.get("url"):
            report_lines.append(f"- {wiki.get('url', 'Wikipedia')}: {wiki.get('page_title', '')}")

    if state["worker_errors"]:
        report_lines.extend([
            "",
            "### Research Notes",
            f"⚠ {len(state['worker_errors'])} data collection error(s) occurred.",
            "Some information may be incomplete.",
        ])

    final_report = "\n".join(report_lines)

    # Save to file
    filename = f"{OUTPUT_DIR}/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_report)
    print(f"\n[Supervisor] Report saved: {filename}")

    return {"final_report": final_report}


# ─────────────────────────────────────────────
# Graph Assembly
# ─────────────────────────────────────────────

def build_research_graph():
    """
    Assemble the multi-agent research graph.

    Graph topology:
    supervisor_plan → [parallel: web_researcher, data_analyst]
                    ↓ (both merge into writer)
                    writer → fact_checker → supervisor_synthesize → END
    """
    builder = StateGraph(ResearchState)

    builder.add_node("supervisor_plan", supervisor_plan_node)
    builder.add_node("web_researcher", web_researcher_node)
    builder.add_node("data_analyst", data_analyst_node)
    builder.add_node("writer", writer_node)
    builder.add_node("fact_checker", fact_checker_node)
    builder.add_node("supervisor_synthesize", supervisor_synthesize_node)

    # Entry
    builder.set_entry_point("supervisor_plan")

    # Parallel dispatch using Send API
    builder.add_conditional_edges(
        "supervisor_plan",
        dispatch_workers,
    )

    # Both parallel workers converge on writer
    # (LangGraph waits for all parallel branches to complete before running writer)
    builder.add_edge("web_researcher", "writer")
    builder.add_edge("data_analyst", "writer")

    # Linear chain after research
    builder.add_edge("writer", "fact_checker")
    builder.add_edge("fact_checker", "supervisor_synthesize")
    builder.add_edge("supervisor_synthesize", END)

    return builder.compile()


# ─────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────

def research(question: str) -> str:
    """
    Run the full multi-agent research pipeline.
    Returns the final Markdown report.
    """
    graph = build_research_graph()

    print(f"\n{'='*60}")
    print(f"Research Question: {question}")
    print('='*60)

    result = graph.invoke(initial_state(question))

    print(f"\n{'='*60}")
    print("FINAL REPORT:")
    print('='*60)
    print(result["final_report"])

    if result["worker_errors"]:
        print(f"\n⚠ {len(result['worker_errors'])} worker(s) encountered errors.")

    return result["final_report"]


def test_fault_tolerance():
    """
    TODO: Test fault tolerance by injecting failures.
    Steps:
      1. Monkey-patch web_search to raise an exception
      2. Run the pipeline and verify it completes
      3. Verify worker_errors is populated
      4. Verify the report mentions the limitation
      5. Restore web_search and repeat with wikipedia_fetch failing
    """
    print("\n[Fault Tolerance Test] Not yet implemented — complete the TODO above")


if __name__ == "__main__":
    import sys
    question = (
        sys.argv[1] if len(sys.argv) > 1
        else "What are the economic impacts of AI adoption on manufacturing employment?"
    )
    research(question)
```
