# Multi-Head Attention — Interview Q&A

## Beginner

**Q1. What is multi-head attention and why do we need more than one head?**

Multi-head attention runs h separate attention operations on the same input in parallel. Each head has its own learned weight matrices W_Q, W_K, W_V. After each head computes its own attention output, all outputs are concatenated and projected through W_O.

We need multiple heads because a single attention distribution has to simultaneously represent many different relationships in language. One attention head might focus on subject-verb agreement, another on pronoun resolution, another on word proximity. One head can't do all of this at once without compromising. Multiple heads let each one specialize in a different aspect.

---

**Q2. How does multi-head attention relate to single-head attention?**

Multi-head attention is multiple single-head attention operations running in parallel on the same input. The difference is that each head uses different learned weight matrices, so each head can learn to focus on different patterns.

The final step concatenates all h head outputs (each of dimension d_k) into one vector of dimension d_model (since h × d_k = d_model), then applies a linear projection W_O. This projection learns to optimally combine the insights from all heads.

---

**Q3. What happens to the dimension per head as you add more heads?**

The per-head dimension is d_model / h. As you add more heads, each head gets a smaller slice of the total dimension to work with.

Example: d_model = 512, h = 8 → each head works with 64-dimensional Q/K/V vectors.

This design keeps the total computational cost roughly constant regardless of head count. You're not adding parameters by adding heads — you're subdividing the same total capacity into more specialized sub-tasks.

---

## Intermediate

**Q4. What do different attention heads learn in practice?**

Research analyzing trained BERT models shows that different heads specialize in different linguistic relationships:

- Some heads track syntactic relationships: subject-verb agreement, noun-determiner pairs
- Some heads perform coreference resolution: linking pronouns ("it", "she") to their antecedents
- Some heads attend mostly to adjacent positions, acting like local context windows
- Some heads attend heavily to special tokens like [CLS] and [SEP]
- Some heads capture semantic similarity across long distances

These specializations emerge from training, not from any explicit labeling. The model discovers that dividing the workload this way is the optimal strategy for the training objective.

---

**Q5. What is the W_O projection matrix and why is it important?**

W_O is the output projection applied after concatenating all head outputs.

After concatenation, you have a vector where different segments contain different types of information (syntax from head 1, coreference from head 2, etc.). W_O is a learned linear transformation that takes this concatenated vector and produces the final output.

Its role is to learn how to mix the different heads' contributions. Some downstream tasks may benefit from syntactic information more than semantic, or vice versa. W_O adapts this mixing. Without W_O, the different heads' outputs would just be stacked with equal weight — no learned combination.

---

**Q6. How does the number of attention heads affect model performance?**

More heads generally improves performance up to a point, then plateaus or even degrades. Research has shown:

- Too few heads: the model can't capture diverse relationship types simultaneously
- Optimal range: typically 8–16 heads for most sizes (BERT-base uses 12)
- Too many heads with fixed d_model: each head gets very few dimensions to work with (d_k = d_model / h becomes tiny), limiting each head's expressiveness

Studies on head pruning showed that many heads can be removed from trained models with minimal accuracy loss — suggesting significant redundancy. Some heads are genuinely useful; others learn redundant or weak patterns.

---

## Advanced

**Q7. What is grouped query attention (GQA) and why is it used in modern LLMs?**

In standard multi-head attention, each of the h heads has its own K and V matrices. This means storing h separate K/V caches during inference — expensive for large models.

Grouped query attention (GQA) divides the heads into groups. Each group shares one K/V pair, but each head within the group has its own Q. For example, 32 query heads might share 8 K/V pairs (4 queries per K/V group).

Benefits:
- Dramatically reduces KV cache memory (4× in the example above)
- Faster inference — fewer K/V computations
- Minimal quality loss compared to full multi-head attention

GQA is used in Llama 2/3, Mistral, Falcon, and most modern efficient LLMs. The extreme case (1 K/V pair for all heads) is called multi-query attention (MQA), which is even faster but sacrifices more quality.

---

**Q8. Can you prune attention heads from a trained transformer without retraining?**

Yes, to a surprising degree. Research (Michel et al., 2019 "Are Sixteen Heads Really Better than One?") showed that:

- In BERT, most attention heads can be removed with less than 1% accuracy drop on downstream tasks
- A small number of "important" heads account for most of the model's performance
- The important heads differ by task — different tasks rely on different head specializations

Methods:
- Compute importance scores (gradient-based, or ablation-based)
- Remove heads below the threshold
- Optional: fine-tune after pruning to recover accuracy

Pruning heads reduces inference cost proportionally — if you remove half the heads, attention computation is roughly halved.

---

**Q9. How does flash attention make multi-head attention faster without changing the math?**

Flash attention (Dao et al., 2022) is an algorithm optimization that computes the exact same multi-head attention output as the standard algorithm, but reorders operations to minimize slow memory reads/writes.

The standard algorithm:
1. Compute full Q K^T matrix in GPU global memory: O(n²) memory
2. Compute softmax row by row
3. Multiply by V

Flash attention uses tiling — processes small blocks of the Q K^T matrix that fit in fast SRAM (L2 cache), computing partial softmax values on the fly. Never materializes the full n×n attention matrix.

Results:
- 2–4× faster in practice for typical sequence lengths
- O(n) memory instead of O(n²) — enables much longer sequences
- Exact same mathematical output — no approximation

Flash attention is now the default implementation in PyTorch and HuggingFace transformers.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [03 Self Attention](../03_Self_Attention/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Positional Encoding](../05_Positional_Encoding/Theory.md)
