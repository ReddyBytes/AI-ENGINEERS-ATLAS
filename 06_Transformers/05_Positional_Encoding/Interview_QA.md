# Positional Encoding — Interview Q&A

## Beginner

**Q1. Why do transformers need positional encoding?**

<details>
<summary>💡 Show Answer</summary>

Self-attention is permutation-invariant — it doesn't care about word order. When computing the attention score between two words, only their embedding vectors matter, not where they sit in the sentence.

This means "The dog bit the man" and "The man bit the dog" would produce identical attention matrices without positional information. These sentences have opposite meanings, so the model would fail at tasks that depend on order.

Positional encoding adds position information directly to the word embeddings before they enter attention. Now position 3's embedding looks different from position 7's embedding of the same word, giving the model a way to distinguish "dog at position 2" from "dog at position 5."

</details>

---

**Q2. How does sine/cosine positional encoding work at an intuitive level?**

<details>
<summary>💡 Show Answer</summary>

Think of a clock with multiple hands, each cycling at a different speed. The seconds hand completes a cycle every 60 seconds. The minutes hand every hour. The hours hand every 12 hours. Together, they can represent any time uniquely.

Sine/cosine positional encoding does the same thing with vector dimensions. Each dimension of the position vector oscillates at a different frequency — high frequency for early dimensions (fast-changing), low frequency for later dimensions (slow-changing).

When you look at the full vector for position 42, the pattern of high-frequency dimensions is different from position 43, and the low-frequency dimensions are different from position 142. Together, they create a unique fingerprint for every position.

</details>

---

**Q3. How is positional encoding added to word embeddings?**

<details>
<summary>💡 Show Answer</summary>

Positional encodings are vectors of the same dimension as word embeddings. They are added element-wise to the word embeddings:

```
input_i = word_embedding_i + positional_encoding_i
```

This modified embedding is what goes into the first self-attention layer. The model then uses Q/K/V projections on these enriched inputs. Position information flows into the Q and K vectors, allowing the model to include position when computing attention scores.

</details>

---

## Intermediate

**Q4. What is the difference between absolute and relative positional encoding?**

<details>
<summary>💡 Show Answer</summary>

**Absolute positional encoding** encodes where each token sits in the sequence: token at position 1, token at position 2, etc. The original transformer and BERT use this.

Problem: the model learns relationships like "position 5 is usually a verb" but can't easily learn "subject is typically 3 positions before the verb" — it needs to see all combinations of absolute positions.

**Relative positional encoding** encodes the distance between pairs of tokens: "these two tokens are 3 positions apart." The model learns patterns based on relative distance instead of absolute position.

Benefits: better at capturing relationships like subject-verb distance, negation proximity, etc. Also generalizes better to longer sequences because distance patterns are consistent regardless of where they appear in the absolute sequence.

</details>

---

**Q5. What is RoPE (Rotary Position Embedding) and why is it popular in modern LLMs?**

<details>
<summary>💡 Show Answer</summary>

RoPE encodes position by rotating the Query and Key vectors by an angle that depends on position. Instead of adding a PE vector to the embedding, it applies a rotation matrix to Q and K before computing attention.

The key insight: when you compute Q · K (the attention score), the rotation factors cancel out into a term that depends only on the relative position (pos_i - pos_j). The model naturally gets relative position information through the attention computation itself.

Why popular:
- Extrapolates to longer sequences than trained on (with techniques like NTK/YaRN scaling)
- Relative position falls out naturally — no need to design separate relative PE mechanisms
- Computationally efficient
- Used in Llama, Mistral, Falcon, Qwen, and most modern open-source LLMs

</details>

---

**Q6. Can a transformer be trained without positional encoding?**

<details>
<summary>💡 Show Answer</summary>

Yes — but it loses word order information. The model processes the sentence as a set, not a sequence. "Dog bites man" and "Man bites dog" become equivalent.

There are scenarios where this might be intentional:
- Bag-of-words-style classification where order doesn't matter
- Processing structured data (tables, graphs) where positions have different semantics

Some recent work (e.g., in set-based models) deliberately omits positional encoding and instead models sets of items. But for any task where word order matters, positional encoding is essential.

</details>

---

## Advanced

**Q7. How does positional encoding enable the transformer to generalize to longer sequences than it was trained on?**

<details>
<summary>💡 Show Answer</summary>

With sine/cosine encoding: the formula is defined for any position, so vectors for positions 512 and 1024 are well-defined even if the model was trained on 512-length sequences. Whether the model can use these unseen positions well depends on whether the model learned patterns that transfer.

In practice, vanilla absolute PE doesn't generalize well beyond training length — the model hasn't seen those position embeddings and they're outside the distribution.

Better approaches:
- **RoPE with NTK scaling:** rescales the base frequency so position vectors interpolate within the trained range rather than extrapolating outside it
- **ALiBi:** uses additive position biases that decay with distance — naturally encourages the model to rely on local context and generalizes to longer sequences
- **YaRN (Yet Another RoPE extensioN):** fine-tunes the model on longer sequences using modified RoPE frequencies

These techniques allowed models like Llama 2 (trained at 4k context) to be extended to 100k+ context without full retraining.

</details>

---

**Q8. How does positional encoding interact with multi-head attention?**

<details>
<summary>💡 Show Answer</summary>

Positional encoding is added to word embeddings before any projections. When the model computes Q = X × W_Q and K = X × W_K, the positional signal is mixed in.

Each head's W_Q and W_K then determine how much that head uses the position signal vs. the word meaning signal. In practice:
- Some heads learn to rely heavily on position (acting as local attention windows)
- Others largely ignore position and focus on semantic content

This is why heads specialize: the model learns that some tasks (like NER) benefit from local attention, while others (like coreference) benefit from content-based long-range attention. Positional encoding gives all heads the option to use position — which heads actually do is learned during training.

</details>

---

**Q9. What is ALiBi and how does it handle long contexts without positional embeddings in embeddings?**

<details>
<summary>💡 Show Answer</summary>

ALiBi (Attention with Linear Biases) doesn't add positional encodings to embeddings at all. Instead, it adds a negative linear bias directly to the attention score matrix:

```
attention_score(i, j) = Q_i · K_j / √d_k - m × |i - j|
```

Where m is a head-specific slope (different for each head).

The further apart two positions are, the more the score is penalized. Closer positions are penalized less. Each head has a different slope — some heads have steep slopes (very local), others have shallow slopes (global context).

Benefits:
- No position vectors added to embeddings — cleaner
- Linear extrapolation: the bias formula works naturally for any distance, even unseen at training
- Proven to generalize well to sequences 4–8× longer than training without modification
- Used in models like BLOOM

The trade-off is that the model must rely entirely on content-based attention for long-range reasoning — there's no "this word is at position 512" signal, only "this word is 100 positions away from that word."

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind positional encoding |

⬅️ **Prev:** [04 Multi-Head Attention](../04_Multi_Head_Attention/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Transformer Architecture](../06_Transformer_Architecture/Theory.md)
