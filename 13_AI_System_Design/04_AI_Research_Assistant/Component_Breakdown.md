# Component Breakdown
## Design Case 04: AI Research Assistant

The challenging components in this design are orchestration (managing multiple agents without losing control), deduplication (identifying overlapping content from different sources), and conflict detection (identifying when sources contradict each other).

---

## 1. Research Planner (Orchestrator Agent)

The planner is the most important component. It determines the quality of the research by how well it decomposes the question.

**What makes a good research plan:**

A bad decomposition: "What is AI?" → ["What is artificial intelligence?", "History of AI", "Types of AI"]
These are too broad and don't lead to a focused, answerable report.

A good decomposition: "What are the most effective approaches to reducing LLM hallucination?" →
1. "What are the primary causes of factual hallucination in transformer language models?"
2. "What retrieval-augmented generation (RAG) techniques have been shown to reduce hallucination rates, and by how much?"
3. "What non-RAG approaches (RLHF, Constitutional AI, fine-tuning) reduce hallucination, and what are their limitations?"
4. "What evaluation benchmarks exist for measuring hallucination rates, and what do state-of-the-art models score?"
5. "What production deployments have published results on hallucination reduction strategies?"

**System prompt for the planner:**
```
You are a research strategist. Your job is to decompose a complex research question
into 3-6 specific sub-questions that:
1. Together, fully answer the original question when synthesized
2. Are independently searchable (each maps to clear search queries)
3. Are specific enough to yield focused results (not "what is X" but "how does X affect Y")
4. Cover different aspects (mechanisms, evidence, real-world applications, limitations)

For each sub-question, specify:
- The sub-question text
- Whether to search: web, academic, or both
- Suggested search query for each source type
- Why this sub-question is important to the overall question
```

**Why the planner runs before agents start:**
The plan is shown to the user for approval. The user can: add a sub-question ("also research cost implications"), remove one ("I don't need history"), or modify one ("focus on recent papers from 2022 onwards"). This human checkpoint prevents the entire research session from going in the wrong direction before spending 30+ LLM API calls.

---

## 2. Sub-Agent Pool

Each sub-agent is a specialized instance of the same underlying pattern: receive a sub-question → generate search queries → execute searches → extract content → return structured findings.

**Web Search Agent internals:**

```
Sub-question → Generate 2-3 Google queries (using LLM)
             → Execute Serper API searches (parallel, 3 queries × 5 results = 15 URLs)
             → Filter: remove paywalls, social media, spam
             → Extract content from top 5 URLs (trafilatura)
             → Extract: title, date, author, content, URL
             → Return: list of {source_info, extracted_text}
```

**Why generate multiple queries per sub-question?**
One query misses relevant results due to phrasing. "RAG reduces hallucination" and "retrieval augmented generation accuracy improvement" will return different URLs. Running both and merging results increases recall significantly.

**Academic Paper Agent internals:**

```
Sub-question → Generate academic search terms
             → Search arXiv API (keyword search)
             → Search Semantic Scholar API (add citation count data)
             → Merge and deduplicate by title/DOI
             → For open-access papers: download PDF and extract text
             → For restricted papers: use abstract only
             → Return: list of {paper_metadata, abstract_or_full_text, citation_count}
```

**Rate limiting and retry logic:**
arXiv and Semantic Scholar have rate limits (arxiv: 3 req/sec, Semantic Scholar: 100 req/5 min). Each agent implements:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def search_arxiv_with_retry(query: str) -> list:
    return await search_arxiv(query)
```

**Agent failure handling:**
If the web search agent fails (Serper API down, rate limit exceeded), the orchestrator should:
1. Try once more after 5 seconds
2. If still failing: mark this sub-question as "search failed", proceed with available data
3. Note in the report: "Web search for sub-question 3 failed. This aspect of the report relies on academic sources only."

Never let one failed sub-agent block the entire research job.

---

## 3. Deduplication Service

When 5 sub-agents each return 5-10 sources on related topics, you get significant overlap. Two agents both retrieve the same landmark paper. Three web sources all cite the same blog post. Deduplication prevents the synthesizer from repeating the same claim five times.

**Two levels of deduplication:**

**Exact deduplication:** Simple URL matching + title matching (with normalization). A paper retrieved by both the arXiv agent and the Semantic Scholar agent has the same DOI — trivial to detect.

**Semantic deduplication (the hard part):**
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def deduplicate_by_content(findings: list[dict]) -> list[dict]:
    """Remove findings that are too similar to already-seen findings."""
    embeddings = model.encode([f["content"][:500] for f in findings])
    deduplicated = []
    seen_embeddings = []

    for i, finding in enumerate(findings):
        if not seen_embeddings:
            deduplicated.append(finding)
            seen_embeddings.append(embeddings[i])
            continue

        # Check similarity against all already-seen findings
        similarities = np.dot(seen_embeddings, embeddings[i]) / (
            np.linalg.norm(seen_embeddings, axis=1) * np.linalg.norm(embeddings[i])
        )
        if max(similarities) < 0.92:  # Threshold: >0.92 cosine = probably duplicate
            deduplicated.append(finding)
            seen_embeddings.append(embeddings[i])

    return deduplicated
```

