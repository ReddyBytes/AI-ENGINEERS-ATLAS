# Tokens and Context Window — Cheatsheet

**One-liner:** A token is a sub-word BPE unit (~0.75 words in English); the context window is the maximum total tokens (input + output) Claude can process in one API call — currently 200k for all Claude models.

---

## Key terms

| Term | What it means |
|------|---------------|
| Token | Sub-word piece from BPE tokenizer; not a word |
| BPE | Byte Pair Encoding — algorithm that builds the token vocabulary |
| Vocabulary | All possible tokens the model knows (~100,000 for Claude) |
| Context window | Maximum input + output tokens for one API call |
| max_tokens | The limit you set on how long Claude's response can be |
| stop_reason: end_turn | Normal completion — EOS token generated |
| stop_reason: max_tokens | Output was truncated — increase max_tokens |
| Prompt caching | Store first N tokens of prompt to avoid re-processing cost |
| Lost in the middle | LLMs recall info at start/end of context better than middle |
| count_tokens | Anthropic API endpoint to count tokens without generating output |

---

## Token conversion rules of thumb

| Unit | Approx tokens |
|------|--------------|
| 1 word (English) | ~1.3 |
| 1 sentence | ~15–20 |
| 1 paragraph | ~75–100 |
| 1 page | ~400–500 |
| 1,000 words | ~1,300 |
| 10-page document | ~4,000 |
| 100-page document | ~40,000 |
| Novel (80k words) | ~107,000 |

Code, JSON, and non-English text tokenize differently — always measure with the API.

---

## Context window limits by model

| Model | Context Window | ~Words |
|-------|---------------|--------|
| claude-haiku-4-5 | 200,000 tokens | ~150,000 |
| claude-sonnet-4-6 | 200,000 tokens | ~150,000 |
| claude-opus-4 | 200,000 tokens | ~150,000 |

Context window = input tokens + output tokens combined.

---

## What happens at the limit

| Scenario | What happens | How to detect |
|----------|-------------|---------------|
| Input > context window | API error before any generation | Exception with error type |
| Generated tokens hit max_tokens | Output truncated silently | Check `stop_reason == "max_tokens"` |
| Normal completion | EOS token generated | `stop_reason == "end_turn"` |

---

## Token counting with the API

```python
# Count tokens without generating output
response = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    system="You are helpful.",
    messages=[{"role": "user", "content": "Your text here"}]
)
print(response.input_tokens)  # exact count
```

---

## Cost formula

```
cost = (input_tokens / 1_000_000) × input_rate
     + (output_tokens / 1_000_000) × output_rate

Approximate rates (mid-2025):
  Haiku:  $0.25 input / $1.25 output  (per million tokens)
  Sonnet: $3.00 input / $15.00 output
  Opus:   $15.00 input / $75.00 output
```

Output tokens are ~5x more expensive than input tokens on average.

---

## Tokenization quirks to know

| Quirk | Example |
|-------|---------|
| Leading space matters | "I" ≠ " I" (different tokens) |
| Long words split | "extraordinarily" → 3+ tokens |
| Numbers split | "2024-01-15" → 5+ tokens |
| Code patterns tokenize well | "def ", "import " are single tokens |
| Non-English is less efficient | CJK: often 2–3 tokens per character |
| JSON whitespace costs tokens | Compact JSON is cheaper than pretty-printed |

---

## Strategies for managing context

| Strategy | When to use |
|----------|------------|
| Chunking + RAG | Documents too large for one call |
| Conversation summarization | Long chat sessions — summarize old turns |
| Prompt caching | Static system prompts repeated across many calls |
| Model routing | Simple tasks to Haiku (smaller cost, same token count) |
| Truncation | Drop oldest messages when history approaches limit |
| max_tokens budgeting | Set tight limits on response length for structured tasks |

---

## Golden rules

1. Token ≠ word — measure with count_tokens, never guess
2. Context window = input + output, not just input
3. Always check `stop_reason` — "max_tokens" means truncated output
4. Output tokens cost ~5x input tokens — keep responses concise
5. Put critical information at the start AND end of long prompts (lost in the middle)
6. Use prompt caching for system prompts that repeat across many calls
7. Route simple tasks to Haiku — same token count, dramatically lower cost

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Token counting code |

⬅️ **Prev:** [02 How Claude Generates Text](../02_How_Claude_Generates_Text/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Transformer Architecture](../04_Transformer_Architecture/Theory.md)
