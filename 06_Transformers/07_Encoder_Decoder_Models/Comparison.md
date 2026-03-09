# Encoder-Decoder Models — Comparison

## Architecture Comparison Table

| | Encoder-only | Decoder-only | Encoder-Decoder |
|---|---|---|---|
| **Architecture** | Encoder stack only | Decoder stack only | Encoder + Decoder stacks |
| **Attention** | Bidirectional self-attention | Masked (causal) self-attention | Bidir. encoder + causal decoder + cross-attention |
| **Training objective** | Masked Language Modeling | Next-token prediction | Varies (text-to-text, denoising) |
| **Can generate text?** | No | Yes | Yes |
| **Sees full input?** | Yes (whole sequence) | Only past tokens | Encoder sees all; decoder generates causally |
| **Best tasks** | Classification, NER, search, QA extractive | Generation, chatbots, code, few-shot | Translation, summarization, generative QA |
| **Fine-tuning approach** | Add task-specific head | Prompt fine-tuning or last-token head | Task-specific fine-tuning |
| **Inference cost** | Fast (one forward pass) | Slow for long outputs (sequential generation) | Medium |
| **Typical size** | 66M–340M (BERT-base to BERT-large) | 117M–175B+ (GPT-2 to GPT-4) | 60M–11B (T5-small to T5-11B) |

---

## Training Objective Comparison

| Model family | Objective | What it learns |
|---|---|---|
| BERT (encoder-only) | MLM: predict 15% of masked tokens | Deep bidirectional context |
| RoBERTa | MLM (more data, no NSP) | Better bidirectional context |
| GPT (decoder-only) | Next-token prediction on all tokens | Autoregressive generation |
| T5 (enc-dec) | Text-to-text span corruption | Input understanding + generation |
| BART (enc-dec) | Denoising (reconstruct corrupted text) | Robust generation from noisy input |

---

## Popular Models by Family

### Encoder-only (BERT family)

| Model | Year | Parameters | Key innovation |
|---|---|---|---|
| BERT | 2018 | 110M / 340M | First bidirectional pretrained transformer |
| RoBERTa | 2019 | 125M / 355M | Better training recipe (more data, no NSP) |
| DistilBERT | 2019 | 66M | Knowledge distillation — 60% of BERT size, 97% performance |
| ALBERT | 2019 | 12M–235M | Parameter sharing and factorized embeddings |
| DeBERTa | 2020 | 140M–1.5B | Disentangled attention with position |

### Decoder-only (GPT family)

| Model | Year | Parameters | Key innovation |
|---|---|---|---|
| GPT-1 | 2018 | 117M | First GPT: pretraining + fine-tuning |
| GPT-2 | 2019 | 1.5B | Scale + zero-shot abilities |
| GPT-3 | 2020 | 175B | Few-shot in-context learning |
| LLaMA 2 | 2023 | 7B–70B | Open-source, efficient |
| Mistral 7B | 2023 | 7B | Sliding window attention, GQA |
| Claude | 2023+ | Unknown | Constitutional AI, RLHF |
| GPT-4 | 2023 | Unknown | Multimodal, state-of-the-art |

### Encoder-Decoder

| Model | Year | Parameters | Key innovation |
|---|---|---|---|
| T5 | 2019 | 60M–11B | Text-to-text unification |
| BART | 2019 | 140M–400M | Denoising pretraining |
| mT5 | 2020 | 300M–13B | Multilingual T5 |
| FLAN-T5 | 2022 | 80M–11B | Instruction fine-tuned T5 |

---

## When to choose which

| Situation | Recommendation |
|---|---|
| Deploying a text classifier at scale | Encoder-only (BERT) — fast inference |
| Building a chatbot or assistant | Decoder-only (GPT) — natural generation |
| Machine translation with labeled data | Encoder-decoder (BART or T5) |
| Semantic search / embedding retrieval | Encoder-only or fine-tuned SBERT |
| Few-shot learning without fine-tuning | Decoder-only (GPT-3+) |
| Low resource (CPU/edge) | DistilBERT (encoder) or small decoder |
| Multi-task learning across NLP tasks | T5 / FLAN-T5 — text-to-text handles all |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [06 Transformer Architecture](../06_Transformer_Architecture/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 BERT](../08_BERT/Theory.md)
