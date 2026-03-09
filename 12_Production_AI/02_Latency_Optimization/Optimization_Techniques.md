# Optimization Techniques — Latency Optimization

A comprehensive reference for every major latency optimization technique in AI serving systems. Each entry includes: what it does, expected speedup, how to apply it, and caveats.

---

## Master Reference Table

| Technique | Category | Speedup | Memory Impact | Quality Impact | Effort | When to Use |
|---|---|---|---|---|---|---|
| **INT8 Quantization** | Model compression | 2-3x | -50% | Negligible | Low | First thing to try; almost always worth it |
| **INT4 Quantization** | Model compression | 3-4x | -75% | Small | Low | When INT8 not enough; check quality carefully |
| **FP16/BF16** | Model compression | 1.5-2x vs FP32 | -50% | Negligible | Very Low | Default for all GPU inference |
| **ONNX export** | Compilation | 1.5-3x | Neutral | None | Low | PyTorch models going to production |
| **TensorRT** | Compilation | 2-5x | Slight reduction | None | Medium | NVIDIA GPU only; major win |
| **Flash Attention** | Architecture | 1.5-2x + memory | -60% memory | None | Low (library) | All transformer models |
| **Dynamic batching** | Serving | 5-20x throughput | Neutral | None | Low | Any multi-user API |
| **Continuous batching** | Serving | 3-10x throughput | Neutral | None | Medium | LLM serving specifically |
| **Response caching** | Caching | Near-zero latency | +storage | None | Low | Repeated exact queries |
| **Semantic caching** | Caching | Near-zero latency | +storage | None | Medium | Near-duplicate queries |
| **KV cache / Prompt caching** | Caching | 2-10x for cached prefix | +VRAM | None | Low | Long shared system prompts |
| **Streaming** | UX | Same total, better TTFT | None | None | Very Low | All interactive LLM apps |
| **Speculative decoding** | Decoding | 2-3x | +small model VRAM | None | High | Long text generation |
| **Model distillation** | Model compression | 3-10x | 60-90% smaller | Small | Very High | When you can retrain |
| **Pruning** | Model compression | 1.5-3x | 20-50% smaller | Small-medium | High | Sparse hardware support needed |
| **Early exit** | Architecture | 1.5-5x (avg case) | None | Small | High | When most inputs are "easy" |
| **Hardware upgrade** | Infrastructure | 2-10x | N/A | None | High (cost) | After software options exhausted |
| **Tensor parallelism** | Infrastructure | Near-linear with GPUs | Distributed | None | High | Models too large for one GPU |
| **Compiled kernels (Triton/CUDA)** | Low-level | 2-4x on hot paths | Neutral | None | Very High | Custom architectures |

---

## Technique Deep Dives

### 1. Quantization

**What it does:** Reduces the bit-width of model weights and activations. FP32 → INT8 cuts memory 4x and enables integer arithmetic which is faster on modern hardware.

**How to apply:**

```python
# Option A: Dynamic quantization (CPU, zero calibration needed)
import torch
model_int8 = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear, torch.nn.LSTM},
    dtype=torch.qint8
)

# Option B: HuggingFace bitsandbytes (GPU, LLMs)
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,          # INT8
    # load_in_4bit=True,        # INT4 (more aggressive)
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b",
    quantization_config=quantization_config,
    device_map="auto"
)
```

**Speedup details:**
- CPU: 1.5-2x (integer ops faster, memory bandwidth reduced)
- GPU with INT8 Tensor Cores (A100, H100): 2-3x
- GPTQ INT4: 3-4x; GGUF INT4 (llama.cpp): 3-5x on CPU

**When to be careful:** Complex arithmetic tasks (math, code) can degrade with int4. Always test on your evaluation set.

---

### 2. Flash Attention

**What it does:** Rewrites the attention computation to use GPU SRAM (fast cache) instead of HBM (slow VRAM). Standard attention materializes an N×N matrix in HBM; Flash Attention computes attention in tiles that fit in SRAM.

**How to apply:**

```python
# Option A: Install flash-attn library
# pip install flash-attn

# Option B: Use HuggingFace integration (automatic)
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    attn_implementation="flash_attention_2",
    torch_dtype=torch.float16
)
```

**Impact:**
- Memory: 5-20x reduction in attention memory usage (enables longer context)
- Speed: 1.5-3x faster for long sequences (memory bandwidth bound)
- Quality: mathematically equivalent to standard attention (no quality loss)

