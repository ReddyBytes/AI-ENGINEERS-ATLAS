"""
Multi-Agent Research System with LangGraph Supervisor Pattern
Workers: WebResearcher, DataAnalyst, Writer, FactChecker
Supervisor: Decomposes question, dispatches workers in parallel,
            synthesizes final report, handles worker failures gracefully.

Usage:
    python src/starter.py "What are the economic impacts of AI on manufacturing employment?"
    python src/starter.py  # uses default question
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
OUTPUT_DIR = "research_output"   # ← generated reports saved here
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# State Schema
# ─────────────────────────────────────────────
# Annotated[list, operator.add] means LangGraph APPENDS parallel worker
# outputs rather than overwriting — key insight for multi-agent state.
# ─────────────────────────────────────────────

class ResearchState(TypedDict):
    research_question: str
    sub_tasks: list[dict]
    current_task: Optional[dict]            # ← set by Send API for each worker
    web_results: Annotated[list, operator.add]    # ← appended by WebResearcher
    wiki_results: Annotated[list, operator.add]   # ← appended by DataAnalyst
    draft_sections: Annotated[list, operator.add] # ← appended by Writer
    fact_check_results: list[dict]
    final_report: str
    worker_errors: Annotated[list, operator.add]  # ← appended by any failing worker


def initial_state(research_question: str) -> dict:
    """Create a clean initial state for a new research session."""
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
            return {"title": topic, "summary": f"No Wikipedia page found for '{topic}'", "url": ""}
        return {
            "title": page.title,
            "summary": page.summary[:2000],   # ← limit for token budget
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

    TODO: Implement task decomposition.
    Steps:
      1. Build a prompt asking Claude to decompose the question into:
           - One web_search task with a specific search query
           - One wiki_lookup task with a specific Wikipedia topic
      2. Request JSON output:
           [
             {"task_id": "t1", "type": "web_search", "query": "..."},
             {"task_id": "t2", "type": "wiki_lookup", "topic": "..."}
           ]
      3. Parse JSON and return {"sub_tasks": parsed_tasks}

    Handle JSON parse errors with a fallback set of tasks.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    question = state["research_question"]
    print(f"\n[Supervisor] Planning research for: {question[:80]}...")

    # Placeholder tasks — replace with Claude-generated decomposition
    fallback_tasks = [
        {"task_id": "t1", "type": "web_search",
         "query": f"{question} research 2024"},
        {"task_id": "t2", "type": "wiki_lookup",
         "topic": " ".join(question.split()[:3])},   # ← first 3 words as topic
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
    LangGraph executes all Send objects simultaneously.

    Each Send gives the worker a full copy of state PLUS the specific task
    as current_task. Workers return partial state updates only.
    """
    sends = []
    for task in state["sub_tasks"]:
        task_state = {**state, "current_task": task}   # ← inject specific task
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

    TODO: Replace placeholder summarization with a Claude call.
    Steps:
      1. Get query from state["current_task"]["query"]
      2. Call web_search(query) to get raw results
      3. Format results as readable text
      4. Call Claude: "Extract the 3 most important facts relevant to [query].
         Return JSON: [{"fact": "...", "source_url": "..."}]"
      5. Return {"web_results": summaries}

    On any exception: return {"worker_errors": [{...}]} — do NOT raise.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    task = state.get("current_task", {})
    query = task.get("query", state["research_question"])
    task_id = task.get("task_id", "t_web")

    print(f"\n[WebResearcher] Searching: '{query}'...")

    try:
        raw_results = web_search(query)
        print(f"[WebResearcher] Got {len(raw_results)} results")

        # Placeholder: use raw excerpts without Claude summarization
        # TODO: Replace with Claude-based fact extraction
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

    TODO: Replace placeholder extraction with a Claude call.
    Steps:
      1. Get topic from state["current_task"]["topic"]
      2. Call wikipedia_fetch(topic)
      3. Use Claude to extract from wiki_data["summary"]:
           - Key statistics (numbers, percentages, dates)
           - Important claims and definitions
         Request JSON: {"facts": [...], "stats": [...]}
      4. Return {"wiki_results": [result]}

    On any exception: return {"worker_errors": [{...}]}
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    task = state.get("current_task", {})
    topic = task.get("topic", state["research_question"])
    task_id = task.get("task_id", "t_wiki")

    if isinstance(topic, list):
        topic = " ".join(topic)   # ← handle list-format topics

    print(f"\n[DataAnalyst] Fetching Wikipedia: '{topic}'...")

    try:
        wiki_data = wikipedia_fetch(topic)
        print(f"[DataAnalyst] Fetched '{wiki_data['title']}' ({len(wiki_data['summary'])} chars)")

        # Placeholder: return summary excerpt without Claude extraction
        # TODO: Replace with Claude-based structured extraction
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

    TODO: Replace placeholder with a Claude writing call.
    Steps:
      1. Build a research brief combining web_results and wiki_results
         Format each source with its task_id for citation
      2. Call Claude: "Using ONLY the provided research, write a 400-600 word
         analysis of [research_question]. Cite sources as [task_id]. Do not add
         information not in the research. End with a 2-3 sentence conclusion."
      3. Return {"draft_sections": [{"content": text, "word_count": N}]}

    Fault handling: if both result lists are empty, return a note that
    research data was unavailable.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print(f"\n[Writer] Drafting report section...")
    print(f"[Writer] Available: {len(state['web_results'])} web results, "
          f"{len(state['wiki_results'])} wiki results")

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

    TODO: Implement fact checking with Claude.
    Steps:
      1. Get latest draft from state["draft_sections"][-1]["content"]
      2. Build fact-checking prompt including:
           - The draft text
           - All raw research (web_results + wiki_results) as sources
      3. Ask Claude to extract each factual claim and rate:
           VERIFIED / PARTIALLY_SUPPORTED / UNSUPPORTED
      4. Request JSON:
           [{"claim": "...", "verdict": "VERIFIED", "source_ref": "t1", "notes": "..."}]
      5. Return {"fact_check_results": parsed_results}

    Limit to top 5 most specific claims to keep token usage manageable.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    if not state["draft_sections"]:
        return {"fact_check_results": [{"error": "No draft to fact-check"}]}

    latest_draft = state["draft_sections"][-1]["content"]
    print(f"\n[FactChecker] Checking draft ({len(latest_draft.split())} words)...")

    # Placeholder — replace with Claude fact-checking call
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
    Produce the final report incorporating fact-check corrections.

    TODO: Implement final synthesis with Claude.
    Steps:
      1. Get latest draft from state["draft_sections"]
      2. Get fact_check_results — identify UNSUPPORTED and PARTIALLY_SUPPORTED claims
      3. Ask Claude to produce a final, corrected Markdown report:
           - Fix UNSUPPORTED claims (remove or hedge)
           - Fix PARTIALLY_SUPPORTED claims (adjust figures to match sources)
           - Add ## Sources section with all URLs
           - Add ## Research Notes section listing limitations
      4. Save to file, return {"final_report": markdown_text}
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print(f"\n[Supervisor] Synthesizing final report...")

    if state["worker_errors"]:
        print(f"[Supervisor]   {len(state['worker_errors'])} worker error(s):")
        for err in state["worker_errors"]:
            print(f"   - {err['worker']}: {err['error']}")

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
            f"  {len(state['worker_errors'])} data collection error(s) occurred.",
            "Some information may be incomplete.",
        ])

    final_report = "\n".join(report_lines)

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

    Topology:
    supervisor_plan --> [parallel: web_researcher, data_analyst]
                     --> writer --> fact_checker --> supervisor_synthesize --> END
    """
    builder = StateGraph(ResearchState)

    builder.add_node("supervisor_plan", supervisor_plan_node)
    builder.add_node("web_researcher", web_researcher_node)
    builder.add_node("data_analyst", data_analyst_node)
    builder.add_node("writer", writer_node)
    builder.add_node("fact_checker", fact_checker_node)
    builder.add_node("supervisor_synthesize", supervisor_synthesize_node)

    builder.set_entry_point("supervisor_plan")

    # Parallel dispatch: supervisor_plan triggers dispatch_workers which
    # returns Send objects — LangGraph executes them simultaneously
    builder.add_conditional_edges("supervisor_plan", dispatch_workers)

    # Both parallel branches converge on writer
    # LangGraph waits for ALL parallel branches before running writer
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
    """Run the full multi-agent research pipeline. Returns the final Markdown report."""
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
        print(f"\n  {len(result['worker_errors'])} worker(s) encountered errors.")

    return result["final_report"]


if __name__ == "__main__":
    import sys
    question = (
        sys.argv[1] if len(sys.argv) > 1
        else "What are the economic impacts of AI adoption on manufacturing employment?"
    )
    research(question)
