# Transformer Architecture — Interview Q&A

## Beginner

**Q1: What is a transformer? Why did it replace RNNs for language modeling?**

<details>
<summary>💡 Show Answer</summary>

A transformer is a neural network architecture that uses self-attention to process sequences. The key innovation is that every token can directly attend to every other token in the sequence, regardless of distance.

RNNs process text sequentially — they pass a "hidden state" forward through the sequence, one word at a time. The problem: information from early in a sequence gets compressed into a fixed-size vector and degrades by the time the model processes the end. Long-range dependencies (like a pronoun referring to a noun 100 words earlier) are hard to capture.

Transformers replace sequential processing with parallel self-attention: every token simultaneously computes how much it should attend to every other token. This enables:
- Processing the entire sequence in parallel during training (much faster)
- Perfect long-range attention — position 1 and position 10,000 can directly attend to each other
- Richer contextual representations at every layer

</details>

---

<br>

**Q2: What are Query, Key, and Value in self-attention?**

<details>
<summary>💡 Show Answer</summary>

Q, K, V are three different projections of the same input, each with a different role:

- **Query (Q)**: "What information am I looking for?" — The current token's search query
- **Key (K)**: "What information do I offer?" — Each token's label describing its content  
- **Value (V)**: "What is my actual content?" — The information that gets aggregated

The mechanism: compute dot products between the current token's Query and every token's Key. Apply softmax to get attention weights. Then take a weighted average of all Values using those weights.

Analogy: imagine a document search engine. Your search query is Q. The document titles are K (they describe what each document contains). The document content is V (what you actually retrieve). The attention mechanism finds which documents (Keys) best match your query, then returns a blend of those documents' content (Values).

</details>

---

<br>

**Q3: What is multi-head attention and why use multiple heads?**

<details>
<summary>💡 Show Answer</summary>

Multi-head attention runs the self-attention mechanism h times in parallel, each with different learned projection matrices. Each "head" sees the same tokens but projects them into a different subspace.

Why multiple heads: a single attention head computes one type of relationship between tokens. But language has many simultaneous relationships — syntactic (subject-verb), semantic (coreference), positional (adjacent words), logical (cause-effect). Multiple heads can each specialize in capturing different relationship types.

In practice, heads do sometimes specialize: research has found heads that focus on syntactic dependencies, heads that track coreference, heads that attend to local context, etc. The outputs of all heads are concatenated and projected to form the final attention output.

</details>

---

## Intermediate

**Q4: What is the causal mask in a decoder-only transformer and why is it necessary?**

<details>
<summary>💡 Show Answer</summary>

A decoder-only model (like Claude) generates text autoregressively — it predicts each token one at a time, left to right. During training, you have the complete correct sequence and can compute all positions in parallel. But each position should only see its own and earlier tokens, not future tokens — that would be cheating.

The causal mask enforces this by setting future attention scores to -infinity before softmax, which makes them effectively 0 after softmax. The resulting attention weight matrix is lower-triangular:

```
Position: 0  1  2  3
       0 [1  0  0  0]  # can see only itself
       1 [1  1  0  0]  # can see pos 0 and 1
       2 [1  1  1  0]  # can see pos 0,1,2
       3 [1  1  1  1]  # can see all
```

This is what makes the same transformer usable for both training (parallel) and inference (sequential) — the causal mask enforces the sequential constraint during parallel training.

</details>

---

<br>

**Q5: What are residual connections and layer normalization, and why are they both necessary?**

<details>
<summary>💡 Show Answer</summary>

**Residual connections** add the input directly to the output of a sub-layer: `output = x + SubLayer(x)`. Without them, gradients in a deep network (60-96 layers) must flow through every layer to reach the early layers. If any layer shrinks the gradient, it compounds across layers and vanishes. Residuals create "highways" for gradient flow — the gradient can bypass any layer through the skip path.

**Layer normalization** normalizes the activations at each token position across the feature dimension. Without it, as features pass through many layers, values can explode or vanish due to accumulating nonlinearities. LayerNorm keeps activations in a stable range.

Both are necessary: residuals solve gradient flow, LayerNorm solves activation stability. Modern transformers use Pre-LayerNorm (normalize before the sub-layer, not after) which trains even more stably for very deep models.

</details>

---

<br>

**Q6: What is the feed-forward network in a transformer block and what does it do?**

