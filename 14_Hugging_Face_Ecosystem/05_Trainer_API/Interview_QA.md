# Trainer API — Interview Q&A

## Beginner Level

**Q1: What is the Hugging Face Trainer and what does it replace?**

<details>
<summary>💡 Show Answer</summary>

**A:** The `Trainer` class is a high-level abstraction that encapsulates a complete PyTorch training loop. It replaces the boilerplate code that every ML engineer would otherwise write from scratch for every project.

Without `Trainer`, a proper training loop requires manually writing:
- The forward pass and loss computation
- Gradient accumulation logic
- Mixed precision (AMP) context management
- DataLoader creation with proper settings
- Evaluation loop with no_grad
- Checkpoint saving and loading
- Learning rate scheduler step
- Logging to TensorBoard or W&B
- Progress bar updates
- Distributed training setup

With `Trainer`, you provide the model, training arguments, and datasets, then call `trainer.train()`. All of the above is handled for you, tested, and works consistently across hardware configurations.

</details>

---

**Q2: What is `TrainingArguments` and why is it important to keep it as a separate object?**

<details>
<summary>💡 Show Answer</summary>

**A:** `TrainingArguments` is a dataclass (essentially a configuration object) that holds all hyperparameters and settings for a training run. It includes things like learning rate, batch size, number of epochs, evaluation strategy, precision settings, and logging configuration.

Keeping it as a separate object has several practical benefits:

1. **Version control** — you can serialize `TrainingArguments` to JSON and commit it alongside your code, giving you a complete record of exactly how each model was trained
2. **Reproducibility** — recreating a training run means loading the same `TrainingArguments` JSON
3. **Separation of concerns** — the model architecture is separate from training hyperparameters, making it easy to train the same model with different settings
4. **Hub integration** — when you push a model with `push_to_hub`, the training args are included, making your results reproducible by others

```python
# Save args to JSON
args.to_json_file("training_args.json")

# Load them back
from transformers import TrainingArguments
args = TrainingArguments.from_json_file("training_args.json")
```

</details>

---

**Q3: Explain gradient accumulation. Why would you use it and what setting controls it?**

<details>
<summary>💡 Show Answer</summary>

**A:** Gradient accumulation is a technique for simulating a larger batch size than your GPU can hold in memory at once.

Normally, with `per_device_train_batch_size=16`, the Trainer processes 16 examples, computes gradients, and updates the model weights. Repeat.

With `gradient_accumulation_steps=4`, the Trainer processes 16 examples and computes gradients, but *does not update the weights yet*. It processes another 16 examples, accumulates the gradients, does this 4 times total, then updates the weights once. The effective batch size becomes 16 × 4 = 64.

**Why this matters:** Larger batch sizes often lead to more stable training (smoother gradient estimates) and are sometimes required to match the training setup of a model you're fine-tuning from. Gradient accumulation lets you achieve this without having a GPU with 4× the VRAM.

**Trade-off:** Gradient accumulation is slower per optimizer step (you process 4× as many examples before updating), but often converges in fewer steps overall for large effective batch sizes.

</details>

---

## Intermediate Level

**Q4: What is the `compute_metrics` function and how does the Trainer use it?**

<details>
<summary>💡 Show Answer</summary>

**A:** `compute_metrics` is a user-provided function that the Trainer calls at evaluation time to compute custom metrics beyond the training loss.

It receives a named tuple `EvalPrediction` with two fields:
- `predictions`: the model's raw output (logits for classification, numpy array)
- `label_ids`: the ground truth labels (numpy array)

It must return a Python dictionary mapping metric names to float values.

```python
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)  # For classification

    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1": f1_score(labels, predictions, average="macro"),
        "precision": precision_score(labels, predictions, average="macro"),
        "recall": recall_score(labels, predictions, average="macro"),
    }
```

The Trainer uses these metrics in two ways:
1. **Logging** — all metrics are logged to TensorBoard/W&B automatically
2. **Best model selection** — if `load_best_model_at_end=True` and `metric_for_best_model="f1"`, the Trainer compares `eval_f1` across checkpoints and loads the best one

</details>

---

**Q5: How does mixed precision training work in the Trainer and when should you use `fp16` vs `bf16`?**

<details>
<summary>💡 Show Answer</summary>

**A:** Mixed precision training uses 16-bit floating point numbers for most operations (reducing VRAM use and speeding up computation on modern GPUs) while keeping certain critical operations (like loss scaling and normalization) in 32-bit for numerical stability.

**How it works internally:** The Trainer wraps the training step with PyTorch's `torch.cuda.amp.autocast()` context, which automatically casts tensors to FP16 for forward pass and matrix multiplications. It also uses a `GradScaler` to scale the loss before backward pass and unscale before the optimizer step — this prevents the tiny FP16 gradients from becoming zero (underflow).

**`fp16=True` vs `bf16=True`:**

| Format | Range | Precision | Best for |
|--------|-------|-----------|---------|
| FP32 | Very wide | High | Baseline, no compromise |
| FP16 | Moderate | Moderate | NVIDIA V100, T4, older GPUs |
| BF16 | Wide (same as FP32) | Lower | NVIDIA A100, A10, RTX 3090+, TPUs |

`bf16` has the same exponent range as FP32 (avoiding overflow issues) but lower mantissa precision. This makes it more numerically stable than FP16 for training, especially for large models with large activations. If your GPU supports it (Ampere architecture or newer), prefer `bf16=True` over `fp16=True`.

</details>

---

**Q6: What is a `DataCollator` and why is `DataCollatorWithPadding` recommended over always padding to max_length at tokenization time?**

