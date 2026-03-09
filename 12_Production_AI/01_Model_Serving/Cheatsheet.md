# Cheatsheet — Model Serving

**Model serving** is the process of exposing a trained ML model as a live API that accepts inputs, runs inference, and returns predictions in real time.

---

## Key Terms

| Term | Definition |
|---|---|
| **Inference** | Running a trained model on new input to generate a prediction |
| **Inference server** | Software that hosts the model and handles requests (TorchServe, Triton, vLLM) |
| **Endpoint** | The URL/address clients call to get predictions |
| **Latency** | Time from request to response (measured in ms) |
| **Throughput** | Number of requests handled per second (RPS) |
| **Online inference** | Real-time, one request at a time (low latency) |
| **Batch inference** | Process many inputs at once, asynchronously (high throughput) |
| **Model replica** | A copy of the model running on separate hardware for redundancy/scale |
| **Blue-green deployment** | Two identical environments; swap traffic between them for zero-downtime updates |
| **Canary release** | Route a small % of traffic to the new model, monitor, then ramp up |
| **A/B test** | Split traffic between two model versions to compare performance |

---

## Serving Options Comparison

| Option | Examples | Pros | Cons |
|---|---|---|---|
| **Self-hosted (framework)** | TorchServe, Triton, vLLM | Full control, no per-token cost | Ops burden, GPU infra needed |
| **Self-hosted (DIY FastAPI)** | FastAPI + model | Simple, flexible | No batching/scaling built-in |
| **Managed cloud** | AWS SageMaker, GCP Vertex AI | Auto-scaling, monitoring included | Vendor lock-in, higher cost |
| **Third-party API** | OpenAI, Anthropic, Cohere | Zero infra, always updated | Per-token cost, no customization |

---

## Scaling Strategies

| Strategy | How | When to use |
|---|---|---|
| **Horizontal scaling** | Add more inference servers behind a load balancer | High request volume |
| **Vertical scaling** | Use a bigger GPU (A100 → H100) | Model too large for current GPU |
| **Auto-scaling** | Spin up/down servers based on queue depth or CPU/GPU % | Variable traffic |
| **Request batching** | Group multiple inputs for one GPU forward pass | High-throughput scenarios |

---

## Deployment Patterns

```
Blue-Green:   [100% → v1]  swap  [100% → v2]       (instant rollback)
Canary:       [95% → v1, 5% → v2]  → monitor → ramp  (gradual rollout)
A/B Test:     [50% → v1, 50% → v2]  → measure quality  (controlled experiment)
```

---

## When to Use Each Serving Approach

**Use a third-party API when:**
- You are prototyping or have low request volume
- You need the latest model capabilities without infra work
- Per-token cost is acceptable at your scale

**Use managed cloud serving when:**
- You need auto-scaling but don't want to manage Kubernetes
- You are already on AWS/GCP/Azure ecosystem

**Use self-hosted when:**
- You have high volume where API costs exceed GPU costs
- You need data privacy / can't send data to third parties
- You need custom model architectures or fine-tuned models

---

## Golden Rules

- **Load the model once** at startup, never per request
- **Always version your models** so you can roll back instantly
- **Monitor latency at P95/P99**, not just the average
- **Use health checks** so the load balancer removes unhealthy replicas
- **Test your rollback procedure** before you need it in production
- **Batch requests** to maximize GPU utilization
- **Set timeouts** on inference calls — never let a stuck request block others

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Model serving architectures |

⬅️ **Prev:** [09 Connect MCP to Agents](../../11_MCP_Model_Context_Protocol/09_Connect_MCP_to_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Latency Optimization](../02_Latency_Optimization/Theory.md)
