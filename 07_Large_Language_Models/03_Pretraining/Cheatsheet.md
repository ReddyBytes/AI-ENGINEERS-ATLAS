# Pretraining — Cheatsheet

**One-liner:** Pretraining is self-supervised training on trillions of tokens using next-token prediction — the model learns language, facts, and reasoning as side effects of this one objective.

---

## Key terms

| Term | What it means |
|------|---------------|
| Pretraining | Initial large-scale training on raw text data |
| Self-supervised learning | Labels are derived from the input data itself (no human annotation) |
| Next-token prediction | Predict the next token given all previous tokens |
| Cross-entropy loss | The training objective — minimized when predictions are accurate |
| Perplexity | How "surprised" the model is by test text; lower = better |
| Common Crawl | Massive web crawl dataset (~100B+ pages); backbone of most training sets |
| Tokens | Roughly 0.75 words; GPT-3 trained on 300B, Llama 3 on 15T |
| FLOPs | Floating point operations — unit of compute cost |
| Gradient clipping | Prevents unstable training by capping gradient magnitude |
| Checkpointing | Saving model state periodically during training |
| Data deduplication | Removing near-identical documents to prevent memorization |
| Tokenizer | Converts raw text to token IDs before training |
| Learning rate schedule | Controls step size during training (warmup → decay) |
| Distributed training | Running training across hundreds or thousands of GPUs in parallel |

---

## Common pretraining data sources

| Source | Tokens (approx) | Quality |
|--------|----------------|---------|
| Common Crawl (filtered) | Trillions | Medium (noisy, filtered) |
| Wikipedia | ~4B | High |
| Books (BookCorpus, Gutenberg) | ~26B | High |
| GitHub code | ~200B | High (for code) |
| ArXiv papers | ~30B | High (for STEM) |
| StackOverflow | ~20B | High (for code Q&A) |
| News (RealNews, CC-News) | ~60B | Medium-High |

---

## Compute cost reference

| Model | Parameters | Training tokens | Approx cost |
|-------|-----------|----------------|-------------|
| GPT-3 | 175B | 300B | ~$4.6M |
| PaLM | 540B | 780B | ~$8–10M |
| Llama 2 70B | 70B | 2T | ~$2–3M |
| GPT-4 (est.) | ~1T | ~13T | ~$50–100M |
| Llama 3 8B | 8B | 15T | ~$0.5–1M |

---

## Training pipeline overview

```
Raw text → Collect → Deduplicate → Filter → Tokenize
→ Distributed Training (hundreds of GPUs)
→ Loss decreases over trillions of steps
→ Checkpoint every N steps
→ Final pretrained base model
```

---

## What pretraining gives you vs doesn't

| Does give you | Does NOT give you |
|--------------|-------------------|
| Language understanding | Instruction following |
| Factual knowledge | Helpfulness |
| Reasoning patterns | Safety or refusals |
| Code and math skills | Conversational style |
| Multiple languages | Alignment to human values |

---

## Data quality rules

1. Deduplicate — duplicates cause memorization, not generalization
2. Filter quality — spam, gibberish, and low-quality HTML harm the model
3. Balance sources — don't let raw crawl drown out books and Wikipedia
4. Diversity matters — models trained on narrow data fail on broad tasks
5. More tokens beats bigger model — Chinchilla laws: train smaller models longer

---

## Golden rules

1. Pretraining is the most expensive step. It happens once, then you fine-tune.
2. Self-supervised = no human labels needed. The text supervises itself.
3. The model doesn't "learn facts" explicitly — it learns to predict text accurately, and facts emerge from that
4. Data quality beats data quantity. A 1T token clean corpus beats 10T tokens of garbage
5. Base models are not safe or helpful. Never deploy a raw pretrained model to users
6. Token efficiency matters — the Chinchilla finding: 70B model + 1.4T tokens beats 280B model + 300B tokens

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Pretraining architecture deep dive |

⬅️ **Prev:** [02 How LLMs Generate Text](../02_How_LLMs_Generate_Text/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Fine Tuning](../04_Fine_Tuning/Theory.md)
