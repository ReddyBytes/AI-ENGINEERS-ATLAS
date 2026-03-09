# Interview QA — Latency Optimization

## Beginner

**Q1: What is latency and why do we measure it in percentiles instead of averages?**

**A:** Latency is the elapsed time from when a client sends a request to when it receives a complete response. We measure it in milliseconds.

Averages are misleading because they hide tail latency. Imagine 99 requests take 100ms and 1 request takes 10,000ms. The average is ~200ms, which looks acceptable — but 1% of your users are experiencing a 10-second hang. That 1% is real people having a terrible experience.

Percentiles tell the truth: P99 of 10,000ms means "1 in 100 requests is terrible." We set SLOs (Service Level Objectives) on P95 and P99 because that is where real user pain lives. A rule of thumb: if P99 > 3x your P50, you have a tail latency problem worth investigating.

---

**Q2: What is quantization in the context of model inference, and what are its tradeoffs?**

**A:** Quantization reduces the numerical precision of model weights. Standard models use float32 (32-bit floating point, 4 bytes per value). Quantizing to int8 (8-bit integer) cuts memory usage by 75% and speeds up computation because integer math is faster and allows 4 values to pack into one register.

Tradeoffs:
- **Speedup**: 2-3x faster on CPU; on GPUs with int8 support (e.g. NVIDIA A100 Tensor Cores) you get 2-3x compute speedup
- **Memory**: 50-75% reduction depending on format
- **Quality**: int8 causes negligible quality loss (< 0.5% on most benchmarks) for most tasks. int4 can cause 1-3% quality loss on complex reasoning tasks — always measure after quantizing

The key is: quantize by default, then run your evaluation suite to check whether quality is acceptable for your use case.

---

**Q3: How does request batching reduce latency at the system level, even though it might add per-request wait time?**

**A:** This is a common point of confusion. Batching reduces *system-level latency* (time to process all requests) even though it increases *per-request latency* (time for one specific request).

Here is why: A GPU running one request might use 5% of its capacity. The same GPU, running 20 requests at once, completes all 20 in roughly the same time as it would complete 1 (because of parallelism). So system throughput improves 20x.

For the individual user: if your batch wait timeout is 10ms and the speedup from batching reduces inference time by 100ms, the net gain is +90ms. The user waits 10ms more for batching but the actual inference is 100ms faster — net win.

The key is setting the right batch timeout. For interactive applications, 2-10ms is typical. For background processing, you might wait 100-500ms.

---

## Intermediate

**Q4: Explain speculative decoding. How does it speed up LLM inference?**

**A:** Standard LLM inference is inherently sequential: you generate token 1, which is needed to generate token 2, which is needed for token 3. You can't parallelize this within a single sequence.

Speculative decoding breaks this sequential dependency:
1. A **small, fast "draft" model** (e.g., 7B parameters) generates N candidate tokens very quickly (in one pass)
2. The **large "verify" model** (e.g., 70B parameters) checks all N tokens in a single parallel forward pass — much faster than generating them sequentially
3. The verify model accepts tokens that match its distribution and rejects the first wrong one
4. If 4 out of 5 draft tokens are accepted, you have produced 4 tokens in roughly the same time it would normally take to produce 1

Typical speedup: 2-3x for long text generation. The key insight is that verifying N tokens in parallel is much faster than generating N tokens sequentially — even in a large model.

Requirements: the draft model must be from the same model family as the verify model (same tokenizer, same architecture family) for the acceptance rates to be high.

---

**Q5: What is the KV cache in LLMs, and how does prompt caching use it to reduce latency?**

**A:** In a transformer, the attention mechanism computes Key (K) and Value (V) matrices for every token. These matrices are expensive to compute. When generating text, K and V for all previous tokens must be recomputed at each step unless you cache them.

The **KV cache** stores the K and V matrices for all tokens processed so far. Each new token only requires computing K and V for itself and attending to the cached K/Vs — rather than reprocessing the entire context from scratch.

**Prompt caching** (offered by Anthropic and OpenAI) extends this idea to the serving infrastructure: if you have a long system prompt that is the same across many requests (e.g., "You are a customer service agent for Acme Corp..."), the server can cache the K/V state for that system prompt prefix. Subsequent requests that start with the same prefix don't re-process those tokens — they jump straight to the cached state.

Result: up to 90% cost reduction and significant latency reduction for the cached portion. This is especially valuable for RAG applications where the same context document is injected repeatedly.

---

**Q6: How would you go about diagnosing a latency regression after deploying a new model version?**

**A:** A structured debugging approach:

1. **Compare profiles, not just headlines**: Use distributed tracing (e.g., OpenTelemetry) to get a breakdown of time spent in each component: preprocessing, queue wait, inference, postprocessing, network.

