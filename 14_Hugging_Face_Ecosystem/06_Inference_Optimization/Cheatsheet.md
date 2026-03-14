# Inference Optimization — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Quantization** | Reduce weight precision (FP32 → FP16 → INT8 → INT4) to save memory and increase speed |
| **bitsandbytes** | Python library that implements INT8 and INT4 quantization for transformers |
| **device_map="auto"** | Automatically distribute model layers across all available GPUs and CPU |
| **Flash Attention** | Memory-efficient attention algorithm — linear memory instead of quadratic |
| **batch inference** | Process multiple inputs simultaneously — the single biggest throughput lever |
| **Optimum** | Hugging Face library for exporting models to ONNX, TensorRT, OpenVINO |
| **GGUF** | Quantized model format used by llama.cpp and Ollama for local CPU inference |
| **torch.compile** | JIT-compiles PyTorch ops into fused GPU kernels for faster inference |
| **speculative decoding** | Use a small draft model to propose tokens, large model verifies — faster generation |
| **NF4** | 4-bit Normal Float — the quantization format used in QLoRA/bitsandbytes INT4 |

---

## Loading at Different Precisions

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# FP32 (default) — full precision, most memory
model_fp32 = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")

# FP16 — half precision, 2× less memory, faster on GPU
model_fp16 = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",
    torch_dtype=torch.float16,
    device_map="auto"
)

# BF16 — same range as FP32, more stable on Ampere+ GPUs
model_bf16 = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# INT8 — 4× less memory than FP32, minimal quality loss
model_int8 = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",
    load_in_8bit=True,
    device_map="auto"
)

# INT4 (QLoRA style) — 8× less memory than FP32, small quality loss
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
model_int4 = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",
    quantization_config=bnb_config,
    device_map="auto"
)
```

---

## Quantization Comparison Table

| Format | Bytes/param | 7B model VRAM | Speed vs FP32 | Quality loss |
|--------|------------|---------------|---------------|--------------|
| FP32 | 4 bytes | ~28 GB | 1× | None (baseline) |
| FP16 | 2 bytes | ~14 GB | 1.5–2× | Negligible |
| BF16 | 2 bytes | ~14 GB | 1.5–2× | Negligible |
| INT8 | 1 byte | ~7 GB | 1.5–2× | Very small |
| INT4 (NF4) | 0.5 bytes | ~4 GB | 1.5–2× | Small |
| GGUF Q4_K_M | ~0.45 bytes | ~3.8 GB | CPU-optimized | Small |

---

## Device Map Options

```python
# Auto: best automatic distribution
model = AutoModelForCausalLM.from_pretrained("...", device_map="auto")

# Balanced: try to load equal amount on each GPU
model = AutoModelForCausalLM.from_pretrained("...", device_map="balanced")

# Sequential: fill GPU 0 first, then GPU 1, etc.
model = AutoModelForCausalLM.from_pretrained("...", device_map="sequential")

# Manual: exact control
model = AutoModelForCausalLM.from_pretrained("...", device_map={
    "model.embed_tokens": 0,
    "model.layers.0": 0,
    "model.layers.1": 1,
    "lm_head": 1,
})

# Limit GPU memory, spill overflow to CPU
model = AutoModelForCausalLM.from_pretrained("...", device_map="auto",
    max_memory={0: "20GiB", 1: "20GiB", "cpu": "60GiB"})
```

---

## Flash Attention 2

```python
# pip install flash-attn --no-build-isolation (requires CUDA)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    attn_implementation="flash_attention_2",  # Use Flash Attention 2
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
# Up to 3× faster and much less memory for long sequences
```

---

## torch.compile for Faster Inference

```python
import torch

# Compile model for optimized GPU execution
model = AutoModelForCausalLM.from_pretrained("...", torch_dtype=torch.float16).cuda()
model.eval()

# Compile: first call is slow (JIT compilation), subsequent calls are fast
model = torch.compile(model, mode="reduce-overhead")

# Now run inference — significantly faster on 2nd+ call
with torch.no_grad():
    output = model.generate(inputs, max_new_tokens=100)
```

---

## Optimum — ONNX Runtime (CPU Speedup)

```python
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

# Loads model as ONNX and runs with ONNX Runtime
# Typically 2–4× faster than PyTorch on CPU
model = ORTModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english",
    from_transformers=True
)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
inputs = tokenizer("This is great!", return_tensors="pt")
outputs = model(**inputs)
```

---

## When to Use vs When NOT to Use Each Optimization

| ✅ Use when | ❌ Avoid when |
|------------|--------------|
| FP16/BF16: any GPU inference | FP16: on CPUs (slower, errors) |
| INT8: large model, tight VRAM budget | INT8: small models (<1B) — overhead not worth it |
| INT4: model barely fits in GPU at all | INT4: safety-critical tasks needing max precision |
| `device_map="auto"`: multi-GPU or too-large models | device_map: single GPU + model fits — adds overhead |
| Batching: offline processing 100+ samples | Batching: real-time single-query APIs |
| Flash Attention: long sequences (> 1000 tokens) | Flash Attention: very short sequences |
| torch.compile: stable models, many inferences | torch.compile: frequent model changes |

---

## Golden Rules

1. **Always use FP16 or BF16 on GPU** — there is no reason to run FP32 for inference.
2. **Batch your inputs** — single-sample inference wastes GPU parallelism; batch 32+ samples.
3. **Use `device_map="auto"` for large models** — it handles multi-GPU and CPU offloading automatically.
4. **Profile before optimizing** — use `torch.profiler` or `nvidia-smi` to find the actual bottleneck.
5. **INT8 before INT4** — try INT8 first; only drop to INT4 if INT8 doesn't fit in VRAM.
6. **Test quality after quantization** — always benchmark your actual task metric after quantizing.

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full inference optimization explanation |
| 📄 **Cheatsheet.md** | Quick reference (you are here) |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | Working optimization examples |
| [📄 Comparison.md](./Comparison.md) | FP32 vs INT8 vs INT4 vs GGUF comparison |

⬅️ **Prev:** [Trainer API](../05_Trainer_API/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Spaces and Gradio](../07_Spaces_and_Gradio/Theory.md)
