# Inference Optimization — Interview Q&A

## Beginner Level

**Q1: What is model quantization and why does it help with inference?**

**A:** Quantization is the process of representing model weights with lower-precision numbers. Neural network weights are typically stored as 32-bit floating point numbers (FP32). Quantization maps them to 16-bit floats (FP16), 8-bit integers (INT8), or 4-bit integers (INT4).

Why it helps:
1. **Memory reduction** — halving precision from FP32 to FP16 halves the VRAM required. A 7B model that needs 28 GB in FP32 fits in 14 GB in FP16 and just ~4 GB in INT4. This is the difference between needing 4× A100s vs a single consumer GPU.

2. **Speed increase** — modern GPUs have dedicated hardware (Tensor Cores) that perform INT8 and FP16 operations 2-8× faster than FP32. Operations that are memory-bandwidth bound (common in transformers) benefit even more.

3. **Cost reduction** — smaller memory footprint = fewer GPUs needed = lower cloud costs.

The trade-off is a small quality loss: some information is lost when mapping continuous FP32 values to a small set of discrete integers. In practice, INT8 quantization is nearly lossless for most tasks; INT4 introduces a small but measurable quality decrease.

---

**Q2: What does `device_map="auto"` do when you pass it to `from_pretrained`?**

**A:** `device_map="auto"` tells the `accelerate` library to automatically distribute the model layers across all available hardware — multiple GPUs if present, plus CPU as an overflow.

Without `device_map`, `from_pretrained` loads the entire model onto a single device. For a 7B model in FP16 (14 GB) on a GPU with 10 GB of VRAM, this fails with an out-of-memory error.

With `device_map="auto"`:
- `accelerate` measures how much VRAM each device has
- It creates a "device map" that assigns each layer to a device that has room for it
- Layers assigned to GPU execute at GPU speed; layers on CPU execute at CPU speed (slower but still functional)
- Activations are automatically moved between devices as needed during the forward pass

```python
# Check where layers ended up
print(model.hf_device_map)
# {'model.embed_tokens': 0, 'model.layers.0-15': 0, 'model.layers.16-31': 1, 'lm_head': 1}
```

This makes it possible to run very large models on hardware that would otherwise be insufficient.

---

**Q3: What is the difference between FP16 and BF16? Which should you prefer?**

**A:** Both FP16 and BF16 use 16 bits per number, but they allocate those bits differently:

- **FP16:** 1 sign bit, 5 exponent bits, 10 mantissa bits. High precision but limited range.
- **BF16 (Brain Float 16):** 1 sign bit, 8 exponent bits, 7 mantissa bits. Same range as FP32 but lower precision.

The key practical difference: FP16 has a narrower range of representable values. Large activations in transformer models can overflow FP16 (become ±Inf), causing loss spikes or NaN values during training. BF16 has the same exponent range as FP32, so these overflow events can't happen.

**Recommendation:**
- **For inference:** Either works fine. FP16 and BF16 produce essentially identical quality at inference time.
- **For training:** Prefer BF16 if your GPU supports it (NVIDIA Ampere = A100, A10, RTX 3090+ series). It avoids overflow issues and training instabilities, especially for large models.
- **For older GPUs (V100, T4):** FP16 is the only option; BF16 requires Ampere architecture.

In `TrainingArguments`, use `bf16=True` for Ampere GPUs and `fp16=True` for V100/T4.

---

## Intermediate Level

**Q4: Explain how bitsandbytes INT8 quantization (LLM.int8()) works. Why does it maintain quality better than naive INT8 quantization?**

**A:** Naive INT8 quantization maps the full range of a weight matrix to 256 integer values using a single scale factor. The problem: transformer weight matrices contain **outlier features** — a small number of dimensions with values 10-100× larger than the typical values. A single scale factor optimized for the outliers wastes resolution on the normal values, and vice versa.

**LLM.int8()** (from Tim Dettmers) solves this with a mixed decomposition:

1. **Identify outlier dimensions** — scan the input activations to find which feature dimensions have values above a threshold (e.g., > 6.0)
2. **Decompose the matrix multiplication into two parts:**
   - Outlier dimensions: compute in FP16 (preserves precision for the tricky values)
   - Normal dimensions: quantize to INT8 and compute in INT8 (fast, memory-efficient)
3. **Combine the two results** in FP16

The result: weights are stored in INT8 (half the memory of FP16), computation is mostly INT8 (fast), but outlier features that would cause accuracy loss are handled in FP16. The overhead of the decomposition is small (~20% slower than pure FP16) but the memory saving is significant.

