# CAG — Cache-Augmented Generation Cheatsheet

## When to Use CAG vs RAG

| Use CAG when... | Use RAG when... |
|---|---|
| Document fits in context window (<500K tokens) | Knowledge base is too large for context (millions of tokens) |
| Many queries against the same document | Queries are against a large, diverse corpus |
| High accuracy needed (no retrieval misses) | Document updates frequently |
| Minimal infrastructure preferred | Multiple document sources |
| Long Q&A sessions on a single document | Complex multi-document retrieval needed |

**Break-even**: after ~2 queries on the same cached document, CAG is cheaper than re-processing.

---

## Anthropic Prompt Caching

```python
import anthropic

client = anthropic.Anthropic()
document_text = open("document.txt").read()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    system="Answer questions based on the provided document.",
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": document_text,
                "cache_control": {"type": "ephemeral"},   # ← mark for caching
            },
            {
                "type": "text",
                "text": "Your question here"
            }
        ]
    }]
)

# Check cache usage
usage = response.usage
print(f"Cache write: {usage.cache_creation_input_tokens}")   # first call: tokens stored
print(f"Cache read:  {usage.cache_read_input_tokens}")       # subsequent: tokens reused
print(f"New tokens:  {usage.input_tokens}")                  # question tokens (always charged)
```

**Pricing (Anthropic):**
| Token type | Cost |
|---|---|
| Normal input | $3.00 / MTok |
| Cache write | $3.75 / MTok (paid once) |
| **Cache read** | **$0.30 / MTok (90% off)** |
| Output | $15.00 / MTok |

---

## OpenAI Automatic Caching

```python
from openai import OpenAI

client = OpenAI()

# OpenAI caches automatically — no explicit opt-in needed
# Prefix must be ≥1024 tokens and reused verbatim
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.\n\nDocument:\n" + document_text
        },
        {"role": "user", "content": "What is clause 14?"}
    ]
)

# Check cached tokens
cached = response.usage.prompt_tokens_details.cached_tokens
total = response.usage.prompt_tokens
print(f"Cached: {cached} / {total} tokens ({100*cached/total:.0f}%)")
```

**OpenAI cache pricing**: cached tokens cost ~50% of normal input price (vs Anthropic's 10%).

---

## Reusable CAG Class

```python
import anthropic
from pathlib import Path

class CAGSystem:
    def __init__(self, document_path: str, system_prompt: str = None, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.document = Path(document_path).read_text()
        self.system = system_prompt or "Answer questions based only on the provided document."
        self.query_count = 0

    def ask(self, question: str, max_tokens: int = 1024) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self.document,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {"type": "text", "text": question}
                ]
            }]
        )
        self.query_count += 1
        return response.content[0].text

    def ask_stream(self, question: str):
        with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system=self.system,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": self.document,
                        "cache_control": {"type": "ephemeral"},
                    },
                    {"type": "text", "text": question}
                ]
            }]
        ) as stream:
            for text in stream.text_stream:
                yield text

# Usage
cag = CAGSystem("technical_spec.pdf.txt")
print(cag.ask("What is the maximum supported payload size?"))
print(cag.ask("What authentication methods are supported?"))  # cache hit
```

---

## Multi-Document CAG

```python
# Load multiple related documents into one context
documents = {
    "Contract": open("contract.txt").read(),
    "Appendix": open("appendix.txt").read(),
    "Amendments": open("amendments.txt").read(),
}

combined = "\n\n---\n\n".join(
    f"## {name}\n{text}" for name, text in documents.items()
)

# Total must fit in context window — check token count first
import anthropic
client = anthropic.Anthropic()
count = client.beta.messages.count_tokens(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": combined}]
)
print(f"Total tokens: {count.input_tokens}")   # must be < 200K for Claude
```

---

## Token Size Reference

| Content Type | Approx Tokens |
|---|---|
| 1 page of text (~500 words) | ~700 tokens |
| 10-page document | ~7,000 tokens |
| 50-page report | ~35,000 tokens |
| 400-page book | ~280,000 tokens |
| Software codebase (medium) | ~100K–500K tokens |

**Context window limits:**
| Model | Context Window |
|---|---|
| Claude Sonnet 4.6 | 200K tokens |
| Claude Opus 4.6 | 200K tokens |
| GPT-4o | 128K tokens |
| Gemini 1.5 Pro | 1M tokens |
| Gemini 1.5 Flash | 1M tokens |

---

## Cache Expiration Rules

| Provider | Cache Duration | Behavior on Expiry |
|---|---|---|
| **Anthropic** | 5 min of inactivity | Cache miss — pays full input price |
| **OpenAI** | ~1 hour (undocumented) | Automatic, no control |
| **Google** (Gemini) | Configurable TTL | Set expiry in API call |

---

## CAG vs RAG vs Long-Context (Summary)

```
APPROACH        INFRA NEEDED    BEST DOCUMENT SIZE    ACCURACY    COST PER QUERY
──────────────────────────────────────────────────────────────────────────────────
Standard RAG    Vector DB       Any size              Variable    Low (small context)
CAG             None            Fits in context       High        Low after cache
Long-context    None            Fits in context       High        High (full tokens)
GraphRAG        Graph DB        Any size              High+       High (LLM extraction)
```

---

## Golden Rules

1. Always check document token count before using CAG — use `client.beta.messages.count_tokens`
2. Keep the cache prefix identical across calls — any change in system prompt or document invalidates the cache
3. After 2+ queries on the same document, CAG is cheaper than re-processing each time
4. Anthropic cache expires after 5 minutes of inactivity — handle cache misses in long sessions
5. CAG is not a replacement for RAG on large corpora — it's a complement for focused, in-context knowledge sources