---

### 3. Continuous Batching (LLMs)

**What it does:** Processes new requests at each token generation step rather than waiting for a full batch to complete.

```
Static batching:
  Time: [----R1----][----R1----][----R1----] GPU busy
         wait for short R2       R2 starts

Continuous batching:
  Time: [R1,R2,R3,R4,R5,R6,R7,R8] all running
         R2 finishes → R9 joins immediately
```

**How to apply:** Use vLLM, TGI, or TensorRT-LLM — they implement this automatically.

```python
# vLLM example
from vllm import LLM, SamplingParams

llm = LLM(model="mistralai/Mistral-7B-v0.1")
sampling_params = SamplingParams(temperature=0.8, max_tokens=256)

# vLLM handles batching, continuous batching, KV cache management
outputs = llm.generate(["Explain quantum computing", "Write a poem"], sampling_params)
```

**Impact:** 3-10x throughput improvement for mixed-length workloads.

---

### 4. Speculative Decoding

**What it does:** Uses a small draft model to propose N tokens, then verifies them all in one pass with the large model.

```
Standard:    [big model] → token1 → [big model] → token2 → [big model] → token3
Speculative: [small model] → [t1,t2,t3,t4,t5] → [big model verifies all 5 at once]
             Accept t1,t2,t3,t4; reject t5; generate t5 from big model
             Net: 4 tokens for the price of ~1.5 big model forward passes
```

**Requirements:**
- Draft model must be from the same family (same tokenizer, compatible architecture)
- Best when draft model acceptance rate > 70%

**When to use:** Large models (30B+), long output sequences (500+ tokens), GPU with enough VRAM for both models.

---

### 5. Model Distillation

**What it does:** Train a small "student" model to match the output distribution of a large "teacher" model. The student learns both the correct answers AND the teacher's confidence levels (soft labels).

```python
# Distillation loss = cross-entropy loss + KL divergence with teacher
import torch.nn.functional as F

def distillation_loss(student_logits, teacher_logits, labels, temperature=4.0, alpha=0.5):
    # Hard label loss
    hard_loss = F.cross_entropy(student_logits, labels)

    # Soft label loss (distillation)
    soft_student = F.log_softmax(student_logits / temperature, dim=-1)
    soft_teacher = F.softmax(teacher_logits / temperature, dim=-1)
    soft_loss = F.kl_div(soft_student, soft_teacher, reduction='batchmean') * (temperature ** 2)

    return alpha * hard_loss + (1 - alpha) * soft_loss
```

**Result:** A student model that is 5-10x smaller but retains 90-95% of the teacher's quality.

**Examples:** DistilBERT (66% smaller than BERT, 97% of BERT's performance), TinyBERT, DistilGPT2.

---

### 6. ONNX Export + TensorRT

**What it does:** Converts a PyTorch model to an optimized computation graph. TensorRT further compiles it with kernel fusion, precision calibration, and GPU-specific optimizations.

```python
# Step 1: Export to ONNX
import torch
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=17,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}}
)

# Step 2: Convert to TensorRT (trtexec CLI)
# trtexec --onnx=model.onnx --saveEngine=model.trt --fp16

# Step 3: Run inference with TensorRT engine
import tensorrt as trt
# (Load engine and run with CUDA context)
```

**Impact:** 2-5x over PyTorch, especially for vision models. TensorRT fuses operations (e.g., conv + batchnorm + relu into one CUDA kernel).

---

## Optimization Decision Tree

```
Q1: Is this an LLM?
  YES → Enable continuous batching + Flash Attention first
  NO  → Continue to Q2

Q2: Is model too large for VRAM?
  YES → Quantize to INT8/INT4 first; if still too large → tensor parallel
  NO  → Continue to Q3

Q3: Is GPU utilization below 60%?
  YES → Implement request batching
  NO  → Continue to Q4

Q4: Are any requests identical/similar?
  YES → Add response caching / semantic caching
  NO  → Continue to Q5

Q5: Is it a PyTorch model on NVIDIA GPU?
  YES → Try ONNX export → TensorRT
  NO  → Continue to Q6

Q6: Still not fast enough?
  → Profile individual layers; consider distillation or hardware upgrade
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Optimization_Techniques.md** | ← you are here |

⬅️ **Prev:** [01 Model Serving](../01_Model_Serving/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Cost Optimization](../03_Cost_Optimization/Theory.md)
