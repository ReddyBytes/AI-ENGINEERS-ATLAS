# How LLMs Generate Text — Cheatsheet

**One-liner:** LLMs generate text by repeatedly predicting the next token using a probability distribution over the vocabulary, controlled by temperature and sampling strategy.

---

## Key terms

| Term | What it means |
|------|---------------|
| Token | Sub-word unit of text; ~0.75 words on average |
| Vocabulary | All possible tokens the model knows (~32k–100k) |
| Logit | Raw score output by the model for each vocabulary token |
| Softmax | Converts logits to probabilities (all sum to 1.0) |
| Greedy decoding | Always pick highest-probability token |
| Sampling | Pick token randomly according to probabilities |
| Temperature | Scalar that sharpens (low) or flattens (high) the distribution |
| Top-p (nucleus) | Keep smallest set of tokens with cumulative probability ≥ p |
| Top-k | Keep only the top k most probable tokens |
| Stop token | Special token that signals the model to stop generating |
| KV cache | Cached key/value pairs from previous tokens to speed up generation |
| Autoregressive | Generating one token at a time, each conditioned on all previous tokens |

---

## Temperature quick reference

| Temperature | Effect | Use when |
|-------------|--------|----------|
| 0 | Deterministic (greedy) | Need exact, reproducible output |
| 0.1–0.3 | Very focused, predictable | JSON output, factual Q&A, code |
| 0.5–0.7 | Balanced | Most chat applications |
| 0.8–1.0 | Creative, varied | Brainstorming, creative writing |
| 1.2–2.0 | Wild, sometimes incoherent | Experimental, adversarial testing |

---

## Sampling strategies compared

| Strategy | How it works | Pros | Cons |
|----------|-------------|------|------|
| Greedy | Pick argmax(probability) | Fast, deterministic | Repetitive, misses good paths |
| Pure sampling | Sample from full distribution | Diverse | Can be incoherent at high temp |
| Top-k | Sample from top k tokens | Limits randomness | Fixed k is brittle |
| Top-p | Sample from min set summing to p | Adapts to confidence | Slightly more complex |
| Top-p + temperature | Combine both | Best of both worlds | Two params to tune |

---

## Token counting rules of thumb

| Text | Approximate tokens |
|------|--------------------|
| 1 word | ~1.3 tokens |
| 1 sentence | ~15–20 tokens |
| 1 paragraph | ~75–100 tokens |
| 1 page | ~400–500 tokens |
| 1,000 words | ~1,300 tokens |
| 1 novel (90k words) | ~120k tokens |

---

## Generation loop pseudocode

```
tokens = tokenize(prompt)
while not done:
    logits = model.forward(tokens)        # shape: [vocab_size]
    probs = softmax(logits / temperature) # apply temperature
    probs = apply_top_p(probs, p=0.9)    # filter to nucleus
    next_token = sample(probs)           # pick one token
    tokens.append(next_token)
    if next_token == STOP_TOKEN:
        break
return detokenize(tokens[len(prompt):])
```

---

## When to use what

**Use temperature=0 when:**
- Generating structured data (JSON, CSV)
- Writing code that must compile
- Factual answers where hallucination is risky
- Tests/evaluations that need reproducibility

**Use temperature=0.5–0.8 when:**
- General chat responses
- Explanation or summarization
- Customer service

**Use temperature=0.9–1.0 when:**
- Creative writing, poetry, stories
- Generating multiple diverse options
- Brainstorming sessions

---

## Golden rules

1. LLMs don't write text — they sample from a probability distribution, one token at a time
2. The same prompt can give different outputs. That's by design (unless temp=0)
3. Low temperature = safer but more boring. High temperature = creative but riskier
4. Top-p is better than top-k in most cases because it adapts to confidence
5. Tokens are not words — always count tokens, not words, when dealing with context limits
6. Every generated token increases the context for the next one — generation is O(n²) in naive form

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [01 LLM Fundamentals](../01_LLM_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Pretraining](../03_Pretraining/Theory.md)
