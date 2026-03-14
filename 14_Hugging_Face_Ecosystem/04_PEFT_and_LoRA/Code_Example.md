# PEFT and LoRA — Code Examples

## Setup

```python
# pip install peft transformers bitsandbytes accelerate datasets torch

from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    PeftModel,
    TaskType,
)
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
)
from datasets import load_dataset
import torch
```

---

## Example 1: Basic LoRA Setup — Check Trainable Parameters

```python
from transformers import AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType

# Load a small model for demonstration
# In practice: "meta-llama/Llama-2-7b-hf", "mistralai/Mistral-7B-v0.1", etc.
model = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",      # ~700MB — good for demos
    torch_dtype=torch.float16,
    device_map="auto"
)

print("BASE MODEL:")
total_params = sum(p.numel() for p in model.parameters())
print(f"  Total parameters: {total_params:,}")

# Define LoRA configuration
lora_config = LoraConfig(
    r=8,                               # Rank — bottleneck dimension
    lora_alpha=16,                     # Scaling factor (usually 2×r)
    target_modules=["q_proj", "v_proj"],  # Apply LoRA to query and value projections
    lora_dropout=0.05,                 # Dropout for regularization
    bias="none",                       # Don't train bias terms
    task_type=TaskType.CAUSAL_LM,      # Task type
)

# Wrap model with LoRA
lora_model = get_peft_model(model, lora_config)

print("\nLORA MODEL:")
lora_model.print_trainable_parameters()
# → trainable params: 1,769,472 || all params: 332,396,544 || trainable%: 0.53%

# Inspect which parameters are trainable
print("\nTrainable parameter names:")
for name, param in lora_model.named_parameters():
    if param.requires_grad:
        print(f"  {name}: {param.shape}")
```

---

## Example 2: QLoRA Setup (4-bit Quantization + LoRA)

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

# Step 1: Configure 4-bit quantization (QLoRA)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                         # Enable 4-bit loading
    bnb_4bit_use_double_quant=True,            # Save even more memory
    bnb_4bit_quant_type="nf4",                 # NF4: best format for LLM weights
    bnb_4bit_compute_dtype=torch.bfloat16,     # BF16 for actual computation
)

# Step 2: Load model in 4-bit — drastically reduced VRAM
model = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",                       # Replace with any model
    quantization_config=bnb_config,
    device_map="auto",                         # Auto-distribute across GPU/CPU
)

print(f"Model device: {next(model.parameters()).device}")
print(f"Model dtype: {next(model.parameters()).dtype}")  # → torch.uint8 (4-bit)

# Step 3: Prepare for k-bit training (required before applying LoRA)
# This enables gradient checkpointing and sets up proper layer norms
model = prepare_model_for_kbit_training(
    model,
    use_gradient_checkpointing=True   # Reduces memory at cost of speed
)

# Step 4: Apply LoRA adapters on top of quantized model
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "out_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# → trainable params: 3,539,968 || all params: 332,921,856 || trainable%: 1.063%
```

---

## Example 3: LoRA Fine-Tuning for Classification

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import numpy as np

# --- Data ---
ds = load_dataset("imdb")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def preprocess(examples):
    tokenized = tokenizer(examples["text"], truncation=True, padding="max_length", max_length=256)
    tokenized["labels"] = examples["label"]
    return tokenized

tokenized_ds = ds.map(preprocess, batched=True, remove_columns=["text", "label"])
tokenized_ds.set_format("torch")

# --- Model with LoRA ---
base_model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=2
)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_lin", "v_lin"],   # DistilBERT uses different names
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.SEQ_CLS,           # Sequence classification
)

model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()

# --- Training ---
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    accuracy = (preds == labels).mean()
    return {"accuracy": accuracy}

training_args = TrainingArguments(
    output_dir="./lora-sentiment-classifier",
    num_train_epochs=3,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=64,
    learning_rate=2e-4,             # LoRA benefits from higher LR than full fine-tune
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    fp16=True,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_ds["train"].select(range(5000)),  # Subset for demo
    eval_dataset=tokenized_ds["test"].select(range(1000)),
    compute_metrics=compute_metrics,
)

trainer.train()
print("Training complete!")
```

