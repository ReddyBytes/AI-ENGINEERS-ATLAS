# Hugging Face Hub and Model Cards — Code Examples

## Setup

```python
# Install required libraries
# pip install transformers huggingface_hub datasets

from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification
from huggingface_hub import HfApi, login
import torch
```

---

## Example 1: Loading a Model and Tokenizer from the Hub

```python
# The simplest case — load a well-known model
# from_pretrained downloads on first call, uses cache on subsequent calls

from transformers import AutoTokenizer, AutoModel

model_name = "bert-base-uncased"

# Download tokenizer (vocab + rules for splitting text into tokens)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Download model weights (~440MB for BERT base)
model = AutoModel.from_pretrained(model_name)

print(f"Model type: {type(model).__name__}")
print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")

# Quick test — tokenize a sentence
tokens = tokenizer("Hello, Hugging Face!", return_tensors="pt")
print(f"\nInput IDs: {tokens['input_ids']}")
print(f"Tokens: {tokenizer.convert_ids_to_tokens(tokens['input_ids'][0])}")

# Run a forward pass
with torch.no_grad():
    output = model(**tokens)

print(f"\nOutput shape: {output.last_hidden_state.shape}")
# → torch.Size([1, 7, 768])  = [batch, sequence_len, hidden_dim]
```

---

## Example 2: Pinning to a Specific Version (Production Pattern)

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# NEVER do this in production — main can change anytime
# model = AutoModel.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

# DO this instead — pin to a specific commit hash
PINNED_REVISION = "af0f99b"  # short hash works too

model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english",
    revision=PINNED_REVISION
)
tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english",
    revision=PINNED_REVISION
)

# Run inference
text = "The Hugging Face Hub makes AI incredibly accessible!"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits

predicted_class = logits.argmax(-1).item()
label = model.config.id2label[predicted_class]
confidence = torch.softmax(logits, dim=-1).max().item()

print(f"Text: {text}")
print(f"Sentiment: {label} (confidence: {confidence:.2%})")
```

---

## Example 3: Authenticating and Loading a Private Model

```python
import os
from huggingface_hub import login
from transformers import AutoModel, AutoTokenizer

# Option A: Login interactively (prompts for token)
login()

# Option B: Login with token directly (for scripts/CI)
login(token="hf_your_token_here")

# Option C: Use environment variable (most secure for production)
# export HUGGING_FACE_HUB_TOKEN=hf_your_token_here
# Then from_pretrained automatically reads it — no login() call needed

# Now load a private model exactly like a public one
private_model_id = "your-org/your-private-model"
tokenizer = AutoTokenizer.from_pretrained(private_model_id)
model = AutoModel.from_pretrained(private_model_id)

print("Private model loaded successfully!")
```

---

## Example 4: Pushing a Fine-Tuned Model to the Hub

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from huggingface_hub import login

# Authenticate first
login(token="hf_your_token_here")

# --- Assume you have a fine-tuned model ---
# (In practice you would train it, here we just load one for demo)
model_name = "distilbert-base-uncased"
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Give your model a name — format: "your-username/your-model-name"
hub_model_id = "your-username/my-sentiment-classifier"

# Push the model weights
model.push_to_hub(hub_model_id)

# Push the tokenizer (must be done separately)
tokenizer.push_to_hub(hub_model_id)

print(f"Model pushed to: https://huggingface.co/{hub_model_id}")
```

---

## Example 5: Creating a Model Card Programmatically

```python
from huggingface_hub import ModelCard, ModelCardData

# Build the model card metadata (frontmatter)
card_data = ModelCardData(
    language="en",
    license="apache-2.0",
    tags=["text-classification", "sentiment-analysis", "distilbert"],
    datasets=["sst2"],
    metrics=["accuracy", "f1"],
    model_name="My Sentiment Classifier",
    base_model="distilbert-base-uncased",
)

# Write the model card content (Markdown)
card_content = """
# My Sentiment Classifier

A DistilBERT model fine-tuned for binary sentiment classification (positive/negative).

## Model Details

- **Base model:** distilbert-base-uncased
- **Fine-tuned on:** SST-2 (Stanford Sentiment Treebank)
- **Task:** Binary text classification (POSITIVE / NEGATIVE)
- **Language:** English

## Performance

| Dataset | Accuracy | F1 Score |
|---------|----------|----------|
| SST-2 test | 91.3% | 91.1% |

## Usage

```python
from transformers import pipeline
classifier = pipeline("sentiment-analysis", model="your-username/my-sentiment-classifier")
result = classifier("This product is absolutely fantastic!")
print(result)  # [{'label': 'POSITIVE', 'score': 0.9987}]
```

## Limitations

- English only. Performance degrades significantly on other languages.
- Trained on movie/product review text; may not generalize to formal or technical text.
- Does not handle sarcasm reliably.

## Training Details

- **Epochs:** 3
- **Batch size:** 32
- **Learning rate:** 2e-5
- **Optimizer:** AdamW with linear warmup
"""

# Create and push the card
card = ModelCard(card_content, card_data=card_data)
card.push_to_hub("your-username/my-sentiment-classifier")

print("Model card pushed successfully!")
```

---

## Example 6: Using the Hub API for Discovery and Management

```python
from huggingface_hub import HfApi

api = HfApi()

# ── Search for models ────────────────────────────────────────────
# Find the most-downloaded English text classification models
models = api.list_models(
    task="text-classification",
    language="en",
    sort="downloads",
    direction=-1,  # descending
    limit=5
)

print("Top 5 text-classification models:")
for m in models:
    print(f"  {m.id} — {m.downloads:,} downloads")

# ── Get detailed info about a specific model ─────────────────────
info = api.model_info("bert-base-uncased")
print(f"\nBERT tags: {info.tags}")
print(f"BERT created: {info.created_at}")
print(f"BERT last modified: {info.last_modified}")

# ── List files in a repository ───────────────────────────────────
files = api.list_repo_files("bert-base-uncased")
print(f"\nBERT repo files: {list(files)}")

# ── Create a new empty repository ────────────────────────────────
# api.create_repo(
#     repo_id="your-username/new-model",
#     private=True,    # Set True for private
#     exist_ok=True    # Don't error if repo already exists
# )

# ── Delete a repository ──────────────────────────────────────────
# api.delete_repo("your-username/old-model")
```

---

## Example 7: Loading with Custom Cache Directory

```python
import os
from transformers import AutoModel, AutoTokenizer

# Useful on servers where home directory has limited space
# Point to a large attached volume

cache_path = "/mnt/large-disk/hf_cache"
os.makedirs(cache_path, exist_ok=True)

tokenizer = AutoTokenizer.from_pretrained(
    "bert-base-uncased",
    cache_dir=cache_path
)

model = AutoModel.from_pretrained(
    "bert-base-uncased",
    cache_dir=cache_path
)

# OR set globally via environment variable (affects all calls in the process)
os.environ["TRANSFORMERS_CACHE"] = cache_path
os.environ["HF_DATASETS_CACHE"] = cache_path

print(f"Models cached at: {cache_path}")
```

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full Hub explanation with diagrams |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference commands |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| 📄 **Code_Example.md** | Working code examples (you are here) |

⬅️ **Prev:** [Section README](../Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Transformers Library](../02_Transformers_Library/Theory.md)
