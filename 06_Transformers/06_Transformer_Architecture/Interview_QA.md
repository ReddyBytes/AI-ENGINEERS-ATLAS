# Transformer Architecture — Interview Q&A

## Beginner

**Q1. What are the two main parts of the transformer architecture?**

<details>
<summary>💡 Show Answer</summary>

The transformer has an encoder and a decoder.

The encoder reads the full input sequence (e.g., the source sentence in translation) and produces a set of rich contextual representations — one for each input token. Every token can attend to every other token bidirectionally.

The decoder generates the output sequence one token at a time. It uses masked self-attention on its own generated output (so it can't cheat by looking ahead), then cross-attention to look at the encoder's representations of the source. It generates the next token based on both what it has generated and what it read.

</details>

---

**Q2. What is a residual connection and why is it used?**

<details>
<summary>💡 Show Answer</summary>

A residual (skip) connection adds the input of a sub-layer directly to its output:

```
output = LayerNorm(x + SubLayer(x))
```

Without it, in a deep network (e.g., 12 or 96 layers), gradients can vanish as they propagate backwards — later layers update well but early layers barely learn.

The residual connection creates a direct path for gradients to flow backward, bypassing the sub-layer. This enables training very deep networks. It also means each sub-layer only needs to learn the "correction" to add on top of the identity — a much easier optimization problem.

</details>

---

**Q3. What is the feed-forward network (FFN) in a transformer layer and what does it do?**

<details>
<summary>💡 Show Answer</summary>

After multi-head attention, each transformer layer has a feed-forward network applied independently to each position:

```
FFN(x) = max(0, x × W1 + b1) × W2 + b2
```

Two linear transformations with a ReLU in between. The inner dimension is 4× d_model (e.g., 2048 for a 512-dim model).

The attention mechanism gathers context — it figures out which words to pay attention to. The FFN then processes and transforms that gathered information. Research suggests the FFN stores factual knowledge from pretraining: facts, patterns, and associations that were learned from the training corpus.

</details>

---

## Intermediate

**Q4. What is the difference between the encoder's self-attention and the decoder's self-attention?**

<details>
<summary>💡 Show Answer</summary>

Encoder self-attention is bidirectional — every token attends to every other token (including future tokens). The encoder has access to the complete input sequence.

Decoder self-attention is masked (causal/autoregressive) — each token can only attend to past tokens and itself, not future tokens. This masking is enforced by setting future attention scores to -infinity before softmax. The reason: during training the decoder predicts token t+1 from tokens 1..t. If it could see future tokens, it could trivially copy them without learning anything.

</details>

---

**Q5. What is cross-attention in the transformer decoder?**

<details>
<summary>💡 Show Answer</summary>

Cross-attention is the second attention sub-layer in the decoder. It lets the decoder attend to the encoder's output representations.

- Query (Q) comes from the decoder's current state
- Key (K) and Value (V) come from the encoder's output

At each decoding step, the decoder uses cross-attention to ask: "Which part of the source sentence is most relevant for generating my next output word?" This is the mechanism that aligns source tokens to target tokens in translation, or source document tokens to summary tokens.

</details>

---

**Q6. How does the transformer handle inputs of different lengths in a batch?**

<details>
<summary>💡 Show Answer</summary>

All sequences in a batch must be the same length for efficient matrix operations. Shorter sequences are padded with a special [PAD] token to match the length of the longest sequence in the batch.

Padding masks are used during attention to prevent any position from attending to padding tokens. The padding mask sets attention scores to -infinity for padding positions before softmax, so they receive zero attention weight and don't contribute to context vectors.

The model is trained to learn that [PAD] tokens are meaningless. At inference time, single-sequence processing doesn't need padding.

</details>

---

## Advanced

**Q7. Why does the FFN use a 4× expansion in the inner dimension?**

<details>
<summary>💡 Show Answer</summary>

The FFN inner dimension (d_ff = 4 × d_model) is an empirical design choice from the original paper, but there's intuition behind it.

The attention layer compresses information — each token's new representation is a weighted sum of value vectors. The FFN then expands this into a higher-dimensional space where more nuanced transformations can happen, then projects back down.

The expansion ratio trades off:
- Higher ratio: more capacity per layer, better quality, more parameters
- Lower ratio: fewer parameters, faster, less quality

4× became the standard after showing good quality-efficiency tradeoffs. Modern research (e.g., mixture-of-experts) replaces the FFN with a sparse mixture, using much larger total capacity while only activating a small fraction per token.

</details>

---

**Q8. What is pre-norm vs post-norm in transformer layers?**

<details>
<summary>💡 Show Answer</summary>

The original "Attention is All You Need" used post-norm:
```
x = LayerNorm(x + SubLayer(x))
```

Modern models like GPT-2/3 use pre-norm:
```
x = x + SubLayer(LayerNorm(x))
```

Pre-norm (applying layer norm to the input before the sub-layer):
- Easier to train — gradients flow more cleanly
- Less warmup needed
- More stable at high learning rates
- Preferred in practice for deep models

Post-norm (original) can achieve slightly better quality on some tasks but requires careful learning rate warmup and is harder to train at scale.

</details>

---

**Q9. How does the transformer's O(n²) attention complexity compare to alternatives, and what optimizations exist?**

<details>
<summary>💡 Show Answer</summary>

Standard attention requires O(n²) time and memory for the n×n attention matrix.

For n=512: fine. For n=100,000: ~40GB for the attention matrix alone.

Key optimizations:

**Flash Attention:** Same exact math, but computed in tiles that fit in GPU SRAM. Reduces memory from O(n²) to O(n). 2–4× speedup. No quality loss. Standard in all modern training.

**Sparse attention (Longformer, BigBird):** Each token attends to a local window + a few global tokens instead of all tokens. O(n) time. Some quality loss for tasks requiring global attention.

**Linear attention:** Approximates the attention operation with a kernel trick to get O(n) complexity. Quality trade-offs depend on the approximation.

**Sliding window attention (Mistral):** Each token attends only to a local window. Very efficient. Long-range patterns are captured by combining short windows across many layers.

Flash Attention is the default recommendation for anyone training transformers today.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full architecture deep dive |
| [📄 Component_Breakdown.md](./Component_Breakdown.md) | Component-by-component breakdown |

⬅️ **Prev:** [05 Positional Encoding](../05_Positional_Encoding/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Encoder-Decoder Models](../07_Encoder_Decoder_Models/Theory.md)
