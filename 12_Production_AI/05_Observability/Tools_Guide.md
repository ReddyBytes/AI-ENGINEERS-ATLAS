# Tools Guide — Observability

A comprehensive comparison of observability tools for AI/LLM systems. Choose based on your scale, team size, and specific needs.

---

## LLM-Specific Observability Platforms

| Tool | Type | Free Tier | Self-Hostable | Best For | Standout Feature |
|---|---|---|---|---|---|
| **Langfuse** | LLM Observability | Yes (generous) | Yes (open-source) | Full-featured OSS option | Best OSS option; prompt management + evals |
| **LangSmith** | LLM Observability | Yes (500 traces/month) | No | LangChain projects | Tight LangChain integration |
| **Arize Phoenix** | LLM + ML Obs | Yes (open-source) | Yes | Evaluation-focused teams | Best for RAG evaluation + debugging |
| **Helicone** | LLM Proxy + Logging | Yes (limited) | Yes | Simple API proxy logging | Zero-code integration (proxy model) |
| **Braintrust** | Eval + Observability | Yes | No | Evaluation-first teams | Integrated eval + production monitoring |
| **Weights & Biases** | ML Training + LLM | Yes (limited) | No | Teams also doing ML training | Unified training + production view |
| **Traceloop** | LLM + OpenTelemetry | Yes | Yes | OpenTelemetry-first teams | Native OTel integration |

---

## General Observability Infrastructure

### Metrics

| Tool | Type | Strengths | Weaknesses |
|---|---|---|---|
| **Prometheus** | Open-source metrics | Powerful, huge ecosystem, free | Requires ops expertise |
| **Grafana** | Visualization | Works with any data source | Configuration overhead |
| **Datadog** | SaaS all-in-one | Easy setup, great AI integrations | Expensive at scale |
| **CloudWatch (AWS)** | Managed | No setup if on AWS, native integration | Less flexible querying |
| **Google Cloud Monitoring** | Managed | Native GCP integration | GCP-specific |

### Logs

| Tool | Type | Strengths | Weaknesses |
|---|---|---|---|
| **ELK Stack** (Elasticsearch + Logstash + Kibana) | Open-source | Powerful search, free | Complex to operate |
| **Loki + Grafana** | Open-source | Lightweight, pairs with Prometheus | Less powerful search than ELK |
| **Datadog Logs** | SaaS | Unified with metrics/traces | Cost scales with log volume |
| **CloudWatch Logs** | Managed | Simple if on AWS | Limited querying |

### Traces

| Tool | Type | Strengths | Weaknesses |
|---|---|---|---|
| **Jaeger** | Open-source | Full-featured, free | Requires infrastructure |
| **Zipkin** | Open-source | Lightweight, simple | Less features than Jaeger |
| **OpenTelemetry** | Standard | Vendor-neutral, broad support | Instrumentation effort |
| **Datadog APM** | SaaS | Easy, great UI, AI-native | Cost |

---

## Langfuse — Detailed Setup Guide

Langfuse is the recommended starting point for most LLM projects. It is open-source, free to self-host, and covers logging, cost tracking, evals, and prompt management.

### Installation

```bash
pip install langfuse
```

### Environment Setup

```bash
# .env
LANGFUSE_PUBLIC_KEY=pk-lf-...   # From langfuse.com or your self-hosted instance
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com  # Or your self-hosted URL
```

### Basic Integration (Decorator Pattern)

```python
from langfuse.decorators import observe, langfuse_context
import anthropic

client = anthropic.Anthropic()

@observe()
def answer_question(question: str, user_id: str) -> str:
    langfuse_context.update_current_trace(
        name="customer-support",
        user_id=user_id,
        tags=["production", "support"]
    )

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=512,
        messages=[{"role": "user", "content": question}]
    )

    output = response.content[0].text

    langfuse_context.update_current_observation(
        input=question,
        output=output,
        usage={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
            "unit": "TOKENS"
        }
    )

    return output
```

### What You Get in the Langfuse Dashboard

