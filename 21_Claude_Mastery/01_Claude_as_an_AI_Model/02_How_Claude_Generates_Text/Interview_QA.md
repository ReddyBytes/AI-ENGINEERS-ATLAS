# How Claude Generates Text — Interview Q&A

## Beginner

**Q1: How does Claude actually produce a response? Walk me through it step by step.**

<details>
<summary>💡 Show Answer</summary>

When you send a message, Claude does the following:

1. **Tokenize**: Your text is split into tokens (sub-word pieces). "Hello world" might become 2 tokens; "tokenization" might become 3.
2. **Forward pass**: All tokens are fed through the transformer. Billions of parameters run attention and feed-forward computations across every layer.
3. **Logits**: The final layer outputs one raw score (logit) per token in the vocabulary — Claude's vocabulary is ~100,000 tokens.
4. **Softmax + Temperature**: Logits are converted to probabilities. Temperature reshapes the distribution before softmax.
5. **Sampling**: One token is selected based on those probabilities (top-p nucleus sampling in practice).
6. **Append and repeat**: The selected token is added to the sequence. The forward pass runs again on the full sequence (with the KV cache speeding this up).
7. **Stop**: The loop ends when a stop token is generated, a stop sequence is matched, or max_tokens is hit.

The key insight: there is no planning ahead or rewriting — Claude commits to each token and moves on.

</details>

---

<br>

**Q2: What is temperature in an LLM? How does it affect output?**

<details>
<summary>💡 Show Answer</summary>

Temperature controls how "peaked" or "flat" the probability distribution is before sampling.

Mathematically: each logit is divided by temperature before softmax. This means:
- Low temperature (0.1): high-probability tokens become even more dominant; the model always picks safe, expected words
- Temperature = 1.0: standard behavior; probabilities match what the model learned
- High temperature (1.5): probabilities flatten out; surprising or unlikely tokens get more chances

Real-world intuition: think of a recipe recommendation system. At temperature=0 it always suggests pasta bolognese. At temperature=1.0 it picks from the top 10 recipes with realistic probabilities. At temperature=2.0 it might suggest mango-anchovy fusion or a recipe it barely learned.

For production: factual tasks use low temperature (0.1–0.3), creative tasks use higher (0.7–1.0).

</details>

---

<br>

**Q3: What is the difference between top-p and top-k sampling?**

<details>
<summary>💡 Show Answer</summary>

Both limit which tokens are candidates for the next selection.

**Top-k**: Keep exactly the k highest-probability tokens. If k=50, always 50 candidates — even when the model is highly confident or highly uncertain.

**Top-p (nucleus sampling)**: Keep the smallest set of tokens whose cumulative probability reaches p. When the model is confident, this might be 3 tokens. When uncertain, it might be 500 tokens.

Top-p is adaptive; top-k is fixed. This is why top-p is preferred — it lets the model's own confidence determine how many options are considered.

</details>

---

## Intermediate

**Q4: What is greedy decoding and why isn't it used for most production applications?**

<details>
<summary>💡 Show Answer</summary>

Greedy decoding always picks the highest-probability token at every step. It is deterministic and fast.

The problem: local optimality doesn't guarantee global optimality. Consider:
- "The best solution is to" — greedy might pick "use" next because it's most common
- But "refactor the existing architecture first" might be a better full continuation that starts with a lower-probability first token

Additionally, greedy decoding causes:
- Repetitive loops: "The cat sat on the mat. The cat sat on the mat..."
- "Safe" boring outputs that always take the expected path
- No diversity between runs — same input always gives same output

For most applications, sampling with moderate temperature and top-p gives better results. Greedy (temperature=0) is appropriate for structured outputs where you need exact reproducibility.

</details>

---

<br>

**Q5: How does the KV cache work and why is it important?**

<details>
<summary>💡 Show Answer</summary>

During the transformer forward pass, each attention layer computes three things for each token: a Query (Q), a Key (K), and a Value (V). Computing attention requires comparing the current token's Q against all previous tokens' K vectors, then weighing their V vectors.

Without caching: every new token generation would re-compute K and V for ALL previous tokens — O(n²) computation as context grows.

With KV cache: after computing K and V for each token, they are stored. On the next generation step, only the new token needs new K and V computed. All previous K and V are read from cache.

Why it matters:
- Makes generation roughly O(n) in practice instead of O(n²)
- Enables practical long-context inference
- The cache is stored in GPU VRAM — at 200k tokens with a large model, this can be tens of GB
- When context is full, older cache entries must be evicted (sliding window attention)

