# Tokens and Context Window — Interview Q&A

## Beginner

**Q1: What is a token? How is it different from a word?**

<details>
<summary>💡 Show Answer</summary>

A token is the atomic unit that language models process. It is produced by a Byte Pair Encoding (BPE) tokenizer — an algorithm that learns sub-word pieces from a training corpus by repeatedly merging the most frequent adjacent character pairs.

The result is that common words become a single token ("the", "is"), while rare or long words get split into multiple tokens ("extraordinarily" → 3 tokens). Numbers, punctuation, and code fragments also tokenize in non-obvious ways.

The practical implication: you cannot assume 1 word = 1 token. The rule of thumb for English text is 1 token ≈ 0.75 words (or 1 word ≈ 1.3 tokens). Always use the model's token counting API for precise measurement rather than estimating from word count.

</details>

---

**Q2: What is the context window and why does it matter to engineers?**

<details>
<summary>💡 Show Answer</summary>

The context window is the maximum number of tokens Claude can process in a single API call — covering both the input you send (system prompt + message history + user message) and the output Claude generates.

Current Claude models support 200,000 tokens (about 150,000 words or 500 pages).

Why it matters:
1. **Hard limit**: Exceed it and the API returns an error — no graceful degradation
2. **Cost**: You pay per token; a larger context directly increases cost
3. **Architecture driver**: Anything involving long documents, long conversations, or large agent state must be designed around this limit
4. **Quality**: Very long contexts can degrade model attention (lost in the middle problem)

The context window is arguably the most important operational constraint when building Claude applications.

</details>

---

**Q3: What does stop_reason: "max_tokens" mean and why is it dangerous?**

<details>
<summary>💡 Show Answer</summary>

It means Claude ran out of room to generate — it hit the `max_tokens` limit you set before it reached a natural stopping point. The response is truncated.

Why it's dangerous: it fails silently. If your code just takes Claude's output and processes it, you might get:
- Incomplete JSON (crashes your parser)
- A half-written code function
- A sentence cut mid-thought

How to handle it:
```python
response = client.messages.create(...)
if response.stop_reason == "max_tokens":
    # Handle truncation: retry with higher max_tokens,
    # or continue generation by appending the partial response
    pass
```

Always set max_tokens generously (at least 2x the expected output length) and check stop_reason in your response handling code.

</details>

---

## Intermediate

**Q4: How does BPE tokenization work and what are the engineering implications?**

<details>
<summary>💡 Show Answer</summary>

BPE (Byte Pair Encoding) starts with a character-level vocabulary and iteratively merges the most frequent adjacent token pair into a new token. After millions of merges on the training corpus, you get a vocabulary of ~100,000 subword pieces.

The algorithm:
1. Initialize vocabulary with all individual characters
2. Count frequency of all adjacent token pairs in the training corpus
3. Merge the most frequent pair into a new token
4. Repeat until vocabulary reaches target size

Engineering implications:

1. **Asymmetric tokenization**: The same text tokenizes differently depending on surrounding context (leading spaces become part of tokens)
2. **Code vs English**: Code tokenizes more efficiently for common patterns (keywords, operators) but less efficiently for arbitrary variable names
3. **Non-English**: Languages underrepresented in training data tokenize less efficiently (more tokens per character) — increasing cost for non-English use cases
4. **Precision tasks**: String matching tasks must account for the fact that "user" at word start vs middle may be different tokens
5. **Prompt optimization**: Rewording to use common words reduces token count and cost

</details>

---

**Q5: A user sends a document that's 350,000 words. How do you handle it with Claude's 200k token limit?**

<details>
<summary>💡 Show Answer</summary>

350,000 words ≈ 455,000 tokens — well over the 200k limit. Options:

**Option 1 — Chunking with summarization**: Split the document into 50k-token chunks. Process each chunk separately with prompts like "Summarize the key facts in this section." Then combine summaries and process the combined summary.

**Option 2 — Retrieval-Augmented Generation (RAG)**: Embed the document in a vector database. For each user query, retrieve the top-k most relevant chunks (typically 3–5 chunks totaling 5–10k tokens) and inject only those into Claude's context.

**Option 3 — Hierarchical processing**: Process the document in sections, maintain a running summary, and update it incrementally. Final answer is generated from the compressed summary.

The right choice depends on the task:
- Need to find specific facts? → RAG
- Need holistic synthesis of the whole document? → Chunking + summarization
- Need to track evolving narrative? → Hierarchical

</details>

---

**Q6: How does prompt caching work and when should you use it?**

<details>
<summary>💡 Show Answer</summary>