This is why `load_in_8bit=True` maintains quality so well compared to simpler INT8 quantization approaches.

---

**Q5: What is Flash Attention and when should you use it?**

**A:** Standard transformer self-attention has memory complexity O(n²) in sequence length n. For a sequence of 2048 tokens, the attention matrix is 2048 × 2048 per head — manageable. For 8192 tokens, it's 8192 × 8192 — 16× larger. At some point (typically around 2K-4K tokens on consumer GPUs), you run out of VRAM just for the attention computation.

**Flash Attention** (and Flash Attention 2) is a rewrite of the attention algorithm that uses tiling (processing small blocks of the attention matrix at a time) to avoid materializing the full n × n attention matrix in memory:

- **Memory**: O(n) instead of O(n²) — scales linearly with sequence length
- **Speed**: 2-3× faster than standard attention for sequences > 512 tokens, because SRAM (on-chip memory) access is much faster than DRAM

```python
# Enable Flash Attention 2 (requires flash-attn package)
model = AutoModelForCausalLM.from_pretrained(
    "...",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.bfloat16,
)
```

**When to use it:**
- Long context applications (summarization of long documents, RAG with long retrieved chunks, code files)
- Any inference involving sequences > 1K tokens
- Production systems where GPU VRAM is constrained

**When NOT to use it:**
- Short sequences (< 512 tokens) — the tiling overhead means little benefit
- When building on non-NVIDIA hardware (Flash Attention requires CUDA)

---

**Q6: You're running a text classification service that receives 10,000 requests per day. The current setup processes one request at a time on a T4 GPU. How would you optimize the inference pipeline?**

**A:** This scenario is a classic case where batching and precision optimization will give massive improvements. Here's a step-by-step plan:

**Step 1 — Switch to FP16:** If still running FP32, switch to `torch_dtype=torch.float16` immediately. Halves memory, speeds up compute.

**Step 2 — Implement batching:** 10,000 requests/day = ~7 requests/minute on average. If requests arrive asynchronously, use a request queue that accumulates inputs for 50-100ms before processing them as a batch. A batch of 32 requests takes roughly the same GPU time as 1 request.

```python
# Async batching pattern
import asyncio
from collections import deque

request_queue = deque()

async def process_batch():
    while True:
        await asyncio.sleep(0.05)  # Wait 50ms to accumulate requests
        if request_queue:
            batch = [request_queue.popleft() for _ in range(min(32, len(request_queue)))]
            results = classifier([r.text for r in batch], batch_size=32)
            for req, result in zip(batch, results):
                req.future.set_result(result)
```

**Step 3 — Consider ONNX Runtime:** For a classification model (not generation), export to ONNX and run with Optimum. On T4, ONNX Runtime is typically 2-3× faster than PyTorch for classifier inference.

**Step 4 — Quantize to INT8:** Use `load_in_8bit=True` to halve VRAM, potentially allowing a larger batch size.

**Step 5 — Dynamic padding:** Ensure `DataCollatorWithPadding` is used in the DataLoader so each batch only pads to its longest sequence, not the model's max length.

With these changes, throughput could increase 10-20× from the baseline.

---

## Advanced Level

**Q7: What is speculative decoding and how does it speed up LLM generation?**

**A:** LLM generation is **sequential** — each token depends on all previous tokens. You cannot parallelize across tokens. This makes generation fundamentally different from classification (where the entire sequence is processed in one forward pass).

**Speculative decoding** exploits the fact that a smaller "draft" model runs much faster than the target model, and the target model can verify multiple tokens in a single forward pass:

1. **Draft phase:** A small, fast model (draft model, e.g., 68M params) generates `k` candidate tokens speculatively (e.g., k=4)
2. **Verify phase:** The large target model processes all `k` draft tokens in a single parallel forward pass (since it sees them all at once) and computes probabilities for each
3. **Accept/reject:** The target model accepts draft tokens where its probability matches the draft model's distribution. At the first rejection, it samples a new token from the target model's distribution and discards subsequent draft tokens
4. **Repeat**

**Why this helps:** The target model's forward pass is parallel across positions. Verifying 4 tokens takes barely more time than verifying 1 token. If the draft model gets 3 out of 4 tokens right (common for easy continuations), you effectively generated 3 tokens for the cost of 1 target model forward pass.

Typical speedup: 2-3× for most language generation tasks. Works best when the target model would produce predictable (greedy) outputs.

