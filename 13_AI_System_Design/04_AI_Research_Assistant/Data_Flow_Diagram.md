# Data Flow Diagram
## Design Case 04: AI Research Assistant

Two flows: the main research flow from question to report (with parallel sub-agents and human checkpoints), and the synthesis flow (how collected evidence becomes a structured report).

---

## Main Research Flow

```mermaid
sequenceDiagram
    actor User
    participant Planner as Research Planner
    participant HP1 as Human Checkpoint 1\n(Plan Review)
    participant WebAgent as Web Search Agent
    participant PaperAgent as Paper Search Agent
    participant WikiAgent as Wikipedia Agent
    participant HP2 as Human Checkpoint 2\n(Source Review, optional)
    participant Synth as Synthesis Layer
    participant DB as PostgreSQL

    User->>Planner: "What are the effects of intermittent fasting on metabolic health?"

    Planner->>Planner: Generate research plan\n4 sub-questions\nAgent routing for each

    Planner->>HP1: Present research plan to user\n"Here's my plan. Approve or modify?"
    HP1-->>User: Show plan with sub-questions
    User-->>HP1: "Add: focus on type 2 diabetes specifically"
    HP1->>Planner: Updated plan (5 sub-questions)

    Note over Planner: Plan approved. Dispatch agents in parallel.

    par Parallel Agent Execution
        Planner->>WebAgent: Sub-question 1, 2 (web sources)
        WebAgent->>WebAgent: Generate 3 search queries each
        WebAgent->>WebAgent: Serper API search (15 results each)
        WebAgent->>WebAgent: Extract content from top 5 URLs
        WebAgent-->>Planner: 10 web findings with metadata
    and
        Planner->>PaperAgent: Sub-question 2, 3, 4 (academic)
        PaperAgent->>PaperAgent: arXiv search + Semantic Scholar
        PaperAgent->>PaperAgent: Retrieve abstracts + citation counts
        PaperAgent-->>Planner: 12 paper findings with citation data
    and
        Planner->>WikiAgent: Sub-question 1 (factual grounding)
        WikiAgent->>WikiAgent: Wikipedia API lookup
        WikiAgent-->>Planner: 2 structured Wikipedia sections
    end

    Planner->>Planner: Merge all findings (24 total)
    Planner->>Planner: Exact deduplication (remove 4 duplicates)
    Planner->>Planner: Semantic deduplication (remove 2 near-duplicates)
    Planner->>Planner: Score credibility for remaining 18 sources

    Planner->>HP2: Optional: "Here are 18 sources. Add/remove before synthesis?"
    HP2-->>User: Show source list with credibility scores
    User-->>HP2: "Remove source X (paywalled), add this URL"
    HP2->>Planner: Adjusted source list

    Planner->>Synth: 17 sources + credibility scores
    Synth->>Synth: Conflict detection across sources
    Synth->>Synth: Generate structured report with citations
    Synth->>DB: Save report + research session

    Synth-->>User: Structured research report (Markdown)\n~1,500-3,000 words\nWith citations and conflict sections
```

---

## Parallel Sub-Agent Detail (Zoomed In)

Each sub-agent runs this internal flow independently and concurrently.

```mermaid
flowchart TD
    SQ["Sub-question input\n'What does clinical research show\nabout IF and insulin sensitivity?'"]

    QG["Query Generation (LLM)\nGenerate 3 search queries:\n1. 'intermittent fasting insulin sensitivity clinical trial'\n2. 'time-restricted eating glucose metabolism RCT'\n3. 'IF metabolic effects type 2 diabetes evidence'"]

    Search["Parallel Search Execution\n3 queries × {web/academic}"]

    subgraph WebPath["Web Path"]
        W1["Serper API\n5 results per query = 15 URLs"]
        W2["Filter URLs\nRemove: paywalls, social media, spam"]
        W3["trafilatura extraction\nTop 5 URLs → text content"]
    end

    subgraph AcademicPath["Academic Path"]
        A1["arXiv API\n5 papers per query"]
        A2["Semantic Scholar\ncitation counts, DOIs"]
        A3["Merge + deduplicate\nby DOI / title similarity"]
    end

    Format["Format Findings\n{source_type, url, title, date, content, citation_count}"]
    Score["Credibility Scoring\nRules-based: type + domain + recency + citations"]
    Return["Return to Orchestrator\nList of scored findings"]

    SQ --> QG
    QG --> Search
    Search --> W1
    Search --> A1
    W1 --> W2
    W2 --> W3
    A1 --> A2
    A2 --> A3
    W3 --> Format
    A3 --> Format
    Format --> Score
    Score --> Return
```

---

## Synthesis Flow (Detailed)

How 18 raw findings become a coherent research report.

```mermaid
flowchart TD
    Findings["18 Scored Findings\nfrom all sub-agents"]

    Chroma["Store in Chroma\n(in-memory vector store)\nFor semantic grouping"]

    Group["Topic Clustering (LLM)\nGroup findings by the\ntopic they address"]

    subgraph ConflictDetection["Conflict Detection (per topic group)"]
        Compare["Compare claims\nwithin each group"]
        Classify["Classify: minor / major\nContradict or complement?"]
        Explain["Explain conflict:\ndifferent conditions?\ndifferent definitions?"]
    end

    Synthesis["Report Synthesis (LLM)\nAll findings + conflicts + credibility scores\n→ Structured Markdown report"]

    subgraph Report["Final Report Structure"]
        Exec["Executive Summary"]
        Key["Key Findings (cited)"]
        Detail["Detailed Analysis"]
        Conflicts["Conflicting Evidence"]
        Gaps["Limitations & Gaps"]
        Refs["References (with scores)"]
    end

    Findings --> Chroma
    Chroma --> Group
    Group --> Compare
    Compare --> Classify
    Classify --> Explain
    Explain --> Synthesis
    Findings --> Synthesis
    Synthesis --> Exec
    Synthesis --> Key
    Synthesis --> Detail
    Synthesis --> Conflicts
    Synthesis --> Gaps
    Synthesis --> Refs
```

---

## Token Budget for the Full Research Session

A typical research session with 4 sub-questions and 18 sources:

```
Planning phase:
- Planner call (question → plan): ~1,500 tokens in, ~500 tokens out
- Total: 2,000 tokens

Sub-agent execution (per agent, per sub-question):
- Query generation: ~300 tokens in, ~100 out = 400 tokens
- × 4 sub-questions × 1.5 agents average = ~2,400 tokens

Conflict detection:
- ~800 tokens per topic pair × 4 topic groups = ~3,200 tokens

Synthesis (the big one):
- 18 sources × ~400 tokens average = 7,200 tokens context
- System prompt + instructions: ~800 tokens
- Output (2,000-word report): ~2,500 tokens
- Total synthesis call: ~10,500 tokens

Approximate session total:
Input: ~18,000 tokens × $3/1M = $0.054
Output: ~5,000 tokens × $15/1M = $0.075
Total per research session: ~$0.13
```

This is remarkably cheap for a research session that would take a human researcher 2-4 hours. The economics make it viable even for individual use at low scale.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| 📄 **Data_Flow_Diagram.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Tech_Stack.md](./Tech_Stack.md) | Technology stack choices |

⬅️ **Prev:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Multi-Agent Workflow](../05_Multi_Agent_Workflow/Architecture_Blueprint.md)