Prompt caching allows Claude to store the computed representations (KV cache) for a prefix of your prompt and reuse them across multiple API calls. Instead of re-processing the same system prompt or documents on every call, the cached portion is retrieved from storage.

How to use it (Anthropic API):
```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    system=[{
        "type": "text",
        "text": "You are an expert in...[2000 tokens of context]",
        "cache_control": {"type": "ephemeral"}
    }],
    messages=[...]
)
```

When to use it:
- System prompts with large context (documentation, rules, examples) that don't change
- Long system instructions that repeat across every call in an application
- RAG scenarios where the retrieved context is reused across multiple queries

Cost impact: Cached input tokens are billed at ~10% of normal input price. If your system prompt is 10,000 tokens and you make 1,000 calls per day, caching saves ~90% of the input cost for that portion.

</details>

---

## Advanced

**Q7: What is the "lost in the middle" problem and how does it affect production system design?**

<details>
<summary>💡 Show Answer</summary>

Research (Liu et al., 2023) demonstrated that LLMs retrieve information from the start and end of long contexts significantly better than from the middle. In retrieval tasks with 20 relevant documents, models performed best when the relevant document was first or last, and worst when it was in the middle.

The mechanism: transformer attention at inference time can be uneven for very long sequences. The beginning gets "primed" by positional encoding, the end is most recently processed, but middle content may receive less focused attention during generation.

Production design implications:

1. **Prompt ordering**: Put the most critical instructions in the system prompt (which comes first) and repeat key constraints at the end of the user message
2. **RAG ordering**: When injecting multiple retrieved chunks, put the most relevant chunk first, not last
3. **Long document analysis**: For tasks requiring synthesis of a long document, consider asking Claude to first identify all relevant sections (allowing it to scan the whole document) before synthesizing
4. **Multi-step processing**: For very long documents, intermediate summarization passes ensure no section's content is "lost" by being in the middle at final synthesis time

This is especially important for legal document analysis, medical record review, and other high-stakes applications where missing middle content is unacceptable.

</details>

---

**Q8: How do you accurately budget tokens for a production agent that has long-running conversations?**

<details>
<summary>💡 Show Answer</summary>

Token budgeting for agents requires tracking three pools:

1. **Fixed overhead**: System prompt + tool schemas. Measure once at startup.
2. **Growing history**: Each turn adds ~(user_message + assistant_response) tokens. Grows unboundedly.
3. **Dynamic context**: Retrieved documents, tool outputs injected per turn. Variable.

Strategy:

```python
class TokenBudget:
    def __init__(self, model, context_limit=200_000, max_output=4096):
        self.context_limit = context_limit
        self.max_output = max_output
        self.fixed_overhead = 0  # measure system prompt + tools
        self.history_tokens = 0
        
    def available(self):
        return self.context_limit - self.fixed_overhead - self.history_tokens - self.max_output
    
    def should_compress(self):
        return self.available() < 20_000  # compress when < 20k tokens remain
```

Compression strategies when budget is tight:
1. **Summarize oldest turns**: Replace old conversation turns with a summary
2. **Drop tool outputs**: Keep tool call schemas but remove verbose outputs
3. **Truncate retrieved context**: Reduce chunk count from 5 to 2
4. **Checkpoint and reset**: Save important state externally, start a new conversation with a compressed summary

The agent should proactively compress before hitting limits, not reactively after getting an error.

</details>

---

**Q9: How does the context window size affect transformer attention computation and memory?**

<details>
<summary>💡 Show Answer</summary>

The context window directly drives memory and compute costs in the transformer:

**Attention computation**: Standard self-attention is O(n²) in sequence length n. Processing a 200k token context in a single attention operation would require 200,000² = 40 billion attention scores per layer — prohibitively expensive.

In practice, modern models use:
- **Flash Attention**: A memory-efficient attention algorithm that reduces memory from O(n²) to O(n) by computing attention in tiles without materializing the full matrix
- **Sliding window attention**: Some layers only attend within a local window (e.g., 4096 tokens) to reduce cost
- **KV cache**: Stores previously computed keys/values, making each incremental generation step O(n) in memory rather than O(n²)

**Memory**: The KV cache grows linearly with context length. For a large model with 200k tokens:
- KV cache ≈ 2 × layers × heads × head_dim × seq_len × dtype_bytes
- For a 70B model: roughly 80–100 GB for 200k tokens — comparable to or exceeding model weights

This is why very long context inference is expensive and why cloud providers price 200k context calls higher than 8k context calls even at the same model tier.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Token counting code |

⬅️ **Prev:** [02 How Claude Generates Text](../02_How_Claude_Generates_Text/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Transformer Architecture](../04_Transformer_Architecture/Theory.md)
