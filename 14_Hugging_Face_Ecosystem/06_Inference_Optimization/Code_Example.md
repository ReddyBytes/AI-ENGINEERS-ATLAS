# Inference Optimization — Code Examples

## Setup

```python
# pip install transformers bitsandbytes accelerate optimum[onnxruntime] torch

from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)
import torch
import time
```

---

## Example 1: Comparing Precision Formats — Memory and Speed

```python
import torch
import time
import psutil
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "facebook/opt-350m"  # Small enough to test locally
tokenizer = AutoTokenizer.from_pretrained(model_id)

def measure_inference(model, inputs, label, num_runs=10):
    """Measure average inference time and print model memory usage."""
    # GPU memory
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        _ = model(**inputs)  # Warm-up
        torch.cuda.synchronize()

        start = time.perf_counter()
        for _ in range(num_runs):
            with torch.no_grad():
                _ = model(**inputs)
        torch.cuda.synchronize()
        elapsed = (time.perf_counter() - start) / num_runs * 1000

        peak_mem = torch.cuda.max_memory_allocated() / 1e9
        print(f"{label:20s} | Time: {elapsed:6.1f}ms | GPU Peak: {peak_mem:.2f} GB")
    else:
        # CPU measurement
        start = time.perf_counter()
        for _ in range(3):
            with torch.no_grad():
                _ = model(**inputs)
        elapsed = (time.perf_counter() - start) / 3 * 1000
        print(f"{label:20s} | Time: {elapsed:6.1f}ms | (CPU mode)")

text = "Hugging Face makes AI accessible to everyone."
inputs = tokenizer(text, return_tensors="pt")

# ── FP32 (baseline) ───────────────────────────────────────────────
print("Loading FP32 model...")
model_fp32 = AutoModelForCausalLM.from_pretrained(model_id)
model_fp32.eval()
if torch.cuda.is_available():
    inputs = {k: v.cuda() for k, v in inputs.items()}
    model_fp32 = model_fp32.cuda()
measure_inference(model_fp32, inputs, "FP32")
del model_fp32
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# ── FP16 ─────────────────────────────────────────────────────────
print("Loading FP16 model...")
model_fp16 = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="auto" if torch.cuda.is_available() else None
)
model_fp16.eval()
if not torch.cuda.is_available():
    model_fp16 = model_fp16.float()
else:
    inputs = {k: v.to("cuda") for k, v in inputs.items()}
measure_inference(model_fp16, inputs, "FP16")
del model_fp16
if torch.cuda.is_available():
    torch.cuda.empty_cache()

# ── INT8 ──────────────────────────────────────────────────────────
if torch.cuda.is_available():
    print("Loading INT8 model (bitsandbytes)...")
    model_int8 = AutoModelForCausalLM.from_pretrained(
        model_id,
        load_in_8bit=True,
        device_map="auto"
    )
    model_int8.eval()
    measure_inference(model_int8, inputs, "INT8 (bitsandbytes)")
    del model_int8
    torch.cuda.empty_cache()

print("\nComparison complete!")
print("FP16 typically: ~50% less memory than FP32, similar speed or faster")
print("INT8 typically: ~75% less memory than FP32, similar speed")
```

---

## Example 2: Load a 7B Model in 4-bit (QLoRA style)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# Configure 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",               # NF4 format
    bnb_4bit_compute_dtype=torch.bfloat16,   # Computation in BF16
    bnb_4bit_use_double_quant=True,          # Extra memory savings
)

model_id = "facebook/opt-1.3b"  # Replace with Llama/Mistral 7B if available
tokenizer = AutoTokenizer.from_pretrained(model_id)

print("Loading model in 4-bit...")
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
)

# Check memory usage
if torch.cuda.is_available():
    mem_gb = torch.cuda.memory_allocated() / 1e9
    print(f"GPU memory used after loading: {mem_gb:.2f} GB")

