# Trainer API — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Trainer** | Pre-built training loop that handles gradient steps, eval, saving, and logging |
| **TrainingArguments** | Config object holding all training hyperparameters |
| **compute_metrics** | User-defined function that receives logits+labels and returns metric dict |
| **data_collator** | Function that batches examples together (handles dynamic padding) |
| **gradient_accumulation_steps** | Process N mini-batches before one optimizer step — simulates larger batch |
| **fp16 / bf16** | Mixed precision training — speeds up on GPU, reduces VRAM |
| **evaluation_strategy** | When to run eval: `"no"`, `"steps"`, or `"epoch"` |
| **load_best_model_at_end** | After training, reload the checkpoint with best eval metric |
| **warmup_ratio** | Fraction of steps for linear LR warmup from 0 to target LR |
| **TrainerCallback** | Hook class to inject logic at on_train_begin, on_evaluate, etc. |
| **DataCollatorWithPadding** | Pads sequences to max length in each batch (dynamic, not global) |

---

## Minimal Working Trainer

```python
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from datasets import load_dataset
import numpy as np

# Data
ds = load_dataset("imdb")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def preprocess(examples):
    return {**tokenizer(examples["text"], truncation=True, max_length=256),
            "labels": examples["label"]}

ds = ds.map(preprocess, batched=True, remove_columns=["text", "label"])
ds.set_format("torch")

# Model
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=2)

# Metrics
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": (preds == labels).mean()}

# Training config
args = TrainingArguments(
    output_dir="./output",
    num_train_epochs=3,
    per_device_train_batch_size=32,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    fp16=True,
)

# Train
trainer = Trainer(model=model, args=args,
                  train_dataset=ds["train"], eval_dataset=ds["test"],
                  tokenizer=tokenizer, compute_metrics=compute_metrics,
                  data_collator=DataCollatorWithPadding(tokenizer))
trainer.train()
```

---

## TrainingArguments — Full Reference

```python
TrainingArguments(
    # ── Paths ──────────────────────────────────────────────────
    output_dir="./output",           # Where to save model + checkpoints
    logging_dir="./logs",            # TensorBoard logs
    run_name="experiment-001",       # Name for W&B / MLflow

    # ── Batch size ─────────────────────────────────────────────
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    gradient_accumulation_steps=4,   # Effective batch = 16×4 = 64

    # ── Epochs / steps ─────────────────────────────────────────
    num_train_epochs=3,
    max_steps=-1,                    # Override epochs if set > 0

    # ── Learning rate ──────────────────────────────────────────
    learning_rate=2e-5,
    lr_scheduler_type="linear",      # "cosine", "polynomial", "constant"
    warmup_ratio=0.1,                # 10% of steps for warmup
    warmup_steps=0,                  # OR: explicit step count

    # ── Evaluation ─────────────────────────────────────────────
    evaluation_strategy="epoch",     # "no", "steps", "epoch"
    eval_steps=500,                  # When strategy="steps"
    metric_for_best_model="f1",      # Metric to determine best checkpoint
    greater_is_better=True,

    # ── Saving ─────────────────────────────────────────────────
    save_strategy="epoch",           # Must match evaluation_strategy
    save_steps=500,
    save_total_limit=3,              # Keep only N checkpoints on disk
    load_best_model_at_end=True,

    # ── Precision ──────────────────────────────────────────────
    fp16=False,                      # FP16 on NVIDIA GPUs
    bf16=False,                      # BF16 on Ampere+ (more stable than FP16)
    tf32=True,                       # TF32 for matmuls on Ampere+

    # ── Performance ────────────────────────────────────────────
    dataloader_num_workers=4,
    group_by_length=True,            # Group similar-length inputs (less padding)
    dataloader_pin_memory=True,      # Speed up CPU→GPU transfer

    # ── Logging ────────────────────────────────────────────────
    logging_steps=50,
    report_to="wandb",               # "tensorboard", "wandb", "mlflow", "none"

    # ── Regularization ─────────────────────────────────────────
    weight_decay=0.01,
    max_grad_norm=1.0,               # Gradient clipping

    # ── Optimizer ──────────────────────────────────────────────
    optim="adamw_torch",             # "adamw_hf", "adafactor", "adamw_bnb_8bit"

    # ── Seed ───────────────────────────────────────────────────
    seed=42,
)
```

---

## Key Callbacks

```python
from transformers import (
    EarlyStoppingCallback,
    TensorBoardCallback,
    WandbCallback,
)

# Early stopping — stop if eval metric doesn't improve
early_stop = EarlyStoppingCallback(
    early_stopping_patience=3,      # Wait 3 evals without improvement
    early_stopping_threshold=0.001  # Minimum improvement to count
)

trainer = Trainer(..., callbacks=[early_stop])

# Custom callback template
from transformers import TrainerCallback, TrainerState, TrainerControl

class MyCallback(TrainerCallback):
    def on_train_begin(self, args, state, control, **kwargs):
        print("Training started!")

    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"Epoch {state.epoch} complete. Loss: {state.log_history[-1]}")

    def on_evaluate(self, args, state, control, metrics, **kwargs):
        print(f"Eval metrics: {metrics}")

    def on_save(self, args, state, control, **kwargs):
        print(f"Checkpoint saved at step {state.global_step}")

    def on_train_end(self, args, state, control, **kwargs):
        print("Training complete!")
```

---

## Quick Reference: Evaluation vs Save Strategy Match

| evaluation_strategy | save_strategy | load_best_model_at_end works? |
|--------------------|---------------|-------------------------------|
| `"epoch"` | `"epoch"` | ✅ Yes |
| `"steps"` | `"steps"` (same eval_steps) | ✅ Yes |
| `"epoch"` | `"steps"` | ❌ No — mismatch |
| `"steps"` | `"epoch"` | ❌ No — mismatch |

**Rule:** `evaluation_strategy` and `save_strategy` must match (and `eval_steps == save_steps`) for `load_best_model_at_end=True` to work.

---

## Golden Rules

1. **Match `evaluation_strategy` and `save_strategy`** — mismatches cause `load_best_model_at_end` to fail silently.
2. **Use `DataCollatorWithPadding` for variable-length inputs** — dynamic padding reduces wasted computation by 30-50%.
3. **Set `fp16=True` on NVIDIA GPUs** (or `bf16=True` on Ampere+) — free speed boost.
4. **Use `gradient_accumulation_steps`** when your desired batch size exceeds GPU memory.
5. **Set `group_by_length=True`** for efficiency — sequences of similar length get batched together.
6. **Use `save_total_limit=3`** — prevents checkpoints from filling up disk.
7. **Set `seed`** for reproducibility — ensures same data shuffling and model initialization.

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full Trainer API explanation |
| 📄 **Cheatsheet.md** | Quick reference (you are here) |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | Full working training loop |

⬅️ **Prev:** [PEFT and LoRA](../04_PEFT_and_LoRA/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Inference Optimization](../06_Inference_Optimization/Theory.md)