<details>
<summary>💡 Show Answer</summary>

Each transformer block contains a feed-forward network (FFN) applied independently to each token position after attention. It's a two-layer MLP:

```
FFN(x) = Activation(x × W_1 + b_1) × W_2 + b_2
```

Key properties:
- **Position-wise**: Each token's FFN computation is independent — no cross-token interaction (that happened in attention)
- **Expanded dimension**: W_1 expands to 4× the model dimension (d_ff = 4 × d_model), then W_2 contracts back
- **Where knowledge lives**: Research suggests the FFN layers store much of the model's factual knowledge — "fact retrieval" happens in FFN, while "fact lookup" by context happens in attention

This is why LoRA fine-tuning targets FFN weight matrices — you can update the knowledge stored there without touching the attention mechanism.

</details>

---

## Advanced

**Q7: What is Grouped Query Attention (GQA) and why does it matter for long-context inference?**

<details>
<summary>💡 Show Answer</summary>

Standard multi-head attention has h query heads, h key heads, and h value heads. This means the KV cache stores h separate key and value matrices per layer, per token.

For a 200k token context, a large model with 64 heads: the KV cache can exceed 100 GB — a significant infrastructure cost.

**GQA** uses fewer K and V heads than Q heads. Common configuration: 64 query heads sharing 8 KV heads (8:1 ratio). Multiple query heads "share" the same key and value projections.

Benefits:
- KV cache is 8x smaller with 8:1 GQA vs standard MHA
- Makes long-context inference feasible on smaller hardware
- Quality degradation is minimal — the shared KV heads still capture sufficient information for the queries to specialize

This is why modern models like Llama 2/3 and presumably Claude use GQA — it's essential for making 200k context windows practically deployable.

</details>

---

<br>

**Q8: Explain the scaling behavior of attention and how Flash Attention addresses it.**

<details>
<summary>💡 Show Answer</summary>

Self-attention is O(n²) in sequence length n. For n=200k:
- 200,000² = 40 billion attention score values per layer
- At 2 bytes each = 80 GB just to store the attention matrix for one layer
- Impossible with standard GPU memory (typically 40-80 GB total)

Standard attention materializes this full n×n matrix. Flash Attention (Dao et al., 2022) avoids this:

The core insight: the bottleneck is memory bandwidth (moving data from GPU memory to registers), not raw compute. Flash Attention decomposes the attention computation into tiles:

1. Load a tile of Q and K from memory
2. Compute partial attention scores for that tile
3. Update running softmax statistics (using the "online softmax" algorithm)
4. Accumulate the weighted V contribution
5. Repeat for all tiles

The full n×n matrix is never materialized — partial statistics are accumulated on-chip. Memory complexity drops from O(n²) to O(n). Compute complexity stays O(n²) but the constant factor is much smaller because memory bandwidth is no longer the bottleneck.

Result: Flash Attention 2 is ~2-4x faster than naive attention in practice and enables 100k+ token contexts that would otherwise be impossible.

</details>

---

<br>

**Q9: How does RoPE (Rotary Position Embedding) differ from sinusoidal encoding, and why is it preferred for long contexts?**

<details>
<summary>💡 Show Answer</summary>

Sinusoidal encoding adds a fixed position vector to each token embedding. This means positional information is added once at the input and must be preserved through all transformer layers. At long contexts or positions not seen during training, the model can fail to generalize.

RoPE encodes position by rotating the query and key vectors at each attention layer:

```
RoPE(x, pos) = rotation_matrix(pos) × x
```

The rotation angle is proportional to the position index and varies by feature dimension. When you compute the dot product QK^T:

```
(Q_rotated × K_rotated^T)[i,j] = Q_i × R^T(i-j) × K_j
```

This means the dot product naturally depends only on the relative position (i-j), not absolute positions. This relative position encoding:

1. Extrapolates better to positions not seen in training
2. Can be extended to longer contexts via "position interpolation" techniques (used in LongRoPE, rope-scaling in practice)
3. Is applied at every attention layer — richer positional information than adding it once at input

This is why models with RoPE can often be extended to longer contexts than their training distribution, and why all modern frontier models (Llama, Gemini, Claude) use RoPE or a variant.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full visual stack |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Attention math explained |

⬅️ **Prev:** [03 Tokens and Context Window](../03_Tokens_and_Context_Window/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Pretraining](../05_Pretraining/Theory.md)
