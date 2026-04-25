# Project 09 — Custom LoRA Fine-Tuning

## The Story

In 2023, a startup was building a customer support tool for a specialty chemicals company. The company's products had highly specific names, grades, and safety classifications — "Toluene 99.8% ACS Reagent Grade" is not the same as "Toluene Technical Grade", and mixing them up in a response to a customer could cause real problems.

They tried prompt engineering. They wrote detailed system prompts explaining the product catalog. It helped, but not enough — the base model still occasionally invented products, confused grades, and used the wrong safety classifications. They tried RAG. That was better, but the model's output style was generic and did not match how the company communicated with customers.

Then they fine-tuned. They collected 200 examples of ideal customer support responses — correct products, correct grades, correct tone, correct safety language. They ran LoRA fine-tuning for 3 hours on a single GPU. The result was a model that spoke the company's language, consistently used the right product names, and matched the expected response style. Prompt engineering gets you 80%. Fine-tuning with even a small, high-quality dataset gets you the rest.

This project teaches you the mechanism. You will create your own dataset, run LoRA fine-tuning on a small open-source model, evaluate the difference, and share the result on Hugging Face Hub. By the end you will understand exactly what LoRA is doing — and when to reach for it versus RAG versus prompt engineering.

---

## What You Will Build

A fine-tuned language model using **LoRA (Low-Rank Adaptation)** on a custom Q&A dataset you create yourself. Specifically:

1. Create a dataset of at least 50 question-answer pairs on a topic of your choice (formatted for instruction fine-tuning)
2. Set up a LoRA config for a small base model (`TinyLlama-1.1B-Chat` or `facebook/opt-125m`)
3. Fine-tune using `SFTTrainer` from the `trl` library
4. Evaluate by comparing base model vs fine-tuned model responses on held-out questions
5. Push the LoRA adapter (not the full model weights) to Hugging Face Hub
6. Build a Gradio demo and deploy it to Hugging Face Spaces

### Expected Output

Before fine-tuning (base model):
```
Q: What are the key hyperparameters in LoRA?
A: I don't know. LoRA is a type of low-rank matrix factorization...
   [generic, off-topic, or wrong answer]
```

After fine-tuning:
```
Q: What are the key hyperparameters in LoRA?
A: The main LoRA hyperparameters are: r (rank, controls adapter size,
   typically 4-64), lora_alpha (scaling factor, often set to 2*r),
   target_modules (which weight matrices to adapt, usually q_proj and v_proj
   in attention layers), and lora_dropout (regularization, 0.05-0.1 is common).
   Higher r gives more capacity but more parameters.
```

---

## Real-World Motivation

LoRA is the standard technique for customizing LLMs in production:
- Adapting a base model to a company's tone, vocabulary, and domain
- Teaching a model a new task format (structured extraction, code generation style)
- Personalizing models for different customers from a shared base
- Reducing hallucinations on domain-specific terminology

---

## Concepts Covered

| Concept | What You Learn |
|---|---|
| LoRA mechanics | Rank decomposition of weight updates; why it is parameter-efficient |
| Hyperparameters | `r`, `lora_alpha`, `target_modules`, `lora_dropout` — what each controls |
| Dataset formatting | Instruction-following JSONL format with system/user/assistant roles |
| SFTTrainer | Supervised fine-tuning loop without writing the training code manually |
| 4-bit quantization | Loading large models on small GPUs with `bitsandbytes` |
| Evaluation | Qualitative before/after comparison on held-out questions |
| HF Hub publishing | Pushing adapter weights (not full model) to Hugging Face Hub |
| Gradio deployment | Building an interactive demo and deploying to Spaces |

---

## Theory Files

| Section | Topic | File |
|---|---|---|
| 14_Hugging_Face_Ecosystem | PEFT and LoRA | `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/Theory.md` |
| 14_Hugging_Face_Ecosystem | Trainer API | `14_Hugging_Face_Ecosystem/05_Trainer_API/Theory.md` |
| 14_Hugging_Face_Ecosystem | Hub and Model Cards | `14_Hugging_Face_Ecosystem/01_Hub_and_Model_Cards/Theory.md` |
| 14_Hugging_Face_Ecosystem | Transformers Library | `14_Hugging_Face_Ecosystem/02_Transformers_Library/Theory.md` |

---

## Prerequisites

- Completed Projects 07–08 or strong Python background
- Hugging Face account (free at huggingface.co)
- GPU access strongly recommended: Google Colab (free T4), Kaggle notebooks, or local GPU
- Comfortable reading Python classes and understanding class instantiation

### Hardware Requirements

| Hardware | Training time (TinyLlama, 50 examples, 3 epochs) |
|---|---|
| NVIDIA T4 (Colab free tier) | ~15 minutes |
| NVIDIA A100 | ~3 minutes |
| M2 MacBook Pro (MPS) | ~30–45 minutes |
| CPU only | Several hours — not recommended |

---

## Learning Format

**Tier:** Hard (4 / 5 stars)

The complexity here is not in any single concept but in the ecosystem: you must understand Transformers, PEFT, Datasets, and TRL libraries and how they interact. If something breaks, the error messages can be cryptic. Plan time for debugging. GPU access is required for reasonable training times. Plan approximately 4–5 hours plus training time.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 01_MISSION.md | you are here |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [03_GUIDE.md](./03_GUIDE.md) | Progressive build steps |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | What you built + next steps |

⬅️ **Prev:** [08 — Multi-Tool Research Agent](../08_Multi_Tool_Research_Agent/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 — Production RAG System](../10_Production_RAG_System/01_MISSION.md)