# Check dtypes of different components
print("\nParameter dtypes:")
dtypes = {}
for name, param in model.named_parameters():
    dtype = str(param.dtype)
    dtypes[dtype] = dtypes.get(dtype, 0) + 1
for dtype, count in dtypes.items():
    print(f"  {dtype}: {count} tensors")

# Run generation
prompt = "The future of artificial intelligence is"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    output_ids = model.generate(
        **inputs,
        max_new_tokens=50,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )

generated = tokenizer.decode(output_ids[0][inputs['input_ids'].shape[1]:],
                               skip_special_tokens=True)
print(f"\nPrompt: {prompt}")
print(f"Generated: {generated}")
```

---

## Example 3: Batch Inference for High Throughput

```python
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import time

model_id = "distilbert-base-uncased-finetuned-sst-2-english"

# ── Method A: Pipeline with batching ──────────────────────────────
clf = pipeline(
    "text-classification",
    model=model_id,
    device=0 if torch.cuda.is_available() else -1,
    batch_size=64,    # Process 64 inputs at a time
)

# Generate 1000 test texts
texts = [f"This product is {'great' if i % 2 == 0 else 'terrible'}! Item number {i}."
         for i in range(1000)]

# Time batch inference vs one-by-one
print("=== Throughput Comparison ===\n")

# One by one
start = time.perf_counter()
results_one = [clf(t)[0] for t in texts[:100]]  # Test on 100 samples
elapsed_one = time.perf_counter() - start
print(f"One-by-one (100 texts):  {elapsed_one:.2f}s  ({100/elapsed_one:.0f} texts/sec)")

# Batch (all at once via pipeline)
start = time.perf_counter()
results_batch = clf(texts[:100], batch_size=64)
elapsed_batch = time.perf_counter() - start
print(f"Batched (100 texts):     {elapsed_batch:.2f}s  ({100/elapsed_batch:.0f} texts/sec)")
print(f"\nSpeedup: {elapsed_one/elapsed_batch:.1f}×")

# ── Method B: Manual batching with AutoModel ──────────────────────
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id)
model.eval()
if torch.cuda.is_available():
    model = model.cuda()

from transformers import DataCollatorWithPadding
from torch.utils.data import DataLoader, Dataset

class TextDataset(Dataset):
    def __init__(self, texts):
        self.encodings = tokenizer(texts, truncation=True, max_length=128)

    def __len__(self):
        return len(self.encodings['input_ids'])

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

dataset = TextDataset(texts)
loader = DataLoader(
    dataset,
    batch_size=64,
    collate_fn=DataCollatorWithPadding(tokenizer, return_tensors="pt")
)

all_predictions = []
start = time.perf_counter()
with torch.no_grad():
    for batch in loader:
        if torch.cuda.is_available():
            batch = {k: v.cuda() for k, v in batch.items()}
        logits = model(**batch).logits
        preds = logits.argmax(-1).cpu().numpy()
        all_predictions.extend(preds)

elapsed_manual = time.perf_counter() - start
print(f"\nManual batched DataLoader: {elapsed_manual:.2f}s  ({len(texts)/elapsed_manual:.0f} texts/sec)")
```

---

## Example 4: Multi-GPU Device Map

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# This example shows device mapping patterns
# (Requires model too large for one GPU to see real benefit)

model_id = "facebook/opt-1.3b"

# ── Auto distribution ─────────────────────────────────────────────
model_auto = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16,
)

if hasattr(model_auto, 'hf_device_map'):
    print("Device map (auto):")
    # Group by device
    device_groups = {}
    for layer, device in model_auto.hf_device_map.items():
        if device not in device_groups:
            device_groups[device] = []
        device_groups[device].append(layer)
    for device, layers in device_groups.items():
        print(f"  {device}: {len(layers)} modules")

# ── Limit GPU memory and spill to CPU ─────────────────────────────
if torch.cuda.is_available():
    max_memory = {
        0: "4GiB",    # Limit GPU 0 to 4 GB
        "cpu": "20GiB"  # Allow 20 GB CPU overflow
    }

    model_limited = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        max_memory=max_memory,
        torch_dtype=torch.float16,
    )

    print("\nDevice map with memory limits:")
    device_counts = {}
    for layer, device in model_limited.hf_device_map.items():
        device_counts[str(device)] = device_counts.get(str(device), 0) + 1
    for device, count in device_counts.items():
        print(f"  {device}: {count} modules")
```

