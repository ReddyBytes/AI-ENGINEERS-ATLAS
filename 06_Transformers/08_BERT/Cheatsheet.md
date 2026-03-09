# BERT — Cheatsheet

**One-liner:** BERT is a bidirectional encoder-only transformer pretrained on masked language modeling, producing rich contextual token representations that can be fine-tuned for virtually any NLP task.

---

## Key Terms

| Term | Definition |
|---|---|
| MLM | Masked Language Modeling — predict randomly masked tokens from full context |
| NSP | Next Sentence Prediction — predict if sentence B follows sentence A |
| [CLS] | Special start token; its final hidden state is used for classification |
| [SEP] | Separator token between two sequences |
| [MASK] | Token placeholder during MLM pretraining |
| Bidirectional | Every token attends to every other token (left and right context) |
| Fine-tuning | Additional training of BERT on a specific task with a small labeled dataset |
| WordPiece | BERT's subword tokenizer |

---

## BERT input format

```
Single sentence:
[CLS] Token1 Token2 ... [SEP]

Sentence pair:
[CLS] SentA1 SentA2 ... [SEP] SentB1 SentB2 ... [SEP]
```

Input embeddings = token embedding + segment embedding + positional embedding

---

## BERT sizes

| Model | Layers | d_model | Heads | Parameters |
|---|---|---|---|---|
| BERT-base | 12 | 768 | 12 | 110M |
| BERT-large | 24 | 1024 | 16 | 340M |
| DistilBERT | 6 | 768 | 12 | 66M |

---

## Fine-tuning approaches

| Task | Output used | Head added |
|---|---|---|
| Classification | [CLS] hidden state | Linear → num_classes |
| NER / POS | Each token's hidden state | Linear per token → num_labels |
| Extractive QA | Each token's hidden state | Linear → start/end logits |
| Sentence similarity | [CLS] hidden state | Linear → similarity score |

---

## When to use BERT (not GPT)

| Use BERT | Use GPT |
|---|---|
| Classification task | Generation task |
| Need sentence embeddings | Need to generate text |
| Token labeling (NER, POS) | Chatbots, assistants |
| Extractive QA | Open-ended QA |
| Low latency production | Long-form generation |

---

## Notable BERT variants

| Model | Key difference |
|---|---|
| RoBERTa | More data, no NSP, longer training |
| ALBERT | Parameter sharing, reduces size 18× |
| DistilBERT | Distilled from BERT-base, 60% size, 97% quality |
| DeBERTa | Disentangled attention + enhanced mask decoder |
| mBERT | Multilingual BERT (104 languages) |

---

## Golden Rules

1. For classification, NER, and search — fine-tune BERT on your labeled data.
2. [CLS] token's final hidden state = sentence-level representation for classification.
3. Use DistilBERT when inference speed matters and you can accept a small accuracy trade-off.
4. BERT's WordPiece tokenizer is specific to BERT — always use the matching tokenizer.
5. Fine-tune all layers (not just the head) — BERT's representations adapt to your domain.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [07 Encoder-Decoder Models](../07_Encoder_Decoder_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 GPT](../09_GPT/Theory.md)
