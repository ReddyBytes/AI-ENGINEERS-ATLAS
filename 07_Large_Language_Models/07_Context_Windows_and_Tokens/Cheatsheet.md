# Context Windows and Tokens — Cheatsheet

**One-liner:** A token is the basic unit of LLM text (~0.75 words), and the context window is the maximum tokens the model can process at once — setting the limit on what it can "see" and driving API costs.

---

## Key terms

| Term | What it means |
|------|---------------|
| Token | Sub-word unit of text; roughly 0.75 words or 4 characters |
| Context window | Maximum tokens processable in one forward pass (prompt + output combined) |
| Tokenizer | Algorithm that converts text → token IDs |
| BPE | Byte Pair Encoding — most common tokenization algorithm |
| Vocabulary | All valid tokens; typically 32k–128k entries |
| Input tokens | Tokens in your prompt (system + user messages) |
| Output tokens | Tokens the model generates |
| KV cache | Cached attention keys/values for previous tokens; speeds up generation |
| Positional encoding | How the model knows token order (RoPE, ALiBi, sinusoidal) |
| RoPE | Rotary Position Embedding — used in Llama, Gemini; better extrapolation |
| Context overflow | When conversation/input exceeds the context window limit |
| Lost in the middle | Models recall beginning/end of context better than middle |
| Sliding window | Strategy: drop oldest tokens when context fills up |
| Summarization buffer | Strategy: summarize old context to free up window space |

---

## Token count reference table

| Content | Approximate tokens |
|---------|-------------------|
| 1 average word | ~1.3 |
| 1 short sentence | ~15–20 |
| 1 paragraph (5 sentences) | ~75–100 |
| 1 page of text | ~400–500 |
| 1,000 words | ~1,300 |
| 10 pages | ~4,000–5,000 |
| A research paper (8 pages) | ~4,000 |
| A short story (5,000 words) | ~6,500 |
| A novel chapter | ~8,000–15,000 |
| A full novel (90k words) | ~120,000 |
| 1 hour of speech transcript | ~10,000 |
| A Python file (500 lines) | ~3,000–6,000 |

---

## Context window evolution

| Model | Context (tokens) | Equivalent text |
|-------|-----------------|-----------------|
| GPT-2 | 1,024 | ~2 pages |
| GPT-3 | 4,096 | ~8 pages |
| GPT-3.5 Turbo | 16,384 | ~33 pages |
| GPT-4 | 128,000 | ~256 pages |
| Claude 3 | 200,000 | ~400 pages |
| Gemini 1.5 Pro | 1,000,000 | ~2,000 pages |

---

## Positional encoding methods

| Method | Used by | Extrapolation | Notes |
|--------|---------|--------------|-------|
| Sinusoidal | Original Transformer | Poor | Can't go beyond training length |
| Learned absolute | BERT, early GPT | Poor | Fixed maximum length |
| RoPE | Llama, Gemini, Mistral | Good | Rotation-based; most widely used now |
| ALiBi | MPT, BLOOM | Good | Linear bias on attention; efficient |
| YaRN | Extended-context Llama | Very good | RoPE extension for 2x+ extrapolation |

---

## Context window management strategies

When your content is bigger than the context window:

| Strategy | How it works | Best for |
|----------|-------------|---------|
| Truncation | Drop oldest tokens | Simple chatbots |
| Sliding window | Keep most recent N tokens | Real-time chat |
| Summarization buffer | Compress old context with LLM | Long conversations |
| RAG | Retrieve only relevant chunks | Document Q&A |
| MapReduce | Split → process each part → combine | Document summarization |
| Hierarchical | Summarize sections → summarize summaries | Very long documents |

---

## API cost: how tokens work

```
Total cost = (input_tokens × input_price) + (output_tokens × output_price)

Example (Claude Sonnet, approximate 2024 pricing):
  Input:  $3.00 per million tokens
  Output: $15.00 per million tokens

A typical API call:
  System prompt: 500 tokens
  User message: 100 tokens
  Response: 200 tokens

  Input cost:  600 / 1M × $3.00  = $0.0018
  Output cost: 200 / 1M × $15.00 = $0.003
  Total: $0.0048 per call

  At 100,000 calls/day: $480/day
```

Output tokens cost 3–5x more than input tokens per million — generate concisely.

---

## KV cache memory reference

Approximate KV cache memory for a complete context:

| Model size | Tokens | KV cache memory (approx) |
|-----------|--------|--------------------------|
| 7B | 8k | ~1 GB |
| 7B | 128k | ~16 GB |
| 70B | 8k | ~8 GB |
| 70B | 128k | ~128 GB |
| 70B | 200k | ~200 GB |

For very long contexts, KV cache often exceeds model weight memory.

---

## Golden rules

1. Tokens ≠ words. Use a tokenizer to count — don't guess.
2. Context window = working memory. Once full, old content disappears.
3. KV cache is why long contexts are expensive. It's not just the attention math.
4. "Lost in the middle" is real. Put critical info at start or end of context.
5. Output tokens cost more than input tokens. Be concise in your generated outputs.
6. RAG is the answer to "I have 10x more data than my context window."
7. Bigger context window ≠ better recall. Attention degrades at extreme lengths.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [06 RLHF](../06_RLHF/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Hallucination and Alignment](../08_Hallucination_and_Alignment/Theory.md)
