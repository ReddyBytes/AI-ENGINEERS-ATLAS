# PEFT and LoRA — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **PEFT** | Parameter-Efficient Fine-Tuning — fine-tune with a tiny fraction of parameters updated |
| **LoRA** | Low-Rank Adaptation — inject small trainable matrices alongside frozen attention layers |
| **QLoRA** | LoRA on a 4-bit quantized base model — enables fine-tuning on consumer GPUs |
| **Rank (r)** | Bottleneck dimension of LoRA matrices — higher = more capacity, more parameters |
| **lora_alpha** | Scaling factor for LoRA updates — controls how strongly the adapter affects output |
| **target_modules** | Which weight matrices in the model get LoRA adapters |
| **Adapter** | Generic term for a small trainable module added to a frozen base model |
| **merge_and_unload** | Folds LoRA weights into the base model — eliminates inference overhead |
| **NF4** | 4-bit Normal Float — QLoRA's quantization format, tuned for normally distributed weights |
| **bitsandbytes** | Python library that implements INT8/INT4 quantization for transformers |
| **trainable_parameters** | Only LoRA A and B matrices — the base model weights are frozen |

---

## LoRA Setup — Core Pattern

```python
# pip install peft transformers bitsandbytes accelerate

from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer

# 1. Load base model (frozen)
model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")

# 2. Configure LoRA
config = LoraConfig(
    r=8,                              # Rank — start here, tune up if needed
    lora_alpha=16,                    # Scaling: usually 2*r
    target_modules=["q_proj", "v_proj"],  # Which layers get adapters
    lora_dropout=0.05,                # Regularization for adapter layers
    bias="none",                      # Don't train bias terms
    task_type=TaskType.CAUSAL_LM,     # Task type for correct output handling
)

# 3. Wrap the model with LoRA
lora_model = get_peft_model(model, config)

# 4. Check how few parameters are trainable
lora_model.print_trainable_parameters()
# → trainable params: 1,769,472 || all params: 332,396,544 || trainable%: 0.532%
```

---

## QLoRA Setup — 4-bit Quantization

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import torch

# Configure 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,              # Enable 4-bit loading
    bnb_4bit_use_double_quant=True, # Double quantization (saves a bit more memory)
    bnb_4bit_quant_type="nf4",      # NF4 format (best for normally distributed weights)
    bnb_4bit_compute_dtype=torch.bfloat16  # Computation in bfloat16
)

# Load model in 4-bit
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto"
)

# Required step before LoRA on quantized models
model = prepare_model_for_kbit_training(model)

# Apply LoRA on top of quantized model
lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"],
                          lora_dropout=0.05, bias="none", task_type="CAUSAL_LM")
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

---

## LoRA Hyperparameter Guide

| Hyperparameter | Common Values | Effect |
|---------------|---------------|--------|
| `r` (rank) | 4, 8, 16, 32, 64 | Higher = more capacity, more params. Start at 8. |
| `lora_alpha` | = r or 2×r | Higher = stronger LoRA update. Usually 16 or 32. |
| `target_modules` | `["q_proj","v_proj"]` (light) to all attention+FFN layers | More modules = more coverage, more params |
| `lora_dropout` | 0.0 – 0.1 | Regularizes adapters. Use 0.05 for most tasks. |
| `bias` | `"none"`, `"all"`, `"lora_only"` | `"none"` is standard |

---

## Comparison Table: Fine-Tuning Approaches

| Approach | VRAM for 7B | Trainable Params | Speed | Quality |
|----------|-------------|-----------------|-------|---------|
| Full fine-tune | ~56 GB | 100% | Slowest | Best |
| LoRA (FP16) | ~14 GB | 0.1–1% | Fast | Near full |
| QLoRA (INT4) | ~6–10 GB | 0.1–1% | Fast | Slightly below LoRA |
| Prompt tuning | ~14 GB | <0.01% | Fastest | Weakest |

---

## Loading and Using a LoRA Adapter

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load base model
base_model = AutoModelForCausalLM.from_pretrained("facebook/opt-350m")

# Load LoRA adapter on top (the adapter is stored separately from base model)
model = PeftModel.from_pretrained(base_model, "path/to/lora-adapter")

# For production: merge LoRA into base weights (eliminates inference overhead)
merged_model = model.merge_and_unload()

# Now merged_model behaves like a regular model — no PEFT overhead
merged_model.save_pretrained("./my-fine-tuned-model")
```

---

## When to Use vs When NOT to Use LoRA

| ✅ Use LoRA when | ❌ Avoid LoRA when |
|-----------------|-------------------|
| You have < 24GB VRAM | You have 8× A100s and time for full fine-tune |
| You need multiple task-specific adapters | You need maximum possible quality |
| You want to share adapters separately from base model | The task is completely unlike the base model's training |
| Budget is constrained | You're doing continued pretraining on large corpora |

---

## Golden Rules

1. **Start with `r=8, alpha=16`** — this is the most-used default and works well for instruction tuning.
2. **Target at least `q_proj` and `v_proj`** — these are the most important attention matrices for task adaptation.
3. **Always call `prepare_model_for_kbit_training()`** before adding LoRA to a quantized model.
4. **Use `merge_and_unload()`** before deploying to production — removes inference overhead.
5. **Enable `gradient_checkpointing`** when VRAM is tight — trades some speed for memory during backprop.
6. **Push only the adapter, not the full model** — `model.push_to_hub()` on a `PeftModel` uploads only the small adapter files.

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full PEFT and LoRA explanation |
| 📄 **Cheatsheet.md** | Quick reference (you are here) |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | LoRA fine-tuning with PEFT library |
| [📄 When_to_Use.md](./When_to_Use.md) | Decision guide for fine-tuning approaches |

⬅️ **Prev:** [Datasets Library](../03_Datasets_Library/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Trainer API](../05_Trainer_API/Theory.md)