---

## Example 5: Optimum ONNX Runtime (CPU Speedup)

```python
# pip install optimum[onnxruntime]

from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer, pipeline
import time

model_id = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_id)

# ── Regular PyTorch model ─────────────────────────────────────────
from transformers import AutoModelForSequenceClassification
pt_model = AutoModelForSequenceClassification.from_pretrained(model_id)
pt_model.eval()

texts = ["This is an amazing product!"] * 50

pt_pipe = pipeline("text-classification", model=pt_model, tokenizer=tokenizer)
start = time.perf_counter()
_ = pt_pipe(texts, batch_size=16)
pt_time = time.perf_counter() - start

# ── ONNX Runtime model ────────────────────────────────────────────
ort_model = ORTModelForSequenceClassification.from_pretrained(
    model_id,
    from_transformers=True,    # Auto-convert from PyTorch to ONNX
)

ort_pipe = pipeline("text-classification", model=ort_model, tokenizer=tokenizer)
start = time.perf_counter()
_ = ort_pipe(texts, batch_size=16)
ort_time = time.perf_counter() - start

print(f"PyTorch CPU:    {pt_time:.3f}s  ({50/pt_time:.0f} texts/sec)")
print(f"ONNX Runtime:   {ort_time:.3f}s  ({50/ort_time:.0f} texts/sec)")
print(f"Speedup: {pt_time/ort_time:.1f}×")

# Save ONNX model for later use (no re-conversion needed)
ort_model.save_pretrained("./distilbert-onnx")
tokenizer.save_pretrained("./distilbert-onnx")

# Load saved ONNX model
ort_model_loaded = ORTModelForSequenceClassification.from_pretrained("./distilbert-onnx")
```

---

## Example 6: torch.compile for Inference Speed

```python
import torch
import time
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_id = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForSequenceClassification.from_pretrained(
    model_id,
    torch_dtype=torch.float16
)
model.eval()

if torch.cuda.is_available():
    model = model.cuda()

inputs = tokenizer(
    ["This is a great product!"] * 32,
    return_tensors="pt",
    truncation=True,
    padding=True,
    max_length=128
)
if torch.cuda.is_available():
    inputs = {k: v.cuda() for k, v in inputs.items()}

# Baseline: regular PyTorch
with torch.no_grad():
    _ = model(**inputs)  # Warm-up

times_regular = []
for _ in range(20):
    start = time.perf_counter()
    with torch.no_grad():
        _ = model(**inputs)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    times_regular.append(time.perf_counter() - start)

# Compiled: torch.compile
compiled_model = torch.compile(model, mode="reduce-overhead")
with torch.no_grad():
    _ = compiled_model(**inputs)  # First call triggers compilation (slow)

times_compiled = []
for _ in range(20):
    start = time.perf_counter()
    with torch.no_grad():
        _ = compiled_model(**inputs)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    times_compiled.append(time.perf_counter() - start)

import statistics
print(f"Regular:  {statistics.mean(times_regular)*1000:.2f}ms avg")
print(f"Compiled: {statistics.mean(times_compiled)*1000:.2f}ms avg")
print(f"Speedup: {statistics.mean(times_regular)/statistics.mean(times_compiled):.2f}×")
# Typical result: 1.3-2.5× speedup for classification models on GPU
```

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full inference optimization explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| 📄 **Code_Example.md** | Working code (you are here) |
| [📄 Comparison.md](./Comparison.md) | FP32 vs INT8 vs INT4 vs GGUF |

⬅️ **Prev:** [Trainer API](../05_Trainer_API/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Spaces and Gradio](../07_Spaces_and_Gradio/Theory.md)