---

## Example 4: Saving, Loading, and Merging Adapters

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── After training: save the adapter ─────────────────────────────
# Only saves the small adapter files (NOT the full base model)
lora_model.save_pretrained("./my-lora-adapter")
tokenizer.save_pretrained("./my-lora-adapter")
# Creates:
#   ./my-lora-adapter/adapter_config.json    ← LoRA config (r, alpha, target_modules, etc.)
#   ./my-lora-adapter/adapter_model.safetensors  ← The actual A and B matrices

# ── Push only the adapter to Hub ─────────────────────────────────
from huggingface_hub import login
login(token="hf_your_token")
lora_model.push_to_hub("your-username/my-adapter")  # Uploads adapter, not base model

# ── Load and use the adapter ─────────────────────────────────────
base_model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")
model_with_adapter = PeftModel.from_pretrained(base_model, "./my-lora-adapter")

# Run inference with the adapted model
tokenizer = AutoTokenizer.from_pretrained("./my-lora-adapter")
inputs = tokenizer("The capital of France is", return_tensors="pt")

with torch.no_grad():
    outputs = model_with_adapter.generate(**inputs, max_new_tokens=20)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))

# ── Merge for production (eliminates inference overhead) ──────────
merged_model = model_with_adapter.merge_and_unload()
# merged_model is now a regular AutoModelForCausalLM with LoRA baked in
# No PEFT overhead at inference time

merged_model.save_pretrained("./merged-final-model")
tokenizer.save_pretrained("./merged-final-model")

# Later: load like any normal model
final = AutoModelForCausalLM.from_pretrained("./merged-final-model")
```

---

## Example 5: Multiple Adapters — Hot-Swapping for Different Tasks

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# The power of adapters: one base model, many specializations
base_model = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",
    device_map="auto",
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained("facebook/opt-350m")

def generate(model, prompt, max_new_tokens=50):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens,
                                     do_sample=False)
    return tokenizer.decode(output_ids[0][inputs['input_ids'].shape[1]:],
                             skip_special_tokens=True)

# Load model without adapter (base behavior)
print("Base model:", generate(base_model, "Translate to French: Hello world"))

# Load with a code adapter
code_model = PeftModel.from_pretrained(base_model, "./code-adapter")
print("Code adapter:", generate(code_model, "Write a Python function to sort a list:"))

# Load with a different adapter (without reloading base model)
code_model.load_adapter("./sql-adapter", adapter_name="sql")
code_model.set_adapter("sql")
print("SQL adapter:", generate(code_model, "Write a SQL query to get all users:"))

# Switch back to code adapter
code_model.set_adapter("default")
print("Back to code:", generate(code_model, "Python list comprehension example:"))
```

---

## Example 6: Find Target Modules for Any Model

```python
# Before creating a LoraConfig, always check the actual module names
from transformers import AutoModelForCausalLM
import torch

model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m",
                                              torch_dtype=torch.float16)

print("All Linear layers in the model:")
print("=" * 60)
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        print(f"  {name:55s} shape: {list(module.weight.shape)}")

# OPT model output will show:
# model.decoder.layers.0.self_attn.q_proj   shape: [1024, 1024]
# model.decoder.layers.0.self_attn.k_proj   shape: [1024, 1024]
# model.decoder.layers.0.self_attn.v_proj   shape: [1024, 1024]
# model.decoder.layers.0.self_attn.out_proj shape: [1024, 1024]
# model.decoder.layers.0.fc1               shape: [4096, 1024]
# model.decoder.layers.0.fc2               shape: [1024, 4096]
# ... (repeats for all layers)

# Use the last part of the name (after the last dot) in target_modules:
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],  # These names match what we saw above
    task_type=TaskType.CAUSAL_LM,
)
```

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full PEFT and LoRA explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| 📄 **Code_Example.md** | Working code (you are here) |
| [📄 When_to_Use.md](./When_to_Use.md) | Decision guide for fine-tuning approaches |

⬅️ **Prev:** [Datasets Library](../03_Datasets_Library/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Trainer API](../05_Trainer_API/Theory.md)
