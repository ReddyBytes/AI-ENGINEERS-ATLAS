# AI System Production Readiness Checklist

> Use this before shipping any AI feature to production. Each item links to the section that covers it in depth.

---

## 1. Data & Model Foundation

- [ ] Training data is documented — sources, licenses, known biases, and cutoff date (→ [Section 07: LLMs](./07_Large_Language_Models/Readme.md))
- [ ] Tokenization behavior tested at context limit boundaries — no silent truncation (→ [Section 07: Context Windows and Tokens](./07_Large_Language_Models/07_Context_Windows_and_Tokens/Theory.md))
- [ ] Embedding model version is pinned — drift in embeddings breaks retrieval silently (→ [Section 08: Embeddings](./08_LLM_Applications/04_Embeddings/Theory.md))
- [ ] Fine-tuned model evaluated on a held-out set that reflects production distribution (→ [Section 14: Trainer API](./14_Hugging_Face_Ecosystem/05_Trainer_API/Theory.md))
- [ ] Model card reviewed — capabilities, limitations, and known failure modes understood (→ [Section 14: Hub and Model Cards](./14_Hugging_Face_Ecosystem/01_Hub_and_Model_Cards/Theory.md))
- [ ] Quantization impact measured — latency gain vs accuracy loss tradeoff documented (→ [Section 14: Inference Optimization](./14_Hugging_Face_Ecosystem/06_Inference_Optimization/Theory.md))
- [ ] Local vs hosted model decision justified — cost, latency, privacy, and compliance considered (→ [Section 07: Ollama Local LLMs](./07_Large_Language_Models/10_Ollama_Local_LLMs/Theory.md))

---

## 2. Evaluation & Testing

- [ ] Baseline eval scores recorded before any change — no blind deploys (→ [Section 18: Evaluation Fundamentals](./18_AI_Evaluation/01_Evaluation_Fundamentals/Theory.md))
- [ ] Eval set covers failure modes, not just happy-path inputs (→ [Section 18: Red Teaming](./18_AI_Evaluation/06_Red_Teaming/Theory.md))
- [ ] LLM-as-judge prompt reviewed for position and verbosity bias (→ [Section 18: LLM-as-Judge](./18_AI_Evaluation/03_LLM_as_Judge/Theory.md))
- [ ] Automated eval pipeline runs on every PR — regressions block deployment (→ [Section 18: Build an Eval Pipeline](./18_AI_Evaluation/08_Build_an_Eval_Pipeline/Project_Guide.md))
- [ ] Benchmark results contextualized — leaderboard scores don't predict production performance (→ [Section 18: Benchmarks](./18_AI_Evaluation/02_Benchmarks/Theory.md))
- [ ] RAG pipeline evaluated with RAGAS metrics — faithfulness and answer relevance above threshold (→ [Section 18: RAG Evaluation](./18_AI_Evaluation/04_RAG_Evaluation/Theory.md))
- [ ] Agent task completion rate measured on a representative task suite (→ [Section 18: Agent Evaluation](./18_AI_Evaluation/05_Agent_Evaluation/Theory.md))
- [ ] Adversarial inputs tested — prompt injection, jailbreak attempts, boundary inputs (→ [Section 18: Red Teaming](./18_AI_Evaluation/06_Red_Teaming/Theory.md))

---

## 3. RAG & Retrieval

- [ ] Chunk size tuned for retrieval — not just for the LLM context window (→ [Section 09: Chunking Strategies](./09_RAG_Systems/03_Chunking_Strategies/Theory.md))
- [ ] Retrieval precision and recall measured — top-k selection validated against eval set (→ [Section 09: Retrieval Pipeline](./09_RAG_Systems/05_Retrieval_Pipeline/Theory.md))
- [ ] Hybrid search implemented where keyword recall matters — dense alone misses exact matches (→ [Section 09: Advanced RAG Techniques](./09_RAG_Systems/07_Advanced_RAG_Techniques/Theory.md))
- [ ] Document ingestion handles format failures gracefully — corrupt PDFs don't crash the pipeline (→ [Section 09: Document Ingestion](./09_RAG_Systems/02_Document_Ingestion/Theory.md))
- [ ] Stale documents have a TTL or update trigger — retrieval over outdated data is a silent bug (→ [Section 09: RAG Fundamentals](./09_RAG_Systems/01_RAG_Fundamentals/Theory.md))
- [ ] Context assembly respects token budget — retrieved chunks plus system prompt fit the window (→ [Section 09: Context Assembly](./09_RAG_Systems/06_Context_Assembly/Theory.md))
- [ ] Prompt caching applied to static system prompts and repeated context blocks — cost reduction at scale (→ [Section 09: CAG Cache Augmented Generation](./09_RAG_Systems/11_CAG_Cache_Augmented_Generation/Theory.md))

