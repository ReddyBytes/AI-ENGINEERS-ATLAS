# Multi-Head Attention — Cheatsheet

**One-liner:** Multi-head attention runs h parallel attention operations on the same input, each with its own learned weight matrices, then concatenates and projects their outputs to capture multiple relationship types simultaneously.

---

## Key Terms

| Term | Definition |
|---|---|
| Head | One parallel attention computation with its own W_Q, W_K, W_V |
| h | Number of attention heads (typically 8 or 12 or 16) |
| d_model | Full model dimension (e.g., 512 or 768) |
| d_k | Per-head key/query dimension = d_model / h |
| W_O | Output projection matrix that mixes all head outputs |
| Concatenation | Joining head outputs side by side before projection |

---

## Multi-head attention formula

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) × W_O

where head_i = Attention(Q × W_Q_i, K × W_K_i, V × W_V_i)
```

---

## Dimension flow

```
Input: (N × d_model)
  ↓ (split into h heads)
Per head: Q, K, V each (N × d_k) where d_k = d_model / h
  ↓ (attention per head)
Per head output: (N × d_v) where d_v = d_model / h
  ↓ (concatenate h heads)
Concatenated: (N × d_model)
  ↓ (× W_O)
Final output: (N × d_model)
```

---

## Common configurations

| Model | d_model | Heads | d_k per head |
|---|---|---|---|
| BERT-base | 768 | 12 | 64 |
| BERT-large | 1024 | 16 | 64 |
| GPT-2 | 768 | 12 | 64 |
| GPT-3 | 12,288 | 96 | 128 |
| Original Transformer | 512 | 8 | 64 |

---

## What heads learn (observed empirically)

| Head type | Pattern |
|---|---|
| Syntactic | Subject-verb, noun-article links |
| Coreference | Pronouns → their referents |
| Local/positional | Attends to nearby words |
| Semantic | Semantically related content words |
| Global | Attends heavily to [CLS] or separator tokens |

---

## Multi-head vs single-head attention

| Feature | Single-head | Multi-head |
|---|---|---|
| Relationships captured | One type at a time | Multiple simultaneously |
| Per-head dimension | d_model | d_model / h (smaller) |
| Total parameters | ~3 × d_model² | ~4 × d_model² |
| Expressiveness | Limited | Much higher |

---

## Golden Rules

1. Heads learn to specialize automatically — you don't assign them roles manually.
2. d_k = d_model / h keeps the total parameter count manageable as h increases.
3. The W_O projection is essential — it learns how to blend different heads' outputs.
4. More heads ≠ always better — there's a sweet spot (8–16 for most models).
5. Some heads learn useful patterns, some are redundant — pruning attention heads can shrink models with minimal accuracy loss.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [03 Self Attention](../03_Self_Attention/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Positional Encoding](../05_Positional_Encoding/Theory.md)
