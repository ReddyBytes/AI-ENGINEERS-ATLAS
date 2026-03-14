# Datasets Library — Code Examples

## Setup

```python
# pip install datasets transformers torch

from datasets import (
    load_dataset,
    load_from_disk,
    Dataset,
    DatasetDict,
    concatenate_datasets,
)
from transformers import AutoTokenizer
import torch
```

---

## Example 1: Loading Hub Datasets and Exploring Structure

```python
from datasets import load_dataset

# Load a complete dataset with all splits
ds = load_dataset("imdb")
print(ds)
# DatasetDict({
#     train: Dataset({features: ['text', 'label'], num_rows: 25000})
#     test:  Dataset({features: ['text', 'label'], num_rows: 25000})
# })

# Access individual splits
train_ds = ds["train"]
test_ds  = ds["test"]

# Explore structure
print(f"Features: {train_ds.features}")
print(f"Columns: {train_ds.column_names}")
print(f"Number of examples: {len(train_ds)}")

# Access individual examples
first_example = train_ds[0]
print(f"\nFirst example:")
print(f"Label: {first_example['label']}")
print(f"Text preview: {first_example['text'][:200]}")

# Access a range — returns a dict of lists
batch = train_ds[0:5]
print(f"\nBatch labels: {batch['label']}")
print(f"Batch texts (first 50 chars each): {[t[:50] for t in batch['text']]}")

# Use human-readable label names
label_names = train_ds.features["label"].names
print(f"\nLabel names: {label_names}")   # ['neg', 'pos']
print(f"First label: {label_names[first_example['label']]}")  # 'neg'

# Load only one split
train_only = load_dataset("imdb", split="train")
print(f"\nType when single split loaded: {type(train_only)}")  # Dataset (not DatasetDict)

# Load a percentage
small_train = load_dataset("imdb", split="train[:10%]")
print(f"10% of train: {len(small_train)} examples")  # → 2500

# Load a GLUE task (dataset + config name)
mrpc = load_dataset("glue", "mrpc")
print(f"\nGLUE MRPC: {mrpc}")
```

---

## Example 2: Transforming Data with .map()

```python
from datasets import load_dataset
from transformers import AutoTokenizer

ds = load_dataset("imdb")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# ── Basic transformation: add a word count column ─────────────────
def add_word_count(example):
    """Adds a word_count column to each example."""
    return {"word_count": len(example["text"].split())}

ds_with_counts = ds["train"].map(add_word_count)
print(ds_with_counts.column_names)  # ['text', 'label', 'word_count']
print(f"Average word count: {sum(ds_with_counts['word_count']) / len(ds_with_counts):.0f}")

# ── Tokenization: the most common .map() use case ─────────────────
def tokenize_function(examples):
    """
    Tokenizes the 'text' column.
    With batched=True, examples is a dict of lists.
    We return a dict with new keys; original keys are kept unless removed.
    """
    return tokenizer(
        examples["text"],
        truncation=True,       # Truncate to max_length
        padding="max_length",  # Pad to max_length (for uniform tensors)
        max_length=256,        # Shorter than 512 to save memory
    )

# batched=True is critical for speed — uses fast Rust tokenizer
# num_proc=4 uses 4 CPU cores in parallel
# remove_columns removes the original text (no longer needed after tokenization)
tokenized_train = ds["train"].map(
    tokenize_function,
    batched=True,
    num_proc=4,
    remove_columns=["text"],   # Drop raw text after tokenizing
    desc="Tokenizing train set" # Shows progress bar label
)

print(f"\nTokenized columns: {tokenized_train.column_names}")
# ['label', 'input_ids', 'token_type_ids', 'attention_mask']

print(f"Shape of first input_ids: {len(tokenized_train[0]['input_ids'])}")  # 256

# ── Rename columns for the Trainer ────────────────────────────────
# Trainer expects "labels" (plural), not "label"
def rename_label(example):
    return {"labels": example["label"]}

tokenized_train = tokenized_train.map(rename_label, remove_columns=["label"])
print(f"Final columns: {tokenized_train.column_names}")
# ['input_ids', 'token_type_ids', 'attention_mask', 'labels']

# Set format so DataLoader gets tensors, not Python lists
tokenized_train.set_format("torch")
print(f"\nFirst batch type: {type(tokenized_train[0]['input_ids'])}")  # torch.Tensor
```

