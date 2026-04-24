# How LLMs Generate Text — Interview Q&A

## Beginner

**Q1: How does an LLM actually generate a response? Walk me through the steps.**

<details>
<summary>💡 Show Answer</summary>

When you send a prompt to an LLM, the following happens:

1. **Tokenization**: Your text is split into tokens (sub-word units). "Hello world" becomes ["Hello", " world"].
2. **Forward pass**: The tokens are fed into the transformer. The model runs attention and feed-forward layers across all of them.
3. **Logits output**: The model produces a score (logit) for every token in its vocabulary — typically 32,000–100,000 tokens.
4. **Softmax**: Logits are converted to probabilities. They all sum to 1.0.
5. **Sampling**: One token is selected based on those probabilities. This is where temperature and top-p come in.
6. **Append and repeat**: The selected token is appended to the context, and the whole process runs again to generate the next token.
7. **Stop**: This loop runs until the model outputs a special stop token, or until the maximum token limit is reached.

The key insight is that this is entirely sequential and autoregressive — each token depends on all previous tokens.

</details>

---

**Q2: What is temperature in an LLM? How would you explain it to someone non-technical?**

<details>
<summary>💡 Show Answer</summary>

Temperature is a dial that controls how "adventurous" the model is when picking the next word.

Imagine the model has a list of word options, each with a probability score. Temperature=0 always picks the most probable word — safe, predictable, boring. High temperature (like 1.0 or above) spreads out the probabilities so less likely words get picked more often — creative, surprising, sometimes incoherent.

Non-technical version: think of it like a chef following a recipe. Temperature=0 is the chef who follows the recipe exactly every time. Temperature=1 is the chef who might substitute ingredients, add unexpected spices, try something new — sometimes better, sometimes worse.

In practice: use low temperature for factual answers and code, high temperature for creative writing.

</details>

---

**Q3: What is the difference between top-p and top-k sampling?**

<details>
<summary>💡 Show Answer</summary>

Both are ways to limit which tokens the model can choose from during generation.

**Top-k**: Always keep exactly the k most probable tokens. If k=50, only the 50 highest-probability tokens are candidates, regardless of their actual probability values.

Problem: If the model is very confident (top 3 tokens cover 99% of probability), you're still sampling from 50 tokens including very unlikely ones. If the model is very uncertain, you're limiting to 50 tokens even when there are 200 reasonable options.

**Top-p (nucleus sampling)**: Keep the smallest set of tokens whose cumulative probability reaches p. If p=0.9, you keep tokens until their probabilities sum to 0.9.

When the model is confident: maybe only 5 tokens reach 90% → narrow set.
When the model is uncertain: maybe 500 tokens are needed to reach 90% → wider set.

Top-p adapts to the model's confidence. This is why it's generally preferred over top-k.

</details>

---

## Intermediate

**Q4: Why is text generation autoregressive? Are there alternatives?**

<details>
<summary>💡 Show Answer</summary>

Text generation is autoregressive because each token depends on all previous tokens. You can't generate token 10 without having generated tokens 1–9, because the transformer's attention mechanism needs the full previous context to determine what comes next.

This makes generation inherently sequential — you cannot parallelize across tokens the way you can during training.

**Alternatives that have been explored:**

- **Non-autoregressive models**: Generate all tokens simultaneously, then refine. Much faster, but quality is significantly worse because tokens can't condition on each other properly.
- **Diffusion models for text**: Generate noisy text and denoise iteratively. Shows promise but hasn't matched autoregressive quality at scale yet.
- **Speculative decoding**: Use a small draft model to generate candidate tokens quickly, then verify/correct with the large model in parallel. This achieves the quality of the large model at something closer to the speed of the small one. Used in practice (e.g., by Google, Anthropic).

For now, autoregressive sampling remains dominant for high-quality text generation.

</details>

---

**Q5: What problems can arise from greedy decoding? Why don't models always use it?**

<details>
<summary>💡 Show Answer</summary>

Greedy decoding always picks the highest-probability token at each step. This sounds optimal, but it can lead to suboptimal overall sequences because:

1. **Repetition**: The model can get stuck in loops — "The cat sat on the mat. The cat sat on the mat. The cat..."
2. **Missing better paths**: A sequence that starts with a slightly less likely first token might lead to a much better overall sentence. Greedy decoding can't backtrack.
3. **Boring outputs**: It always picks "safe" words. The most probable next word after "The weather is" might be "nice" every time — technically correct but tedious.
4. **Disfluent summaries**: For long generations, always picking the locally best token doesn't guarantee globally coherent text.

**Beam search** is a middle ground — maintain k "beams" (candidate sequences) and explore multiple paths simultaneously, keeping the k highest-probability paths at each step. It's better than greedy but still deterministic and doesn't produce diverse outputs. It's used in older systems but mostly replaced by sampling-based methods in modern LLMs.

</details>

---

**Q6: How does the generation process scale in terms of compute? What is the KV cache?**

<details>
<summary>💡 Show Answer</summary>

