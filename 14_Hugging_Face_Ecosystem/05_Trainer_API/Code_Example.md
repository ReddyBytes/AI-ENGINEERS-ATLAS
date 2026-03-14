# Trainer API — Code Examples

## Setup

```python
# pip install transformers datasets torch scikit-learn accelerate

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    TrainerCallback,
)
from datasets import load_dataset
import numpy as np
import torch
```

---

## Example 1: Minimal Training Loop — Sentiment Analysis

```python
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from datasets import load_dataset
import numpy as np

# ── 1. Data ───────────────────────────────────────────────────────
ds = load_dataset("imdb")
model_checkpoint = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)

def preprocess(examples):
    tokenized = tokenizer(
        examples["text"],
        truncation=True,     # Truncate to model max length
        max_length=256,      # Shorter than max for speed
    )
    tokenized["labels"] = examples["label"]
    return tokenized

tokenized = ds.map(preprocess, batched=True, remove_columns=["text", "label"])
tokenized.set_format("torch")

# ── 2. Model ──────────────────────────────────────────────────────
model = AutoModelForSequenceClassification.from_pretrained(
    model_checkpoint,
    num_labels=2,
    id2label={0: "NEGATIVE", 1: "POSITIVE"},
    label2id={"NEGATIVE": 0, "POSITIVE": 1},
)

# ── 3. Metrics ────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean()
    return {"accuracy": float(accuracy)}

# ── 4. Training Arguments ─────────────────────────────────────────
args = TrainingArguments(
    output_dir="./distilbert-imdb",
    num_train_epochs=3,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    learning_rate=2e-5,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    fp16=torch.cuda.is_available(),  # Auto-enable FP16 on GPU
    logging_steps=50,
    report_to="none",                # Disable W&B for this demo
    seed=42,
)

# ── 5. Trainer ────────────────────────────────────────────────────
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
    data_collator=DataCollatorWithPadding(tokenizer),  # Dynamic padding
)

# ── 6. Train ──────────────────────────────────────────────────────
train_result = trainer.train()
print(f"\nTraining complete!")
print(f"Final train loss: {train_result.training_loss:.4f}")

# ── 7. Evaluate ───────────────────────────────────────────────────
eval_results = trainer.evaluate()
print(f"Test accuracy: {eval_results['eval_accuracy']:.4f}")

# ── 8. Save ───────────────────────────────────────────────────────
trainer.save_model("./distilbert-imdb-final")
tokenizer.save_pretrained("./distilbert-imdb-final")
print("Model saved!")
```

---

## Example 2: Gradient Accumulation for Large Effective Batch Sizes

```python
from transformers import TrainingArguments

# Scenario: You want effective batch size of 256 but only have VRAM for 16
# Per-GPU batch: 16
# Gradient accumulation steps: 16
# Effective batch = 16 × 16 = 256

args = TrainingArguments(
    output_dir="./output-large-batch",
    per_device_train_batch_size=16,    # Actual VRAM limit
    gradient_accumulation_steps=16,    # Accumulate 16 mini-batches
    # Effective batch = 16 × 16 = 256

    # When using large effective batch size, often increase LR
    # (linear scaling rule: LR = base_LR × effective_batch / base_batch)
    learning_rate=2e-4,                # 2e-5 × (256/32) ≈ 1.6e-4

    num_train_epochs=3,
    evaluation_strategy="steps",
    eval_steps=500,
    save_strategy="steps",
    save_steps=500,
    load_best_model_at_end=True,
    fp16=True,
)

print(f"Effective batch size: {args.per_device_train_batch_size * args.gradient_accumulation_steps}")
```

---

## Example 3: Training with Callbacks

```python
from transformers import TrainerCallback, TrainerState, TrainerControl, EarlyStoppingCallback
import time

# ── Built-in Early Stopping ───────────────────────────────────────
early_stopping = EarlyStoppingCallback(
    early_stopping_patience=3,       # Stop if no improvement for 3 eval rounds
    early_stopping_threshold=0.001   # Minimum absolute improvement to count
)

# ── Custom Callback: Learning Rate Logger ─────────────────────────
class LRLoggerCallback(TrainerCallback):
    """Logs the current learning rate at each logging step."""

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs and "learning_rate" in logs:
            print(f"  Step {state.global_step}: LR = {logs['learning_rate']:.2e}")

# ── Custom Callback: Time Estimator ──────────────────────────────
class TimeEstimatorCallback(TrainerCallback):
    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = time.time()
        print("Training started. Estimating completion time...")

    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step > 0 and state.global_step % 100 == 0:
            elapsed = time.time() - self.start_time
            steps_per_sec = state.global_step / elapsed
            remaining_steps = state.max_steps - state.global_step
            remaining_secs = remaining_steps / steps_per_sec
            print(f"  Progress: {state.global_step}/{state.max_steps} | "
                  f"ETA: {remaining_secs/60:.1f} minutes")

    def on_train_end(self, args, state, control, **kwargs):
        total = time.time() - self.start_time
        print(f"Training finished in {total/60:.1f} minutes")

# Use with Trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    compute_metrics=compute_metrics,
    callbacks=[
        early_stopping,
        LRLoggerCallback(),
        TimeEstimatorCallback(),
    ]
)
```

