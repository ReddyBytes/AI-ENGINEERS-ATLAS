# Prompt Caching — Interview Q&A

## Beginner Questions

**Q1: What is prompt caching and what problem does it solve?**

<details>
<summary>💡 Show Answer</summary>

A: Prompt caching stores large, repeated portions of your API request (like system prompts or document context) on Anthropic's servers after the first call. Subsequent calls that use the same prefix read from the cache at 10% of the normal input token price. It solves the problem of paying full price for thousands of tokens that never change between calls — like a 2,000-token system prompt repeated on every request.

</details>

---

<br>

**Q2: How do you mark content for caching?**

<details>
<summary>💡 Show Answer</summary>

A: Add `"cache_control": {"type": "ephemeral"}` to the content block. For the system prompt, you must pass `system` as an array of content blocks (not a string). The marker must be on the last block of the prefix you want cached.

</details>

---

<br>

**Q3: How long does a cache entry last?**

<details>
<summary>💡 Show Answer</summary>

A: 5 minutes from the last access (TTL resets on each cache hit). If no request reads the cached prefix within 5 minutes, it expires and the next call must write to cache again at 1.25× cost. For high-traffic applications, the cache stays warm continuously. For low-traffic apps, you may frequently incur cache-miss costs.

</details>

---

<br>

**Q4: How do you know if caching is working?**

<details>
<summary>💡 Show Answer</summary>

A: Check the `usage` object in the response. On a cache write: `cache_creation_input_tokens` will be non-zero. On a cache read (hit): `cache_read_input_tokens` will be non-zero and `cache_creation_input_tokens` will be 0. If both are 0 even after multiple calls, the cache is not activating — check token count (must exceed minimum) and verify the prefix is identical across calls.

</details>

---

## Intermediate Questions

**Q5: What are the minimum token requirements for caching, and what happens if you're below the minimum?**

<details>
<summary>💡 Show Answer</summary>

A: For Claude Sonnet and Opus: 1,024 tokens minimum. For Claude Haiku: 2,048 tokens minimum. If your cacheable prefix is below the threshold, the `cache_control` marker is silently ignored — no error is raised, you just pay full input price. This is why you should always log `cache_creation_input_tokens` to verify caching actually activated.

</details>

---

<br>

**Q6: What are the three cacheable positions in a request, and which is most commonly used?**

<details>
<summary>💡 Show Answer</summary>

A: (1) `system` parameter — the most commonly cached position; system prompts are large, static, and identical across all calls for the same use case. (2) `tools` array — useful when you have many complex tool definitions (each tool definition costs tokens). (3) Earlier messages in the `messages` array — useful for document Q&A patterns where you load a document once and ask multiple questions. You can use up to 4 cache markers per request.

</details>

---

<br>

**Q7: Why can't you cache the current user message (the final message in the array)?**

<details>
<summary>💡 Show Answer</summary>

A: Caching works by computing a cache key from a prefix — everything up to and including the marked block. The cache key must be stable across calls. The current user message changes with every request (different user questions), so it cannot form part of a stable prefix. Caching is only useful for the static parts of the request that are identical across calls.

</details>

---

<br>

**Q8: What happens to cache efficiency if you inject the user's name into the system prompt?**

<details>
<summary>💡 Show Answer</summary>

A: Cache efficiency drops to near zero. The cache key is computed from the full prefix content. If the system prompt contains `"You are helping {user_name}..."`, every user has a different cache key — each generates a new cache write at 1.25× cost and zero cache reads. To preserve caching, keep the system prompt completely static. Put user-specific context in the user messages array, not in the cached prefix.

</details>

---

## Advanced Questions

**Q9: Design a document Q&A system that maximizes cache hit rate for multiple questions about the same document.**

<details>
<summary>💡 Show Answer</summary>

A: Architecture: (1) Send the document in the first user message as a content block with `cache_control`. (2) Add a brief assistant acknowledgment ("I've read the document."). (3) For each question, append a new user message with the question text. The request structure is: system (possibly cached) + doc message (cached) + ack + question (uncached). The cache key covers everything up to the doc block — all questions about the same document hit the cache. Measure: `cache_read_input_tokens` should equal the document length for all questions after the first. Implementation note: run all questions within 5 minutes of loading the document, or implement a "warm-up" call just before a batch.

</details>

---

<br>

**Q10: How do you calculate the ROI of prompt caching for a specific use case?**

<details>
<summary>💡 Show Answer</summary>

A: ROI formula: `savings = (cache_reads × uncached_cost) - (cache_writes × 1.25 × uncached_cost) - (cache_reads × 0.10 × uncached_cost)`. Simplified: for N requests with P cacheable tokens at $C per token: `savings = P × C × (N × (1 - 0.10) - 1 × 1.25) = P × C × (0.90N - 1.25)`. Break-even at N ≈ 1.4 reads. For 1,000 calls with 2,000 token system prompt at $3/MTok (Sonnet): `savings = 2000 × 0.000003 × (0.90×1000 - 1.25) = $0.006 × 898.75 ≈ $5.39` saved on $5.99 spent uncached — 90% cost reduction.

</details>

---

<br>

**Q11: How does prompt caching interact with streaming and tool use?**

<details>
<summary>💡 Show Answer</summary>

A: Prompt caching is orthogonal to streaming and tool use — all combinations work. For streaming: the cache is read/written on the initial request regardless of stream mode. Cache hits appear in `usage.cache_read_input_tokens` in the `message_start` SSE event. For tool use: tool definitions can be cached by marking the last tool with `cache_control`. On each tool loop iteration, the system prompt and tools are re-sent (and re-read from cache), but only the growing messages array is new. In a 10-iteration tool loop with a 2,000-token system prompt and 1,000-token tool definitions, caching saves 3,000 × 9 × 0.9 = 27,000 token equivalents per conversation.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Working code |

⬅️ **Prev:** [Prompt Engineering](../08_Prompt_Engineering/Interview_QA.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Batching](../10_Batching/Interview_QA.md)