<details>
<summary>💡 Show Answer</summary>

**A:** A `DataCollator` is a function that takes a list of dataset examples (each a dict) and merges them into a single batch. It handles the padding that makes sequences uniform length within each batch.

**Static padding (during tokenization):**
```python
# This pads every example to 512 tokens during tokenization
tokenizer(text, padding="max_length", max_length=512)
```
Problem: A batch containing sentences of 10–50 words all get padded to 512 tokens. You're doing attention on hundreds of useless padding tokens per example, wasting significant compute.

**Dynamic padding with DataCollatorWithPadding:**
```python
# Only truncate at tokenization time — don't pad
tokenizer(text, truncation=True, max_length=512)

# DataCollatorWithPadding pads each batch to its longest sequence
data_collator = DataCollatorWithPadding(tokenizer)
```
Now a batch containing sentences of 10–50 words gets padded to 50 tokens (the longest in that batch), not 512. This typically reduces sequence length by 50-80% for typical NLP datasets, reducing compute by a similar factor.

**Practical impact:** For BERT fine-tuning on short text (tweets, sentences), dynamic padding can reduce training time by 30-50%.

</details>

---

## Advanced Level

**Q7: How does the Trainer handle distributed training? What changes when you go from 1 GPU to 8 GPUs?**

<details>
<summary>💡 Show Answer</summary>

**A:** The Trainer uses the `accelerate` library internally, which abstracts away distributed training setup. The beautiful answer: **almost nothing changes in your code**.

With 1 GPU, you just run your script normally.

With 8 GPUs, you launch with:
```bash
torchrun --nproc_per_node=8 train.py
# OR
accelerate launch --num_processes=8 train.py
```

Under the hood, `accelerate` handles:
- **Data parallelism** — each GPU processes a different slice of each batch
- **Gradient synchronization** — gradients are averaged across GPUs after each backward pass using NCCL
- **Model replication** — each GPU has a copy of the model parameters

The Trainer automatically adjusts the effective batch size: with `per_device_train_batch_size=16` on 8 GPUs, you get a global batch size of 128.

**For extremely large models (model parallelism):** If the model is too large for one GPU even for inference, use `device_map="auto"` when loading the model. This is tensor parallelism at the layer level, handled by `accelerate`. The Trainer handles this case too with no code changes.

**The only thing to watch:** Make sure your `evaluation_strategy` checkpoints are saved from the main process only (Trainer handles this automatically). Also, ensure your dataset is sharded correctly — Trainer's DataLoader handles this when using `DistributedSampler` automatically.

</details>

---

**Q8: How do you resume a training run from a checkpoint if training was interrupted?**

<details>
<summary>💡 Show Answer</summary>

**A:** The Trainer has built-in checkpoint resumption. When you pass `resume_from_checkpoint`, it restores the model weights, optimizer state, learning rate scheduler state, and the RNG states — so training continues exactly where it left off, not just from the model weights.

```python
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

# Resume from a specific checkpoint directory
trainer.train(resume_from_checkpoint="./output/checkpoint-5000")

# Resume from the last checkpoint automatically
trainer.train(resume_from_checkpoint=True)
# This finds the most recent checkpoint in output_dir automatically
```

**What gets restored:**
- Model weights
- Optimizer states (momentum, variance in AdamW)
- LR scheduler state (so warmup isn't repeated)
- RNG states (for exact reproducibility)
- Global step counter (so logging continues from the right step)
- DataLoader position (Trainer skips the already-seen batches in epoch 1)

**Important caveat:** If you changed your dataset or `per_device_train_batch_size`, the step count may not correspond correctly to the data position. In that case, the DataLoader will still resume correctly since Trainer saves and restores the dataloader seed and position separately.

</details>

---

**Q9: What is the difference between using `Trainer.train()` and writing your own training loop? When would you skip `Trainer` entirely?**

<details>
<summary>💡 Show Answer</summary>

**A:** `Trainer` covers the vast majority of standard fine-tuning scenarios perfectly. But there are specific cases where writing your own loop with raw PyTorch (or using `accelerate` directly) is the better choice:

**Skip Trainer when:**

1. **Custom loss functions** — if your loss requires computing something that isn't a simple forward pass (e.g., contrastive losses, triplet losses, reinforce gradients), you need to override `Trainer.compute_loss()` or write your own loop. Overriding `compute_loss` is usually possible, but complex cases are cleaner in custom loops.

2. **Non-standard data iteration** — if training requires interleaving multiple datasets in a specific ratio, alternating between different forward passes (e.g., GAN training), or curriculum learning with dynamic data weighting.

3. **Very custom optimization schemes** — differential learning rates per layer, second-order optimizers, or optimizer architectures not supported by `TrainingArguments.optim`.

4. **Reinforcement learning / RLHF** — while `trl` (Hugging Face's RLHF library) builds on `Trainer`, the RLHF loop itself is not a standard supervised training loop.

5. **When you need total control for debugging** — sometimes a manual loop is easier to instrument and debug than Trainer's internals.

**Good middle ground:** Use `Trainer` but subclass it and override `compute_loss()` for custom losses, or add callbacks for complex logging. This gives you most of Trainer's convenience while keeping the customization you need.

</details>

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full Trainer API explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | Interview questions (you are here) |
| [📄 Code_Example.md](./Code_Example.md) | Full working training loop |

⬅️ **Prev:** [PEFT and LoRA](../04_PEFT_and_LoRA/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Inference Optimization](../06_Inference_Optimization/Theory.md)
