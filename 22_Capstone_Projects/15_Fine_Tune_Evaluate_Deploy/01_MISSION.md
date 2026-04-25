# 01 Mission — Fine-Tune, Evaluate, and Deploy

## The Story

In 2023, a healthcare company needed an AI model that followed their specific clinical documentation style — precise terminology, structured output format, zero tolerance for hedging language. They tried prompt engineering for six months. The model would drift back to its default style within 3–4 turns, especially in edge cases.

The solution was fine-tuning — specifically, parameter-efficient fine-tuning (PEFT) with LoRA, which let them adapt a 7B parameter model to their exact documentation style in 48 hours using two A100 GPUs, at a cost of roughly $40 in compute.

But fine-tuning is only one-third of the problem. The other two thirds are: (1) measuring whether it actually improved anything (evaluation), and (2) serving it to users in a way that is fast, cheap, and observable. This project covers the complete loop.

This is the capstone of the Advanced Path. Everything you have learned — RAG, evaluation, agents, production engineering — converges here.

---

## What You Build

The full MLOps loop for a custom instruction-following model:

1. **Dataset Preparation** — 50+ instruction/output pairs in the Alpaca format, with validation/test splits
2. **QLoRA Fine-Tuning** — LoRA adapters on a 7B HuggingFace model using TRL's SFTTrainer with 4-bit quantization
3. **Before/After Evaluation** — LLM-as-judge scores the base model vs. fine-tuned model on your task
4. **4-bit Quantization** — bitsandbytes int4 quantization for inference
5. **FastAPI Serving** — A REST endpoint that serves the model with streaming support
6. **Observability** — Token logging, latency tracking, cost estimation, per-request telemetry

**Deliverable:** A complete MLOps pipeline: dataset → trained model → evaluation report → live API endpoint with metrics dashboard.

---

## Concepts You Apply

| Topic | What You Apply |
|---|---|
| Fine-Tuning in Production | LoRA, QLoRA, dataset construction |
| PEFT Deep Dive | r, alpha, target_modules, merged adapters |
| Inference Optimization | 4-bit quantization, bitsandbytes |
| Latency Optimization | Streaming, batching, token budget |
| Cost Optimization | Token logging, model routing |
| Observability | Traces, metrics, per-request logging |

**Theory files to read first:**
- `12_Production_AI/08_Fine_Tuning_in_Production/Theory.md`
- `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/Theory.md`
- `14_Hugging_Face_Ecosystem/06_Inference_Optimization/Theory.md`
- `12_Production_AI/05_Observability/Theory.md`
- `12_Production_AI/02_Latency_Optimization/Theory.md`

---

## Prerequisites

- Python advanced: async, context managers, dataclasses
- Familiar with HuggingFace `transformers` and basic model loading
- **GPU required for training:** minimum 16GB VRAM (A100/3090/4090) or Google Colab Pro+
- Anthropic SDK for LLM-as-judge evaluation
- Comfortable running long training jobs (1–3 hours)

---

## Difficulty and Format

**Difficulty: 5 / 5 — Expert**

This project requires GPU compute, deep HuggingFace knowledge, and familiarity with the full ML stack. Each component is non-trivial. Plan for debugging time.

**Learning format tier: Expert Capstone**

Two files: `train.py` and `serve.py`. Each is a near-complete implementation with `# TODO:` markers for the most conceptually important steps. The project can be run phase by phase — you do not need to complete training before testing the API server with a CPU fallback.

**Recommended model:**
- `microsoft/phi-2` (2.7B) for CPU/low-VRAM testing
- `mistralai/Mistral-7B-Instruct-v0.3` (7B, requires 16GB+ VRAM with QLoRA)

---

## Success Looks Like

```
=== Phase 1: Dataset ===
Loaded 50 training examples, 10 validation, 10 test
Average input length: 142 tokens, output: 87 tokens

=== Phase 2: Training ===
Loading base model with 4-bit quantization...
Applying LoRA adapters: r=8, alpha=32, dropout=0.05
  trainable params: 4,718,592 || all params: 2,784,788,480 || trainable%: 0.169
Epoch 3/3: loss=0.7104
Saving adapter to ./adapters/phi2-custom-v1/

=== Phase 3: Evaluation ===
Base model average score:       3.1 / 5
Fine-tuned model average score: 4.4 / 5
Improvement: +1.3 points (42% better)

=== Phase 4: API Server ===
POST /generate {"prompt": "Write a clinical note for..."}
{"response": "...", "latency_ms": 847, "input_tokens": 42, "output_tokens": 118, "cost_usd": 0.000012}
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| **01_MISSION.md** | you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and component table |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code (train.py + serve.py) |
| [04_RECAP.md](./04_RECAP.md) | Concepts applied, extensions, job mapping |

⬅️ **Prev:** [14_Multi_Agent_Research_System](../14_Multi_Agent_Research_System/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Capstone README](../README.md)
