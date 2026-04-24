# Interview QA — Model Serving

## Beginner

**Q1: What is the difference between model training and model serving?**

<details>
<summary>💡 Show Answer</summary>

**A:** Training is the offline process of learning model weights from data — it happens once (or periodically) and takes a long time. Serving is the online process of using those weights to make predictions on new inputs in real time. Training optimizes for accuracy; serving optimizes for latency, throughput, reliability, and cost. A model that performs great in training but crashes under production load is useless.

</details>

---

**Q2: What is an inference server and why do you need one instead of just writing a Flask app?**

<details>
<summary>💡 Show Answer</summary>

**A:** An inference server (like TorchServe, NVIDIA Triton, or vLLM) is purpose-built software for running model inference at scale. It provides: automatic request batching (batching multiple inputs into one GPU call), multi-model management (host several models on one GPU), dynamic batching (gathering requests arriving in a short window), model versioning, and built-in metrics. A plain Flask app gives you none of that. For low traffic it's fine, but under load you quickly hit GPU underutilization and need the batching logic that inference servers provide out of the box.

</details>

---

**Q3: What is the difference between online inference and batch inference?**

<details>
<summary>💡 Show Answer</summary>

**A:** **Online inference** (also called real-time inference) processes one request at a time with low latency — typically under 100-500ms. Used when users are waiting for an answer (chatbot, fraud detection, search ranking). **Batch inference** processes many inputs together, asynchronously, and prioritizes throughput over latency — you might process 1 million records overnight. Online inference needs always-on servers; batch inference can use spot instances and run on a schedule, making it much cheaper.

</details>

---

## Intermediate

**Q4: Explain blue-green deployment vs canary release. When would you use each?**

<details>
<summary>💡 Show Answer</summary>

**A:** In a **blue-green deployment**, you maintain two identical production environments (blue = current, green = new version). You test green thoroughly, then switch 100% of traffic from blue to green in one instant. Rollback is instant — just flip the traffic back. Best for: when you need zero-downtime deployments and the risk of the new model is low (e.g. minor bug fix, same architecture).

In a **canary release**, you route a small percentage of traffic (5-10%) to the new model version while the rest still hits the old one. You monitor error rates, latency, and quality metrics. If everything looks good, you gradually increase the percentage. Best for: when you have a significantly changed model and want to detect regressions on real traffic before full rollout.

</details>

---

**Q5: How does request batching improve GPU utilization, and what are its tradeoffs?**

<details>
<summary>💡 Show Answer</summary>

**A:** GPUs are massively parallel processors — they execute thousands of operations simultaneously. If you send one inference request at a time, you are using maybe 5% of the GPU's capacity. Batching combines multiple inputs into a single tensor and runs one forward pass, spreading the fixed overhead across many requests. This dramatically increases throughput (requests/second).

Tradeoffs: batching adds **latency** for individual requests (a request must wait for the batch to fill or a timeout to expire). There is a sweet spot — if your batch wait time is 10ms and your average user gets 40ms lower response time due to better throughput, that trade-off makes sense. Dynamic batching (Triton does this) collects requests arriving within a configurable window (e.g., 5ms) rather than waiting for a fixed batch size.

</details>

---

**Q6: How would you handle a model version rollback in production?**

<details>
<summary>💡 Show Answer</summary>

**A:** Good rollback requires preparation before deployment:
1. **Never delete old model versions** — keep the previous two versions warm (loaded on servers or at minimum stored and quick to reload)
2. **Blue-green deployment** — new model goes to "green" environment; at the switch, if metrics degrade within 5 minutes, flip traffic back to "blue" in seconds
3. **Traffic shadowing** — send a copy of live requests to the new model but only serve responses from the old one; compare results before switching
4. **Automated rollback triggers** — set alerts: if error rate > 1% or P99 latency > 2x baseline for 2 minutes, auto-revert to previous version
5. **Versioned endpoints** — `/v1/predict` always points to stable, `/v2/predict` is the new one; clients can fall back to v1

</details>

---

## Advanced

**Q7: How would you design a multi-model serving architecture that routes traffic to different models based on request complexity?**

<details>
<summary>💡 Show Answer</summary>

**A:** This is called **model routing** or **cascading inference**. The architecture:

1. A **routing layer** receives all requests and classifies them by complexity (using a tiny classifier or heuristics like input length, keywords, or explicit client flags)
2. **Simple requests** (short, common patterns) → routed to a small, cheap model (e.g., a 7B parameter model on a T4 GPU)
3. **Complex requests** (long, rare, high-stakes) → routed to a large, expensive model (e.g., 70B or an API)
4. **Fallback** — if the small model returns low confidence (measured by log-probability or a calibrated confidence score), escalate to the large model

Implementation considerations: the routing classifier must be extremely fast (microseconds, not milliseconds). You also need to track cost-per-request by tier and monitor quality to ensure the small model handles its tier well. This pattern can reduce inference costs by 60-80% for workloads where most requests are simple.

</details>

---

**Q8: What are the key differences between REST and gRPC for model serving, and when would you choose gRPC?**

<details>
<summary>💡 Show Answer</summary>

**A:** **REST** (HTTP/1.1 + JSON): human-readable, easy to debug, universally compatible with any language/framework. JSON serialization/deserialization adds overhead — especially for large input arrays (images, embeddings).

**gRPC** (HTTP/2 + Protocol Buffers): binary serialization (3-10x smaller payload than JSON), bidirectional streaming, multiplexing multiple requests over one connection, strongly typed contracts via `.proto` files. gRPC is typically 5-10x faster than REST for the same payload.

Choose gRPC when:
- Your clients are internal services (microservices), not browsers or third-party integrations
- You are transferring large tensors, embeddings, or images (binary is much faster)
- You need streaming inference (token-by-token output from LLMs, or video frame-by-frame processing)
- You need high-throughput inter-service communication at low latency

Choose REST when serving external clients, public APIs, or where simplicity matters more than raw performance.

</details>

---

**Q9: How do you handle model serving for very large language models (70B+ parameters) that don't fit on a single GPU?**

<details>
<summary>💡 Show Answer</summary>

**A:** Large models require **model parallelism** — splitting the model across multiple GPUs or machines:

1. **Tensor parallelism** — split individual weight matrices across GPUs. Each GPU holds a shard of each layer and communicates (all-reduce) between layers. Used in frameworks like Megatron-LM and vLLM. Typical: 4-8 GPUs for a 70B model.

2. **Pipeline parallelism** — assign different layers to different GPUs (GPU 1 handles layers 1-16, GPU 2 handles layers 17-32, etc.). Lower communication overhead but introduces pipeline bubbles (idle time between micro-batches).

3. **Tensor + pipeline combined** — large clusters use both simultaneously.

4. **Quantization** — reduce from float16 to int8 or int4, cutting memory by 2-4x. A 70B float16 model needs ~140GB; with int4 quantization it fits in ~35GB (two A100s).

Serving frameworks that handle this automatically: **vLLM** (tensor parallel), **TensorRT-LLM**, **DeepSpeed-Inference**, **llama.cpp** (CPU/mixed).

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Model serving architectures |

⬅️ **Prev:** [09 Connect MCP to Agents](../../11_MCP_Model_Context_Protocol/09_Connect_MCP_to_Agents/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Latency Optimization](../02_Latency_Optimization/Theory.md)
