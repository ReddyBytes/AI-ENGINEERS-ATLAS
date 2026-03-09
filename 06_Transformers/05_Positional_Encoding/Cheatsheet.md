# Positional Encoding — Cheatsheet

**One-liner:** Positional encoding adds position information to word embeddings before self-attention, because attention is order-agnostic and needs external position signals to understand word sequence.

---

## Key Terms

| Term | Definition |
|---|---|
| Positional encoding (PE) | A vector added to each word embedding to encode its position |
| Absolute PE | Encodes the absolute position (1, 2, 3...) of each token |
| Relative PE | Encodes the distance between pairs of tokens |
| RoPE | Rotary Position Embedding — rotates Q/K vectors by position angle |
| ALiBi | Attention with Linear Biases — adds position-based bias to scores |
| Sine/cosine encoding | The original fixed PE from "Attention is All You Need" |
| Learned PE | Position embeddings trained alongside the model |

---

## Sine/cosine formula (original)

For position pos and dimension i:

```
PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))
```

Even dimensions → sine. Odd dimensions → cosine. Each dimension cycles at a different frequency.

---

## How it's used

```
input = word_embedding + positional_encoding
# Both are the same shape: (sequence_length × d_model)
# Added element-wise before the first self-attention layer
```

---

## PE types comparison

| Type | Generalize beyond training length? | Learned? | Used in |
|---|---|---|---|
| Sine/cosine | Yes | No | Original Transformer |
| Learned absolute | Limited | Yes | BERT, GPT-2 |
| Relative | Better | Partial | T5, Transformer-XL |
| RoPE | Good | No | Llama, Mistral, Falcon |
| ALiBi | Strong | No | Some recent models |

---

## Why sine/cosine works

- Unique: every position gets a different vector
- Bounded: values always in [-1, 1]
- Smooth: similar positions have similar vectors
- Generalizable: the formula works for any position, even beyond training length
- Relative distances: PE(pos + k) can be expressed as a linear function of PE(pos), helping the model learn relative position patterns

---

## Golden Rules

1. Without positional encoding, "Dog bites man" and "Man bites dog" produce identical attention outputs.
2. Position encoding is added to embeddings, not concatenated — keeps dimensions manageable.
3. Sine/cosine PE can generalize to longer sequences at test time; learned PE cannot.
4. Modern LLMs use RoPE or ALiBi for better long-context handling.
5. Positional encoding is applied once at the input layer — not at every attention layer.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind positional encoding |

⬅️ **Prev:** [04 Multi-Head Attention](../04_Multi_Head_Attention/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Transformer Architecture](../06_Transformer_Architecture/Theory.md)
