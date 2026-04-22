# Pretraining — Cheatsheet

**One-liner:** Pretraining is training a transformer on trillions of tokens using next-token prediction — the self-supervised objective that gives LLMs their broad knowledge, language ability, and emergent reasoning.

---

## Key terms

| Term | What it means |
|------|---------------|
| Pretraining | Training a model from scratch on massive text corpora |
| Next-token prediction | The training objective: predict what token comes next |
| Self-supervised learning | Learning from unlabeled data by creating artificial labels (next token) |
| Cross-entropy loss | The loss function: how surprised was the model by the actual next token? |
| Teacher forcing | During training, always feed the true previous tokens (not model's predictions) |
| Data curation | Filtering, deduplication, and quality scoring of the training corpus |
| BPE | Byte Pair Encoding — how the corpus is tokenized before training |
| Compute-optimal | Training for the optimal parameter:token ratio given a compute budget |
| Chinchilla scaling | Law showing optimal tokens ≈ 20 × model parameters |
| Emergent capability | Ability that appears suddenly at a certain scale, not predicted by smaller models |
| Scaling law | Mathematical relationship between model size, data, compute, and performance |
| Fine-tuning | Subsequent training phases (SFT, RLHF) layered on top of the pretrained model |
| Knowledge cutoff | Date after which the model has no training data |

---

## Training objective

```
Minimize: L = -1/N × Σ log P(token_t | token_1, ..., token_{t-1})

Where:
- N = total tokens in training dataset
- P(token_t | ...) = model's predicted probability for the correct next token
- Lower loss = model was less surprised = better predictions
```

---

## Chinchilla scaling law

```
Optimal compute allocation:
  N_optimal_parameters ≈ C^0.5
  D_optimal_tokens     ≈ C^0.5 / 20

  → N_tokens = 20 × N_parameters

Examples:
  7B params  → train on ~140B tokens (minimum; 1T+ is better for practical use)
  70B params → train on ~1.4T tokens  
  500B params → train on ~10T tokens
```

GPT-3 (175B params, 300B tokens) was severely undertrained by this metric. Modern models train 5–20× more data per parameter.

---

## Data sources (typical frontier LLM)

| Source | Why included |
|--------|-------------|
| Web crawl (filtered) | Scale — trillions of pages |
| Books | High-quality prose and reasoning |
| Academic papers | Scientific and math knowledge |
| Code (GitHub) | Programming patterns and logic |
| Wikipedia | Factual encyclopedic knowledge |
| High-quality curated | Improves overall quality disproportionately |

Data quality >> data quantity. Deduplicated, filtered data outperforms raw crawl at equal size.

---

## Emergent capabilities

Capabilities that appear suddenly at certain scales:

| Capability | Approximate scale where it emerged |
|------------|-----------------------------------|
| In-context learning | ~1B parameters |
| Multi-step arithmetic | ~10B parameters |
| Chain-of-thought reasoning | ~60B+ parameters (activated by prompting) |
| Code generation | ~10B+ with code data |
| Analogical reasoning | ~100B+ parameters |

These are observed in GPT-3/4 lineage; exact thresholds vary by architecture and training data quality.

---

## Pretraining vs fine-tuning

| Phase | Purpose | Cost | Changes what |
|-------|---------|------|-------------|
| Pretraining | Acquire broad knowledge | $$$$ | All parameters, from scratch |
| SFT | Learn to follow instructions | $$ | All or partial parameters |
| RLHF | Align with human preferences | $$ | All or partial parameters |
| Constitutional AI | Improve safety | $ | Targeted |
| LoRA fine-tuning | Task-specific adaptation | $ | Low-rank adapters only |

---

## Golden rules

1. Pretraining gives capability; fine-tuning gives alignment — you need both
2. Data quality matters more than raw quantity — 100B high-quality tokens > 1T noisy tokens
3. You can't fix missing knowledge via fine-tuning — if a fact wasn't in pretraining data, it's not in the model
4. Emergent capabilities are unpredictable — new abilities appear non-linearly with scale
5. Compute-optimal means more data, smaller model — not just bigger model
6. Knowledge cutoff is a pretraining artifact — RAG is the fix for freshness

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [04 Transformer Architecture](../04_Transformer_Architecture/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 RLHF](../06_RLHF/Theory.md)
