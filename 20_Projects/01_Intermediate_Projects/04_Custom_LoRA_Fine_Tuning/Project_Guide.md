# Project 4 — Custom LoRA Fine-Tuning

## Why This Project Matters

In 2023, a startup was building a customer support tool for a specialty chemicals company. The company's products had highly specific names, grades, and safety classifications — "Toluene 99.8% ACS Reagent Grade" is not the same as "Toluene Technical Grade", and mixing them up in a response to a customer could cause real problems.

They tried prompt engineering. They wrote detailed system prompts explaining the product catalog. It helped, but not enough — the base model still occasionally invented products, confused grades, and used the wrong safety classifications. They tried RAG. That was better, but the model's output style was generic and did not match how the company communicated with customers.

Then they fine-tuned. They collected 200 examples of ideal customer support responses — correct products, correct grades, correct tone, correct safety language. They ran LoRA fine-tuning for 3 hours on a single GPU. The result was a model that spoke the company's language, consistently used the right product names, and matched the expected response style. Prompt engineering gets you 80%. Fine-tuning with even a small, high-quality dataset gets you the rest.

This project teaches you the mechanism. You will create your own dataset, run LoRA fine-tuning on a small open-source model, evaluate the difference, and share the result on Hugging Face Hub. By the end you will understand exactly what LoRA is doing — and when to reach for it versus RAG versus prompt engineering.

---

## What You Will Build

A fine-tuned language model using **LoRA (Low-Rank Adaptation)** on a custom Q&A dataset you create yourself. Specifically:

1. **Create a dataset** of at least 50 question-answer pairs on a topic of your choice (formatted for instruction fine-tuning)
2. **Set up LoRA config** for a small base model (`TinyLlama-1.1B` or `facebook/opt-125m`)
3. **Fine-tune** using `SFTTrainer` from the `trl` library
4. **Evaluate** by comparing base model vs fine-tuned model responses on held-out questions
5. **Push the LoRA adapter** (not the full model weights) to Hugging Face Hub
6. **Build a Gradio demo** and deploy it to Hugging Face Spaces

---

## Learning Objectives

By completing this project you will be able to:

- Explain what LoRA does mathematically (rank decomposition of weight updates)
- Configure LoRA hyperparameters: `r`, `lora_alpha`, `target_modules`, `lora_dropout`
- Format a dataset for instruction fine-tuning (system/user/assistant format)
- Use `SFTTrainer` to run a training loop without writing it manually
- Push model adapters (not full weights) to the Hugging Face Hub
- Write a Gradio interface and deploy it to Spaces

---

## Topics Covered

| Phase | Topic | Theory File |
|---|---|---|
| Phase 5 | PEFT and LoRA | `14_Hugging_Face_Ecosystem/04_PEFT_and_LoRA/Theory.md` |
| Phase 5 | Trainer API | `14_Hugging_Face_Ecosystem/05_Trainer_API/Theory.md` |
| Phase 5 | Hub and Model Cards | `14_Hugging_Face_Ecosystem/01_Hub_and_Model_Cards/Theory.md` |
| Phase 5 | Transformers Library | `14_Hugging_Face_Ecosystem/02_Transformers_Library/Theory.md` |

---

## Prerequisites

- Completed Projects 1–3 or strong Python background
- Hugging Face account (free at huggingface.co)
- GPU access strongly recommended: Google Colab (free T4), Kaggle notebooks, or local GPU
- Comfortable reading Python classes and understanding class instantiation

---

## Difficulty

Hard (4 / 5 stars)

The complexity here is not in any single concept but in the ecosystem: you must understand Transformers, PEFT, Datasets, and TRL libraries and how they interact. If something breaks, the error messages can be cryptic. Plan time for debugging. GPU access is required for reasonable training times — CPU-only training on even a small model takes hours.

---

## Expected Output

### Before fine-tuning (base model — TinyLlama)
```
Q: What are the key hyperparameters in LoRA?

A: I don't know. LoRA is a type of low-rank matrix factorization...
   [generic, off-topic, or wrong answer]
```

### After fine-tuning (your fine-tuned model)
```
Q: What are the key hyperparameters in LoRA?

A: The main LoRA hyperparameters are: r (rank, controls adapter size,
   typically 4-64), lora_alpha (scaling factor, often set to 2*r),
   target_modules (which weight matrices to adapt, usually q_proj and v_proj
   in attention layers), and lora_dropout (regularization, 0.05-0.1 is common).
   Higher r gives more capacity but more parameters.
```

---

## Dataset Requirements

Your Q&A dataset must:
- Have at least 50 examples (80+ recommended)
- Cover a consistent topic you know well
- Include a variety of question types (definition, how-to, comparison, troubleshooting)
- Have accurate answers (you are training a model — bad data = bad model)
- Be formatted as instruction-following examples

Good topic choices:
- AI/ML concepts (use the theory files in this repo as a source)
- A programming language feature set
- A domain you work in professionally
- Historical events or scientific facts

---

## Key Concepts You Will Learn

**LoRA (Low-Rank Adaptation)**: Instead of updating all model weights during fine-tuning (billions of parameters), LoRA freezes the original weights and adds small trainable matrices alongside specific layers. The key insight: meaningful weight changes tend to be low-rank — they can be approximated by two small matrices `A` (d × r) and `B` (r × k) where `r << d, k`. Total new parameters: roughly 1% of the original model.

**`r` (rank)**: The bottleneck dimension of the LoRA matrices. Higher `r` = more capacity = more parameters = more risk of overfitting on small datasets. For 50-100 examples, use `r=8` or `r=16`.

**`lora_alpha`**: Scaling factor applied to the LoRA output. The effective learning rate scale is `lora_alpha / r`. A common heuristic: set `lora_alpha = 2 * r`.

**`target_modules`**: Which weight matrices to apply LoRA to. For attention-based models, adapting `q_proj` and `v_proj` is standard. Adapting more modules (k_proj, o_proj, MLP layers) gives more capacity at the cost of more parameters.

**SFTTrainer**: The `SupervisedFineTuningTrainer` from the `trl` library. Handles the training loop, gradient accumulation, logging, and checkpointing. You configure it and call `.train()`.

---

## Project Structure

```
04_Custom_LoRA_Fine_Tuning/
├── Project_Guide.md
├── Step_by_Step.md
├── Starter_Code.md
├── Architecture_Blueprint.md
├── dataset.jsonl             ← your 50+ Q&A examples
├── fine_tune.py              ← training script
├── evaluate.py               ← before/after comparison
└── app.py                    ← Gradio demo
```

---

## Hardware Requirements

| Hardware | Training time (TinyLlama, 50 examples, 3 epochs) |
|---|---|
| NVIDIA T4 (Colab free tier) | ~15 minutes |
| NVIDIA A100 | ~3 minutes |
| M2 MacBook Pro (MPS) | ~30–45 minutes |
| CPU only | Several hours — not recommended |

Use Google Colab for this project if you do not have a GPU. The free tier provides a T4 GPU.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| Project_Guide.md | ← you are here |
| [Step_by_Step.md](./Step_by_Step.md) | Build instructions |
| [Starter_Code.md](./Starter_Code.md) | Code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [03 — Multi-Tool Research Agent](../03_Multi_Tool_Research_Agent/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Production RAG System](../05_Production_RAG_System/Project_Guide.md)
