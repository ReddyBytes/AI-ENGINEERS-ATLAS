# Transformers Library — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **pipeline** | One-liner that handles tokenization + inference + post-processing |
| **AutoTokenizer** | Loads the right tokenizer for any Hub model automatically |
| **AutoModel** | Loads the right model class for any Hub model automatically |
| **from_pretrained** | Downloads model/tokenizer from Hub (or loads from cache) |
| **return_tensors** | Parameter telling tokenizer what format to return (`"pt"`, `"tf"`, `"np"`) |
| **attention_mask** | Tells model which tokens are real vs padding (1=real, 0=pad) |
| **logits** | Raw unnormalized scores from model output, before softmax |
| **hidden_states** | Intermediate vector representations at each transformer layer |
| **device_map** | Argument to spread model across CPU/GPU automatically |
| **torch.no_grad()** | Context manager that disables gradient computation during inference |

---

## Pipeline Task Reference

```python
from transformers import pipeline

# Text tasks
classifier    = pipeline("text-classification")           # or "sentiment-analysis"
ner           = pipeline("token-classification", aggregation_strategy="simple")
qa            = pipeline("question-answering")
summarizer    = pipeline("summarization")
translator    = pipeline("translation_en_to_fr")
generator     = pipeline("text-generation")
fill          = pipeline("fill-mask")
zero_shot     = pipeline("zero-shot-classification")

# Audio / Vision
asr           = pipeline("automatic-speech-recognition")  # speech-to-text
image_cls     = pipeline("image-classification")
img_to_text   = pipeline("image-to-text")
depth         = pipeline("depth-estimation")

# Always specify model= in production:
prod_clf = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
```

---

## AutoModel Classes Quick Reference

| Task | AutoClass to use |
|------|-----------------|
| Get raw embeddings | `AutoModel` |
| Text / sequence classification | `AutoModelForSequenceClassification` |
| Token labeling (NER, POS) | `AutoModelForTokenClassification` |
| Extractive question answering | `AutoModelForQuestionAnswering` |
| Summarization / translation | `AutoModelForSeq2SeqLM` |
| Text generation (GPT-style) | `AutoModelForCausalLM` |
| Fill mask (BERT-style) | `AutoModelForMaskedLM` |
| Multiple choice | `AutoModelForMultipleChoice` |
| Speech to text | `AutoModelForSpeechSeq2Seq` |
| Image classification | `AutoModelForImageClassification` |
| Image + text generation | `AutoModelForVision2Seq` |

---

## Inference Code Pattern

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 1. Load tokenizer and model (always from same checkpoint)
model_id = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id)

# 2. Set to eval mode (disables dropout)
model.eval()

# 3. Tokenize
inputs = tokenizer(
    "I absolutely loved this film!",
    return_tensors="pt",     # PyTorch tensors
    truncation=True,         # Truncate if over max_length
    padding=True,            # Pad to uniform length in batch
    max_length=512           # Model's maximum context length
)

# 4. Run inference — no gradients needed
with torch.no_grad():
    outputs = model(**inputs)

# 5. Decode output
logits = outputs.logits
predicted_class_id = logits.argmax(-1).item()
label = model.config.id2label[predicted_class_id]
confidence = torch.softmax(logits, dim=-1).max().item()

print(f"{label}: {confidence:.2%}")
```

---

## Pipeline vs AutoClass — When to Use Each

| ✅ Use `pipeline()` when | ✅ Use `AutoModel` directly when |
|--------------------------|----------------------------------|
| Prototyping quickly | You need access to hidden states |
| Standard tasks with default settings | You need custom pre/post processing |
| Teaching or demos | You're building a training loop |
| You don't need to customize | You need batching control |
| Production with default post-processing | You're integrating into a larger system |

---

## Common `from_pretrained` Parameters

```python
AutoModel.from_pretrained(
    "model-id",
    revision="main",           # Git revision — use commit hash in production
    cache_dir="/path/cache",   # Where to store downloads
    device_map="auto",         # Auto-place layers on available GPU/CPU
    torch_dtype=torch.float16, # Use half precision to save memory
    load_in_8bit=True,         # INT8 quantization (requires bitsandbytes)
    load_in_4bit=True,         # INT4 quantization (requires bitsandbytes)
    trust_remote_code=True,    # Allow custom model code (use with caution!)
    ignore_mismatched_sizes=True # Skip weight mismatch errors (fine-tuning)
)
```

---

## Golden Rules

1. **Always load tokenizer and model from the same checkpoint** — mismatches cause silent errors.
2. **Use `model.eval()` and `torch.no_grad()` for inference** — saves memory and prevents accidental training.
3. **Specify `model=` in pipeline for production** — don't rely on default models that can change.
4. **Use `AutoModelForXxx` not `AutoModel`** when you want task-specific output (logits, not hidden states).
5. **`return_tensors="pt"`** is required if you want PyTorch tensors from the tokenizer.
6. **Batch your inputs** — processing one text at a time is 10-100x slower than batching.

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full library explanation with diagrams |
| 📄 **Cheatsheet.md** | Quick reference (you are here) |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | Working pipeline code for 6 tasks |
| [📄 Pipeline_Guide.md](./Pipeline_Guide.md) | Complete guide to all pipeline types |

⬅️ **Prev:** [Hub and Model Cards](../01_Hub_and_Model_Cards/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Datasets Library](../03_Datasets_Library/Theory.md)
