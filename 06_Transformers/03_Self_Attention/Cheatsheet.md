# Self-Attention — Cheatsheet

**One-liner:** Self-attention is attention where a sequence attends to itself — each word computes its own Q, K, V from its embedding and gathers context from all other words in the sequence.

---

## Key Terms

| Term | Definition |
|---|---|
| Self-attention | Attention where Q, K, V all come from the same sequence |
| W_Q, W_K, W_V | Learned weight matrices that project embeddings to queries, keys, values |
| Attention matrix | N×N matrix where cell [i][j] = how much word i attends to word j |
| Contextual representation | Updated word embedding that now contains info from the whole sequence |
| Masked self-attention | Self-attention that only allows attending to past positions (used in GPT) |

---

## Self-attention vs cross-attention vs regular attention

| Type | Q from | K, V from | Used where |
|---|---|---|---|
| Self-attention | Same sequence | Same sequence | Encoder, GPT decoder |
| Cross-attention | Decoder sequence | Encoder sequence | Translation decoder |
| Classic RNN attention | Decoder state | Encoder hidden states | Old seq2seq |

---

## Self-attention formula

```
SelfAttention(X) = softmax( X W_Q (X W_K)^T / √d_k ) × X W_V

Shapes (for N tokens, d_model dimensions, d_k key dimension):
  Input X:         (N × d_model)
  W_Q, W_K, W_V:   (d_model × d_k)
  Q = X × W_Q:    (N × d_k)
  K = X × W_K:    (N × d_k)
  V = X × W_V:    (N × d_v)
  Scores = Q K^T: (N × N)
  Output:         (N × d_v)
```

---

## Properties of self-attention

| Property | What it means |
|---|---|
| Permutation invariant | Without positional encoding, word order doesn't matter |
| O(n²) complexity | Every pair of positions must interact |
| All positions in parallel | Unlike RNN (sequential), attention is fully parallel |
| Long-range free | Distance between positions costs nothing |

---

## What the attention matrix tells you

- High weight [i][j]: word i heavily attends to word j
- Diagonal weights: word attends to itself (common)
- Off-diagonal patterns: syntactic/semantic relationships
- Rows sum to 1: each word distributes 100% attention across all positions

---

## Golden Rules

1. Self-attention is the core building block of transformers — understand it deeply.
2. Q, K, V are different projections of the same input — this is intentional and powerful.
3. The attention matrix is differentiable — the model learns which words should attend to which.
4. Self-attention has no positional info — positional encoding must be added separately.
5. Masked self-attention (used in GPT) zeroes out future positions so the model can't "cheat."

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Walkthrough.md](./Math_Walkthrough.md) | Step-by-step math walkthrough |

⬅️ **Prev:** [02 Attention Mechanism](../02_Attention_Mechanism/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Multi-Head Attention](../04_Multi_Head_Attention/Theory.md)