After deduplication, store all unique findings in Chroma (in-memory vector store) for the synthesizer to query against.

---

## 4. Conflict Detection

This is the component that differentiates a sophisticated research assistant from a simple summarizer. Summarizers hide contradictions. A research assistant surfaces them.

**How conflict detection works:**

```
Step 1: Group all findings by the topic they address (using LLM clustering)

Step 2: For each topic with 2+ findings from different sources:
    - Extract the specific factual claims made in each finding
    - Compare claims using LLM as judge

Step 3: For each detected conflict:
    - Classify severity: minor (nuanced disagreement) vs major (direct contradiction)
    - Apply credibility scores: which source has higher authority?
    - Generate explanation: why do these sources disagree? (different time periods? different methodologies? different definitions?)

Step 4: Include conflicts in the final report with full attribution
```

**Example conflict detection prompt:**
```
You are a fact-checking assistant analyzing research findings.

These two sources make claims about the same topic:

Source A (arXiv paper, 2024, 120 citations):
"RAG-based approaches reduce hallucination rates by 37-42% on the TruthfulQA benchmark
compared to non-augmented models."

Source B (Blog post, 2023):
"RAG doesn't actually fix hallucination — the LLM still makes up citations
and misinterprets retrieved documents. It's not a reliable solution."

Do these sources contradict each other? If yes:
1. What is the contradiction?
2. Is it a direct factual contradiction or a difference in framing/scope?
3. How can both be true simultaneously? (different conditions, definitions, or scope)
4. Which source's claim is more reliable based on the evidence provided?
```

The LLM might respond: "Both can be true. Source A measures a specific benchmark (TruthfulQA) under controlled conditions. Source B describes observed behavior in production deployment. Hallucination reduction in benchmarks does not guarantee elimination in real-world use. This is a framing conflict, not a factual contradiction, though it represents genuinely different conclusions for different contexts."

This is more useful than either source in isolation.

---

## 5. Report Synthesizer

The synthesizer receives: all deduplicated findings, conflict analysis, and credibility scores. It produces a structured report.

**Synthesis prompt structure:**
```
You are a research synthesizer. You will write a structured research report based on
the following collected evidence.

CRITICAL RULES:
1. Only make claims that are supported by the provided sources
2. Use inline citations: [Source 1], [Source 2]
3. When sources disagree, present both views and note the disagreement
4. Distinguish between strong evidence (peer-reviewed, high citations) and weak evidence (blog posts)
5. Do not express personal opinions

Research question: {original_question}

Collected evidence (sorted by credibility score):
{formatted_findings}

Identified conflicts:
{formatted_conflicts}

Write a structured report with these sections:
1. Executive Summary (3-5 sentences)
2. Key Findings (bullet points, each citing sources)
3. Detailed Analysis (expanded sections for each major finding)
4. Conflicting Evidence (if any conflicts detected)
5. Limitations and Gaps (what this research didn't cover)
6. References (full source list with credibility scores)
```

**Report format (Markdown output):**
The report is returned as Markdown with a collapsible source list. Each citation links back to the original URL. Conflict sections are visually highlighted. Credibility scores are shown in the references section: "⭐⭐⭐⭐⭐ Academic (97 citations)" vs "⭐⭐ Web article".

---

## 6. LangGraph for Orchestration

LangGraph is a stateful graph execution framework built on top of LangChain. It's the right tool for this system because:

- **Explicit state management:** The `ResearchState` TypedDict defines exactly what data flows between agents. No implicit state, no hidden side effects.
- **Conditional routing:** After plan review, the graph conditionally routes to "continue" or "revise" based on user approval.
- **Parallel execution:** LangGraph's `send` mechanism dispatches sub-agents to run concurrently, not sequentially. A research plan with 4 sub-questions runs 4 agents simultaneously.
- **Checkpointing:** LangGraph can checkpoint the state after each node. If the system crashes mid-research (an agent fails, timeout), it can resume from the last checkpoint rather than starting over.
- **Human-in-the-loop:** LangGraph's `interrupt` mechanism pauses execution at designated nodes (plan review, source review) and waits for human input before continuing.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| 📄 **Component_Breakdown.md** | ← you are here |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Multi-Agent Workflow](../05_Multi_Agent_Workflow/Architecture_Blueprint.md)