Without optimization, generating text with a transformer is quadratic in context length. To generate token n, you need to compute attention over all n-1 previous tokens. As the context grows, each new token is slower to generate.

The **KV cache** is the key optimization:

During the forward pass, each attention layer computes Key and Value matrices for each token. For all previous tokens, these don't change between steps — only the new token creates new K and V entries.

The KV cache stores all previously computed Keys and Values. When generating the next token, you only compute K and V for that single new token and concatenate with the cache. This reduces the per-step computation dramatically — from O(n²) attention over all tokens to O(n) lookups.

Trade-off: KV cache uses memory proportional to context length × number of layers × model dimension. For very long contexts (100k+ tokens), KV cache memory can become the bottleneck, not compute.

</details>

---

## Advanced

**Q7: What is the "exposure bias" problem in autoregressive generation, and how does it affect model behavior?**

<details>
<summary>💡 Show Answer</summary>

Exposure bias is a training/inference mismatch problem.

During **training**, the model learns to predict the next token given the true previous tokens (teacher forcing). At every step, it sees the ground-truth tokens, not its own predictions.

During **inference**, the model sees its own generated tokens. If the model makes a mistake early in a sequence, subsequent tokens are conditioned on that mistake. The model was never trained to recover from its own errors.

This manifests as:
- Error accumulation: one wrong token can cascade into an increasingly incoherent continuation
- Over-confidence on common patterns and brittleness on edge cases
- The model can't "go back" — once it starts down a wrong path, it tends to stay there

**Mitigations:**
- **Scheduled sampling**: During training, with increasing probability, replace teacher-forced tokens with the model's own predictions. Trains it to handle its own outputs.
- **Chain-of-thought prompting**: Forces the model to reason step-by-step, reducing error accumulation by making intermediate steps explicit.
- **Self-consistency**: Sample multiple outputs and take a majority vote — errors don't all go in the same direction.
- **RLHF**: Trains on complete sequences evaluated holistically, reducing reliance on step-by-step teacher forcing.

</details>

---

**Q8: Explain speculative decoding. Why does it improve throughput without sacrificing quality?**

<details>
<summary>💡 Show Answer</summary>

Standard LLM decoding is bottlenecked by memory bandwidth: for each new token, you load all model weights from GPU memory (often terabytes/second). The actual computation per token is small, but weight loading dominates.

**Speculative decoding** works as follows:

1. A **draft model** (small, fast — e.g., 7B) generates k candidate tokens autoregressively (e.g., k=4 tokens)
2. The **target model** (large, accurate — e.g., 70B) runs a single forward pass over all k+1 tokens (original context + k draft tokens) in parallel — this is possible because the target model is doing verification, not generation
3. The target model checks each draft token:
   - If the target model agrees the token was likely: accept it
   - If the target model disagrees: reject it and resample from the target model's distribution at that position, discarding subsequent tokens
4. In the good case (draft model often right): you get k tokens at the cost of roughly 1 target model pass
5. In the bad case (draft model often wrong): no worse than generating 1 token normally

Throughput improves by ~2–3x in practice because modern hardware can run k+1 parallel verification for barely more cost than 1 token generation, while correct draft tokens are "free."

Quality is maintained because rejected tokens are always replaced by samples from the correct target distribution — the output is statistically identical to standard sampling from the target model.

</details>

---

**Q9: How does the model handle long contexts? What breaks down at very long context lengths?**

<details>
<summary>💡 Show Answer</summary>

Modern LLMs handle long contexts through several mechanisms, but challenges remain:

**Positional encoding**: Transformers need to know the position of each token. Original transformers used fixed sinusoidal encodings, which can't extrapolate beyond training length. Modern solutions:
- **RoPE (Rotary Position Embedding)**: Encodes position as rotation of attention vectors. Better extrapolation, used in Llama, Gemini.
- **ALiBi**: Adds a linear bias to attention scores based on distance. Extrapolates well.
- **Attention with Linear Biases / Sliding window**: Used in some models to handle infinite length.

**What breaks down at very long contexts:**

1. **Lost in the middle**: Research shows LLMs recall information at the start and end of very long contexts well but lose track of information in the middle. Performance degrades on tasks requiring middle-document comprehension.

2. **KV cache memory**: At 128k tokens with a large model, KV cache can require 100+ GB of GPU memory — more than the model weights themselves.

3. **Attention cost**: Even with efficient attention algorithms (Flash Attention, ring attention), processing 1M tokens in a single forward pass is expensive.

4. **Training distribution mismatch**: Models trained mostly on documents under 32k tokens may degrade unpredictably on 500k-token inputs even if positional encoding supports it.

**Practical solutions**:
- Chunk long documents and use RAG to retrieve relevant sections
- Use models specifically trained and tested at long context (Gemini 1.5, Claude 3 with 200k context)
- Summarize intermediate sections to compress context

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [01 LLM Fundamentals](../01_LLM_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Pretraining](../03_Pretraining/Theory.md)
