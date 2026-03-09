# GPT — Cheatsheet

**One-liner:** GPT is a decoder-only transformer trained to predict the next token in a sequence, generating text autoregressively from left to right.

---

## Key Terms

| Term | Definition |
|---|---|
| Autoregressive | Generates output one token at a time, each step conditioned on all previous tokens |
| Causal attention | Masked self-attention — each token only sees past tokens, not future |
| Next-token prediction | The training objective: predict the next token given all previous tokens |
| Zero-shot | Performing a task from a description only, no examples |
| Few-shot | Performing a task from a few examples in the prompt |
| Temperature | Controls randomness in sampling (0 = greedy, >1 = more random) |
| Top-k sampling | Only sample from the k most probable next tokens |
| Top-p (nucleus) sampling | Only sample from tokens covering probability mass p |
| RLHF | Reinforcement Learning from Human Feedback — aligns model to follow instructions |

---

## GPT family comparison

| Model | Year | Parameters | Key milestone |
|---|---|---|---|
| GPT-1 | 2018 | 117M | Pretrain + fine-tune |
| GPT-2 | 2019 | 1.5B | Coherent long-form generation |
| GPT-3 | 2020 | 175B | In-context few-shot learning |
| InstructGPT | 2022 | 175B | RLHF alignment |
| GPT-4 | 2023 | ~1T est | Multimodal, advanced reasoning |

---

## Sampling strategies

| Strategy | How | When to use |
|---|---|---|
| Greedy (temp=0) | Always pick most probable token | Deterministic, factual tasks |
| Temperature sampling | Sample proportional to probs^(1/T) | Most generation tasks |
| Top-k | Sample only from top k tokens | Limits low-quality tokens |
| Top-p (nucleus) | Sample from tokens summing to p | More adaptive than top-k |
| Beam search | Keep top b sequences, pick best | Translation, summarization |

---

## GPT vs BERT quick reference

| | GPT | BERT |
|---|---|---|
| Architecture | Decoder-only | Encoder-only |
| Attention | Causal (left-to-right) | Bidirectional |
| Training | Next-token prediction | Masked LM |
| Primary use | Generation | Understanding/classification |
| Context | Only past tokens | Full sequence |

---

## Golden Rules

1. GPT generates text by predicting the next token — it has no separate understanding vs generation mode.
2. Prompt design matters enormously — the quality of GPT output depends on the quality of the prompt.
3. Temperature controls creativity vs coherence — tune it for your use case.
4. GPT-3 and above can do tasks zero-shot — describe the task clearly in the prompt.
5. RLHF (InstructGPT) is why modern GPT models follow instructions instead of just completing text.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [08 BERT](../08_BERT/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 Vision Transformers](../10_Vision_Transformers/Theory.md)