# Cheatsheet — Observability

**Observability** is the ability to understand the internal state of your AI system from its external outputs — through logs (what happened), metrics (how much/fast), and traces (where time was spent).

---

## Key Terms

| Term | Definition |
|---|---|
| **Log** | Timestamped record of a discrete event ("Request 1234 processed in 340ms") |
| **Metric** | Numerical measurement tracked over time ("P99 latency = 840ms") |
| **Trace** | A detailed timeline of a single request through all system components |
| **Span** | One step in a trace (e.g., "embedding lookup: 12ms") |
| **SLO** | Service Level Objective — the target you commit to ("P99 < 1 second") |
| **SLA** | Service Level Agreement — contractual commitment to external customers |
| **Alert** | Automated notification when a metric crosses a threshold |
| **Dashboard** | Visual display of multiple metrics over time |
| **Cardinality** | Number of unique values a metric label can take (high cardinality = performance risk) |
| **LLM Observability** | Logging prompts, responses, token counts, costs, and quality scores |
| **TTFT** | Time To First Token — key UX metric for streaming LLM responses |

---

## The Three Pillars

| Pillar | Answers | Tools | Storage |
|---|---|---|---|
| **Logs** | What happened? When? For whom? | ELK Stack, Datadog, CloudWatch | Log aggregation store |
| **Metrics** | How fast? How many? How costly? | Prometheus, Grafana, InfluxDB | Time-series DB |
| **Traces** | Where did time go within a request? | Jaeger, Zipkin, Datadog APM, OpenTelemetry | Distributed trace store |

---

## Essential Metrics for AI Systems

### Performance Metrics
| Metric | Target | Alert When |
|---|---|---|
| **P50 latency** | < 500ms | > 2x rolling baseline |
| **P95 latency** | < 1,000ms | > 2x rolling baseline |
| **P99 latency** | < 2,000ms | > 3x rolling baseline |
| **TTFT (streaming)** | < 300ms | > 1,000ms |
| **Requests/second** | (your target) | < 50% of normal (underload) |
| **Error rate** | < 0.1% | > 1% |

### Cost Metrics
| Metric | How to Compute | Alert When |
|---|---|---|
| **Cost per request** | `(input_tokens × price_in + output_tokens × price_out)` | > 2x rolling avg |
| **Daily API spend** | Sum of all request costs | > 120% of 7-day avg at any hour |
| **Tokens per request (avg)** | `total_tokens / total_requests` | > 2x rolling avg (context bloat) |
| **Cache hit rate** | `cache_hits / total_requests` | < 10% (cache may be broken) |

### Quality Metrics
| Metric | How to Compute | Alert When |
|---|---|---|
| **LLM judge score** | GPT-4/Claude rates responses 1-5 on sample | Score drops > 0.5 points vs baseline |
| **Refusal rate** | Fraction of responses that are refusals | Sudden spike (prompt injection?) |
| **Output length** | Avg output tokens | Sudden increase (verbosity regression) |
| **User feedback rate** | Thumbs up/down if available | Negative rate > 20% |

---

## Key Logs to Capture Per LLM Request

```json
{
  "timestamp": "2024-01-15T10:30:15.234Z",
  "request_id": "req_abc123",
  "user_id": "usr_xyz",         // hashed for privacy
  "session_id": "sess_def456",
  "model": "claude-3-5-sonnet-20241022",
  "request_type": "chat",
  "input_tokens": 1450,
  "output_tokens": 342,
  "latency_ms": 1230,
  "ttft_ms": 220,
  "cost_usd": 0.00948,
  "cache_hit": false,
  "error": null,
  "guardrail_triggered": false
}
```

---

## Alert Priority Matrix

| Alert | Severity | Response Time | Action |
|---|---|---|---|
| Error rate > 5% | P0 | Immediate | Page on-call, consider rollback |
| P99 latency > 3x baseline | P1 | < 30 min | Investigate, possible rollback |
| Daily cost > 150% avg | P1 | < 1 hour | Find runaway request, throttle |
| Error rate 1-5% | P2 | < 2 hours | Investigate root cause |
| Cache hit rate < 10% | P3 | Next business day | Check cache health |
| Quality score drops 0.5 pts | P2 | < 2 hours | Review recent prompt/model changes |

---

## Distributed Tracing Example

```
Request: "Summarize this document"
│
├─ [5ms]   auth_check (JWT validation)
├─ [2ms]   rate_limit_check (Redis lookup)
├─ [15ms]  embedding (OpenAI text-embedding-3-small)
├─ [8ms]   vector_search (Pinecone similarity search)
├─ [3ms]   context_assembly (build prompt from retrieved chunks)
├─ [890ms] llm_call (Claude 3.5 Sonnet)  ← biggest span
├─ [3ms]   output_validation (guardrail check)
└─ [2ms]   response_serialization (JSON formatting)
─────────────────────────────────────────
Total: 928ms
```
→ Optimization target: the LLM call (890ms). Everything else is negligible.

---

## LLM-Specific Observability Tools

| Tool | Type | Free Tier | Best For |
|---|---|---|---|
| **Langfuse** | LLM observability | Yes (self-host or cloud) | Full-featured, open-source option |
| **LangSmith** | LLM observability | Yes (limited) | LangChain-native projects |
| **Arize Phoenix** | LLM + ML observability | Yes | Eval-focused, great for RAG |
| **Weights & Biases** | ML + LLM | Yes (limited) | Training + production monitoring |
| **Helicone** | LLM proxy + logging | Yes | Simple API proxy with auto-logging |
| **Braintrust** | Eval + observability | Yes | Evaluation-first approach |

---

## Golden Rules

- **Log every request** — not just errors; you can't compute percentiles from a sample
- **Track cost per request** from day one — not just total daily cost
- **Set latency SLOs on P99**, not average — averages mask tail latency
- **Create alerts before launch** — not after your first incident
- **Sample traces for high-volume** — trace 100% at low traffic, 1-5% at scale
- **Scrub PII from logs** before storing — or apply strict access controls
- **Version your dashboards** — so you can correlate metric changes with code deployments

---

## 📂 Navigation
