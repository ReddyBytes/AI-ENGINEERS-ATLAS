# Fine-Tuning Code Example
# Fine-tuning a small LLM with QLoRA using HuggingFace PEFT

This example shows how to fine-tune a Llama-3-8B model (or any similar causal LM) on a custom instruction dataset using QLoRA. Every important line is commented.

## Prerequisites

```bash
pip install transformers peft bitsandbytes datasets accelerate trl
```

You will need a GPU with at least 12GB VRAM for an 8B model with QLoRA.

---

## The full training script

```python
"""
fine_tune_qlora.py

Fine-tune a causal LLM with QLoRA (4-bit quantization + LoRA adapters).
This is the standard approach for fine-tuning 7B-13B models on a single GPU.
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import (
    LoraConfig,
    get_peft_model,
    TaskType,
    prepare_model_for_kbit_training,
)
from trl import SFTTrainer                    # HuggingFace's SFT wrapper
from datasets import load_dataset


# ─────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# Base model to fine-tune — change this to any causal LM on HuggingFace Hub
# e.g., "mistralai/Mistral-7B-v0.1", "meta-llama/Meta-Llama-3-8B"
MODEL_ID = "meta-llama/Meta-Llama-3-8B"

# Where to save the fine-tuned adapter weights after training
OUTPUT_DIR = "./llama3-8b-finetuned"

# Your training data — a JSONL file with fields: instruction, input, output
# See sample_data.jsonl example below
DATASET_PATH = "./train_data.jsonl"

# LoRA hyperparameters
LORA_R = 16                    # Rank of the LoRA update matrices. Higher = more capacity.
LORA_ALPHA = 32                # Scaling factor = alpha / r. Common to set 2x r.
LORA_DROPOUT = 0.05            # Dropout on LoRA layers — small regularization
# Which layers to apply LoRA to — these are the attention projection layers
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj"]

# Training hyperparameters
NUM_EPOCHS = 3                 # How many full passes through the dataset
BATCH_SIZE = 4                 # Per-GPU batch size — decrease if you run out of memory
GRAD_ACCUMULATION = 4          # Effective batch size = BATCH_SIZE × GRAD_ACCUMULATION = 16
LEARNING_RATE = 2e-4           # Standard starting LR for LoRA fine-tuning
MAX_SEQ_LENGTH = 2048          # Truncate inputs longer than this


# ─────────────────────────────────────────────────────────────────────────────
# 2. QUANTIZATION CONFIG (for QLoRA — loads model in 4-bit)
# ─────────────────────────────────────────────────────────────────────────────

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                        # Load model in 4-bit precision
    bnb_4bit_quant_type="nf4",               # NF4 = NormalFloat4, best for LLM weights
    bnb_4bit_compute_dtype=torch.bfloat16,   # Use bfloat16 for compute (faster, stable)
    bnb_4bit_use_double_quant=True,          # Quantize the quantization constants too (saves ~0.4 bits/param)
)


# ─────────────────────────────────────────────────────────────────────────────
# 3. LOAD THE BASE MODEL
# ─────────────────────────────────────────────────────────────────────────────

print(f"Loading base model: {MODEL_ID}")

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,          # Apply 4-bit quantization
    device_map="auto",                        # Automatically distribute across available GPUs
    trust_remote_code=True,                   # Allow custom model code from HuggingFace Hub
)

# Required when using gradient checkpointing with quantized models
# This enables computing gradients through the frozen quantized base model
model = prepare_model_for_kbit_training(model)

# Load the tokenizer (must match the model)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

# Add padding token if not present (Llama models don't have one by default)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token   # Use EOS as PAD — common practice
    model.config.pad_token_id = tokenizer.eos_token_id


# ─────────────────────────────────────────────────────────────────────────────
# 4. ADD LORA ADAPTERS
# ─────────────────────────────────────────────────────────────────────────────

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,            # We're fine-tuning a causal language model
    r=LORA_R,                                # Rank of the update matrices
    lora_alpha=LORA_ALPHA,                   # Scaling factor
    lora_dropout=LORA_DROPOUT,              # Regularization
    target_modules=LORA_TARGET_MODULES,     # Which layers get LoRA adapters
    bias="none",                             # Don't train bias terms (standard practice)
)

# Wrap the base model with LoRA adapters
# This freezes all base model parameters and makes only adapters trainable
model = get_peft_model(model, lora_config)

# Print how many parameters are trainable — should be ~0.5–1% of total
model.print_trainable_parameters()
# Output example: trainable params: 20,971,520 || all params: 8,051,232,768 || trainable%: 0.26%


# ─────────────────────────────────────────────────────────────────────────────
# 5. LOAD AND FORMAT THE DATASET
# ─────────────────────────────────────────────────────────────────────────────

# Load dataset from JSONL file
# Each line should be: {"instruction": "...", "input": "...", "output": "..."}
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

def format_instruction(example):
    """
    Convert each dataset example into a prompt string.
    This is the Alpaca prompt template — a standard format for instruction fine-tuning.
    The model learns to produce the 'output' given the 'instruction' + 'input'.
    """
    if example.get("input"):
        # Has an additional input (e.g., a document to summarize)
        prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
    else:
        # No additional input — just instruction and response
        prompt = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{example['instruction']}

### Response:
{example['output']}"""

    return {"text": prompt}   # SFTTrainer expects a "text" field

# Apply formatting to every example in the dataset
dataset = dataset.map(format_instruction, remove_columns=dataset.column_names)

print(f"Dataset size: {len(dataset)} examples")
print(f"Sample prompt:\n{dataset[0]['text'][:500]}...")


# ─────────────────────────────────────────────────────────────────────────────
# 6. TRAINING ARGUMENTS
# ─────────────────────────────────────────────────────────────────────────────

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,                    # Where to save checkpoints and final model
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUMULATION,  # Simulate larger batches
    learning_rate=LEARNING_RATE,

    # Learning rate schedule
    warmup_ratio=0.05,                        # 5% of steps for linear warmup
    lr_scheduler_type="cosine",              # Cosine decay after warmup

    # Precision
    bf16=True,                               # Use bfloat16 for training (requires Ampere+ GPU)

    # Memory optimization
    gradient_checkpointing=True,             # Trade compute for memory — re-compute activations on backward

    # Logging and saving
    logging_dir="./logs",
    logging_steps=10,                         # Log metrics every 10 steps
    save_steps=200,                          # Save checkpoint every 200 steps
    save_total_limit=3,                      # Keep only the 3 most recent checkpoints

    # Optimizer
    optim="paged_adamw_32bit",              # Paged AdamW — moves optimizer state to CPU when not needed
                                             # This is the QLoRA-specific optimizer for memory efficiency

    # Reporting (optional — remove if not using W&B)
    report_to="none",                        # Change to "wandb" to enable Weights & Biases logging
)


# ─────────────────────────────────────────────────────────────────────────────
# 7. CREATE THE TRAINER AND TRAIN
# ─────────────────────────────────────────────────────────────────────────────

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=training_args,
    train_dataset=dataset,
    dataset_text_field="text",               # Which field contains the formatted prompt
    max_seq_length=MAX_SEQ_LENGTH,           # Truncate examples longer than this
    packing=True,                            # Pack multiple short examples into one sequence
                                             # Improves GPU utilization for short samples
)

print("Starting training...")
trainer.train()
print("Training complete!")


# ─────────────────────────────────────────────────────────────────────────────
# 8. SAVE THE FINE-TUNED ADAPTER WEIGHTS
# ─────────────────────────────────────────────────────────────────────────────

# Save only the LoRA adapter weights — tiny file (~20–100MB for 7B model with r=16)
# To use this model: load base model + load adapter weights
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Adapter saved to {OUTPUT_DIR}")

# OPTIONAL: Merge adapters into base model weights for simpler inference
# (No separate adapter needed — but file is much larger)
# from peft import PeftModel
# model = model.merge_and_unload()
# model.save_pretrained(OUTPUT_DIR + "-merged")
```