---

## 4. Agents & Tool Use

- [ ] Every tool has a documented failure mode and a graceful fallback — agents must not hang on tool error (→ [Section 10: Tool Use](./10_AI_Agents/03_Tool_Use/Theory.md))
- [ ] Max iteration limit set — unbounded agent loops burn tokens and money (→ [Section 10: Planning and Reasoning](./10_AI_Agents/05_Planning_and_Reasoning/Theory.md))
- [ ] Tool schemas are minimal and unambiguous — ambiguous schemas cause wrong tool selection (→ [Section 08: Tool Calling](./08_LLM_Applications/02_Tool_Calling/Theory.md))
- [ ] Multi-agent communication contracts are explicit — no implicit shared state between agents (→ [Section 10: Multi-Agent Systems](./10_AI_Agents/07_Multi_Agent_Systems/Theory.md))
- [ ] Agent memory bounded — in-context memory growth profiled across a full session (→ [Section 10: Agent Memory](./10_AI_Agents/04_Agent_Memory/Theory.md))
- [ ] Human-in-the-loop breakpoints defined for high-stakes actions — irreversible operations need approval (→ [Section 15: Human-in-the-Loop](./15_LangGraph/05_Human_in_the_Loop/Theory.md))
- [ ] MCP server permissions scoped to minimum required — no wildcard tool access (→ [Section 11: Security and Permissions](./11_MCP_Model_Context_Protocol/07_Security_and_Permissions/Theory.md))

---

## 5. Production Infrastructure

- [ ] Model serving endpoint tested under load — P99 latency measured, not just average (→ [Section 12: Model Serving](./12_Production_AI/01_Model_Serving/Theory.md))
- [ ] Horizontal scaling plan exists — auto-scaling policy defined before traffic spikes occur (→ [Section 12: Scaling AI Apps](./12_Production_AI/09_Scaling_AI_Apps/Theory.md))
- [ ] Graceful degradation path defined — fallback if model endpoint is unavailable (→ [Section 12: Model Serving](./12_Production_AI/01_Model_Serving/Theory.md))
- [ ] Caching layer implemented for repeated identical requests — semantic cache reduces redundant inference (→ [Section 12: Caching Strategies](./12_Production_AI/04_Caching_Strategies/Theory.md))
- [ ] Rate limit handling implemented with exponential backoff — no naive retry loops (→ [Section 21: Error Handling](./21_Claude_Mastery/03_Claude_API_and_SDK/12_Error_Handling/Theory.md))
- [ ] Streaming enabled for user-facing responses — perceived latency matters more than TTFT alone (→ [Section 08: Streaming Responses](./08_LLM_Applications/08_Streaming_Responses/Theory.md))
- [ ] Deployment pipeline runs eval before routing traffic — blue/green or canary deploy with eval gate (→ [Section 12: Evaluation Pipelines](./12_Production_AI/06_Evaluation_Pipelines/Theory.md))

---

## 6. Cost & Latency

- [ ] Token budget per request estimated and capped — runaway prompts are a real incident vector (→ [Section 12: Cost Optimization](./12_Production_AI/03_Cost_Optimization/Theory.md))
- [ ] Prompt caching applied to stable prefixes — cache hit rate tracked in dashboards (→ [Section 12: Cost Optimization](./12_Production_AI/03_Cost_Optimization/Theory.md))
- [ ] Model routing implemented — cheap/fast model for simple tasks, expensive model only when needed (→ [Section 21: Cost Optimization](./21_Claude_Mastery/03_Claude_API_and_SDK/11_Cost_Optimization/Theory.md))
- [ ] Batch API used for non-latency-sensitive workloads — 50% cost reduction for async jobs (→ [Section 21: Batching](./21_Claude_Mastery/03_Claude_API_and_SDK/10_Batching/Theory.md))
- [ ] KV cache and speculative decoding evaluated for latency-critical paths (→ [Section 12: Latency Optimization](./12_Production_AI/02_Latency_Optimization/Theory.md))
- [ ] Cost per request tracked by feature and user segment — not just aggregate billing (→ [Section 21: Cost Optimization](./21_Claude_Mastery/03_Claude_API_and_SDK/11_Cost_Optimization/Theory.md))
- [ ] Output length constrained where possible — `max_tokens` set to realistic ceiling, not unlimited (→ [Section 07: Using LLM APIs](./07_Large_Language_Models/09_Using_LLM_APIs/Theory.md))

