# Cheatsheet — Latency Optimization

**Latency optimization** is the practice of reducing the time from request to response in an AI system — measured in milliseconds, tracked at P50/P95/P99 percentiles.

---

## Key Terms

| Term | Definition |
|---|---|
| **Latency** | Time from request sent to response received (ms) |
| **P50 / P95 / P99** | Percentile latency: P99 = 99% of requests are faster than this value |
| **TTFT** | Time To First Token — for LLMs, how long until the first character appears |
| **Throughput** | Requests (or tokens) processed per second |
| **Quantization** | Reducing numerical precision of weights (float32 → int8 → int4) |
| **Distillation** | Training a small "student" model to mimic a large "teacher" model |
| **Speculative decoding** | Small model drafts tokens; large model verifies in parallel |
| **KV cache** | Cached key-value attention states; avoid recomputing for repeated prefixes |
| **Dynamic batching** | Collect requests arriving within a short window; process together |
| **Continuous batching** | For LLMs: add new requests to the batch as existing ones finish |

---

## Optimization Techniques — Quick Reference

| Technique | Typical Speedup | Memory Impact | Quality Impact | Best For |
|---|---|---|---|---|
| **Quantization int8** | 2-3x | -50% | Tiny (< 1% accuracy drop) | All models |
| **Quantization int4** | 3-4x | -75% | Small-moderate | LLMs, acceptable tradeoff |
| **Dynamic batching** | 5-20x throughput | Neutral | None | High-traffic APIs |
| **Continuous batching** | 3-10x throughput (LLMs) | Neutral | None | LLM serving |
| **Model distillation** | 3-10x | 60-90% smaller | Small | When you can retrain |
| **ONNX export** | 1.5-3x | Neutral | None | PyTorch → production |
| **TensorRT** | 2-5x | Slight reduction | None | NVIDIA GPU only |
| **Speculative decoding** | 2-3x | +small model VRAM | None | Long text generation |
| **Flash Attention** | 2-4x memory, 1.5x speed | -60% memory | None | Transformer attention |
| **KV cache (prompt)** | 10-100x for repeated prefix | +VRAM for cache | None | LLMs with shared context |
| **Response caching** | Near-zero latency | +cache storage | None | Repeated exact queries |
| **Streaming** | Same total time, better perceived | None | None | Any text generation |

---

## GPU Hardware Comparison

| GPU | VRAM | FP16 TFLOPS | Best For | Rough Cost (cloud/hr) |
|---|---|---|---|---|
| **T4** | 16 GB | 65 | Inference, small models | ~$0.35 |
| **A10G** | 24 GB | 125 | Mid-size models, 7B-13B | ~$1.00 |
| **A100 40GB** | 40 GB | 312 | Large models, training | ~$3.50 |
| **A100 80GB** | 80 GB | 312 | 70B models, big batches | ~$5.00 |
| **H100** | 80 GB | 990 | Fastest inference, training | ~$8.00 |

---

## Latency Budget Template

For a target P99 of 500ms, a typical LLM app budget:
```
Network (client → server):   ~50ms
API gateway + auth:           ~10ms
Queue wait:                   ~20ms
Preprocessing (tokenize):     ~5ms
Model inference:             ~380ms  ← biggest opportunity
Postprocessing:               ~5ms
Network (server → client):   ~30ms
───────────────────────────────────
Total:                       ~500ms
```
Profile each layer. Optimize the biggest chunk first.

---

## Quantization Cheat Code

```python
import torch
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")

# Dynamic quantization — no calibration data needed, instant
model_int8 = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},   # quantize all linear layers
    dtype=torch.qint8
)
# Typical result: 1.5-2x faster on CPU, 40% smaller model file
```

---

## When to Use Each Technique

**Quantization** → First thing to try. Free speedup, minimal quality loss. Start with int8; try int4 only if memory is the constraint.

**Batching** → Essential for any API serving multiple users. Set max batch size + short timeout (5-10ms).

**Caching** → If any inputs repeat (same question, same system prompt), caching is free latency wins.

**Distillation** → When quantization is not enough and you can afford retraining. 3-10x win.

**Speculative decoding** → For LLMs where you need faster token generation without changing quality.

**Hardware upgrade** → When you've hit the ceiling on software optimizations. Moving T4→A100 gives ~4x for the same model.

---

## Golden Rules

- **Measure P99 first** — never optimize without a baseline measurement
- **Profile before optimizing** — find the actual bottleneck (it is often not what you expect)
- **Quantize by default** — int8 is almost always worth it; run your eval suite to confirm
- **Stream LLM responses** — perceived latency is dramatically better even if total latency is the same
- **Continuous batching > static batching** for LLMs — never wait for a fixed batch to fill
- **Cache aggressively** — the fastest inference is no inference at all
- **Check quality after every optimization** — latency wins that break quality are not wins

---

## 📂 Navigation
