# LLM API Cost Guide

A practical guide to understanding, estimating, and reducing your LLM API costs.

---

## How token billing works

Every LLM API charges per token. You pay separately for:
- **Input tokens**: everything you send (system prompt + conversation history + user message)
- **Output tokens**: everything the model generates

Output tokens cost 3–5x more per token than input tokens because they require sequential compute (one forward pass per token).

```
Cost = (input_tokens × input_price / 1,000,000)
     + (output_tokens × output_price / 1,000,000)
```

Note: the prices below are approximate 2024 figures. **Always verify current pricing at the provider's pricing page.** Prices change frequently and typically trend downward.

---

## Approximate model pricing (2024)

### Anthropic Claude

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Good for |
|-------|----------------------|----------------------|---------|
| Claude 3.5 Haiku | ~$0.80 | ~$4.00 | Classification, extraction, simple tasks |
| Claude 3.5 Sonnet | ~$3.00 | ~$15.00 | Most production tasks |
| Claude 3 Opus | ~$15.00 | ~$75.00 | Complex reasoning, frontier quality |

### OpenAI GPT

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Good for |
|-------|----------------------|----------------------|---------|
| GPT-4o mini | ~$0.15 | ~$0.60 | Fast, cheap, good quality |
| GPT-4o | ~$2.50 | ~$10.00 | Multimodal, production tasks |
| GPT-4 Turbo | ~$10.00 | ~$30.00 | Complex reasoning |

### Google Gemini

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Good for |
|-------|----------------------|----------------------|---------|
| Gemini 1.5 Flash | ~$0.075 | ~$0.30 | Fastest, cheapest |
| Gemini 1.5 Pro | ~$1.25 | ~$5.00 | Long context, production |

**Important**: These are representative figures. Check current pricing before building cost models for your business.

---

## Real-world cost examples

### Example 1: Simple Q&A chatbot

```
User query: 50 tokens
System prompt: 200 tokens
Conversation history: 500 tokens (10 turns × 50 tokens avg)
Total input: 750 tokens

Response: 150 tokens output

Cost per call (Claude Sonnet):
  Input:  750 / 1M × $3.00  = $0.00225
  Output: 150 / 1M × $15.00 = $0.00225
  Total per call: ~$0.0045

At 10,000 calls/day:
  Daily cost: $45
  Monthly cost: $1,350
```

### Example 2: Document summarization

```
Document: 5,000 tokens (10-page report)
System prompt: 100 tokens
Total input: 5,100 tokens

Summary output: 400 tokens

Cost per document (Claude Sonnet):
  Input:  5,100 / 1M × $3.00  = $0.0153
  Output: 400 / 1M × $15.00   = $0.006
  Total per doc: ~$0.021

At 500 documents/day:
  Daily cost: $10.50
  Monthly cost: $315
```

### Example 3: Long context analysis (RAG with large context)

```
System prompt: 500 tokens
Retrieved documents: 50,000 tokens (large context RAG)
User question: 50 tokens
Total input: 50,550 tokens

Response: 500 tokens

Cost per call (Claude Sonnet, 200k context):
  Input:  50,550 / 1M × $3.00  = $0.1517
  Output: 500 / 1M × $15.00    = $0.0075
  Total per call: ~$0.16

At 1,000 calls/day:
  Daily cost: $160
  Monthly cost: $4,800
```

---

## Cost optimization techniques

### Technique 1: Use the right model size

The most impactful cost decision. Not all tasks need the most powerful model.

```python
def choose_model(task_type: str) -> str:
    """Select the appropriate model based on task complexity."""

    CHEAP_MODEL = "claude-3-5-haiku-20241022"      # ~19x cheaper than Opus
    STANDARD_MODEL = "claude-3-5-sonnet-20241022"   # Good balance
    PREMIUM_MODEL = "claude-3-opus-20240229"         # Best quality, highest cost

    simple_tasks = ["sentiment", "classification", "extraction", "translation"]
    complex_tasks = ["reasoning", "code_generation", "analysis", "research"]

    if task_type in simple_tasks:
        return CHEAP_MODEL
    elif task_type in complex_tasks:
        return PREMIUM_MODEL
    else:
        return STANDARD_MODEL
```