- **Traces view**: Every call logged with prompt, response, latency, tokens
- **Cost analytics**: Per-model cost, cost trends, cost per user
- **Latency analytics**: P50/P95/P99 trends over time
- **Evals view**: Quality scores if you add scoring
- **Prompt management**: Version and A/B test prompts
- **User analytics**: Per-user token usage and cost

---

## Arize Phoenix — Detailed Setup Guide

Phoenix is open-source and excels at RAG evaluation and debugging.

```bash
pip install arize-phoenix opentelemetry-sdk opentelemetry-exporter-otlp
```

```python
import phoenix as px
from openinference.instrumentation.anthropic import AnthropicInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Launch the Phoenix UI (opens at http://localhost:6006)
px.launch_app()

# Set up OpenTelemetry to send traces to Phoenix
endpoint = "http://127.0.0.1:6006/v1/traces"
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(
    SimpleSpanProcessor(OTLPSpanExporter(endpoint))
)
trace_api.set_tracer_provider(tracer_provider)

# Auto-instrument Anthropic SDK
AnthropicInstrumentor().instrument()

# Now all anthropic.Client calls are automatically traced
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=512,
    messages=[{"role": "user", "content": "Hello"}]
)
# This call now appears in Phoenix with full trace
```

---

## Self-Hosted Observability Stack (Production Template)

For teams that want full control over their observability data:

```yaml
# docker-compose.yml — minimal production observability stack
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP

  langfuse:
    image: ghcr.io/langfuse/langfuse:latest
    ports:
      - "3001:3000"
    environment:
      - DATABASE_URL=postgresql://langfuse:password@postgres:5432/langfuse
      - NEXTAUTH_SECRET=your-secret-key

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_USER=langfuse
      - POSTGRES_DB=langfuse

volumes:
  grafana_data:
```

---

## Tool Selection Decision Guide

```
Start here:

Q1: Are you building an LLM/AI application?
  YES → Add Langfuse or Phoenix from day 1
  NO  → Standard observability (Prometheus + Grafana) is sufficient

Q2: Are you using LangChain?
  YES → LangSmith is the easiest integration
  NO  → Langfuse has better multi-framework support

Q3: Do you need to self-host for data privacy?
  YES → Langfuse (open-source) or Phoenix (open-source) on your infra
  NO  → Langfuse Cloud, LangSmith, or Helicone for managed options

Q4: Do you need evaluation built in?
  YES → Phoenix (best eval features), Braintrust (eval-first)
  NO  → Langfuse covers production monitoring well without evals

Q5: Are you at > 1M requests/day?
  YES → Add Prometheus + Grafana for metrics, ELK for logs
      → Use LLM-specific tool only for sampling (1-5% of requests)
  NO  → Full request logging in Langfuse is fine at this scale

Q6: Are you on a major cloud (AWS/GCP/Azure)?
  YES → Consider native tools (CloudWatch, GCP Monitoring) for infra
      → Supplement with LLM-specific tool for AI-specific metrics
  NO  → Self-hosted OSS stack (Prometheus + Grafana + Langfuse)
```

---

## Cost of Observability Tools (Approximate)

| Tool | Free Tier | Paid Starts | At Scale |
|---|---|---|---|
| **Langfuse Cloud** | Unlimited (generous) | $59/month (team) | $199+/month |
| **Langfuse Self-hosted** | Free forever | — | Infra cost only |
| **LangSmith** | 500 traces/month | $39/month/user | $200+/month |
| **Arize Phoenix** | Free forever (OSS) | — | Infra cost only |
| **Datadog** | 5 hosts free | ~$15/host/month | Very expensive at scale |
| **Prometheus + Grafana** | Free (OSS) | — | Infra cost only |
| **Helicone** | 1K requests free | $20/month | $150+/month |

**Recommendation for most teams**: Start with Langfuse Cloud (free) + add Prometheus/Grafana when you outgrow it. Total cost = $0 until you need enterprise features.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Tools_Guide.md** | ← you are here |

⬅️ **Prev:** [04 Caching Strategies](../04_Caching_Strategies/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Evaluation Pipelines](../06_Evaluation_Pipelines/Theory.md)
