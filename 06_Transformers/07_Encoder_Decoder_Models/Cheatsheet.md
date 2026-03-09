# Encoder-Decoder Models — Cheatsheet

**One-liner:** Transformers come in three variants — encoder-only (understand text), decoder-only (generate text), encoder-decoder (understand input, generate output) — and the choice depends on your task.

---

## Key Terms

| Term | Definition |
|---|---|
| Encoder-only | Transformer with only the encoder stack; bidirectional attention |
| Decoder-only | Transformer with only the decoder stack; causal (masked) attention |
| Encoder-decoder | Full transformer with both stacks; cross-attention bridges them |
| Bidirectional | Each token can attend to tokens before AND after it |
| Causal / autoregressive | Each token can only attend to tokens before it |
| MLM | Masked Language Modeling — BERT's training objective |
| CLM | Causal Language Modeling — GPT's training objective |
| Text-to-text | T5's approach: frame every NLP task as text in → text out |

---

## Architecture comparison

| Architecture | Attention type | Training objective | Best for |
|---|---|---|---|
| Encoder-only (BERT) | Bidirectional | Masked LM | Classification, NER, search |
| Decoder-only (GPT) | Causal (left-to-right) | Next-token prediction | Generation, chatbots, code |
| Encoder-decoder (T5) | Bidir. encoder + causal decoder | Text-to-text | Translation, summarization |

---

## Task → Architecture mapping

| Task | Architecture | Why |
|---|---|---|
| Sentiment classification | Encoder-only | Needs to understand text, not generate |
| Machine translation | Encoder-decoder | Understand source, generate target |
| Named entity recognition | Encoder-only | Label each token, not generate |
| Open-ended text generation | Decoder-only | Pure generation |
| Document summarization | Encoder-decoder OR decoder-only | Depends on approach |
| Search / retrieval | Encoder-only | Need sentence embeddings |
| Question answering (extractive) | Encoder-only | Find answer span in text |
| Question answering (generative) | Decoder-only or encoder-decoder | Generate answer text |

---

## Examples by family

| Family | Examples | Parameters |
|---|---|---|
| Encoder-only | BERT, RoBERTa, DistilBERT, ALBERT | 66M–340M |
| Decoder-only | GPT-2, GPT-3, LLaMA, Mistral, Claude | 117M–175B+ |
| Encoder-decoder | T5, BART, mT5, FLAN-T5 | 60M–11B |

---

## Golden Rules

1. For classification, NER, and search: use encoder-only (BERT-family).
2. For generation, chatbots, instruction following: use decoder-only (GPT-family).
3. For translation, summarization, QA (generative): encoder-decoder is the "correct" architecture — but large decoder-only models can do it too.
4. Modern practice: large decoder-only models (GPT-4, Claude) have largely replaced specialized architectures.
5. If you fine-tune for a specific task, always pick the architecture that matches the task type.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Comparison.md](./Comparison.md) | Encoder vs decoder vs encoder-decoder comparison |

⬅️ **Prev:** [06 Transformer Architecture](../06_Transformer_Architecture/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 BERT](../08_BERT/Theory.md)
