# Production Checklist

Before you ship an AI feature to real users, run through this checklist. Each item links to the relevant section.

---

## 🚀 Pre-Launch Checklist

### Serving & Infrastructure
- [ ] Model is deployed behind a load balancer (not directly exposed)
- [ ] Health check endpoint returns 200 when model is ready
- [ ] Auto-scaling configured — scales up under load, down when idle
- [ ] Blue-green or canary deployment set up for zero-downtime updates
- [ ] Rollback procedure documented and tested

### Latency
- [ ] P95 latency measured and within acceptable SLA (typically <2s for chat, <500ms for autocomplete)
- [ ] Streaming enabled for long outputs (users see tokens as they arrive)
- [ ] Batching configured on inference server (improves GPU utilization)
- [ ] Consider quantization if latency is above target

### Cost
- [ ] Token usage logged per request (input + output)
- [ ] Cost per request calculated and within budget
- [ ] Prompt caching enabled where system prompt is repeated (up to 90% savings on cached tokens)
- [ ] Model routing in place — cheap model for simple queries, expensive for complex

### Caching
- [ ] Exact-match cache for FAQs and repeated identical queries
- [ ] Semantic cache considered if many paraphrased duplicates expected
- [ ] Cache TTL set appropriately (not too long for time-sensitive data)
- [ ] Cache hit rate monitored

### Observability
- [ ] Every LLM call logged: prompt, response, latency, tokens, cost
- [ ] Alerting configured: latency spike, error rate > 1%, cost over budget
- [ ] Distributed tracing enabled to debug slow requests
- [ ] LLM observability tool connected (Langfuse, LangSmith, or Helicone)

### Evaluation
- [ ] Baseline evaluation run and scores recorded before launch
- [ ] Evaluation pipeline runs automatically on model/prompt changes
- [ ] Human review sample: spot-check 10 real responses before launch
- [ ] Regression test suite covers known failure cases

### Safety & Guardrails
- [ ] Input validation: length limits, encoding normalization
- [ ] Prompt injection detection enabled
- [ ] PII detection if handling personal data
- [ ] Output filtering for harmful/toxic content (appropriate to your use case)
- [ ] System prompt hardened — tested against common jailbreak attempts
- [ ] Rate limiting per user/IP configured

### Fine-Tuning (if applicable)
- [ ] Training data quality reviewed — no label leakage, no PII
- [ ] Held-out evaluation set used (not part of training)
- [ ] Fine-tuned model compared to base model on eval set
- [ ] Versioning in place — old model preserved for rollback

### Scaling
- [ ] Load tested at expected peak traffic
- [ ] Queue-based architecture for bursty workloads
- [ ] Circuit breaker configured — fail gracefully if model is overwhelmed
- [ ] Degraded mode defined — what happens if the AI is unavailable?

---

## 🔄 Ongoing Operations Checklist

Run weekly or when making changes:

- [ ] Review cost dashboard — any unexpected spikes?
- [ ] Check evaluation scores — any quality regressions?
- [ ] Review error logs — new failure modes appearing?
- [ ] Check cache hit rate — room to improve?
- [ ] Review escalation/fallback rate — are guardrails too aggressive?

---

## 📂 Navigation

⬅️ **Back to:** [12 Production AI Readme](./Readme.md)
