# Tech Stack
## Design Case 01: Customer Support Agent

Every technology choice is a tradeoff. This table documents what we chose, why, and what we would use instead under different constraints.

---

## Full Stack Table

| Component | Technology Choice | Why This Choice | Alternatives | When to Switch |
|---|---|---|---|---|
| **API Gateway** | Kong (self-hosted) or AWS API Gateway | Kong gives full control over rate limiting, auth plugins, and custom middleware. AWS API GW is simpler if you're already AWS-native. | nginx + custom auth, Traefik, Apigee | Switch to AWS API GW if you want managed infra and are already on AWS. Switch to Apigee for enterprise features (analytics, dev portal). |
| **Conversation Manager** | Python FastAPI | Fast async I/O for concurrent requests, native async support, excellent ecosystem for LLM/ML libraries. Type hints + Pydantic for validation. | Node.js (Express/Fastify), Go (Gin) | Go gives better throughput for very high QPS (>10K) but has less mature ML ecosystem. Node.js is fine but Python has better LLM library support. |
| **LLM** | Claude 3.5 Sonnet (Anthropic) | Best cost/quality ratio for conversational tasks. 200K context window, strong instruction following, good tool-calling reliability, $3/1M input. | GPT-4o, Gemini 1.5 Pro, Llama 3.1 70B | GPT-4o for slightly higher accuracy on complex reasoning. Llama 3.1 70B (self-hosted) if you have strict data privacy requirements and can run the GPU infrastructure. |
| **LLM for routing/classification** | Claude 3.5 Haiku / GPT-4o-mini | 10x cheaper than flagship models. Use for: intent classification, escalation detection, sentiment analysis. Don't use for final response generation. | Llama 3.1 8B (self-hosted), Mistral 7B | For very high volume classification, fine-tune a smaller model (BERT, DistilBERT) — 100x cheaper and sub-10ms latency. |
| **Embedding Model** | text-embedding-3-small (OpenAI) | 1536 dimensions, excellent quality, $0.02/1M tokens (extremely cheap). Widely tested. | text-embedding-ada-002, Cohere embed-v3, multilingual-e5-large | Switch to Cohere embed-v3 for better multilingual support. Switch to multilingual-e5-large if you need self-hosted/no-API-cost embeddings. |
| **Vector Store** | Pinecone (managed) | Fully managed, no infrastructure to run, excellent Python SDK, built-in metadata filtering, auto-scaling. | Weaviate (self-hosted), Qdrant, pgvector (Postgres extension), Chroma | Switch to Weaviate/Qdrant if you need self-hosted (data privacy). Switch to pgvector if your vector corpus is < 1M chunks and you want to simplify your infra stack to just Postgres. |
| **Relational Database** | PostgreSQL (AWS RDS) | ACID compliance for ticket/user data, excellent for the relational schema, mature ecosystem, AWS RDS gives managed backups/failover. | MySQL, CockroachDB | CockroachDB for multi-region active-active requirements. MySQL if your team has existing expertise. |
| **Session Cache** | Redis (AWS ElastiCache) | Sub-millisecond reads, native TTL support for session expiry, cluster mode for HA, pub/sub for escalation notifications. | Memcached, DynamoDB | Memcached if you only need simple key-value cache (no TTL control, no pub/sub). DynamoDB for serverless, but latency is higher (~10ms). |
| **Ticket System** | Zendesk (via REST API) | Industry standard, rich API, good agent UI, native escalation routing, CRM integrations. | Jira Service Management, Freshdesk, custom-built | Jira if your company already uses Jira for engineering (unified tooling). Build custom only if you need deep integration with proprietary systems. |
| **LLM Observability** | Langfuse (self-hosted) or LangSmith | Full LLM call tracing (input/output/tokens/latency), session grouping, evaluation pipelines, cost dashboard. Langfuse is open-source and self-hostable. | LangSmith (hosted), Helicone, Arize AI | LangSmith if you use LangChain heavily (tight integration). Helicone for a lightweight proxy-based solution with minimal code change. |
| **Infrastructure Observability** | Datadog | Unified metrics/traces/logs, excellent APM, pre-built LLM cost dashboards, alerting. | New Relic, Grafana + Prometheus, AWS CloudWatch | Grafana + Prometheus for cost savings if you have the DevOps bandwidth. CloudWatch if you're AWS-only and want to minimize tooling. |
| **Orchestration Framework** | LangChain (basic) or direct API calls | For this design, the tool-calling loop is simple enough that LangChain adds unnecessary abstraction. Prefer direct Anthropic/OpenAI API calls. | LangGraph, LlamaIndex | Use LangGraph if the tool-calling flow becomes complex (multi-step reasoning, parallel tool execution). Use LlamaIndex if your RAG pipelines become complex. |
| **Deployment** | AWS ECS (Fargate) or Kubernetes | Fargate for managed container orchestration without managing EC2 instances. Kubernetes if you need more control over scheduling and resource allocation. | AWS Lambda (serverless), Google Cloud Run | Lambda/Cloud Run for simple low-traffic deployments. For sustained high traffic, Fargate/K8s gives better cost at scale. |

