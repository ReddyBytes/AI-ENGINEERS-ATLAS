# Hugging Face Hub and Model Cards — Cheatsheet

## Key Terms

| Term | One-line meaning |
|------|-----------------|
| **Hub** | huggingface.co — the central registry for models, datasets, and Spaces |
| **Model card** | README.md for a model — documents purpose, training data, metrics, and limits |
| **from_pretrained** | Downloads model + tokenizer from Hub and caches locally |
| **push_to_hub** | Uploads your model/tokenizer to your Hub repository |
| **Revision** | A specific git commit, tag, or branch to pin a model version |
| **Safetensors** | Safe, fast binary weight format (preferred over .bin/pickle) |
| **Git LFS** | Large File Storage — how the Hub stores large weight files in Git |
| **Frontmatter** | YAML block at top of README.md that Hub reads for search/filter metadata |
| **Private repo** | Hub repo that requires authentication — for internal/proprietary models |
| **Space** | A Hub-hosted live demo (Gradio or Streamlit) |

---

## Core Commands

```python
# ── LOADING ──────────────────────────────────────────────────────
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Pin to a specific version (use in production)
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    revision="a265f773a47193eed794233aa2a0f0bb6d3eaa63"
)

# Custom cache location
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    cache_dir="/data/hf_cache"
)

# ── AUTHENTICATION ────────────────────────────────────────────────
from huggingface_hub import login
login(token="hf_your_token_here")   # or just login() to prompt

# ── PUSHING ──────────────────────────────────────────────────────
model.push_to_hub("your-username/my-model")
tokenizer.push_to_hub("your-username/my-model")

# ── HUB API ──────────────────────────────────────────────────────
from huggingface_hub import HfApi
api = HfApi()

api.create_repo("your-username/my-model")             # Create repo
api.upload_file(path_or_fileobj="file.txt",
                path_in_repo="file.txt",
                repo_id="your-username/my-model")     # Upload a file
api.list_models(filter="text-classification")         # Search models
api.model_info("bert-base-uncased")                   # Get model metadata
```

---

## Model Card Required Fields

```yaml
---
# Minimum viable model card frontmatter
language: en                    # ISO 639-1 language code(s)
license: apache-2.0             # SPDX license identifier
tags:
  - text-classification         # Task tag
  - sentiment-analysis          # Additional descriptive tags
datasets:
  - sst2                        # Hugging Face dataset ID(s)
metrics:
  - accuracy                    # Metric name(s)
model-index:                    # Optional: structured benchmark results
  - name: My Model
    results:
      - task:
          type: text-classification
        dataset:
          name: SST-2
          type: sst2
        metrics:
          - type: accuracy
            value: 0.934
---
```

---

## When to Use vs When NOT to Use

| ✅ Use the Hub when | ❌ Avoid / be careful when |
|---------------------|--------------------------|
| You want a pre-trained model for a common NLP task | The license is "non-commercial" and your use is commercial |
| You want to share a model with the community | The model card has no training data documentation |
| You need versioned, reproducible model artifacts | You need sub-millisecond latency (Hub adds download overhead once) |
| You want private model storage for your team | You have sensitive model weights that should never leave your infra |
| You want others to find and cite your model | — |

---

## Quick Decision Guide

```
Need a pre-trained model?
├── Common task (sentiment, NER, translation)?
│   └── → Search Hub by task filter → pick most downloaded with matching license
├── Domain-specific (medical, legal, code)?
│   └── → Search Hub with domain tag → read card carefully for training data
└── Need to publish your own?
    ├── Public → push_to_hub, write a thorough model card
    └── Private / team use → create private repo, use org access tokens
```

---

## Golden Rules

1. **Always read the license** before using a model in any product — "non-commercial" means no revenue-generating use.
2. **Pin `revision=` in production** — `main` branch can change; use a commit hash for stability.
3. **Prefer safetensors** — it's faster to load and cannot contain executable malicious code.
4. **Write a model card before pushing** — even a minimal one. Future-you will thank present-you.
5. **Set a custom `cache_dir`** on servers — the default home directory fills up fast with large models.
6. **Use org repos for team projects** — individual repos are tied to a person; org repos survive team changes.

---

## 📂 Navigation

**In this folder:**

| File | Description |
|------|-------------|
| [📄 Theory.md](./Theory.md) | Full Hub explanation with diagrams |
| 📄 **Cheatsheet.md** | Quick reference (you are here) |
| [📄 Interview_QA.md](./Interview_QA.md) | 9 interview questions |
| [📄 Code_Example.md](./Code_Example.md) | Working code examples |

⬅️ **Prev:** [Section README](../Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Transformers Library](../02_Transformers_Library/Theory.md)
