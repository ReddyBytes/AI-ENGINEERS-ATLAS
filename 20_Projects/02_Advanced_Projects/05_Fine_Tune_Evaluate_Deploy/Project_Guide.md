# Project 5: Fine-Tune, Evaluate, and Deploy

## Why This Project Matters

In 2023, a healthcare company needed an AI model that followed their specific clinical documentation style — precise terminology, structured output format, zero tolerance for hedging language. They tried prompt engineering for six months. The model would drift back to its default style within 3-4 turns, especially in edge cases.

The solution was fine-tuning — specifically, parameter-efficient fine-tuning (PEFT) with LoRA, which let them adapt a 7B parameter model to their exact documentation style in 48 hours using two A100 GPUs, at a cost of roughly $40 in compute.

But fine-tuning is only one-third of the problem. The other two thirds are: (1) measuring whether it actually improved anything (evaluation), and (2) serving it to users in a way that's fast, cheap, and observable. This project covers the complete loop.

This is the capstone of the Advanced Path. Everything you've learned — RAG, evaluation, agents, production engineering — converges here.

---

## What You'll Build

The full MLOps loop for a custom instruction-following model:

1. **Dataset Preparation** — 50+ instruction/output pairs in the Alpaca format, with validation/test splits
2. **QLoRA Fine-Tuning** — LoRA adapters on a 7B HuggingFace model using TRL's SFTTrainer with 4-bit quantization
3. **Before/After Evaluation** — LLM-as-judge scores the base model vs. fine-tuned model on your task
4. **4-bit Quantization** — bitsandbytes int4 quantization for inference
5. **FastAPI Serving** — A REST endpoint that serves the model with streaming support
6. **Observability** — Token logging, latency tracking, cost estimation, per-request telemetry

**Deliverable:** A complete MLOps pipeline: dataset → trained model → evaluation report → live API endpoint with dashboard.

---

## Learning Objectives

By completing this project, you will:

- Prepare a fine-tuning dataset in the correct chat template format
- Configure LoRA hyperparameters (`r`, `alpha`, `target_modules`)
- Run QLoRA training with gradient checkpointing and 4-bit quantization
- Evaluate before/after improvement using LLM-as-judge
- Quantize a model to 4-bit with bitsandbytes for memory-efficient inference
- Serve a HuggingFace model via FastAPI with streaming
- Instrument LLM calls with latency, token count, and cost tracking

---

## Topics Covered

| Advanced Path Topic | What You Apply Here |
|---|---|
| Topic 3 — Fine-Tuning in Production | LoRA, QLoRA, dataset construction |
| Topic 4 — PEFT Deep Dive | r, alpha, target_modules, merged adapters |
| Topic 5 — Inference Optimization | 4-bit quantization, bitsandbytes |
| Topic 27 — Latency Optimization | Streaming, batching, token budget |
| Topic 28 — Cost Optimization | Token logging, model routing |
| Topic 29 — Observability | Traces, metrics, per-request logging |

---

## Prerequisites

- Python advanced: async, context managers, dataclasses
- Familiar with HuggingFace `transformers` and basic model loading
- **GPU required** for training: minimum 16GB VRAM (A100/3090/4090) or Google Colab Pro+
- Anthropic SDK for LLM-as-judge evaluation
- Comfortable running long training jobs (1–3 hours)

---

## Difficulty

**5 / 5 — Expert**

This project requires GPU compute, deep HuggingFace knowledge, and familiarity with the full ML stack. Each component is non-trivial. Plan for debugging time.

---

## Tools & Libraries

| Tool | Purpose |
|---|---|
| `transformers` | Model loading, tokenization, generation |
| `peft` | LoRA adapter application and management |
| `trl` | SFTTrainer for supervised fine-tuning |
| `bitsandbytes` | 4-bit and 8-bit quantization |
| `datasets` | Dataset loading and processing |
| `fastapi` | REST API serving |
| `uvicorn` | ASGI server for FastAPI |
| `anthropic` | LLM-as-judge evaluation |
| `torch` | PyTorch (GPU) |

---

## Recommended Model

**`microsoft/phi-2`** (2.7B) for CPU/low-VRAM testing, or
**`mistralai/Mistral-7B-Instruct-v0.3`** (7B, requires 16GB+ VRAM with QLoRA).

The starter code uses Phi-2 for accessibility but documents the Mistral configuration.

---

## Expected Output

```
=== Phase 1: Dataset ===
Loaded 50 training examples, 10 validation, 10 test
Average input length: 142 tokens, output: 87 tokens

=== Phase 2: Training ===
Loading base model with 4-bit quantization...
Applying LoRA adapters: r=8, alpha=32, dropout=0.05
  trainable params: 4,718,592 || all params: 2,784,788,480 || trainable%: 0.169
Epoch 1/3: loss=1.2341
Epoch 2/3: loss=0.8923
Epoch 3/3: loss=0.7104
Saving adapter to ./adapters/phi2-custom-v1/

=== Phase 3: Evaluation ===
Evaluating base model vs. fine-tuned model on 10 test examples...
Base model average score:      3.1 / 5
Fine-tuned model average score: 4.4 / 5
Improvement: +1.3 points (42% better)

=== Phase 4: API Server ===
FastAPI server starting on http://localhost:8000
Docs: http://localhost:8000/docs

POST /generate {"prompt": "Write a clinical note for..."} →
{"response": "...", "latency_ms": 847, "input_tokens": 42, "output_tokens": 118, "cost_usd": 0.000012}
```

---

## Extension Challenges

1. Implement DPO (Direct Preference Optimization) using TRL's `DPOTrainer` as an alternative to SFT
2. Merge LoRA adapters into the base model for faster inference
3. Add model versioning: track which adapter version produced which outputs
4. Implement A/B testing: randomly route 50% of requests to base, 50% to fine-tuned, compare quality
5. Add a continuous retraining trigger: when average judge score drops below 3.5, flag for retraining
6. Deploy with Docker and serve with vLLM for production throughput

---

## Theory Files to Read First

Before coding, read:
- `12_Production_AI/08_Fine_Tuning_in_Production/Theory.md`
- `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/Theory.md`
- `14_Hugging_Face_Ecosystem/06_Inference_Optimization/Theory.md`
- `12_Production_AI/02_Latency_Optimization/Theory.md`
- `12_Production_AI/05_Observability/Theory.md`
- `12_Production_AI/03_Cost_Optimization/Theory.md`
