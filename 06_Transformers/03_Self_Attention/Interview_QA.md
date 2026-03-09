# Self-Attention — Interview Q&A

## Beginner

**Q1. What is self-attention and how does it differ from regular attention?**

Self-attention is a form of attention where the sequence attends to itself. The Query, Key, and Value vectors all come from the same sequence.

Regular attention (used in encoder-decoder models) has the Query come from the decoder and the Keys/Values come from the encoder — two different sequences communicating.

In self-attention, every word in a sentence computes attention scores against every other word in the same sentence. This lets each word build a contextual representation that incorporates information from the entire sequence.

---

**Q2. How are Q, K, and V derived from the input in self-attention?**

Each word's embedding is multiplied by three separate learned weight matrices to produce three different representations:

- Query: embedding × W_Q (what this word is looking for)
- Key: embedding × W_K (what this word contains for others to find)
- Value: embedding × W_V (what this word contributes when found)

The same word embedding produces three different views. These weight matrices are trained through backpropagation to make the attention maximally useful for the task.

---

**Q3. What does the attention matrix in self-attention represent?**

The attention matrix is an N×N table (for a sequence of N words). Cell [i][j] contains the attention weight from word i to word j — how much word i is "looking at" word j when building its updated representation.

Each row sums to 1 (softmax ensures this). High weights in a row indicate which words word i is gathering information from. This matrix can be visualized as a heatmap and often shows interpretable patterns like subject-verb dependencies or pronoun resolution.

---

## Intermediate

**Q4. Why is self-attention better than an RNN for capturing long-range dependencies?**

In an RNN, information from word 1 must travel through N-1 sequential steps to influence word N. Each step applies a transformation that can degrade the signal. For long sequences, word 1's information is largely gone by the time you reach word 100.

In self-attention, word 1 and word 100 interact directly with a single dot product. Distance is irrelevant. The attention score between word 1 and word 100 is computed in the same way as between word 50 and word 51.

This is why transformers with self-attention can handle long documents much better than LSTMs.

---

**Q5. What is masked self-attention and why is it needed in GPT?**

GPT is a generative model — it predicts the next word given all previous words. During training, you show the model a sentence like "The cat sat on the mat" and train it to predict each word from the words before it.

Without masking, the model could "cheat" by attending to future positions when predicting the current one. Word 3 could attend to words 4, 5, 6 and trivially predict correctly without learning anything.

Masked self-attention sets all attention weights where position j > position i to -infinity before softmax. After softmax, these become zero — the model literally cannot see future positions. This is called causal or autoregressive masking.

---

**Q6. What is the computational cost of self-attention and what are its implications?**

Self-attention has O(n²) time and memory complexity, where n is the sequence length.

For each of the n positions, you compute attention scores against all n other positions: n × n operations. The attention matrix itself requires O(n²) memory.

Practical implications:
- Sequences of 512 tokens: fine (BERT uses 512)
- Sequences of 4096 tokens: manageable with optimization
- Sequences of 100,000 tokens: attention alone would require ~40GB memory — requires specialized techniques (sparse attention, flash attention, sliding window attention)

This is why there was an engineering race to extend transformer context windows after the original paper.

---

## Advanced

**Q7. How does the choice of d_k (key/query dimension) affect self-attention?**

d_k is the dimension of the Query and Key vectors. It affects two things:

1. **Scaling:** attention scores are divided by √d_k. If d_k is large and you don't scale, dot products grow proportionally to d_k, pushing softmax into saturation. Scaling keeps gradients healthy regardless of d_k.

2. **Expressiveness vs efficiency trade-off:** larger d_k gives each head more capacity to represent complex queries and keys, but increases computational cost. Typical transformers use d_k = d_model / num_heads.

3. **Rank bottleneck:** the attention matrix is computed as Q K^T, which has rank at most min(n, d_k). If d_k is too small relative to n, the attention matrix may not be expressive enough to represent all necessary word relationships.

---

**Q8. Can self-attention learn positional relationships between words, and how?**

On its own, self-attention is permutation-invariant — it produces the same output regardless of word order. "Dog bites man" and "Man bites dog" would have identical self-attention outputs without positional information.

Positional encoding injects position information into the embeddings before self-attention. The position signal becomes part of the Q, K, V projections. The model can then learn to use position differences when computing attention scores.

Additionally, relative positional encodings (used in Transformer-XL, T5) directly modify the attention score by adding a learned position bias: score(i, j) = Q_i · K_j + b(i-j), where b is a learned scalar for each relative distance. This is more flexible than absolute positional encoding.

---

**Q9. What patterns do self-attention heads typically learn in practice?**

Research analyzing BERT's attention heads found several interpretable patterns:

- **Syntactic heads:** some heads track grammatical relationships — subject to verb, noun to its article
- **Positional heads:** some heads mostly attend to adjacent positions (acting like local convolutions)
- **Coreference heads:** some heads link pronouns to their antecedents ("it" → "the animal")
- **Separator heads:** in BERT, some heads attend heavily to the [CLS] or [SEP] tokens
- **Uniform heads:** some heads distribute attention nearly uniformly — acting as "gather all information" aggregators

These patterns aren't explicitly programmed — they emerge from training. Different layers learn different levels of abstraction: lower layers tend to capture local/syntactic patterns, upper layers capture semantic relationships.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Walkthrough.md](./Math_Walkthrough.md) | Step-by-step math walkthrough |

⬅️ **Prev:** [02 Attention Mechanism](../02_Attention_Mechanism/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Multi-Head Attention](../04_Multi_Head_Attention/Theory.md)