---

## Example 4: Training with Custom Loss Function

```python
from transformers import Trainer
import torch
import torch.nn as nn

class FocalLossTrainer(Trainer):
    """
    Custom Trainer that uses Focal Loss instead of standard cross-entropy.
    Focal Loss is useful for imbalanced datasets — it down-weights easy examples.
    """

    def __init__(self, *args, focal_gamma=2.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.focal_gamma = focal_gamma

    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")

        # Standard forward pass
        outputs = model(**inputs)
        logits = outputs.logits

        # Focal loss computation
        probs = torch.softmax(logits, dim=-1)
        log_probs = torch.log_softmax(logits, dim=-1)

        # Cross entropy component
        ce_loss = -log_probs.gather(dim=-1, index=labels.unsqueeze(1)).squeeze(1)

        # Focal weight
        p_t = probs.gather(dim=-1, index=labels.unsqueeze(1)).squeeze(1)
        focal_weight = (1 - p_t) ** self.focal_gamma

        loss = (focal_weight * ce_loss).mean()

        return (loss, outputs) if return_outputs else loss


# Use exactly like regular Trainer
focal_trainer = FocalLossTrainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    compute_metrics=compute_metrics,
    focal_gamma=2.0,   # Focus parameter — higher = more focus on hard examples
)

focal_trainer.train()
```

---

## Example 5: Full Pipeline — Load, Fine-Tune, Push to Hub

```python
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    Trainer, TrainingArguments, DataCollatorWithPadding
)
from datasets import load_dataset
from huggingface_hub import login
import numpy as np

# Authenticate for Hub push
login(token="hf_your_token_here")

# ── Data ──────────────────────────────────────────────────────────
ds = load_dataset("ag_news")   # 4-class news classification
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

label_map = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}

def preprocess(examples):
    return {
        **tokenizer(examples["text"], truncation=True, max_length=128),
        "labels": examples["label"]
    }

ds = ds.map(preprocess, batched=True, remove_columns=["text", "label"])
ds.set_format("torch")

# ── Model ─────────────────────────────────────────────────────────
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=4,
    id2label=label_map,
    label2id={v: k for k, v in label_map.items()},
)

# ── Metrics ───────────────────────────────────────────────────────
from sklearn.metrics import accuracy_score, f1_score

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1_macro": f1_score(labels, preds, average="macro"),
    }

# ── Training ──────────────────────────────────────────────────────
HUB_MODEL_ID = "your-username/bert-ag-news-classifier"

args = TrainingArguments(
    output_dir=f"./{HUB_MODEL_ID.split('/')[-1]}",
    num_train_epochs=4,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_ratio=0.1,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1_macro",
    fp16=True,
    logging_steps=100,
    push_to_hub=True,               # Push to Hub after training!
    hub_model_id=HUB_MODEL_ID,
    hub_strategy="every_save",      # Push at each checkpoint
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=ds["train"],
    eval_dataset=ds["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
    data_collator=DataCollatorWithPadding(tokenizer),
)

trainer.train()

# Final push — includes model card with training args
trainer.push_to_hub(
    commit_message="Best model checkpoint after 4 epochs",
    language="en",
    license="apache-2.0",
    tags=["text-classification", "news", "bert"],
)

print(f"Model published at: https://huggingface.co/{HUB_MODEL_ID}")
```

---

## Example 6: Inspecting Training State and History

```python
# After training, inspect what happened
print("\n=== Training History ===")
print(f"Total steps: {trainer.state.global_step}")
print(f"Best metric: {trainer.state.best_metric}")
print(f"Best model checkpoint: {trainer.state.best_model_checkpoint}")

# Log history is a list of dicts with step + metrics at each logging point
print(f"\nFirst log entry: {trainer.state.log_history[0]}")
print(f"Last log entry: {trainer.state.log_history[-1]}")

# Extract loss curve
train_logs = [l for l in trainer.state.log_history if "loss" in l]
eval_logs = [l for l in trainer.state.log_history if "eval_loss" in l]

print(f"\nTrain loss progression:")
for log in train_logs[::5]:   # Every 5th entry
    print(f"  Step {log['step']:5d}: loss = {log['loss']:.4f}")

# Make predictions on new data
predictions = trainer.predict(tokenized["test"])
print(f"\nPredictions object keys: {predictions._fields}")
print(f"Logits shape: {predictions.predictions.shape}")
print(f"Label IDs shape: {predictions.label_ids.shape}")
print(f"Test metrics: {predictions.metrics}")
```

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full Trainer API explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| 📄 **Code_Example.md** | Working code (you are here) |

⬅️ **Prev:** [PEFT and LoRA](../04_PEFT_and_LoRA/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Inference Optimization](../06_Inference_Optimization/Theory.md)