---

## 7. Safety & Alignment

- [ ] System prompt defines scope clearly — what the model should and should not do (→ [Section 21: System Prompts](./21_Claude_Mastery/03_Claude_API_and_SDK/04_System_Prompts/Theory.md))
- [ ] Output validation layer implemented — structured outputs validated against schema before use (→ [Section 08: Structured Outputs](./08_LLM_Applications/03_Structured_Outputs/Theory.md))
- [ ] Input guardrails screen for prompt injection — especially in RAG and agent pipelines (→ [Section 12: Safety and Guardrails](./12_Production_AI/07_Safety_and_Guardrails/Theory.md))
- [ ] Hallucination risk assessed for the use case — mitigation strategy documented (→ [Section 07: Hallucination and Alignment](./07_Large_Language_Models/08_Hallucination_and_Alignment/Theory.md))
- [ ] Constitutional AI and safety layers understood for the model in use (→ [Section 21: Constitutional AI](./21_Claude_Mastery/01_Claude_as_an_AI_Model/07_Constitutional_AI/Theory.md))
- [ ] Tool permissions scoped to minimum necessary — agents cannot call destructive tools without explicit allow-list (→ [Section 21: Safety in Agents](./21_Claude_Mastery/04_Claude_Agent_SDK/10_Safety_in_Agents/Theory.md))
- [ ] Red team exercise completed before launch — at least one person tried to break the system (→ [Section 18: Red Teaming](./18_AI_Evaluation/06_Red_Teaming/Theory.md))
- [ ] Data privacy review done — PII not passed unnecessarily to external model APIs (→ [Section 12: Safety and Guardrails](./12_Production_AI/07_Safety_and_Guardrails/Theory.md))

---

## 8. Monitoring & Observability

- [ ] Structured logs capture: model, prompt hash, token counts, latency, and outcome for every request (→ [Section 12: Observability](./12_Production_AI/05_Observability/Theory.md))
- [ ] LLM-specific metrics tracked: input tokens, output tokens, cache hit rate, refusal rate (→ [Section 12: Observability](./12_Production_AI/05_Observability/Theory.md))
- [ ] Distributed traces connect user request → retrieval → model call → response for end-to-end visibility (→ [Section 12: Observability](./12_Production_AI/05_Observability/Theory.md))
- [ ] Alerts defined for anomalies: latency spikes, error rate increase, cost per request drift (→ [Section 12: Observability](./12_Production_AI/05_Observability/Theory.md))
- [ ] Eval scores tracked over time — production drift detected before users notice (→ [Section 12: Evaluation Pipelines](./12_Production_AI/06_Evaluation_Pipelines/Theory.md))
- [ ] Feedback loop exists — user signals (thumbs, corrections, escalations) feed back into eval (→ [Section 18: Evaluation Fundamentals](./18_AI_Evaluation/01_Evaluation_Fundamentals/Theory.md))
- [ ] Shadow mode or canary deployment used for model updates — no blind cutover to new model version (→ [Section 12: Scaling AI Apps](./12_Production_AI/09_Scaling_AI_Apps/Theory.md))

---

## How to Use This Checklist

1. Work through each section relevant to your system — not every item applies to every architecture.
2. For each unchecked item, link to the failing item in your team's issue tracker before launch.
3. Re-run this checklist after any major model update, prompt change, or retrieval pipeline change.
4. Items marked `→ Section XX` link directly to the Atlas content that explains the concept in depth — read before deciding an item does not apply.

---

## 📂 Navigation

⬅️ **Back to:** [README](./README.md)