---

## Example 3: Filtering and Selecting Data

```python
from datasets import load_dataset

ds = load_dataset("imdb", split="train")

# ── Filter: keep only positive reviews ───────────────────────────
positive_only = ds.filter(lambda example: example["label"] == 1)
print(f"Original: {len(ds)}, Positive only: {len(positive_only)}")

# ── Filter: keep reviews with at least 100 words ─────────────────
long_reviews = ds.filter(lambda example: len(example["text"].split()) >= 100)
print(f"Long reviews (≥100 words): {len(long_reviews)}")

# ── Filter with batched=True (faster for large datasets) ──────────
def is_long_batch(examples):
    return [len(text.split()) >= 100 for text in examples["text"]]

long_reviews_fast = ds.filter(is_long_batch, batched=True)
print(f"Same result: {len(long_reviews_fast)}")

# ── Select: take a specific subset ───────────────────────────────
first_100 = ds.select(range(100))
print(f"First 100: {len(first_100)}")

# Random subset for quick experiments
import random
random_indices = random.sample(range(len(ds)), 500)
random_500 = ds.select(random_indices)

# Shuffle then select (more convenient random sample)
random_500_v2 = ds.shuffle(seed=42).select(range(500))

# ── Create a validation split from train ─────────────────────────
# When a dataset has no validation split, create one from train
split = ds.train_test_split(test_size=0.1, seed=42)
print(f"\nAfter splitting:")
print(f"  New train: {len(split['train'])}")    # 22,500
print(f"  Validation: {len(split['test'])}")     # 2,500
```

---

## Example 4: Streaming a Large Dataset

```python
from datasets import load_dataset

# Streaming: no full download required
# Great for datasets like C4, RedPajama, etc. that are hundreds of GB

print("Creating streaming dataset (no download)...")
stream_ds = load_dataset("c4", "en", split="train", streaming=True)

# Peek at the structure by looking at the first example
first = next(iter(stream_ds))
print(f"Columns: {list(first.keys())}")
print(f"Text preview: {first['text'][:200]}")

# take(n) is a convenient way to get the first n examples
print("\nFirst 3 texts:")
for i, example in enumerate(stream_ds.take(3)):
    word_count = len(example["text"].split())
    print(f"  [{i}] {word_count} words: {example['text'][:60]}...")

# Apply transformations in streaming mode
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("gpt2")

def tokenize_streaming(examples):
    return tokenizer(examples["text"], truncation=True, max_length=1024)

tokenized_stream = stream_ds.map(tokenize_streaming, batched=True,
                                  remove_columns=["text", "timestamp", "url"])

# Shuffle with a rolling buffer (approximate, but usually sufficient)
shuffled_stream = tokenized_stream.shuffle(seed=42, buffer_size=5_000)

# Iterate through the stream (this is how you'd use it in training)
print("\nIterating through shuffled stream:")
for i, batch in enumerate(shuffled_stream.take(5)):
    print(f"  Batch {i}: {len(batch['input_ids'])} tokens")
```

---

## Example 5: Loading Local and Custom Data

