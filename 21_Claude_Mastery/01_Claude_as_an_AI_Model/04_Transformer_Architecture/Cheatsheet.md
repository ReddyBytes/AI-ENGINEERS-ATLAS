# Transformer Architecture — Cheatsheet

**One-liner:** A transformer is a stack of self-attention + feed-forward layers that lets every token attend to every other token in the sequence, enabling rich contextual representations across long inputs.

---

## Key terms

| Term | What it means |
|------|---------------|
| Transformer | Neural architecture built on self-attention; backbone of all modern LLMs |
| Self-attention | Mechanism where each token attends to every other token |
| Query (Q) | "What am I looking for?" — projection of current token |
| Key (K) | "What do I offer?" — projection of all tokens |
| Value (V) | "What is my content?" — projection of all tokens |
| Multi-head attention | Attention computed h times in parallel with different learned projections |
| Causal mask | Masks future tokens so decoder-only models can't attend forward |
| Feed-forward network | Two-layer MLP applied to each token position independently |
| Layer normalization | Normalizes activations across the feature dimension per token |
| Residual connection | Skip connection: output = LayerNorm(x + SubLayer(x)) |
| Positional encoding | Adds position information to token embeddings |
| RoPE | Rotary Position Embedding — modern positional encoding via rotations |
| GQA | Grouped-Query Attention — multiple query heads share K and V |
| KV cache | Cached keys/values for past tokens — avoids recomputation |
| d_model | The embedding dimension (e.g., 4096 for large models) |
| d_ff | FFN hidden dimension — typically 4× d_model |

---

## Self-attention formula

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) × V
```

Step by step:
1. `QK^T` — dot product: how much does each query match each key?
2. `/ sqrt(d_k)` — scale to prevent softmax saturation
3. `softmax(...)` — convert to probabilities over all positions
4. `× V` — take weighted average of value vectors

---

## Multi-head attention formula

```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) × W_O
head_i = Attention(Q × W_Q_i, K × W_K_i, V × W_V_i)
```

h heads, each with dimension d_model/h. All computed in parallel.

---

## Transformer block structure

```
Input x
  ↓
LayerNorm
  ↓
Multi-Head Self-Attention
  ↓ 
+ x  (residual)
  ↓
LayerNorm
  ↓
Feed-Forward Network (expand × 4, then contract)
  ↓
+ prev (residual)
  ↓
Output to next block
```

---

## Positional encodings compared

| Method | How | Used in |
|--------|-----|---------|
| Sinusoidal (fixed) | sin/cos at different frequencies | Original transformer |
| Learned positions | Trainable embedding per position | GPT-2, BERT |
| RoPE | Rotate Q, K by angle proportional to position | LLaMA, Gemini, Claude |
| ALiBi | Linear bias added to attention scores | BLOOM |

---

## Architecture evolution: Original vs Claude

| Feature | Original (2017) | Claude / Modern |
|---------|----------------|----------------|
| Type | Encoder-Decoder | Decoder-only |
| Positional | Sinusoidal | RoPE |
| Normalization | Post-LN | Pre-LN |
| Activation | ReLU | SwiGLU / GELU |
| Attention | MHA | GQA |
| Context | 512 tokens | 200,000 tokens |
| Vocabulary | ~37k | ~100k |

---

## Compute complexity

| Operation | Complexity |
|-----------|-----------|
| Self-attention (naive) | O(n²d) — quadratic in sequence length |
| Flash Attention | O(n²) compute but O(n) memory |
| FFN | O(nd²) per layer |
| KV cache (inference) | O(n) per new token (amortized) |
| Full inference (no cache) | O(n²d × L) for n tokens, d dim, L layers |

---

## Golden rules

1. Every token attends to every other token in the same layer — that's what makes transformers different from RNNs
2. Residual connections are load-bearing — they prevent vanishing gradients in deep stacks
3. Multi-head attention heads can specialize — some attend locally, some globally
4. The FFN is where much of the model's "knowledge" is stored
5. KV cache is why long-context inference is feasible — without it, each token would require O(n²) recomputation
6. Causal masking enforces autoregressive generation — decoders can't cheat by looking ahead

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full visual stack |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Attention math explained |

⬅️ **Prev:** [03 Tokens and Context Window](../03_Tokens_and_Context_Window/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Pretraining](../05_Pretraining/Theory.md)
