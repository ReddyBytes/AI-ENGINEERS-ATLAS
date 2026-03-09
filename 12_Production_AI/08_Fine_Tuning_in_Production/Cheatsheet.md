# Cheatsheet — Fine-Tuning in Production

**Fine-tuning** continues training a pre-trained model on a task-specific dataset, updating weights to optimize performance on your exact use case — format, domain, style, or specialized task.

---

## Key Terms

| Term | Definition |
|---|---|
| **Fine-tuning** | Continuing training a pre-trained model on a specific dataset |
| **SFT** | Supervised Fine-Tuning — train on (input, desired_output) pairs |
| **LoRA** | Low-Rank Adaptation — add small trainable matrices without modifying original weights |
| **QLoRA** | Quantized LoRA — LoRA on a quantized (int4) base model; reduces VRAM 4x |
| **PEFT** | Parameter-Efficient Fine-Tuning — umbrella term for LoRA, prefix tuning, etc. |
| **Catastrophic forgetting** | Model loses general capabilities while specializing |
| **Overfitting** | Model memorizes training examples rather than learning generalizable patterns |
| **JSONL** | JSON Lines format — one training example per line, used for fine-tuning data |
| **Training loss** | Measure of how well the model is fitting training data (should decrease) |
| **Evaluation loss** | Loss on held-out data (should decrease then plateau; rising = overfitting) |
| **Continuous fine-tuning** | Scheduled periodic retraining as new labeled data accumulates |

---

## Fine-Tuning Methods Comparison

| Method | Trainable Params | VRAM (7B model) | Quality | Speed | Best For |
|---|---|---|---|---|---|
| **Full SFT** | 100% (7B) | ~120 GB | Best | Slow | Small models, max quality |
| **LoRA (r=16)** | ~0.1% | ~16 GB | Nearly as good | Fast | Most production use cases |
| **QLoRA (4-bit)** | ~0.1% | ~8 GB | Slight loss | Medium | Limited GPU (consumer cards) |
| **Prefix tuning** | Very small | ~4 GB | Lower | Very fast | Experimental, not recommended |

---

## Training Data Format (OpenAI & Most APIs)

```jsonl
{"messages": [{"role": "system", "content": "You are a product classifier."}, {"role": "user", "content": "Blue denim jeans, size 32x30"}, {"role": "assistant", "content": "{\"category\": \"Bottoms\", \"subcategory\": \"Jeans\", \"gender\": \"Unisex\"}"}]}
{"messages": [{"role": "system", "content": "You are a product classifier."}, {"role": "user", "content": "Red cotton t-shirt, women's medium"}, {"role": "assistant", "content": "{\"category\": \"Tops\", \"subcategory\": \"T-Shirts\", \"gender\": \"Women's\"}"}]}
```

**Rules for good training data:**
- Minimum: 50-100 examples (more is always better)
- Sweet spot: 500-5,000 high-quality examples
- Format must be perfectly consistent — every example follows the exact same structure
- Include edge cases and difficult examples from your actual production distribution
- Hold out 10-20% for evaluation — never use eval data in training

---

## When to Fine-Tune Decision Matrix

| Situation | Fine-Tune? | Alternative |
|---|---|---|
| Need specific output format | **Yes** | Prompt with format example (few-shot) |
| Domain-specific terminology | **Yes** (if large vocab gap) | Add glossary to system prompt |
| Reduce prompt token usage | **Yes** (if cost-sensitive) | Optimize prompt first |
| Need latest information | **No** | RAG |
| Fewer than 100 examples | **No** | Few-shot prompting |
| Task changes frequently | **No** | Prompt engineering |
| One-time task | **No** | Prompt engineering |
| Consistent tone/style | **Yes** | |
| Cost reduction (10x+ volume) | **Yes** (smaller fine-tuned model) | |

---

## Fine-Tuning APIs — Quick Reference

### OpenAI Fine-Tuning

```python
from openai import OpenAI
client = OpenAI()

# Upload training file
file = client.files.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune"
)

# Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-3.5-turbo",  # or "gpt-4o-mini"
    hyperparameters={"n_epochs": 3}
)

print(f"Job ID: {job.id}")  # Monitor at platform.openai.com/fine-tuning
```

### HuggingFace PEFT (LoRA)

```python
from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

# Load base model
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")

# Apply LoRA
lora_config = LoraConfig(
    r=16,                          # Rank — higher = more capacity, more params
    lora_alpha=32,                  # Scaling factor
    target_modules=["q_proj", "v_proj"],  # Which layers to add LoRA to
    lora_dropout=0.05,
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # Should show ~0.1% trainable
```

---

## Hyperparameters Guide

| Hyperparameter | Typical Range | Effect |
|---|---|---|
| **learning_rate** | 1e-5 to 5e-4 | Higher = faster learning, more forgetting risk |
| **n_epochs** | 1-5 | More = better fit, more overfitting risk; 1-3 is usually enough |
| **batch_size** | 4-32 | Larger = more stable gradients; limited by VRAM |
| **LoRA rank (r)** | 4-128 | Higher = more capacity; 8-64 is typical |
| **max_seq_length** | 512-8192 | Match your actual input length; longer = more VRAM |
| **warmup_steps** | 5-10% of total steps | Prevents large early updates destabilizing the model |

---

## Versioning and Rollback

```
model_registry/
├── product-classifier/
│   ├── v1/  (baseline — fine-tuned 2024-01-01, accuracy=0.91)
│   ├── v2/  (current — fine-tuned 2024-03-01, accuracy=0.94)  ← production
│   └── v3/  (candidate — fine-tuned 2024-06-01, accuracy=0.95)  ← canary 5%
```

Rollback protocol:
1. Quality alert fires (v3 degrading on new data type)
2. Shift traffic: v3 → 0%, v2 → 100%
3. Total rollback time: < 60 seconds
4. Investigate v3 failure offline; fix training data

---

## Golden Rules

- **Evaluate baseline first** — measure current quality before training; you need a number to beat
- **Quality > quantity for training data** — 500 perfect examples beats 5,000 mediocre ones
- **Hold out 15-20% for evaluation** — never test on training data
- **Watch training AND validation loss** — training goes down always; validation plateauing or rising = overfitting
- **Use LoRA by default** — full SFT is rarely necessary for adapting an existing model
- **Version every fine-tuned model** — keep the previous version warm for rollback
- **Monitor quality in production** — data drift requires periodic retraining
- **Always compare to baseline** — a fine-tuned model that doesn't beat prompting is not worth deploying

---

## 📂 Navigation