</details>

---

<br>

**Q6: What are stop sequences and how should you use them in production?**

<details>
<summary>💡 Show Answer</summary>

Stop sequences are strings that, when produced by the model, immediately terminate generation. You specify them in the API call.

Common uses:

1. **Structured extraction**: Set `stop_sequences=["</answer>"]` and your prompt asks Claude to write `<answer>...</answer>`. The stop sequence ensures you get clean content without the closing tag.

2. **One-shot responses**: Set `stop_sequences=["User:"]` so the model stops before it would simulate the next user turn in a dialogue format.

3. **Format enforcement**: For code generation, set stop after the closing fence (` ``` `) so you don't get extra text.

4. **Controlled length**: Set stop on `"\n\n"` for single-paragraph outputs.

Important caveat: if `max_tokens` is hit before the stop sequence appears, the sequence won't trigger. Always set max_tokens large enough that stop sequences reliably fire.

</details>

---

## Advanced

**Q7: Why is text generation autoregressive rather than parallel? What are the trade-offs?**

<details>
<summary>💡 Show Answer</summary>

Autoregressive generation (left-to-right, one token at a time) is standard because each token semantically depends on what came before. A transformer trained to condition token t on tokens 1..t-1 learns patterns that require that conditioning at inference time.

Trade-offs vs alternatives:

**Non-autoregressive (NAR) generation**: Generate all tokens simultaneously, then iteratively refine. Dramatically faster but significantly worse quality — tokens can't condition on each other, leading to repetition and incoherence. Used for simple tasks where speed > quality.

**Masked diffusion**: Apply diffusion to discrete tokens. Allows bidirectional context at generation time but is computationally expensive and still lags autoregressive quality at scale.

**Speculative decoding**: Keeps autoregressive quality while speeding up wall-clock time. A small draft model generates k candidate tokens; the large model verifies them all in one parallel forward pass. In the best case, k tokens are produced at the cost of ~1 target model pass. Throughput improvement: 2–3x in practice.

For Claude-scale models, autoregressive with speculative decoding is currently the practical optimum.

</details>

---

<br>

**Q8: How does temperature interact with top-p? Which is applied first?**

<details>
<summary>💡 Show Answer</summary>

The order of operations matters:

1. **Temperature** is applied first: divide all logits by temperature, then apply softmax. This reshapes the entire distribution — making it sharper or flatter.

2. **Top-p** is applied second: after computing the temperature-adjusted probabilities, sort tokens by probability, accumulate until cumulative probability ≥ p, then sample from only those tokens.

Why the order matters:
- If you apply top-p first on raw logits, the nucleus selection is based on raw scores, not probabilities — incorrect
- Temperature changes which tokens make it into the nucleus by changing the probability mass distribution

In practice, many frameworks apply them together: `logits / temperature → softmax → top-p filter → sample`. Setting temperature very low makes the nucleus very small (maybe 1 token) regardless of top-p, effectively making top-p irrelevant at temperature=0.

</details>

---

<br>

**Q9: What is the "exposure bias" problem and how does it affect Claude's generation quality?**

<details>
<summary>💡 Show Answer</summary>

Exposure bias is a train/inference mismatch.

During training: the model predicts token t given the true tokens at positions 1..t-1 (teacher forcing). It always sees ground truth.

During inference: the model generates token t given its own predictions at positions 1..t-1. If it made an error at position 5, it must now generate token 6 conditioned on a wrong token 5 — a situation it was never trained for.

Manifestations:
- Error accumulation in long generations: one wrong prediction cascades into increasingly incoherent text
- The model can't "recover" — it was never trained to recover from its own mistakes

Mitigations used:
- **RLHF**: Trains on complete rollouts evaluated holistically, partially closing the gap
- **Chain-of-thought prompting**: Forces explicit intermediate steps, reducing error propagation
- **Self-consistency**: Generate multiple completions and vote — errors don't correlate across samples
- **Scheduled sampling** (older technique): Occasionally substitute ground-truth tokens with model predictions during training

Extended thinking in Claude partially addresses this by making the reasoning explicit and checkable before the final answer.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Visual_Guide.md](./Visual_Guide.md) | Step-by-step diagrams |

⬅️ **Prev:** [01 What is Claude](../01_What_is_Claude/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Tokens and Context Window](../03_Tokens_and_Context_Window/Theory.md)
