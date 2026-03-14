# Datasets Library — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **load_dataset** | Downloads and caches a Hub dataset (or loads a local file) |
| **DatasetDict** | A dict of splits: `{"train": ..., "test": ..., "validation": ...}` |
| **Dataset** | A single split — an immutable, indexed collection of examples |
| **IterableDataset** | Streaming version — sequential access only, no random indexing |
| **Apache Arrow** | Columnar binary format used internally — enables memory mapping |
| **memory-mapped** | Data stays on disk; only accessed pages load into RAM |
| **.map()** | Apply a transformation function to every example (or batch) |
| **.filter()** | Keep only examples where a condition is True |
| **.select()** | Return a subset of rows by index |
| **batched=True** | Process multiple examples per `.map()` call — much faster |
| **streaming=True** | Load data on-the-fly without downloading everything first |
| **set_format** | Convert columns to PyTorch/NumPy/etc. for use with DataLoader |

---

## Core Functions

```python
from datasets import load_dataset, Dataset, DatasetDict, concatenate_datasets

# ── LOADING ──────────────────────────────────────────────────────
ds = load_dataset("imdb")                           # Hub dataset
ds = load_dataset("glue", "mrpc")                   # Dataset + config
ds = load_dataset("imdb", split="train")            # Single split only
ds = load_dataset("imdb", split="train[:10%]")      # First 10% of train

# From local files
ds = load_dataset("csv",  data_files="data.csv")
ds = load_dataset("json", data_files="data.jsonl")
ds = load_dataset("parquet", data_files="data.parquet")

# From pandas
import pandas as pd
ds = Dataset.from_pandas(pd.read_csv("data.csv"))

# ── EXPLORATION ───────────────────────────────────────────────────
ds["train"][0]              # First example as dict
ds["train"][0:5]            # First 5 examples as dict of lists
ds["train"].features        # Schema / data types
ds["train"].column_names    # List of column names
len(ds["train"])            # Number of examples

# ── TRANSFORMATION ────────────────────────────────────────────────
# Apply function to all examples
new_ds = ds["train"].map(my_function)

# Batched (faster — process N examples at once)
new_ds = ds["train"].map(my_function, batched=True, batch_size=1000)

# Parallel processing
new_ds = ds["train"].map(my_function, batched=True, num_proc=4)

# Drop original columns
new_ds = ds["train"].map(tokenize_fn, batched=True, remove_columns=["text"])

# ── FILTERING & SELECTING ─────────────────────────────────────────
filtered = ds["train"].filter(lambda x: x["label"] == 1)
subset   = ds["train"].select(range(1000))
shuffled = ds["train"].shuffle(seed=42)
sorted_ds = ds["train"].sort("label")

# ── FORMAT FOR TRAINING ───────────────────────────────────────────
ds["train"].set_format("torch", columns=["input_ids", "attention_mask", "labels"])
ds["train"].set_format("numpy")

# Convert to PyTorch DataLoader
from torch.utils.data import DataLoader
loader = DataLoader(ds["train"], batch_size=32, shuffle=True)

# ── STREAMING ─────────────────────────────────────────────────────
stream = load_dataset("c4", "en", split="train", streaming=True)
for example in stream.take(10):    # First 10 examples
    print(example["text"][:50])

# ── SAVING & LOADING LOCALLY ─────────────────────────────────────
ds["train"].save_to_disk("/path/to/saved_dataset")
from datasets import load_from_disk
ds = load_from_disk("/path/to/saved_dataset")

# ── COMBINING DATASETS ────────────────────────────────────────────
combined = concatenate_datasets([ds1, ds2])
```

---

## .map() Patterns

```python
# Pattern 1: Add a new column
def add_word_count(example):
    return {"word_count": len(example["text"].split())}

# Pattern 2: Tokenize (most common use case)
def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length")

# Pattern 3: Rename / reformat labels
def rename_labels(example):
    return {"labels": example["label"]}  # Trainer expects "labels" column

# Pattern 4: Multi-column transform
def format_for_qa(examples):
    return tokenizer(
        examples["question"],
        examples["context"],   # Second sequence for QA models
        truncation=True,
        max_length=512
    )
```

---

## Split Slicing Syntax

```python
# These all work as the split= argument
load_dataset("imdb", split="train")         # Full train set
load_dataset("imdb", split="train[:1000]")  # First 1000 examples
load_dataset("imdb", split="train[-1000:]") # Last 1000 examples
load_dataset("imdb", split="train[:10%]")   # First 10%
load_dataset("imdb", split="train[10%:20%]") # 10% to 20%

# Combine splits
load_dataset("imdb", split="train+test")    # Merge train and test
```

---

## When to Use vs When NOT to Use Streaming

| ✅ Use `streaming=True` when | ❌ Use regular loading when |
|-----------------------------|---------------------------|
| Dataset is larger than disk space | Dataset fits on disk |
| You only need one pass | You need multiple passes (multiple epochs) |
| You want to start iterating immediately | Random access is required |
| Exploratory analysis of huge datasets | You need `.filter()` and `.select()` with indexing |

---

## Golden Rules

1. **Always use `batched=True` in `.map()`** — it's 10-50x faster than per-example processing.
2. **Use `remove_columns=` after tokenization** — keep only the columns the model needs.
3. **Cache is your friend** — `.map()` with the same function and args reuses cached results instantly.
4. **Use `num_proc=`** for CPU-bound transforms (tokenization, text cleaning) — speeds up by number of cores.
5. **Call `.set_format("torch")`** before DataLoader — raw Dataset returns Python dicts, not tensors.
6. **Save preprocessed datasets** with `.save_to_disk()` — avoids re-running expensive `.map()` calls.

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full datasets library explanation |
| 📄 **Cheatsheet.md** | Quick reference (you are here) |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | Working code: loading, transforms, streaming |

⬅️ **Prev:** [Transformers Library](../02_Transformers_Library/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [PEFT and LoRA](../04_PEFT_and_LoRA/Theory.md)