**Rule of thumb**: Start with Claude Haiku or GPT-4o mini. Upgrade only if quality is insufficient.

Switching from Claude Sonnet to Claude Haiku for simple classification: ~4x cost reduction. Often no quality loss for simple tasks.

### Technique 2: Set max_tokens precisely

```python
# Bad: wasteful max_tokens
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,  # Will never use 4096 for a yes/no question
    messages=[{"role": "user", "content": "Is Paris in France? Answer yes or no."}]
)

# Good: precise max_tokens
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=5,     # "Yes" is 1 token. Being generous with 5.
    messages=[{"role": "user", "content": "Is Paris in France? Answer yes or no."}]
)
```

For different task types:
```python
MAX_TOKENS_BY_TASK = {
    "yes_no": 10,
    "classification": 20,
    "single_sentence": 50,
    "short_answer": 150,
    "paragraph": 300,
    "explanation": 800,
    "analysis": 1500,
    "long_form": 4096,
}
```

### Technique 3: Compress your system prompt

Every character in your system prompt is paid for on every call. Optimize it.

```python
# Before: 312 tokens
VERBOSE_PROMPT = """
You are a helpful AI assistant designed to help users with their questions.
Your job is to provide accurate, thoughtful, and helpful responses to any
questions that users might have. You should always be polite, respectful,
and professional in your communications. When answering questions, try to
be as clear and concise as possible while still providing all the
necessary information that the user needs to understand the topic.
Please also make sure to acknowledge the user's question before providing
your answer, and end your responses with an offer to help further if needed.
"""

# After: 47 tokens (saved 265 tokens per call)
CONCISE_PROMPT = """You are a helpful assistant.
Be clear, accurate, and concise.
Acknowledge questions. Offer to help further."""

# At 100k calls/month:
# Tokens saved: 265 × 100,000 = 26.5M tokens
# Cost saved (Claude Sonnet): 26.5 × $3.00 = $79.50/month
```

### Technique 4: Prompt caching

For long prompts (system + context) repeated across many requests, caching reduces input costs by ~90%.

```python
import anthropic

client = anthropic.Anthropic()

# Add cache_control to mark the system prompt for caching
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=[{
        "type": "text",
        "text": """You are an expert assistant for Acme Corp.

[Very long company documentation — 3,000 tokens]
[Product specifications — 2,000 tokens]
[FAQ — 1,500 tokens]""",
        "cache_control": {"type": "ephemeral"}  # Mark for caching
    }],
    messages=[{"role": "user", "content": "What is our return policy?"}]
)

# First call: pays full input cost + small cache write cost
# Subsequent calls (within 5 min): pays ~10% of normal input cost for cached portion
print(f"Cache created: {response.usage.cache_creation_input_tokens}")
print(f"Cache read: {response.usage.cache_read_input_tokens}")
```

**Cost savings with caching:**
```
Without caching (10k calls, 6,500-token system prompt + docs):
  6,500 × 10,000 calls = 65M tokens × $3/M = $195

With caching:
  Cache write: 6,500 × 1 × ($3.75/M) = $0.024
  Cache reads: 6,500 × 9,999 × ($0.30/M) = $19.50
  Total: ~$19.52

Savings: ~90% ($175/day at this volume)
```

### Technique 5: Reduce conversation history size

Every turn in history costs input tokens on every subsequent call.