```python
from datasets import load_dataset, Dataset, DatasetDict
import pandas as pd

# ── From CSV files ────────────────────────────────────────────────
# Single file (all becomes "train")
ds_csv = load_dataset("csv", data_files="my_reviews.csv")

# Explicit train/test split
ds_csv_split = load_dataset("csv", data_files={
    "train": "train.csv",
    "validation": "val.csv",
    "test": "test.csv"
})

# ── From JSON/JSONL files ─────────────────────────────────────────
# JSONL format (one JSON object per line) is most common
ds_json = load_dataset("json", data_files="data.jsonl")

# Nested JSON with a specific field as the records
ds_nested = load_dataset("json", data_files="data.json", field="records")

# ── From a pandas DataFrame ───────────────────────────────────────
# Most flexible approach — works with any pandas-readable format
train_df = pd.DataFrame({
    "text": ["I love this!", "This is bad.", "It was okay."],
    "label": [1, 0, 0]
})
test_df = pd.DataFrame({
    "text": ["Excellent product!", "Terrible service."],
    "label": [1, 0]
})

# Create Dataset from DataFrame
train_ds = Dataset.from_pandas(train_df, preserve_index=False)
test_ds  = Dataset.from_pandas(test_df, preserve_index=False)

# Combine into DatasetDict (same structure as Hub datasets)
custom_ds = DatasetDict({
    "train": train_ds,
    "test": test_ds
})

print(custom_ds)
# DatasetDict({ train: Dataset(...), test: Dataset(...) })

# Works exactly like a Hub dataset
print(custom_ds["train"][0])
```

---

## Example 6: Saving, Loading, and Combining Datasets

```python
from datasets import load_dataset, load_from_disk, concatenate_datasets

# ── Save preprocessed dataset to disk ────────────────────────────
# This is valuable when tokenization takes a long time
ds = load_dataset("imdb")
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

tokenized_ds = ds.map(
    lambda ex: tokenizer(ex["text"], truncation=True, padding="max_length", max_length=256),
    batched=True,
    remove_columns=["text"]
)

# Save (Arrow format — fast to load)
tokenized_ds.save_to_disk("/tmp/tokenized_imdb")
print("Dataset saved!")

# ── Load a saved dataset (instant — just memory-maps the files) ───
loaded_ds = load_from_disk("/tmp/tokenized_imdb")
print(f"Loaded: {loaded_ds}")

# ── Combine multiple datasets ─────────────────────────────────────
# Useful when building training data from multiple sources
ds_yelp = load_dataset("yelp_review_full", split="train[:5000]")
ds_imdb = load_dataset("imdb", split="train[:5000]")

# Both must have the same columns (or you select matching ones)
# Rename/align columns first if needed
ds_yelp_aligned = ds_yelp.select_columns(["text", "label"])
ds_imdb_aligned = ds_imdb.select_columns(["text", "label"])

# Binarize yelp (5-class → positive/negative)
ds_yelp_binary = ds_yelp_aligned.map(
    lambda ex: {"label": 1 if ex["label"] >= 3 else 0}
)

combined = concatenate_datasets([ds_imdb_aligned, ds_yelp_binary])
print(f"Combined dataset: {len(combined)} examples")
combined_shuffled = combined.shuffle(seed=42)
```

---

## Example 7: Full Pipeline — Load, Tokenize, Train-Ready

```python
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader

# 1. Load data
ds = load_dataset("imdb")

# 2. Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# 3. Tokenize all splits
def preprocess(examples):
    tokenized = tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=256
    )
    tokenized["labels"] = examples["label"]  # Trainer expects "labels"
    return tokenized

tokenized = ds.map(preprocess, batched=True, remove_columns=["text", "label"])
tokenized.set_format("torch")

# 4. Create DataLoaders
train_loader = DataLoader(tokenized["train"], batch_size=32, shuffle=True)
test_loader  = DataLoader(tokenized["test"],  batch_size=64, shuffle=False)

# 5. Verify
batch = next(iter(train_loader))
print("Batch keys:", list(batch.keys()))
print("input_ids shape:", batch["input_ids"].shape)   # [32, 256]
print("labels shape:", batch["labels"].shape)          # [32]

print("\nDataset is ready for training!")
```

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full datasets library explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| 📄 **Code_Example.md** | Working code (you are here) |

⬅️ **Prev:** [Transformers Library](../02_Transformers_Library/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [PEFT and LoRA](../04_PEFT_and_LoRA/Theory.md)
