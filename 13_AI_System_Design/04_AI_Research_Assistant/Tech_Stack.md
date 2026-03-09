# Tech Stack
## Design Case 04: AI Research Assistant

Technology choices for the multi-agent orchestration layer, search integrations, content extraction, and synthesis components.

---

## Full Stack Table

| Component | Technology Choice | Why This Choice | Alternatives | When to Switch |
|---|---|---|---|---|
| **Orchestration Framework** | LangGraph | Stateful graph execution, explicit state management, native parallel execution, checkpoint/resume support, human-in-the-loop interrupts, built by the LangChain team. | CrewAI, AutoGen, custom async Python | CrewAI for simpler role-based setups (less graph complexity). AutoGen for dynamic agent creation. Custom Python if you need maximum control and LangGraph's abstractions are limiting you. |
| **Orchestrator LLM (Planner)** | Claude 3.5 Sonnet | Strong at decomposing complex questions, good at following structured output formats (JSON research plans), reliable function calling. | GPT-4o, Claude 3 Opus | GPT-4o for comparable quality. Claude 3 Opus if you need maximum reasoning depth for complex academic topics. |
| **Sub-Agent LLM** | Claude 3.5 Haiku | Query generation and search query formulation doesn't require the most powerful model. 10x cheaper, fast. | GPT-4o-mini | GPT-4o-mini for equivalent speed and quality at comparable cost. |
| **Synthesis LLM** | Claude 3.5 Sonnet | Synthesis requires high-quality reasoning, proper handling of conflicting sources, and coherent multi-thousand-word generation. Quality matters here. | GPT-4o | GPT-4o is comparable. For very long-form synthesis (>5,000 words), both work well. |
| **Web Search API** | Serper API (Google search) | Real Google results, simple REST API, $50/month for 10K searches, JSON output with snippets. | Bing Web Search API (Azure), SerpAPI, Brave Search API | Bing API for Microsoft Azure integration. Brave Search for privacy-respecting results without personalization. SerpAPI for multi-engine support (Google + Bing + DuckDuckGo). |
| **Web Content Extraction** | trafilatura | Best open-source article extractor. Removes boilerplate (ads, navigation, footers), preserves article text and tables. Faster than BeautifulSoup for article extraction. | BeautifulSoup + html2text, Playwright (JS sites), Diffbot API | Playwright for JavaScript-rendered content (SPAs). Diffbot for high-quality extraction with structured data (paid, $299/month). |
| **Academic Paper Search** | arXiv API + Semantic Scholar API | arXiv: largest preprint server for CS/ML/physics/math. Semantic Scholar: citation data + cross-publisher search. Both free. | PubMed API (biomedical), Elsevier API (paid), Google Scholar (unofficial) | PubMed for biomedical/clinical research. Combine all three for comprehensive coverage. |
| **In-Session Vector Store** | Chroma (in-memory) | Ephemeral per-session storage of research findings for semantic dedup. Lightweight, Python-native, no external service. | FAISS (in-memory), Qdrant (persistent) | FAISS for slightly better performance at large in-session document counts (>10K). Qdrant for persistent multi-session knowledge accumulation. |
| **Persistent Storage** | PostgreSQL | Store completed reports, user sessions, research history. Standard relational storage for structured metadata. | MongoDB, DynamoDB | MongoDB for flexible schema if report structures vary significantly. DynamoDB for serverless/auto-scaling. |
| **Task Queue** | Celery + Redis (or AWS SQS) | Research sessions are async jobs (2-5 minutes). Celery manages worker pools for parallel agent execution, retry logic, and task status tracking. | Dramatiq, AWS SQS + Lambda, Temporal | Temporal for more complex workflow management with durable execution (state persists through crashes without explicit checkpointing). |
| **Source Credibility** | Custom Python rules engine | Domain scoring, citation count lookup, recency rules. Simple deterministic logic that doesn't require an LLM. | LLM-as-judge (expensive), trained ML classifier | LLM-as-judge for more nuanced credibility assessment on borderline sources. Custom ML classifier if you have training data from human-labeled source quality. |
| **Deduplication** | sentence-transformers + numpy | Semantic similarity computation for near-duplicate detection. `all-MiniLM-L6-v2` is fast (~10ms on CPU per embedding) and good quality. | OpenAI embeddings (API cost per dedup), universal-sentence-encoder | OpenAI embeddings for consistent quality with the rest of the pipeline. Universal Sentence Encoder for speed without external API. |
| **API Layer** | FastAPI (Python) | Async WebSocket support for streaming research progress to frontend, Pydantic validation, Python ecosystem. | Node.js, Django | Node.js for TypeScript consistency. Django for batteries-included features if you need auth, admin, etc. |
| **Frontend** | React + WebSockets | Real-time progress streaming (agent status, findings as they arrive), Markdown rendering for reports. | Next.js, Vue.js | Next.js for SSR + better SEO if the reports are public-facing. |

