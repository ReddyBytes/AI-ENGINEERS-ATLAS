# Attention Mechanism — Interview Q&A

## Beginner

**Q1. What problem does the attention mechanism solve in sequence-to-sequence models?**

In early seq2seq models (used for translation), the encoder read the entire input sentence and compressed it into a single fixed-size vector. The decoder then used only this vector to generate the translation. For long sentences, this vector couldn't hold all the information — early words would be lost.

Attention solves this by giving the decoder direct access to all encoder hidden states at each decoding step. Instead of one compressed vector, the decoder computes a weighted mixture of all encoder states, focusing on whichever ones are most relevant for the current output word.

---

**Q2. What are Query, Key, and Value in attention?**

These are three roles that vectors play in attention:

- **Query:** "What am I looking for?" This comes from the decoder (or the current position in self-attention). It represents what the current step needs.
- **Key:** "What do I have?" This comes from the encoder (or each position in self-attention). It labels each memory slot for matching.
- **Value:** "What is my actual content?" This is what gets retrieved when a match is found.

Attention computes how well the Query matches each Key (via dot product), normalizes with softmax to get weights, then returns a weighted sum of Values. It's like a soft database query — you don't get one exact answer, you get a blend of all answers weighted by relevance.

---

**Q3. What is the softmax in attention and why is it used?**

After computing attention scores (dot products between Query and Keys), you need to turn these scores into weights that sum to 1. Softmax does this.

It amplifies the highest scores and suppresses the low ones, while ensuring all weights are positive and sum to exactly 1. This makes the weights interpretable as probabilities: "30% focus on word 1, 60% focus on word 3, 10% elsewhere."

Softmax is differentiable, so gradients flow through it during training. The model can learn which queries should attend to which keys.

---

## Intermediate

**Q4. What is scaled dot-product attention and why is scaling important?**

Scaled dot-product attention is: `Attention(Q, K, V) = softmax(Q K^T / √d_k) V`

The scaling by √d_k is important because:

As d_k (the key/query dimension) grows large, the dot products Q·K can get very large in magnitude. When you feed large values into softmax, most of the output probability concentrates on one element — it becomes nearly a one-hot distribution. This causes near-zero gradients for most positions (saturation), making learning very slow.

Dividing by √d_k normalizes the dot products to have a magnitude similar to 1, keeping softmax in a useful, gradient-rich range.

---

**Q5. What is cross-attention and when is it used?**

Cross-attention is the attention mechanism where the Query comes from one sequence and the Keys and Values come from a different sequence.

In transformer translation (encoder-decoder):
- The encoder processes the source sentence and produces K and V
- The decoder generates Q from its current state
- Cross-attention lets the decoder query the encoder's full output to figure out which source words to focus on for the next translation step

This is the mechanism that aligns source and target words in translation. It replaced the fixed context vector bottleneck of old seq2seq models.

---

**Q6. How do attention weights help with model interpretability?**

Attention weights form a matrix where each row shows how much each output position attended to each input position. You can visualize this as a heatmap.

For translation: if "chat" in French has high attention weight to "cat" in English, the model has learned the word-level alignment.

For BERT: the attention heads often learn interpretable patterns — some heads track subject-verb agreement, others track coreference, others track positional proximity.

Caution: high attention weight doesn't always mean "this is causally important for the prediction." Gradient-based attribution methods are more rigorous for interpretability. But attention visualizations are a useful starting point for debugging and understanding model behavior.

---

## Advanced

**Q7. What is the computational complexity of attention and why does it matter for long sequences?**

Standard self-attention has O(n²) complexity in both time and memory, where n is the sequence length.

For each of the n positions, you compute attention scores against all n other positions: n × n = n² operations. You also store the n × n attention matrix.

For n=512 (BERT): 512² = 262,144 — fine.
For n=16,384 (long document): 16,384² = 268 million — expensive.
For n=100,000 (book): 100,000² = 10 billion — infeasible.

This is why context length was a bottleneck for years. Solutions include sparse attention (attend only to nearby positions + some global tokens), linear attention approximations, flash attention (memory-efficient exact attention), and sliding window approaches.

---

**Q8. What is the difference between additive attention (Bahdanau) and multiplicative attention (Luong/scaled dot-product)?**

**Additive attention (Bahdanau, 2015):**
```
score(Q, K) = v^T × tanh(W_1 × Q + W_2 × K)
```
Uses a learned weight matrix and a tanh nonlinearity. More parameters, but can work better in some lower-dimensional settings.

**Multiplicative attention (scaled dot-product):**
```
score(Q, K) = Q · K / √d_k
```
Uses the dot product directly. No extra parameters for the score computation. Faster and parallelizable. The standard in modern transformers.

At high dimensions, scaled dot-product attention tends to match or exceed additive attention in quality, and is much faster, which is why it became the standard.

---

**Q9. Why can't you use attention without positional encoding?**

Attention is permutation-invariant. The attention score between position 3 and position 7 is computed purely from their embedding vectors — position 3 could be anywhere in the sequence and the score would be the same.

This means "The dog bit the man" and "The man bit the dog" — a complete reversal of meaning — would produce exactly the same attention scores if all four words are in the same sequence.

Without positional information, the model has no way to know word order. Positional encoding adds a position-dependent signal to each embedding so the model can distinguish "dog" at position 2 from "dog" at position 5. The attention mechanism then picks up these position signals through the Q/K/V projections.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Walkthrough.md](./Math_Walkthrough.md) | Step-by-step math walkthrough |

⬅️ **Prev:** [01 Sequence Models Before Transformers](../01_Sequence_Models_Before_Transformers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Self Attention](../03_Self_Attention/Theory.md)
