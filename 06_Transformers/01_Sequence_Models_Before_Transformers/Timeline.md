# NLP Models Timeline

A chronological story of how natural language processing evolved from counting words to predicting the next token of a conversation.

---

## The Timeline

### 1990s — N-gram Language Models

**Key innovation:** Count how often sequences of N words appear. Predict the next word based on the previous N-1 words.

```
"The cat sat on the ___"
P(mat | the) is high. P(astronaut | the) is low.
```

**Why it worked:** Simple, fast, and surprisingly effective for short-range prediction.

**Limitation that led to the next:** N-grams can't capture dependencies beyond N words back. N=5 was practically the limit. No understanding of syntax or meaning.

---

### 1990s–2000s — Hidden Markov Models for NLP

**Key innovation:** Model sequences of words as observable outputs from hidden states (like POS tags). Combine transition probabilities (grammar) with emission probabilities (words).

**Why it worked:** Principled probabilistic framework. Good for speech recognition and POS tagging.

**Limitation that led to the next:** Strong independence assumptions. Can't use rich features. Limited context window.

---

### 2003 — Neural Language Models (Bengio et al.)

**Key innovation:** Use a small neural network to predict the next word. Words are represented as dense embeddings — their first appearance.

**Why it worked:** Words with similar meanings got similar representations naturally.

**Limitation that led to the next:** Still limited context. Slow to train. Not yet scalable.

---

### 2010–2013 — Recurrent Neural Networks (RNNs)

**Key innovation:** Process sequences word by word with a hidden state that carries memory. Can theoretically handle sequences of any length.

**Why it worked:** Natural fit for sequential text. Much more flexible than n-grams.

**Limitation that led to the next:** Vanishing gradients mean the model forgets early context. Sequential processing is slow — no GPU parallelism.

---

### 2013 — Word2Vec (Mikolov et al., Google)

**Key innovation:** Train shallow neural networks to predict context words (CBOW, Skip-gram). The learned vectors capture semantic relationships: king − man + woman ≈ queen.

**Why it worked:** Cheap to train, rich representations, useful across many tasks.

**Limitation that led to the next:** Static embeddings — one vector per word regardless of context. "Bank" (finance) and "bank" (river) get the same vector.

---

### 2014–2015 — LSTMs and GRUs for Seq2Seq

**Key innovation:** Long Short-Term Memory units with forget/input/output gates can preserve information across hundreds of steps. Seq2seq with encoder-decoder architecture for translation.

**Why it worked:** LSTMs dramatically improved over plain RNNs for long sequences.

**Limitation that led to the next:** The fixed-size context vector is a bottleneck. Decoder can't access specific encoder states. Still sequential — slow to train on long sequences.

---

### 2015 — Attention Mechanism (Bahdanau et al.)

**Key innovation:** Give the decoder a learned weighted access to all encoder states. Instead of one context vector, the decoder computes a soft "where to look" at each step.

**Why it worked:** Long-range dependencies solved. Translation quality improved dramatically. The model can directly link a translated word to its source word.

**Limitation that led to the next:** Still built on top of RNNs — sequential bottleneck remains. Attention was an add-on, not the core architecture.

---

### 2016 — ELMo (Peters et al.)

**Key innovation:** Train a deep BiLSTM on language modeling. Use the intermediate layer representations as contextual word embeddings. "Bank" gets different vectors in different contexts.

**Why it worked:** Context-dependent embeddings dramatically improved downstream task performance. Transfer learning for NLP starts here.

**Limitation that led to the next:** Still LSTM-based — slow, sequential, limited parallelism.

---

### 2017 — The Transformer ("Attention is All You Need", Vaswani et al., Google)

**Key innovation:** Replace RNNs entirely with multi-head self-attention. Process all positions in parallel. Every word attends to every other word in one step. Add positional encoding for order.

**Why it worked:** Massive parallelism → faster training. No recurrence → no vanishing gradient through time. Every position directly attends to every other → perfect long-range dependencies.

**Limitation that led to the next:** Pretraining wasn't the default yet. Quadratic attention complexity limits very long sequences.

---

### 2018 — BERT (Devlin et al., Google)

**Key innovation:** Pretrain a bidirectional transformer encoder on masked language modeling (predict masked words) and next sentence prediction. Fine-tune for downstream tasks.

**Why it worked:** Bidirectional context for every word. Massive pretraining on 3B+ words. One model, dozens of tasks. New SOTA on almost every NLP benchmark.

**Limitation that led to the next:** Encoder-only — can't generate text naturally. NSP task proved less useful than expected.

---

### 2018–2020 — GPT Family (Radford et al., OpenAI)

**Key innovation:** Pretrain a decoder-only transformer on next-token prediction. Scale up: GPT-1 (117M) → GPT-2 (1.5B) → GPT-3 (175B). Few-shot learning emerges.

**Why it worked:** Autoregressive generation is natural for language. Scale improved quality dramatically. GPT-3 could follow instructions with just a few examples in the prompt.

**Limitation that led to the next:** Not instruction-following without fine-tuning. Safety and alignment challenges as scale increases.

---

### 2019–2020 — T5, RoBERTa, BART

**Key innovation:** T5 frames all NLP tasks as text-to-text. RoBERTa improves BERT training. BART combines bidirectional encoder with autoregressive decoder.

**Why they worked:** Better training recipes, more data, encoder-decoder flexibility.

---

### 2022–present — GPT-4, Claude, Gemini, and Beyond

**Key innovation:** RLHF (Reinforcement Learning from Human Feedback) aligns models with human intent. Instruction fine-tuning. Multimodal inputs (text + images). Very long context windows (100k+ tokens).

**Why it worked:** Models that follow instructions reliably are far more useful than raw capability. Scale + alignment = product.

---

## One-line summary

```
N-grams (count)
  → HMM (probabilistic sequences)
  → Neural LM (dense representations)
  → RNN (sequential memory)
  → Word2Vec (semantic embeddings)
  → LSTM (long-range memory)
  → Attention (direct context access)
  → Transformer (parallel attention, no recurrence)
  → BERT (bidirectional pretraining)
  → GPT (autoregressive scaling)
  → Modern LLMs (instruction following + alignment)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Timeline.md** | ← you are here |

⬅️ **Prev:** [07 Conditional Random Fields](../../05_NLP_Foundations/07_Conditional_Random_Fields/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Attention Mechanism](../02_Attention_Mechanism/Theory.md)
