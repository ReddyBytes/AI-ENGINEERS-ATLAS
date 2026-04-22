# How Claude Generates Text — Cheatsheet

**One-liner:** Claude generates text by repeatedly sampling the next token from a probability distribution over its vocabulary, shaped by temperature and top-p parameters, until a stop condition is met.

---

## Key terms

| Term | What it means |
|------|---------------|
| Autoregressive | Each token depends on all previous tokens |
| Token | Sub-word unit; the atomic unit of generation |
| Logit | Raw score output by the transformer for each vocabulary token |
| Softmax | Converts logits to probabilities (sum to 1.0) |
| Temperature | Sharpens (low) or flattens (high) the probability distribution |
| Greedy decoding | Always pick the highest-probability token (temperature=0) |
| Sampling | Pick token randomly according to probabilities |
| Top-p (nucleus) | Keep smallest token set with cumulative probability ≥ p |
| Top-k | Keep top k tokens by probability |
| Stop sequence | String that terminates generation when produced |
| KV cache | Cached key/value pairs from previous tokens — avoids recomputation |
| Max tokens | Hard limit on output length |

---

## Generation loop in pseudocode

```
tokens = tokenize(prompt)
while not done:
    logits = transformer.forward(tokens)       # shape: [vocab_size ~100k]
    logits = logits / temperature              # apply temperature
    probs = softmax(logits)                    # convert to probabilities
    probs = apply_top_p(probs, p=0.9)          # filter to nucleus
    next_token = sample(probs)                 # pick one token
    tokens.append(next_token)
    if next_token in stop_tokens or len(tokens) >= max_tokens:
        break
return detokenize(tokens[prompt_length:])
```

---

## Temperature quick reference

| Temperature | Effect | Use when |
|-------------|--------|----------|
| 0 | Deterministic greedy | Structured output, code, reproducible results |
| 0.1–0.3 | Very focused | JSON extraction, factual Q&A |
| 0.5–0.7 | Balanced | General chat, analysis, explanation |
| 0.8–1.0 | Creative and varied | Brainstorming, creative writing |
| > 1.0 | Chaotic | Experimental only |

---

## Sampling strategies compared

| Strategy | How | Pros | Cons |
|----------|-----|------|------|
| Greedy | argmax(probs) | Deterministic, fast | Repetitive, misses good paths |
| Pure sampling | Random from full distribution | Most diverse | Incoherent at high temp |
| Top-k | Keep top k tokens | Caps randomness | Fixed k is context-insensitive |
| Top-p (nucleus) | Keep min set summing to p | Adapts to confidence | Slightly complex |
| Top-p + temperature | Combined | Best of both | Two params to tune |

---

## Softmax formula

```
P(token_i) = exp(z_i / T) / Σ exp(z_j / T)
```

Where `z_i` is the logit for token i and T is temperature.

- T → 0: probability concentrates on highest logit (greedy)
- T = 1: standard softmax
- T → ∞: all tokens equally likely (uniform distribution)

---

## Stop sequences — when to use them

| Stop sequence | Use case |
|---------------|----------|
| `</answer>` | Extract content inside XML tags |
| `\n\n` | Get one paragraph only |
| `User:` | Prevent model from simulating user turns |
| `###` | Stop at markdown header boundary |
| `DONE` | Explicit signal the model should emit when finished |

---

## Golden rules

1. Generation is one token at a time — no skipping ahead
2. temperature=0 gives deterministic output; temperature>0 is stochastic
3. Top-p is preferred over top-k — it adapts to model confidence
4. Temperature reshapes logits BEFORE softmax; top-p filters AFTER softmax
5. Every token costs money and time — keep max_tokens tight for production
6. The KV cache is why sequential generation doesn't scale quadratically in practice
7. Stop sequences are not guaranteed — max_tokens may fire first

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Visual_Guide.md](./Visual_Guide.md) | Step-by-step diagrams |

⬅️ **Prev:** [01 What is Claude](../01_What_is_Claude/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Tokens and Context Window](../03_Tokens_and_Context_Window/Theory.md)
