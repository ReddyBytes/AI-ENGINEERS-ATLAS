# Attention Mechanism — Cheatsheet

**One-liner:** Attention lets a model selectively focus on the most relevant parts of the input by computing a weighted sum of values, where weights are based on similarity between a query and keys.

---

## Key Terms

| Term | Definition |
|---|---|
| Query (Q) | "What am I looking for?" — the current position's search vector |
| Key (K) | "What do I contain?" — each position's label for matching |
| Value (V) | The actual content to retrieve from each position |
| Attention score | Dot product of Query and Key — measures relevance |
| Attention weight | Softmax-normalized attention score (sums to 1) |
| Context vector | Weighted sum of Values using attention weights |
| Scaled dot-product attention | Attention with scores divided by √d to prevent saturation |
| Soft attention | Differentiable weighted sum (vs hard attention: hard argmax) |

---

## The attention formula

```
Attention(Q, K, V) = softmax(Q × K^T / √d_k) × V

Where:
  Q = query matrix
  K = key matrix
  V = value matrix
  d_k = dimension of keys (used for scaling)
```

---

## Step-by-step

```
1. Compute raw scores:   scores = Q × K^T
2. Scale:                scores = scores / √d_k
3. Normalize:            weights = softmax(scores)
4. Retrieve:             context = weights × V
```

---

## Why divide by √d_k?

With high-dimensional vectors, dot products can get very large. Large values fed into softmax produce near-zero gradients (saturation). Dividing by √d_k keeps values in a reasonable range.

---

## Types of attention

| Type | Q comes from | K, V come from | Used in |
|---|---|---|---|
| Self-attention | Input sequence | Input sequence | Transformer encoder |
| Cross-attention | Decoder | Encoder | Transformer decoder |
| Masked attention | Input (past only) | Input (past only) | GPT, decoder |

---

## When attention weights are high / low

| Weight | Meaning |
|---|---|
| High (close to 1) | This position is very relevant to the query |
| Low (close to 0) | This position is irrelevant |
| Uniform | Query has no clear preference — ambiguous |

---

## Golden Rules

1. Attention is differentiable — weights are learned through backpropagation.
2. Attention weights are probabilities — they always sum to 1.
3. Scaling by √d_k is critical for stable training.
4. Context vector is always a weighted sum, not a hard selection.
5. Without positional encoding, attention has no notion of word order.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Walkthrough.md](./Math_Walkthrough.md) | Step-by-step math walkthrough |

⬅️ **Prev:** [01 Sequence Models Before Transformers](../01_Sequence_Models_Before_Transformers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Self Attention](../03_Self_Attention/Theory.md)
