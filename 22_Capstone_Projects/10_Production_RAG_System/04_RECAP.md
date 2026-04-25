# Project 10 — Production RAG System: Recap

## What You Built

A production-grade RAG system that extends a basic question-answering pipeline with four operational layers: semantic caching, input/output safety guardrails, per-query cost tracking, and automated RAGAS evaluation. The system can be deployed with confidence because every query is safe, measured, and economical.

---

## Concepts Applied

| Concept | How You Applied It |
|---|---|
| Semantic Cache | Used cosine similarity on stored embeddings to detect rephrased duplicate queries before hitting the API |
| Input Guardrails | Wrote regex patterns covering 14+ prompt injection and jailbreak templates; enforced length and repetition limits |
| Output Guardrails | Scanned generated responses for PII (email, phone, SSN, credit card) with hard blocks; flagged hallucination markers with soft warnings |
| Cost Tracking | Extracted `usage.input_tokens` and `usage.output_tokens` from every Anthropic response; multiplied by published per-million-token rates; logged to SQLite |
| RAGAS Faithfulness | Used Claude as a judge: decomposed each answer into atomic claims, then checked each claim against the retrieved context |
| RAGAS Answer Relevancy | Generated 3 hypothetical questions from each answer; computed cosine similarity with the original question embedding; averaged scores |
| SQLite for observability | Two-table schema — `query_cache` for caching, `query_stats` for cost logs — gives a queryable audit trail |

---

## Extension Ideas

**1. Cache TTL (Time-to-Live)**
Add a `max_age_hours` parameter to the cache. Entries older than the TTL are excluded from lookup. Useful for knowledge bases that change — clinical documentation gets updated, cached answers should expire.

**2. Guardrail metrics dashboard**
Track how many queries were blocked by each guardrail type. Build a `/guardrail-report` command that shows: "blocked last 7 days: 3 injection, 1 jailbreak, 0 PII, 0 spam." Use this to tune your patterns — if zero jailbreaks are blocked in a month, either the patterns are too narrow or users are not trying.

**3. RAGAS context precision**
Add a third RAGAS metric — context precision (were the retrieved chunks actually relevant to the question?). This identifies whether your retrieval step is the weak link. A high faithfulness score with low context precision means the model is doing well with the chunks it gets, but the chunks themselves may not be optimal.

---

## Job Mapping

| Role | How this project applies |
|---|---|
| ML Engineer | Implements caching, cost tracking, and evaluation pipelines that make AI systems maintainable in production |
| AI Safety Engineer | Designs and tests input/output guardrail systems; adversarially tests for prompt injection and jailbreak bypasses |
| Backend Engineer | Integrates AI pipelines with SQLite persistence, REST CLI interfaces, and operational metrics |
| LLM Evaluation Engineer | Builds automated RAGAS-style evaluation pipelines; interprets faithfulness and relevancy scores to guide system improvement |
| Technical Product Manager | Uses the `/stats` and `/eval` outputs to make data-driven decisions about cache thresholds, model selection, and deployment readiness |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Project context and motivation |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and component table |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable Python skeleton |
| 04_RECAP.md | you are here |

⬅️ **Prev:** [09 — Build a RAG App](../09_Custom_LoRA_Fine_Tuning/01_MISSION.md)