```python
def trim_conversation_history(
    history: list,
    max_tokens: int = 8000,
    chars_per_token: int = 4  # rough approximation
) -> list:
    """
    Keep only as much history as fits in the token budget.
    Removes oldest messages first.
    """
    max_chars = max_tokens * chars_per_token
    total_chars = sum(len(m["content"]) for m in history)

    if total_chars <= max_chars:
        return history  # No trimming needed

    # Remove from the beginning until we fit
    trimmed = history.copy()
    while sum(len(m["content"]) for m in trimmed) > max_chars:
        trimmed.pop(0)  # Remove oldest message

    return trimmed
```

Or use summarization (better context preservation):
```python
def summarize_and_compress(history: list) -> list:
    """Summarize old history to save tokens."""
    if len(history) <= 6:  # Keep recent 3 exchanges
        return history

    # Summarize everything except recent 4 messages
    old_messages = history[:-4]
    recent_messages = history[-4:]

    # Create summary using cheap model
    summary_text = summarize_with_llm(old_messages)

    # Replace old messages with compressed summary
    return [
        {"role": "user", "content": f"[Previous conversation summary: {summary_text}]"},
        {"role": "assistant", "content": "Understood."}
    ] + recent_messages
```

### Technique 6: Batch processing

For offline tasks (not user-facing), the Batch API is 50% cheaper.

```python
import anthropic

client = anthropic.Anthropic()

# Create a batch of requests (up to 10,000 per batch)
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"task_{i}",  # Your ID to match results
            "params": {
                "model": "claude-3-5-haiku-20241022",
                "max_tokens": 100,
                "messages": [{"role": "user", "content": f"Summarize: {text}"}]
            }
        }
        for i, text in enumerate(large_list_of_texts)
    ]
)

# Batch is processed asynchronously (typically within 24 hours)
# Results available via batch.id
print(f"Batch ID: {batch.id}")
print(f"Status: {batch.processing_status}")

# Check results later
results = client.messages.batches.results(batch.id)
for result in results:
    print(f"{result.custom_id}: {result.result.message.content[0].text}")
```

**Batch API savings**: 50% discount on all API costs. Ideal for:
- Data pipelines processing large document sets
- Overnight analytics jobs
- Training data generation
- Evaluation runs across thousands of test cases

### Technique 7: Use stop sequences

Stop generation early when you have enough output.

```python
# Extract a yes/no decision — stop after first line
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=200,
    stop_sequences=["\n"],  # Stop after the first line
    messages=[{
        "role": "user",
        "content": "Is the following review positive or negative? Answer on one line.\n\n" + review
    }]
)
# Output: "Positive" (stops at the newline, saves all subsequent tokens)
```

---

## Cost monitoring: track what you spend

```python
import json
from datetime import datetime, date
from pathlib import Path

class CostLogger:
    """
    Log API usage to a file for daily/monthly cost tracking.
    """

    def __init__(self, log_file: str = "api_costs.jsonl"):
        self.log_file = Path(log_file)

    def log_call(self, response, model: str, task: str = ""):
        """Log a single API call's cost."""

        # Approximate pricing (verify current prices)
        PRICES = {
            "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
            "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
            "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        }

        prices = PRICES.get(model, {"input": 3.00, "output": 15.00})

        input_cost = (response.usage.input_tokens / 1_000_000) * prices["input"]
        output_cost = (response.usage.output_tokens / 1_000_000) * prices["output"]

        record = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "task": task,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(input_cost + output_cost, 6),
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    def today_cost(self) -> float:
        """Sum today's costs."""
        today = date.today().isoformat()
        total = 0.0

        if self.log_file.exists():
            with open(self.log_file) as f:
                for line in f:
                    record = json.loads(line)
                    if record["timestamp"].startswith(today):
                        total += record["total_cost_usd"]

        return total

# Usage
logger = CostLogger()
response = client.messages.create(...)
logger.log_call(response, model="claude-3-5-sonnet-20241022", task="summarization")

print(f"Today's API cost so far: ${logger.today_cost():.4f}")
```

---

## Cost decision framework

