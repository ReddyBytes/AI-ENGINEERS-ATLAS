# 04 Recap — Fine-Tune, Evaluate, and Deploy

## What You Built

The complete MLOps loop for a custom instruction-following model: dataset preparation, QLoRA fine-tuning with 4-bit quantization, before/after evaluation using LLM-as-judge, FastAPI serving with streaming, and a per-request observability layer that tracks latency, token counts, and compute cost. This is not a prototype — it is the same architecture used in production AI engineering teams.

---

## Concepts Applied

| Concept | How It Was Applied |
|---|---|
| QLoRA fine-tuning | Applied LoRA adapters (r=8, alpha=32) to a 4-bit quantized base model using TRL's SFTTrainer. Only ~0.1–0.5% of parameters were trained, but task adherence improved measurably. |
| LoRA hyperparameters | Configured rank (r), alpha, target_modules, and dropout. Understood the trade-off between adapter capacity, VRAM cost, and adaptation strength. |
| NF4 quantization | Used BitsAndBytesConfig with `bnb_4bit_quant_type="nf4"` to compress the base model from 14GB (float16) to ~4GB (4-bit), enabling training on consumer GPUs. |
| Chat template formatting | Applied the Alpaca template to format instruction/input/output triples into training sequences. SFTTrainer trains on the full sequence — not just the response. |
| LLM-as-judge evaluation | Scored base vs. fine-tuned model on task-specific criteria (task adherence, completeness, quality). Used the improvement delta as the primary training success signal. |
| FastAPI serving | Built a REST endpoint that tokenizes input, runs inference, counts tokens, estimates cost, and returns structured metadata with every response. |
| Observability | Logged every request to `request_log.jsonl` with timestamp, latency, token counts, cost, and success flag. Exposed `/metrics` endpoint with p50/p95 percentile latencies. |
| PEFT adapter lifecycle | Saved the adapter (~25MB) separately from the base model, loaded it with `PeftModel.from_pretrained`, and understood the merge-and-unload path for production deployment. |

---

## Extension Ideas

**1. DPO as an alternative to SFT**
Replace the SFTTrainer with TRL's `DPOTrainer` (Direct Preference Optimization). DPO requires preference pairs — (prompt, chosen_response, rejected_response) — but produces models that are better aligned with human preferences without a separate reward model. Compare the resulting quality scores against your SFT baseline.

**2. A/B testing in the API**
Add a `--ab-test` flag to the server that routes 50% of requests to the base model and 50% to the fine-tuned model. Log the model version with each request. After 100 requests, query `/metrics` to see which version has higher average quality scores (requires adding a lightweight judge call per request to the serving layer).

**3. Continuous retraining trigger**
Add a background job that queries `/metrics` every hour. If the average judge score (from a sampled subset of requests) drops below a threshold (e.g., 3.5), write a flag file and send a Slack/webhook alert. This closes the loop from deployment monitoring back to the training pipeline.

---

## Job Mapping

| Role | How This Project Demonstrates Fit |
|---|---|
| ML Engineer | End-to-end fine-tuning pipeline: dataset prep, QLoRA training, adapter management, evaluation. This is the core skillset for model customization roles. |
| MLOps Engineer | Built the full serving and observability stack: FastAPI, JSONL logging, percentile metrics, cost tracking. Directly applicable to any LLM deployment infrastructure role. |
| AI Researcher | Applied and compared evaluation methods (LLM-as-judge, before/after comparison). Understand the limits of automated evaluation and how to design task-specific rubrics. |
| Production Engineer | Instrumented every request with structured telemetry. Built a metrics aggregator that computes p95 latency and total cost — standard SLA monitoring in production AI systems. |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| **04_RECAP.md** | you are here |
