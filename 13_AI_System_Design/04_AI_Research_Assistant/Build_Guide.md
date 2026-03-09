# Build Guide
## Design Case 04: AI Research Assistant

Four phases from a single-source search agent to a full multi-agent research system with conflict detection and credibility scoring.

---

## Phase 1: Single-Agent Web Research (Week 1-2)

**Goal:** An agent that can search the web for a topic, extract content from pages, and summarize findings. One agent, one source type.

**What you build:**
- `POST /research` endpoint: accepts research question, returns summary
- Web search tool (Serper API)
- URL content extractor (trafilatura)
- Single LLM call to synthesize findings

**Serper API (Google Search programmatically):**
```python
import requests

def web_search(query: str, num_results: int = 5) -> list[dict]:
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_API_KEY},
        json={"q": query, "num": num_results}
    )
    results = response.json()["organic"]
    return [{"title": r["title"], "url": r["link"], "snippet": r["snippet"]} for r in results]
```

**Content extraction with trafilatura:**
```python
import trafilatura

def extract_page_content(url: str) -> str | None:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    text = trafilatura.extract(downloaded, include_comments=False, include_tables=True)
    return text[:5000] if text else None  # Limit to 5K chars
```

**Simple research loop:**
```python
async def research(question: str) -> str:
    # 1. Generate search queries from the question
    queries = await generate_search_queries(question, num_queries=3)

    # 2. Search and extract content for each query
    all_content = []
    for query in queries:
        results = web_search(query, num_results=3)
        for result in results:
            content = extract_page_content(result["url"])
            if content:
                all_content.append({"url": result["url"], "title": result["title"], "content": content})

    # 3. Synthesize
    synthesis_prompt = f"""Based on the following sources, answer this question: {question}

Sources:
{format_sources(all_content)}

Provide a structured answer with citations [1], [2], etc.
List all sources at the end."""

    return await llm.generate(synthesis_prompt)
```

**Success criteria:** Can answer a research question with 3-5 cited sources in under 30 seconds.

---

## Phase 2: Academic Paper Integration (Week 3)

**Goal:** Add arXiv and Semantic Scholar for academic questions. The agent selects the right source type based on the question.

**arXiv API integration:**
```python
import arxiv

def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    papers = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [str(a) for a in result.authors],
            "summary": result.summary,
            "url": result.pdf_url,
            "published": str(result.published),
            "categories": result.categories
        })
    return papers
```

**Semantic Scholar API for citation data:**
```python
import requests

def get_paper_citations(paper_title: str) -> dict:
    response = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={
            "query": paper_title,
            "fields": "title,year,citationCount,authors,abstract",
            "limit": 1
        }
    )
    data = response.json()
    if data.get("data"):
        return data["data"][0]
    return {}
```

**Source type routing:**
Add this to the planner:
```python
def route_query_to_agents(sub_question: str) -> list[str]:
    """Determine which agents should handle this sub-question."""
    academic_keywords = ["study", "research", "paper", "evidence", "efficacy", "mechanism", "clinical"]
    web_keywords = ["latest", "news", "company", "product", "tutorial", "how to", "price"]

    agents = []
    question_lower = sub_question.lower()

    if any(kw in question_lower for kw in academic_keywords):
        agents.append("academic")
    if any(kw in question_lower for kw in web_keywords) or not agents:
        agents.append("web")

    return agents if agents else ["web", "academic"]  # Default: both
```

**Success criteria:** Academic questions (research methodology, scientific findings) use paper sources with citation counts. Current events questions use web sources with recency filters.

---

## Phase 3: Research Planner + Parallel Sub-Agents (Week 4-5)

**Goal:** The orchestrator breaks the research question into sub-questions and runs agents in parallel.

**Research Planner implementation with LangGraph:**
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class ResearchState(TypedDict):
    question: str
    sub_questions: list[str]
    plan_approved: bool
    findings: Annotated[list, operator.add]  # Aggregated from parallel agents
    conflicts: list[dict]
    report: str