---

## Key Architecture Decisions Explained

### Why not use an all-in-one LLM framework (like LangChain) for everything?

LangChain is excellent for prototyping but adds abstraction that hides what's actually happening. For production systems:

- The tool-calling loop in this design is 50 lines of direct API code. LangChain would add 3+ abstraction layers.
- When things break (wrong tool called, context assembled incorrectly), debugging LangChain abstractions is painful.
- LangChain's abstraction version-locks you — upgrading often breaks things.

**Rule of thumb:** Use LangChain's specific utilities you need (text splitters, document loaders, prompt templates) without adopting the full agent framework. Write the orchestration loop yourself.

### Why Pinecone instead of pgvector?

pgvector is a great choice for small to medium knowledge bases (< 1M vectors). Its advantages: one less database to manage, transactions span both relational and vector data, simpler ops.

**Switch to Pinecone (or Weaviate/Qdrant) when:**
- You exceed ~5M vectors (pgvector query performance degrades without significant tuning)
- You need sub-100ms P99 at high QPS
- You want built-in managed scaling without DBA involvement

For this design with 500K chunks and >1,000 QPS peak, Pinecone is the right call.

### Why Claude 3.5 Sonnet over GPT-4o?

At time of design, Claude 3.5 Sonnet offers:
- Comparable response quality for conversational/support tasks
- 200K context window vs GPT-4o's 128K (future-proofing for long conversation support)
- Lower cost: $3/1M input vs $5/1M input for GPT-4o
- Anthropic's constitutional AI training tends to produce better adherence to "don't answer what you don't know" instructions — reducing hallucination in support contexts

**The right answer in any interview:** Don't be dogmatic. Benchmark both on your actual queries and pick the one with better quality at your price point. The architecture is model-agnostic — you can swap LLMs by changing one config variable.

---

## Cost Model Summary

| Item | Unit Cost | Daily Volume | Daily Cost |
|---|---|---|---|
| Claude 3.5 Sonnet (input) | $3/1M tokens | 175M tokens (50K turns × 3,500 tokens) | $525 |
| Claude 3.5 Sonnet (output) | $15/1M tokens | 25M tokens (50K turns × 500 tokens) | $375 |
| text-embedding-3-small | $0.02/1M tokens | 2.5M tokens (50K queries × 50 tokens) | $0.05 |
| Pinecone (p2.x1 pod) | $0.096/hr | 24 hours | $2.30 |
| AWS RDS Postgres (db.r6g.large) | ~$0.24/hr | 24 hours | $5.76 |
| AWS ElastiCache Redis | ~$0.10/hr | 24 hours | $2.40 |
| Langfuse (self-hosted on ECS) | ~$0.05/hr | 24 hours | $1.20 |
| **Total** | | | **~$912/day** |

With **40% semantic cache hit rate** on FAQ queries: **~$550/day**

With **model tiering** (20% of simple queries routed to Haiku at $0.25/1M input): **~$480/day**

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

⬅️ **Prev:** [09 Scaling AI Apps](../../12_Production_AI/09_Scaling_AI_Apps/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 RAG Document Search System](../02_RAG_Document_Search_System/Architecture_Blueprint.md)
