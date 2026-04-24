# Datasets Library — Interview Q&A

## Beginner Level

**Q1: What is the Hugging Face `datasets` library and what problems does it solve?**

<details>
<summary>💡 Show Answer</summary>

**A:** The `datasets` library is a Python package that provides a unified API for loading, exploring, and transforming machine learning datasets. It solves three main problems:

1. **Format fragmentation** — datasets come as CSV, JSON, Parquet, plain text, and custom formats. `load_dataset()` handles all of them with the same interface.
2. **Memory limitations** — traditional approaches load data entirely into RAM. `datasets` uses memory-mapped Apache Arrow files, so a 500GB dataset can be processed on a 16GB RAM laptop by loading only accessed pages.
3. **Slow preprocessing** — tokenizing millions of examples one-at-a-time in Python is very slow. The `.map(batched=True, num_proc=N)` pattern parallelizes this across CPU cores and processes examples in chunks.

The library also provides instant access to 50,000+ Hub datasets with a single `load_dataset("dataset-name")` call.

</details>

---

<br>

**Q2: What does `load_dataset("imdb")` return? Walk through the data structure.**

<details>
<summary>💡 Show Answer</summary>

**A:** `load_dataset("imdb")` returns a `DatasetDict` — a dictionary-like object where keys are split names and values are `Dataset` objects:

```python
DatasetDict({
    train: Dataset({features: ['text', 'label'], num_rows: 25000})
    test:  Dataset({features: ['text', 'label'], num_rows: 25000})
})
```

You access splits with `ds["train"]` and individual examples with `ds["train"][0]`, which returns a dictionary:
```python
{'text': 'I rented I AM CURIOUS-YELLOW...', 'label': 0}
```

The `features` attribute tells you the schema — column names and types. `ClassLabel` features include the string names of each class (e.g., `['neg', 'pos']`), which is useful for converting integer labels back to strings.

</details>

---

<br>

**Q3: What is the difference between `.map()`, `.filter()`, and `.select()`?**

<details>
<summary>💡 Show Answer</summary>

**A:**
- **`.map(fn)`:** Applies a function to every example and returns a new dataset. The function can add new columns, modify existing columns, or both. This is the primary transformation tool — used for tokenization, normalization, feature engineering, etc.

- **`.filter(fn)`:** Applies a boolean function to each example and keeps only examples where the function returns `True`. This is for removing unwanted rows — e.g., removing short texts, removing examples from certain classes, etc.

- **`.select(indices)`:** Returns a new dataset containing only the rows at the specified indices. This is for taking a subset — useful for quick experiments on a small sample (`ds.select(range(100))`) or for splitting a single split into train/validation.

All three return a new `Dataset` object (the original is not modified) and produce a cached Arrow file so repeated calls with the same parameters are instant.

</details>

---

## Intermediate Level

**Q4: Explain why `batched=True` in `.map()` is significantly faster than the default per-example processing.**

<details>
<summary>💡 Show Answer</summary>

**A:** When `batched=False` (the default), the map function is called once per example with a single dictionary as input. Python function call overhead, type conversion, and tokenizer initialization happen 25,000 times for a 25,000-example dataset.

When `batched=True`, the function is called with a dictionary of lists (N examples at once, where N is `batch_size`, default 1000). This is faster because:

1. **Tokenizer batch mode is optimized** — `tokenizer(list_of_texts)` uses Rust-based fast tokenizers with internal parallelism, often 10-100x faster than calling `tokenizer(single_text)` in a loop
2. **Less Python overhead** — 25 function calls (for 25,000 examples with batch_size=1000) vs 25,000 function calls
3. **Better cache write patterns** — Arrow writes large chunks more efficiently than individual rows

Rule of thumb: always use `batched=True` for tokenization. The only time you might not is if your function inherently processes one example at a time and isn't compatible with batching.

</details>

---

<br>

**Q5: How does streaming mode work and what are its limitations?**

<details>
<summary>💡 Show Answer</summary>

**A:** Streaming mode (enabled with `streaming=True`) returns an `IterableDataset` instead of a `Dataset`. The key difference:

- **Regular `Dataset`:** Downloads everything, converts to Arrow files on disk, then memory-maps them. Random access: `ds[1000]` works.
- **`IterableDataset`:** Downloads and processes data row-by-row (or small chunk-by-chunk) as you iterate. No full download needed. No random access.

Under the hood, streaming fetches dataset files in chunks using HTTP range requests. The library handles decompression and format parsing on-the-fly.

**Limitations:**
1. **No random access** — `streaming_ds[100]` raises an error. You can only iterate sequentially.
2. **No `.filter()` or `.select()` with indices** — you can use `.filter(fn)` (iterates through all, keeps matching), but it can't skip to a specific row
3. **No caching of transforms** — every time you iterate, transformations re-run. Regular `.map()` caches results.
4. **Shuffling is approximate** — true shuffling requires random access. Streaming uses a buffer shuffle (`ds.shuffle(buffer_size=10000)`) which shuffles within a rolling window.
5. **`len()` is unavailable** — since the total size may not be known until the full dataset is read, `len(streaming_ds)` raises an error.

Use streaming for very large datasets where you cannot afford the storage for a full download, or for one-off passes.

</details>

---

<br>

**Q6: A colleague says the first call to `.map()` was slow but subsequent calls were instant. Why?**

<details>
<summary>💡 Show Answer</summary>

