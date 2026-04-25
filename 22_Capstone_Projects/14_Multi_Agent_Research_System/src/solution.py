"""
Multi-Agent Research System with LangGraph Supervisor Pattern — Project 14 SOLUTION
Workers: WebResearcher, DataAnalyst, Writer, FactChecker
Supervisor: Decomposes question, dispatches workers in parallel,
            synthesizes final report, handles worker failures gracefully.

Usage:
    python solution.py "What are the economic impacts of AI on manufacturing employment?"
    python solution.py  # uses default question

Setup:
    pip install langgraph langchain-anthropic anthropic duckduckgo-search wikipedia-api
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
# Each parallel worker returns a partial update; operator.add merges them.
# ─────────────────────────────────────────────

class ResearchState(TypedDict):
    research_question: str
    sub_tasks: list[dict]
    current_task: Optional[dict]               # ← injected by Send API for each worker
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
    DuckDuckGo rate-limits: add delay between calls in production.
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
    Summary capped at 2000 chars to stay within token budget.
    """
    try:
        import wikipediaapi
        wiki = wikipediaapi.Wikipedia(
            user_agent="MultiAgentResearchBot/1.0 (educational project)",  # ← required by Wikipedia API
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
    Decompose the research question into exactly 2 worker tasks using Claude.
    One web_search task and one wiki_lookup task.
    Falls back to a heuristic decomposition if Claude's JSON fails to parse.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    question = state["research_question"]
    print(f"\n[Supervisor] Planning research for: {question[:80]}...")

    prompt = (
        f'Decompose this research question into exactly 2 tasks.\n'
        f'Question: "{question}"\n\n'
        f'Task 1: A web search query (specific, 4-8 words, optimized for search engine results)\n'
        f'Task 2: A Wikipedia article title (a specific topic, not a question)\n\n'
        f'Return ONLY valid JSON array, no other text:\n'
        f'[{{"task_id": "t1", "type": "web_search", "query": "..."}},\n'
        f' {{"task_id": "t2", "type": "wiki_lookup", "topic": "..."}}]'
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        text = response.content[0].text.strip()
        # Extract JSON array from response (handles markdown fences)
        start = text.index("[")
        end = text.rindex("]") + 1
        tasks = json.loads(text[start:end])

        # Validate structure
        for task in tasks:
            if "task_id" not in task or "type" not in task:
                raise ValueError("Invalid task structure")

    except (json.JSONDecodeError, ValueError, AttributeError) as e:
        print(f"[Supervisor] JSON parse failed ({e}) — using fallback tasks")
        tasks = [
            {"task_id": "t1", "type": "web_search",
             "query": f"{question} 2024 research study"},       # ← heuristic search query
            {"task_id": "t2", "type": "wiki_lookup",
             "topic": " ".join(question.split()[:4])},          # ← first 4 words as Wikipedia topic
        ]

    print(f"[Supervisor] Tasks: {json.dumps(tasks, indent=2)}")
    print(f"[Supervisor] Dispatching {len(tasks)} worker tasks")
    return {"sub_tasks": tasks}


# ─────────────────────────────────────────────
# Node: Worker Dispatcher (Conditional Edge Source)
# ─────────────────────────────────────────────

def dispatch_workers(state: ResearchState):
    """
    Called as a conditional edge from supervisor_plan.
    Returns a list of Send objects — LangGraph executes them simultaneously.

    Each Send injects the specific task as current_task into the worker's state.
    Workers receive a full copy of state plus their specific task, then return
    partial updates that are merged back using the operator.add reducers.
    """
    sends = []
    for task in state["sub_tasks"]:
        task_state = {**state, "current_task": task}   # ← each worker gets its own task injected
        if task["type"] == "web_search":
            sends.append(Send("web_researcher", task_state))
        elif task["type"] == "wiki_lookup":
            sends.append(Send("data_analyst", task_state))

    print(f"[Dispatch] Sending {len(sends)} worker tasks in parallel")
    return sends


# ─────────────────────────────────────────────
# Node: WebResearcher Worker
# ─────────────────────────────────────────────

def web_researcher_node(state: ResearchState) -> dict:
    """
    Search the web and use Claude to extract key facts from the results.
    Returns structured facts with source URLs for citation in the report.
    On any exception: returns worker_errors entry (does NOT raise).
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    task = state.get("current_task", {})
    query = task.get("query", state["research_question"])
    task_id = task.get("task_id", "t_web")

    print(f"\n[WebResearcher] Searching: '{query}'...")

    try:
        raw_results = web_search(query)
        print(f"[WebResearcher] Got {len(raw_results)} raw results")

        # Format top results for Claude to analyze
        formatted = []
        for i, r in enumerate(raw_results[:5]):
            formatted.append(
                f"[Result {i+1}]\n"
                f"Title: {r.get('title', 'N/A')}\n"
                f"URL: {r.get('href', '')}\n"
                f"Excerpt: {r.get('body', '')[:300]}"
            )
        results_text = "\n\n".join(formatted)

        # Use Claude to extract structured facts from raw search results
        extract_prompt = (
            f"Search query: '{query}'\n\n"
            f"Search results:\n{results_text}\n\n"
            f"Extract the 3 most important, specific, factual findings relevant to this query. "
            f"Each fact must be a specific claim (with numbers, dates, or names where available). "
            f"Include the source URL for each fact.\n\n"
            f"Return ONLY valid JSON array:\n"
            f'[{{"fact": "specific factual claim", "source_url": "https://..."}}]'
        )

        fact_response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            messages=[{"role": "user", "content": extract_prompt}],
        )

        raw = fact_response.content[0].text.strip()
        # Extract JSON array from response
        try:
            start = raw.index("[")
            end = raw.rindex("]") + 1
            summaries = json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError):
            # Fallback: use raw excerpts if Claude's JSON fails
            summaries = [
                {"fact": r.get("body", "")[:200], "source_url": r.get("href", "")}
                for r in raw_results[:3]
            ]

        # Add task_id for citation tracking
        for s in summaries:
            s["task_id"] = task_id

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
    Fetch Wikipedia content and use Claude to extract structured facts and statistics.
    Returns a structured result with facts list and stats list for the Writer to use.
    On any exception: returns worker_errors entry (does NOT raise).
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    task = state.get("current_task", {})
    topic = task.get("topic", state["research_question"])
    task_id = task.get("task_id", "t_wiki")

    if isinstance(topic, list):
        topic = " ".join(topic)   # ← handle accidentally list-format topics

    print(f"\n[DataAnalyst] Fetching Wikipedia: '{topic}'...")

    try:
        wiki_data = wikipedia_fetch(topic)
        print(f"[DataAnalyst] Fetched '{wiki_data['title']}' ({len(wiki_data['summary'])} chars)")

        # Use Claude to extract structured facts and statistics from the Wikipedia summary
        extract_prompt = (
            f"Wikipedia article: '{wiki_data['title']}'\n\n"
            f"Summary:\n{wiki_data['summary']}\n\n"
            f"Extract:\n"
            f"1. Up to 5 key factual claims (definitions, descriptions, causal relationships)\n"
            f"2. Up to 5 key statistics (numbers, percentages, dates, counts)\n\n"
            f"Return ONLY valid JSON:\n"
            f'{{"facts": ["claim1", "claim2"], "stats": ["stat1 with source", "stat2 with source"]}}'
        )

        extract_response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            messages=[{"role": "user", "content": extract_prompt}],
        )

        raw = extract_response.content[0].text.strip()
        try:
            # Extract JSON object from response
            start = raw.index("{")
            end = raw.rindex("}") + 1
            extracted = json.loads(raw[start:end])
        except (json.JSONDecodeError, ValueError):
            extracted = {"facts": [], "stats": []}

        result = {
            "page_title": wiki_data["title"],
            "summary_excerpt": wiki_data["summary"][:500],  # ← for Writer to use if needed
            "url": wiki_data["url"],
            "facts": extracted.get("facts", []),   # ← structured facts extracted by Claude
            "stats": extracted.get("stats", []),   # ← structured statistics extracted by Claude
            "task_id": task_id,
        }
        print(f"[DataAnalyst] Extracted {len(result['facts'])} facts, {len(result['stats'])} stats")
        return {"wiki_results": [result]}

    except Exception as e:
        print(f"[DataAnalyst] ERROR: {e}")
        return {"worker_errors": [{"worker": "data_analyst", "error": str(e), "task_id": task_id}]}


# ─────────────────────────────────────────────
# Node: Writer Agent
# ─────────────────────────────────────────────

def writer_node(state: ResearchState) -> dict:
    """
    Synthesize web_results and wiki_results into a coherent 400-600 word analysis.
    Cites sources using [task_id] notation for downstream fact-checking.
    Falls back to an error note if no research data is available.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print(f"\n[Writer] Drafting report section...")
    print(f"[Writer] Available: {len(state['web_results'])} web results, "
          f"{len(state['wiki_results'])} wiki results")

    if not state["web_results"] and not state["wiki_results"]:
        draft = (
            "Research data was unavailable due to worker failures. "
            "A manual research pass is required to populate this report."
        )
        return {"draft_sections": [{"content": draft, "word_count": len(draft.split())}]}

    # Build a structured research brief for Claude to write from
    brief_parts = []

    if state["web_results"]:
        brief_parts.append("=== Web Research Findings ===")
        for wr in state["web_results"]:
            brief_parts.append(f"[{wr.get('task_id', 't1')}] {wr.get('fact', '')}")
            if wr.get("source_url"):
                brief_parts.append(f"  Source: {wr['source_url']}")

    if state["wiki_results"]:
        brief_parts.append("\n=== Wikipedia Research ===")
        for wiki in state["wiki_results"]:
            brief_parts.append(f"Article: {wiki.get('page_title', '')} [{wiki.get('task_id', 't2')}]")
            brief_parts.append(f"URL: {wiki.get('url', '')}")
            for fact in wiki.get("facts", []):
                brief_parts.append(f"  - {fact}")
            for stat in wiki.get("stats", []):
                brief_parts.append(f"  * {stat}")

    research_brief = "\n".join(brief_parts)

    write_prompt = (
        f"Research question: '{state['research_question']}'\n\n"
        f"Research findings:\n{research_brief}\n\n"
        f"Write a 400-600 word analytical report section addressing the research question. "
        f"Rules:\n"
        f"- Use ONLY the provided research findings — do not add external knowledge\n"
        f"- Cite sources inline as [task_id] (e.g., [t1], [t2]) after each claim\n"
        f"- Use clear paragraph structure: overview, key findings, implications\n"
        f"- End with a 2-3 sentence conclusion summarizing key takeaways\n"
        f"- Write in a professional, analytical tone"
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": write_prompt}],
    )
    draft = response.content[0].text.strip()
    word_count = len(draft.split())
    print(f"[Writer] Draft complete: {word_count} words")

    return {"draft_sections": [{"content": draft, "word_count": word_count}]}


# ─────────────────────────────────────────────
# Node: FactChecker Agent
# ─────────────────────────────────────────────

def fact_checker_node(state: ResearchState) -> dict:
    """
    Cross-reference the latest draft section's claims against raw research sources.
    Rates each claim as VERIFIED, PARTIALLY_SUPPORTED, or UNSUPPORTED.
    Limits to 5 most specific claims to keep token usage manageable.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    if not state["draft_sections"]:
        return {"fact_check_results": [{"error": "No draft to fact-check"}]}

    latest_draft = state["draft_sections"][-1]["content"]
    print(f"\n[FactChecker] Checking draft ({len(latest_draft.split())} words)...")

    # Build source reference for fact-checking
    source_parts = []
    for wr in state["web_results"]:
        source_parts.append(f"[{wr.get('task_id', 't1')}] Web: {wr.get('fact', '')}")
    for wiki in state["wiki_results"]:
        tid = wiki.get("task_id", "t2")
        for fact in wiki.get("facts", []):
            source_parts.append(f"[{tid}] Wikipedia: {fact}")
        for stat in wiki.get("stats", []):
            source_parts.append(f"[{tid}] Wikipedia stat: {stat}")
    sources_text = "\n".join(source_parts)

    check_prompt = (
        f"Draft text:\n{latest_draft[:1500]}\n\n"  # ← cap to avoid token overflow
        f"Source material:\n{sources_text}\n\n"
        f"For the 5 most specific factual claims in the draft, verify them against sources.\n"
        f"Rate each as: VERIFIED, PARTIALLY_SUPPORTED, or UNSUPPORTED.\n\n"
        f"Return ONLY valid JSON array:\n"
        f'[{{"claim": "exact claim from draft", "verdict": "VERIFIED", '
        f'"source_ref": "t1", "notes": "brief note"}}]'
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=600,
        messages=[{"role": "user", "content": check_prompt}],
    )

    raw = response.content[0].text.strip()
    try:
        start = raw.index("[")
        end = raw.rindex("]") + 1
        fact_check = json.loads(raw[start:end])
    except (json.JSONDecodeError, ValueError):
        fact_check = [{
            "claim": "Unable to parse fact check results",
            "verdict": "PARTIALLY_SUPPORTED",
            "source_ref": "none",
            "notes": "JSON parse error in fact checker",
        }]

    verified = sum(1 for f in fact_check if f.get("verdict") == "VERIFIED")
    unsupported = sum(1 for f in fact_check if f.get("verdict") == "UNSUPPORTED")
    print(f"[FactChecker] {verified} verified, {unsupported} unsupported out of {len(fact_check)} claims")
    return {"fact_check_results": fact_check}


# ─────────────────────────────────────────────
# Node: Supervisor — Synthesize
# ─────────────────────────────────────────────

def supervisor_synthesize_node(state: ResearchState) -> dict:
    """
    Produce the final Markdown report.
    Uses Claude to incorporate fact-check corrections: removes UNSUPPORTED claims,
    hedges PARTIALLY_SUPPORTED ones. Adds Sources and Research Notes sections.
    Saves to file and returns the Markdown text.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    print(f"\n[Supervisor] Synthesizing final report...")

    if state["worker_errors"]:
        print(f"[Supervisor] {len(state['worker_errors'])} worker error(s) to report:")
        for err in state["worker_errors"]:
            print(f"   - {err.get('worker', 'unknown')}: {err.get('error', 'unknown error')}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    draft = state["draft_sections"][-1]["content"] if state["draft_sections"] else "No content generated."
    fact_results = state["fact_check_results"]

    # Categorize fact-check results for the synthesis prompt
    unsupported = [f for f in fact_results if f.get("verdict") == "UNSUPPORTED"]
    partial = [f for f in fact_results if f.get("verdict") == "PARTIALLY_SUPPORTED"]

    # Build the synthesis prompt with correction instructions
    correction_notes = []
    if unsupported:
        correction_notes.append(f"REMOVE or add 'allegedly:' to these unsupported claims:")
        for f in unsupported:
            correction_notes.append(f"  - {f.get('claim', '')}")
    if partial:
        correction_notes.append(f"Hedge these partially supported claims:")
        for f in partial:
            correction_notes.append(f"  - {f.get('claim', '')} (Note: {f.get('notes', '')})")

    # Collect all source URLs
    sources = []
    for wr in state["web_results"]:
        if wr.get("source_url"):
            sources.append(f"- [{wr.get('task_id', 't1')}] {wr['source_url']}")
    for wiki in state["wiki_results"]:
        if wiki.get("url"):
            sources.append(f"- [{wiki.get('task_id', 't2')}] {wiki['url']} ({wiki.get('page_title', '')})")

    synth_prompt = (
        f"Produce a final polished Markdown research report.\n\n"
        f"Original draft:\n{draft}\n\n"
        + (f"Corrections needed:\n" + "\n".join(correction_notes) + "\n\n" if correction_notes else "")
        + f"Apply all corrections and output the final Markdown report with these sections:\n"
        f"1. ## Research Report: [question title]\n"
        f"2. *Generated: {timestamp}*\n"
        f"3. Report body (corrected draft)\n"
        f"4. ## Sources\n"
        f"5. ## Research Notes (limitations, data gaps, worker errors if any)\n\n"
        f"Sources to include:\n" + "\n".join(sources)
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": synth_prompt}],
    )
    final_report = response.content[0].text.strip()

    # Append worker error section if any failures occurred
    if state["worker_errors"]:
        error_notes = "\n".join(
            f"- {e.get('worker', 'unknown')}: {e.get('error', 'unknown')}"
            for e in state["worker_errors"]
        )
        final_report += f"\n\n### Data Collection Errors\n{error_notes}"

    # Save to timestamped file
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
    supervisor_plan ──> [parallel: web_researcher, data_analyst]
                     ──> writer ──> fact_checker ──> supervisor_synthesize ──> END

    The parallel branches converge on writer: LangGraph waits for ALL parallel
    branches to complete before advancing to writer, merging results via operator.add.
    """
    builder = StateGraph(ResearchState)

    builder.add_node("supervisor_plan", supervisor_plan_node)
    builder.add_node("web_researcher", web_researcher_node)
    builder.add_node("data_analyst", data_analyst_node)
    builder.add_node("writer", writer_node)
    builder.add_node("fact_checker", fact_checker_node)
    builder.add_node("supervisor_synthesize", supervisor_synthesize_node)

    builder.set_entry_point("supervisor_plan")

    # Conditional edge: supervisor_plan calls dispatch_workers which returns Send objects
    # LangGraph executes all Send objects simultaneously (true parallel execution)
    builder.add_conditional_edges("supervisor_plan", dispatch_workers)

    # Both parallel branches converge on writer
    # LangGraph waits for ALL parallel branches before running writer
    builder.add_edge("web_researcher", "writer")
    builder.add_edge("data_analyst", "writer")

    # Linear chain after research phase
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