---

## LangGraph vs CrewAI vs AutoGen Decision Guide

This is a common decision point for multi-agent systems. Here's how to choose:

| Criteria | LangGraph | CrewAI | AutoGen |
|---|---|---|---|
| **State management** | Explicit TypedDict state, full control | Implicit (passed via crew context) | Conversation-based, less structured |
| **Graph complexity** | Excellent for complex branching workflows | Good for linear/parallel pipelines | Better for dynamic agent creation |
| **Human-in-the-loop** | Native `interrupt` mechanism | Requires custom implementation | Built-in human proxy agent |
| **Debugging** | Good (explicit state at each step) | Moderate | Harder (conversational trace) |
| **Checkpointing/resume** | Native (MemorySaver, external backends) | Requires custom implementation | Limited |
| **Learning curve** | Steeper (graph mental model) | Easier (role-based, intuitive) | Medium |
| **Best for** | Complex stateful workflows, production systems | Simpler multi-agent collaborations, prototypes | Research, dynamic agent networks |

**For this design:** LangGraph wins because the research workflow has conditional branches (plan review → revise or continue), parallel execution requirements, and human interrupts. These are LangGraph's strengths.

---

## Search API Comparison

| API | Cost | Rate Limit | Quality | Coverage |
|---|---|---|---|---|
| Serper (Google) | $50/10K queries | 100 QPS | Excellent (Google's index) | Web + News + Scholar |
| Bing Web Search | $3/1K queries | 1,000 QPS | Very Good | Web + News |
| Brave Search | $3/1K queries | Custom | Good | Privacy-respecting index |
| SerpAPI | $75/5K queries | 100 QPS | Excellent (multi-engine) | Google + Bing + DDG |
| Exa (ex-Metaphor) | $5/1K queries | Custom | Excellent for AI content | Neural search, great for AI/tech topics |

**Recommendation for this system:**
- Primary: Serper (Google quality, best cost)
- Academic: arXiv + Semantic Scholar (both free)
- For AI/tech research specifically: Exa.ai produces notably better results for AI-domain queries

---

## Cost Model

For a typical research session (4 sub-questions, 18 sources, 2,000-word report):

| Phase | LLM Calls | Input Tokens | Output Tokens | Cost |
|---|---|---|---|---|
| Planning | 1 | 500 | 400 | $0.008 |
| Sub-agent query gen | 5 | 1,500 | 300 | $0.007 |
| Conflict detection | 4 | 3,200 | 800 | $0.022 |
| Synthesis | 1 | 10,000 | 2,500 | $0.068 |
| **Total LLM** | | | | **$0.105** |

| Phase | API Calls | Cost |
|---|---|---|
| Serper searches | 12 | $0.06 |
| arXiv/Semantic Scholar | free | $0 |
| trafilatura extraction | local | $0 |
| **Total APIs** | | **$0.06** |

**Total cost per research session: ~$0.17**

At 10,000 research sessions/month: ~$1,700/month in variable costs + fixed infrastructure (~$500/month). Total: **~$2,200/month** to power a research assistant handling 10K reports/month. That's $0.22 per report — viable for a $20-50/month SaaS product.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | System architecture blueprint |
| [📄 Build_Guide.md](./Build_Guide.md) | Step-by-step build guide |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component breakdown |
| [📄 Data_Flow_Diagram.md](./Data_Flow_Diagram.md) | Data flow diagram |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Tech_Stack.md** | ← you are here |

⬅️ **Prev:** [03 AI Coding Assistant](../03_AI_Coding_Assistant/Architecture_Blueprint.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Multi-Agent Workflow](../05_Multi_Agent_Workflow/Architecture_Blueprint.md)