```
Task requires:
  ├── Simple binary/category output? → Haiku ($0.80/$4.00 per M)
  ├── Factual extraction from text? → Haiku ($0.80/$4.00 per M)
  ├── Moderate reasoning + decent output? → Sonnet ($3.00/$15.00 per M)
  ├── Complex reasoning / writing? → Sonnet or Opus
  ├── Frontier quality required? → Opus ($15.00/$75.00 per M)
  └── Non-real-time, batch job? → Batch API (50% off any model)

Context is large (>10k tokens)?
  ├── Same prompt used many times? → Use prompt caching (90% reduction on cached portion)
  └── Can you reduce the context? → RAG / chunk and summarize

High request volume (>10k/day)?
  ├── Simple task → Switch to smallest model that works
  ├── Long system prompt → Implement prompt caching
  └── Long conversations → Trim/summarize history
```

---

## Monthly cost estimation template

```python
def estimate_monthly_cost(
    daily_requests: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    model: str = "claude-3-5-sonnet-20241022",
    cache_hit_rate: float = 0.0,
    cached_tokens: int = 0
) -> dict:
    """
    Estimate monthly API costs.

    Args:
        daily_requests: How many API calls per day
        avg_input_tokens: Average total input tokens per call
        avg_output_tokens: Average output tokens per call
        model: Model being used
        cache_hit_rate: Fraction of calls that use cached prompt (0.0-1.0)
        cached_tokens: How many input tokens are cached

    Returns:
        dict with cost breakdown
    """

    # Approximate pricing (verify current)
    MODEL_PRICES = {
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00, "cache_read": 0.08, "cache_write": 1.00},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00, "cache_read": 0.30, "cache_write": 3.75},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00, "cache_read": 1.50, "cache_write": 18.75},
    }

    prices = MODEL_PRICES.get(model, MODEL_PRICES["claude-3-5-sonnet-20241022"])
    monthly_requests = daily_requests * 30

    # Non-cached input tokens per request
    non_cached_input = avg_input_tokens - (cached_tokens * cache_hit_rate)

    monthly_input_tokens = monthly_requests * non_cached_input
    monthly_output_tokens = monthly_requests * avg_output_tokens
    monthly_cache_reads = monthly_requests * cache_hit_rate * cached_tokens

    input_cost = (monthly_input_tokens / 1_000_000) * prices["input"]
    output_cost = (monthly_output_tokens / 1_000_000) * prices["output"]
    cache_read_cost = (monthly_cache_reads / 1_000_000) * prices["cache_read"]

    return {
        "monthly_requests": monthly_requests,
        "model": model,
        "input_cost": round(input_cost, 2),
        "output_cost": round(output_cost, 2),
        "cache_savings": round(
            (monthly_cache_reads / 1_000_000) * (prices["input"] - prices["cache_read"]), 2
        ),
        "total_cost": round(input_cost + output_cost + cache_read_cost, 2)
    }


# Example estimation
estimate = estimate_monthly_cost(
    daily_requests=5000,
    avg_input_tokens=800,
    avg_output_tokens=300,
    model="claude-3-5-sonnet-20241022",
    cache_hit_rate=0.8,   # 80% of calls reuse cached system prompt
    cached_tokens=600     # 600 tokens in cached system prompt
)

print(f"Estimated monthly cost: ${estimate['total_cost']:.2f}")
print(f"  Input:  ${estimate['input_cost']:.2f}")
print(f"  Output: ${estimate['output_cost']:.2f}")
print(f"  Savings from caching: ${estimate['cache_savings']:.2f}")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Cookbook.md](./Code_Cookbook.md) | Code cookbook for LLM API calls |
| 📄 **Cost_Guide.md** | ← you are here |

⬅️ **Prev:** [08 Hallucination and Alignment](../08_Hallucination_and_Alignment/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Prompt Engineering](../../08_LLM_Applications/01_Prompt_Engineering/Theory.md)