**A:** The `datasets` library automatically caches the output of `.map()` as an Apache Arrow file on disk. The cache key is determined by:
- The dataset being mapped
- A fingerprint of the map function (its source code hash)
- The parameters passed (e.g., `batched`, `batch_size`, `remove_columns`)

On the first call, the library runs the function on every example and writes the result to `~/.cache/huggingface/datasets/<dataset>/<hash>/`. This can take minutes for large datasets.

On subsequent calls with the same function and parameters, the library detects the existing cache, loads the Arrow file directly, and returns instantly — the function body never executes again.

This behavior is mostly beneficial (speed), but can cause confusion when:
- You modify the function but the cache key doesn't change (modify the function body, not just a variable outside it)
- You want to force re-run: pass `load_from_cache_file=False` to `.map()`
- Disk space fills up: the cache can be cleared manually or via `datasets.utils.file_utils.HfFolder.delete_token()`

</details>

---

## Advanced Level

**Q7: How would you build a custom dataset class for a task that doesn't have a standard Hub dataset — for example, a private corporate email classification dataset?**

<details>
<summary>💡 Show Answer</summary>

**A:** There are two main approaches depending on your data format:

**Approach 1 — Load from local files directly:**
```python
from datasets import load_dataset

# If your data is CSV, JSON, or Parquet, this often works out-of-the-box:
ds = load_dataset("csv", data_files={"train": "emails_train.csv", "test": "emails_test.csv"})
```

**Approach 2 — Create from a pandas DataFrame:**
```python
from datasets import Dataset, DatasetDict
import pandas as pd

train_df = pd.read_csv("train_emails.csv")
test_df = pd.read_csv("test_emails.csv")

ds = DatasetDict({
    "train": Dataset.from_pandas(train_df),
    "test": Dataset.from_pandas(test_df)
})
```

**Approach 3 — Write a custom dataset loading script (for Hub upload):**
Create a Python file `email_dataset.py` that subclasses `datasets.GeneratorBasedBuilder`, defining `_info()` (schema), `_split_generators()` (how to get data), and `_generate_examples()` (yields individual examples). This script can then be loaded with `load_dataset("path/to/email_dataset.py")` or pushed to a private Hub repo.

For a corporate use case, Approach 2 is usually fastest to implement, and the resulting `DatasetDict` works identically to any Hub dataset with `.map()`, `.filter()`, and `Trainer` integration.

</details>

---

<br>

**Q8: You're training a model on a 2TB web crawl dataset. Your server has 500GB of disk space and 64GB of RAM. How do you handle this with the datasets library?**

<details>
<summary>💡 Show Answer</summary>

**A:** This is exactly the use case for streaming mode combined with iterable dataset patterns:

```python
from datasets import load_dataset

# Streaming — never downloads the full 2TB
ds = load_dataset("c4", "en", split="train", streaming=True)

# Apply tokenization in streaming mode
def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, max_length=512)

ds = ds.map(tokenize, batched=True, remove_columns=["text", "timestamp", "url"])

# Shuffle with a rolling buffer (approximate shuffling)
ds = ds.shuffle(seed=42, buffer_size=10_000)

# Pass directly to Trainer — it accepts IterableDataset
from transformers import Trainer, TrainingArguments

trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="./output",
        max_steps=100_000,      # Use max_steps instead of num_epochs
        # (can't compute epochs without knowing total size)
    ),
    train_dataset=ds,           # IterableDataset works here
)
trainer.train()
```

Key considerations:
- Use `max_steps` instead of `num_train_epochs` — you can't compute epoch size without iterating the full stream
- Streaming doesn't support true random shuffling — use a large `buffer_size` for better randomness
- Checkpointing is critical — if training fails, you lose your position in the stream and must restart
- For better shuffling and resumability, consider downloading to cheap object storage (S3/GCS) and loading from there in chunks

</details>

---

<br>

**Q9: What is the Apache Arrow format and why does the datasets library use it instead of something like pickle or HDF5?**

<details>
<summary>💡 Show Answer</summary>

**A:** Apache Arrow is an in-memory columnar data format designed for analytical workloads. The datasets library uses it because of several specific advantages over alternatives:

**Versus pickle:**
- Arrow is language-agnostic (works with Python, Java, R, C++) and can be read by other tools
- Pickle loads entire objects into memory; Arrow supports memory-mapping (only accessed pages load)
- Arrow is not executable — cannot contain malicious code
- Arrow is faster for column access (pickle serializes rows, Arrow stores columns contiguously)

**Versus HDF5:**
- Arrow has better support for variable-length strings and nested data (important for NLP)
- Arrow integrates with the entire data ecosystem (pandas, Spark, Dask) via zero-copy operations
- HDF5 has complex chunking and compression configurations; Arrow's defaults are excellent for ML workloads

**Versus plain CSV/JSON:**
- Arrow is typed — column types are stored and enforced, preventing silent type coercion errors
- Arrow is binary — much faster to read than parsing text formats
- Arrow supports columnar access — fetching one column from a million-row dataset reads only that column's bytes

The key practical benefit: **memory mapping**. Arrow files on disk can be opened as if they're in RAM. The OS only loads the specific pages you access. This is how you can work with a 500GB dataset on a 16GB machine — you never load all 500GB at once, only the rows currently in your batch.

</details>

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full datasets library explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | Interview questions (you are here) |
| [📄 Code_Example.md](./Code_Example.md) | Working code examples |

⬅️ **Prev:** [Transformers Library](../02_Transformers_Library/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [PEFT and LoRA](../04_PEFT_and_LoRA/Theory.md)