```python
# Speculative decoding in transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

draft_model = AutoModelForCausalLM.from_pretrained("facebook/opt-125m")
target_model = AutoModelForCausalLM.from_pretrained("facebook/opt-6.7b")

inputs = tokenizer("The capital of France is", return_tensors="pt")
outputs = target_model.generate(
    **inputs,
    assistant_model=draft_model,  # Enables speculative decoding
    max_new_tokens=100,
)
```

---

**Q8: Compare quantization approaches: bitsandbytes (PyTorch), GGUF (llama.cpp), and GPTQ. What are the trade-offs?**

**A:**

**bitsandbytes (INT8/INT4):**
- **Loading:** Dynamic quantization at load time — weights are quantized when loaded, not pre-quantized
- **Format:** Stored as FP16, quantized in memory
- **GPU required:** Yes (bitsandbytes requires CUDA)
- **Quality:** LLM.int8() maintains very high quality; NF4 has minimal loss
- **Best for:** Fine-tuning (QLoRA), GPU inference in Python/transformers ecosystem

**GGUF (llama.cpp):**
- **Loading:** Pre-quantized file format — weights are stored already quantized
- **Format:** Various levels (Q4_0, Q4_K_M, Q8_0, etc.) in a single file
- **GPU required:** No — runs on CPU, but can offload some layers to GPU
- **Quality:** Q4_K_M is considered the best quality/size tradeoff
- **Best for:** Local inference on consumer hardware (laptops, desktops) without GPU; Ollama uses this format

**GPTQ:**
- **Loading:** Pre-quantized using an optimization algorithm that minimizes quantization error layer by layer
- **Format:** Pre-computed — quantization happens once offline using a calibration dataset
- **GPU required:** Yes — designed for GPU inference
- **Quality:** Often slightly better than bitsandbytes NF4 at same bit-width because it's optimized offline
- **Best for:** Production GPU inference where you can afford the offline quantization step; AutoGPTQ library

**Summary:**
- Running locally on laptop without GPU → GGUF
- Fine-tuning on GPU → bitsandbytes (QLoRA)
- Production GPU inference with best quality → GPTQ
- Quick GPU inference without pre-quantization → bitsandbytes INT4

---

**Q9: You need to serve a 70B parameter LLM with < 200ms latency for an API. Walk through your optimization strategy.**

**A:** A 70B model is roughly 140 GB in FP16 — requiring at minimum 2× A100 80GB GPUs. Achieving 200ms latency for generation (say, up to 200 output tokens) requires:

**Hardware setup:**
- 2-4× A100 80GB or H100s with NVLink (fast GPU-to-GPU transfer)
- High memory bandwidth CPUs (for KV cache management)

**Model loading:**
```python
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-70b-hf",
    torch_dtype=torch.bfloat16,         # BF16 for stability
    device_map="auto",                   # Auto-distribute across GPUs
    attn_implementation="flash_attention_2",  # Essential for long contexts
)
```

**Serving framework:** Don't use raw transformers for production serving. Use **vLLM**:
- Implements **continuous batching** (batch across concurrent requests, not just one request at a time)
- **PagedAttention** — manages KV cache memory in pages, allowing 2-5× more concurrent requests
- Supports tensor parallelism natively

**Quantization consideration:** INT4 (bitsandbytes NF4 or GPTQ) would halve memory to ~35-40 GB total, fitting on 1× A100 80GB. The latency trade-off: slightly slower compute but potentially faster due to better memory bandwidth. Benchmark both.

**KV cache:** For a 70B model with 80 transformer layers and typical KV dimensions, each generated token adds ~20 MB to the KV cache per request. For 8 concurrent requests generating 500 tokens, that's ~80 GB just in KV cache. Use PagedAttention (vLLM) to manage this efficiently.

**Latency benchmark target:**
- Time to first token (TTFT): the first forward pass, typically 50-100ms with optimized setup
- Inter-token latency: subsequent tokens, ~10-30ms each on A100
- Total for 50 tokens: TTFT + 49 × inter_token ≈ 150-200ms — achievable

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full inference optimization explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | Interview questions (you are here) |
| [📄 Code_Example.md](./Code_Example.md) | Working optimization examples |
| [📄 Comparison.md](./Comparison.md) | FP32 vs INT8 vs INT4 vs GGUF |

⬅️ **Prev:** [Trainer API](../05_Trainer_API/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Spaces and Gradio](../07_Spaces_and_Gradio/Theory.md)