# Define the graph
workflow = StateGraph(ResearchState)

workflow.add_node("planner", plan_research)
workflow.add_node("human_review", human_plan_review)
workflow.add_node("web_agent", run_web_search_agent)
workflow.add_node("paper_agent", run_paper_search_agent)
workflow.add_node("synthesizer", synthesize_report)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "human_review")
workflow.add_conditional_edges(
    "human_review",
    lambda state: "continue" if state["plan_approved"] else "revise",
    {"continue": "web_agent", "revise": "planner"}
)
# web_agent and paper_agent run in parallel (LangGraph handles this)
workflow.add_edge("web_agent", "synthesizer")
workflow.add_edge("paper_agent", "synthesizer")
workflow.add_edge("synthesizer", END)

app = workflow.compile()
```

**Running sub-agents in parallel:**
LangGraph's `send` mechanism dispatches parallel sub-graph executions. Each sub-question gets its own agent invocation, all running concurrently.

**Success criteria:** A complex question like "What are the effects of sleep deprivation on cognitive performance?" decomposes into 4 sub-questions, runs 4 agents in parallel, and returns a report in ~45 seconds instead of ~3 minutes sequentially.

---

## Phase 4: Conflict Detection and Credibility Scoring (Week 6-8)

**Goal:** The report explicitly surfaces when sources disagree and weights evidence by source quality.

**Conflict Detection implementation:**
```python
async def detect_conflicts(findings: list[dict]) -> list[dict]:
    """Find contradictions between findings from different sources."""

    # Group findings by sub-question / topic
    grouped = group_findings_by_topic(findings)

    conflicts = []
    for topic, topic_findings in grouped.items():
        if len(topic_findings) < 2:
            continue

        # Use LLM to compare claims
        conflict_check_prompt = f"""
You are analyzing research findings on the same topic from different sources.
Identify any direct contradictions or significant disagreements.

Topic: {topic}

Findings:
{format_findings_for_comparison(topic_findings)}

Return a JSON list of conflicts found. For each conflict:
- claim_a: first claim (with source)
- claim_b: contradicting claim (with source)
- severity: "minor" | "major"
- explanation: why these claims conflict
"""
        response = await llm.generate(conflict_check_prompt, response_format="json")
        detected_conflicts = json.loads(response)
        conflicts.extend(detected_conflicts)

    return conflicts
```

**Credibility scoring:**
```python
def score_source_credibility(source: dict) -> int:
    score = 50  # Base score for any web source

    # Source type bonus
    if source["type"] == "academic":
        score = 85
    elif source["type"] == "wikipedia":
        score = 60

    # Citation count (academic papers only)
    citations = source.get("citation_count", 0)
    if citations > 100:
        score += 10
    elif citations > 10:
        score += 5

    # Recency
    age_years = (datetime.now().year - source.get("year", datetime.now().year))
    if age_years < 1:
        score += 5
    elif age_years > 5:
        score -= 15

    # Domain authority heuristics
    domain = extract_domain(source["url"])
    if domain.endswith(".edu") or domain.endswith(".gov"):
        score += 10
    if domain in TRUSTED_NEWS_DOMAINS:
        score += 5
    if domain in KNOWN_LOW_QUALITY_DOMAINS:
        score -= 20

    return max(0, min(100, score))
```

**Including conflict sections in the report:**
When conflicts are detected, the synthesizer adds a section:
```
## Conflicting Evidence

On the question of [topic], sources disagree:

- [Source A, credibility 85]: Claims X
- [Source B, credibility 72]: Claims Y

This is a MAJOR conflict. Source A is a 2024 peer-reviewed paper with 45 citations.
Source B is a 2022 blog post. On balance, Source A's position is better supported.
```

**Success criteria:** Reports on contested topics (nutrition science, AI capability claims) include conflict sections with source credibility justification, not just one-sided synthesis.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| 📄 **Build_Guide.md** | ← you are here |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Multi-Agent Workflow](../05_Multi_Agent_Workflow/Architecture_Blueprint.md)