---

## Sample training data format (train_data.jsonl)

Each line is a separate JSON object:

```jsonl
{"instruction": "Summarize the following in one sentence.", "input": "The mitochondria is the powerhouse of the cell. It is responsible for producing ATP through cellular respiration.", "output": "The mitochondria produces ATP energy for the cell through cellular respiration."}
{"instruction": "Write a Python function that returns the factorial of a number.", "input": "", "output": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)"}
{"instruction": "What is the difference between supervised and unsupervised learning?", "input": "", "output": "Supervised learning uses labeled data where the correct output is known during training. Unsupervised learning finds patterns in unlabeled data without predefined correct answers."}
```

---

## Loading and using the fine-tuned model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# Load the base model
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Load the LoRA adapters on top
model = PeftModel.from_pretrained(base_model, "./llama3-8b-finetuned")
tokenizer = AutoTokenizer.from_pretrained("./llama3-8b-finetuned")

# Generate a response using the fine-tuned model
prompt = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
Explain what gradient descent is to a beginner.

### Response:
"""

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        do_sample=True,
    )

response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
print(response)
```

---

## Memory requirements reference

| Model size | QLoRA (4-bit + r=16) | LoRA (16-bit + r=16) | Full fine-tune (16-bit) |
|-----------|---------------------|---------------------|------------------------|
| 7B | ~8 GB | ~16 GB | ~80 GB (4×A100 20GB) |
| 13B | ~12 GB | ~28 GB | ~140 GB |
| 70B | ~48 GB | ~140 GB | ~600 GB |

QLoRA makes 7B fine-tuning possible on a single RTX 3090 or 4090 (24GB VRAM).

---

## Common errors and fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `CUDA out of memory` | Batch too large | Reduce `per_device_train_batch_size`, increase `gradient_accumulation_steps` |
| `RuntimeError: Expected all tensors on same device` | Model sharded across GPUs incorrectly | Set `device_map="auto"` and use `accelerate` |
| `ValueError: pad_token is None` | Llama has no pad token | Set `tokenizer.pad_token = tokenizer.eos_token` |
| Loss is NaN from step 1 | Bad data (empty strings, nulls) or too high LR | Clean dataset; reduce learning rate to 1e-4 |
| Very slow training | `packing=False` leaving empty padding | Set `packing=True` or at least `DataCollatorForSeq2Seq` |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 When_to_Use.md](./When_to_Use.md) | When to fine-tune vs other approaches |

⬅️ **Prev:** [03 Pretraining](../03_Pretraining/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Instruction Tuning](../05_Instruction_Tuning/Theory.md)