2. **Check model size and architecture**: Did the new model have more parameters? A different architecture? Sometimes a "minor update" switches from an efficient architecture to a slower one.

3. **Check batch behavior**: Is the new model being batched differently? If the new model has a larger memory footprint, fewer requests fit in a batch, reducing GPU utilization.

4. **Check output length**: For LLMs, if the new model produces longer responses on average (more verbose), total generation time increases even if tokens/second is the same.

5. **Check hardware utilization**: Is GPU memory higher? Are you hitting memory bandwidth limits? A model that just barely fits in VRAM will constantly spill to slower memory.

6. **A/B the serving config**: Run old model and new model side by side on identical traffic and compare profiled traces. The difference points to the root cause.

---

## Advanced

**Q7: Explain continuous batching vs static batching for LLM serving. Why does continuous batching matter?**

**A:** In **static batching**, you define a fixed batch size (e.g., 8 requests) and wait until 8 requests arrive, process them all together, and return all results when the slowest one finishes. Problem: if one request needs to generate 100 tokens and another needs 500 tokens, the GPU is idle for the 8-request slot waiting for the longest one to finish. GPU utilization can drop to 20-30%.

In **continuous batching** (also called dynamic batching or iteration-level scheduling), new requests are inserted into the batch at the token iteration level. When a sequence finishes generating its last token, it is removed from the batch and a new waiting request is immediately inserted for the next iteration. The GPU is always processing a full batch.

Result: GPU utilization goes from 20-30% to 80-95%. For variable-length LLM workloads (some requests are 10 tokens, some are 2,000 tokens), continuous batching gives 3-10x better throughput with the same hardware.

vLLM, TGI, and TensorRT-LLM all implement continuous batching. This is one of the most important advances in LLM serving infrastructure in recent years.

---

**Q8: Describe the memory hierarchy of a modern GPU inference stack and how it impacts latency.**

**A:** GPU inference performance is often bounded by memory bandwidth, not compute. Understanding the hierarchy:

```
Registers (fastest):     Per-SM, ~256KB, sub-nanosecond access
L1 Cache:                Per-SM, ~192KB, ~20 cycles
L2 Cache:                On-die, ~40MB (A100), ~200 cycles
HBM (VRAM):              On-package, 40-80GB, ~350 cycles, 2 TB/s bandwidth
PCIe (System RAM):       Off-package, ~700 GB/s bandwidth, ~μs latency
CPU DRAM:                Fallback, ~50 GB/s bandwidth, ~μs latency
```

For a 70B float16 model: 140GB of weights. They must fit in VRAM. If they don't, the system pages to system RAM — which is 30-40x slower bandwidth. This is why model quantization (reducing from float16 to int4) is not just about speed — it is often about whether the model fits in VRAM at all.

**Flash Attention** is the key innovation that addresses the attention bottleneck: it recomputes attention in blocks that fit in L1/L2 cache rather than materializing the full N×N attention matrix in HBM, reducing memory bandwidth usage by 5-20x for the attention layers.

---

**Q9: How would you design a latency optimization strategy for an LLM application with P99 > 15 seconds that needs to reach P99 < 1 second?**

**A:** A 15x improvement is achievable but requires attacking multiple layers simultaneously:

**Step 1 — Profile** (2 days): Instrument every stage with OpenTelemetry. Find where the 15 seconds actually lives. Common finding: 10s is output generation (too many tokens), 3s is context processing, 2s is network.

**Step 2 — Reduce output length** (1 week): If the model is generating 2,000 tokens per response, you can reduce to 500 with: shorter prompts that ask for concise answers, adding `max_tokens` limits, output format constraints (JSON instead of prose), system prompt instructions ("answer in 3 sentences").

**Step 3 — Quantize** (1-2 days): Move to int8 or int4. This reduces the per-token generation time by 2-3x.

**Step 4 — Implement caching** (1 week): If system prompt is long and shared, enable prompt caching. If responses repeat (FAQ-type), add semantic caching. A 30% cache hit rate at 1ms vs 5s latency changes your P99 dramatically.

**Step 5 — Streaming** (1 day): Even if total latency is 2 seconds, streaming makes P99 for "user sees first token" drop to ~200ms. The perceived experience is completely different.

**Step 6 — Hardware** (if needed): Move from T4 to A100. Cost increases 10x but you get 4-5x faster inference.

**Step 7 — Smaller model** (2-4 weeks): If a 7B model can handle 80% of requests, route those to the 7B (fast) and only send the hard 20% to the 70B (slow). Reduces average latency by 5-8x.

Combined, these steps routinely get teams from 15s P99 to sub-1s P99.

---

## 📂 Navigation
