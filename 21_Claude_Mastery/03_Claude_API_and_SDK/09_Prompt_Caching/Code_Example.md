# Prompt Caching — Code Examples

## Example 1: Cache a system prompt — first call writes, subsequent reads

```python
import anthropic

client = anthropic.Anthropic()

# Large system prompt (must be > 1024 tokens for Sonnet caching)
SYSTEM_PROMPT = """You are a specialized financial analysis assistant with deep expertise in:
- Equity valuation (DCF, comparables, precedent transactions)
- Financial statement analysis (income statement, balance sheet, cash flow)
- Risk assessment (market, credit, operational, liquidity)
- Investment thesis construction and critique

Always cite your reasoning. Use industry-standard terminology.
When analyzing numbers, show key ratios and benchmarks.
""" + ("This assistant knows comprehensive financial modeling frameworks. " * 50)  
# Padding to exceed 1024 token minimum

def analyze_financial(query: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"}  # mark for caching
            }
        ],
        messages=[{"role": "user", "content": query}]
    )
    
    return {
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "cache_created": response.usage.cache_creation_input_tokens,
        "cache_read": response.usage.cache_read_input_tokens,
        "output_tokens": response.usage.output_tokens,
    }

# Call 1 — writes cache
r1 = analyze_financial("What is P/E ratio and how is it used?")
print(f"Call 1 — cache created: {r1['cache_created']} tokens")

# Call 2 (within 5 min) — reads cache
r2 = analyze_financial("Explain EBITDA margin.")
print(f"Call 2 — cache read: {r2['cache_read']} tokens")
print(f"Answer: {r2['text'][:200]}")
```

---

## Example 2: Cache tools array

```python
import anthropic

client = anthropic.Anthropic()

# Many complex tools — expensive to resend every call
tools = [
    {
        "name": "get_stock_price",
        "description": "Get current stock price for a ticker symbol.",
        "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}
    },
    {
        "name": "get_financials",
        "description": "Get annual financial statements for a company.",
        "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}, "year": {"type": "integer"}}, "required": ["ticker"]}
    },
    {
        "name": "calculate_ratio",
        "description": "Calculate a financial ratio from two values.",
        "input_schema": {
            "type": "object",
            "properties": {
                "numerator": {"type": "number"},
                "denominator": {"type": "number"},
                "ratio_name": {"type": "string"}
            },
            "required": ["numerator", "denominator", "ratio_name"]
        },
        # Cache up to and including this final tool
        "cache_control": {"type": "ephemeral"}
    }
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What is Apple's P/E ratio?"}]
)
print(f"Cache created: {response.usage.cache_creation_input_tokens}")
```

---

## Example 3: Document Q&A with cached document

```python
import anthropic

client = anthropic.Anthropic()

DOCUMENT = """
Annual Report 2024 — AcmeCorp

Executive Summary:
Revenue for FY2024 reached $4.2B, up 23% year-over-year...
""" + ("Detailed financial data, product performance metrics, and strategic initiatives. " * 150)

questions = [
    "What was the revenue growth rate?",
    "What are the main strategic initiatives?",
    "What risks does the company face?",
    "How did product performance change year over year?",
]

def ask_about_document(question: str, is_first_call: bool) -> dict:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Here is the annual report to analyze:"},
                {
                    "type": "text",
                    "text": DOCUMENT,
                    "cache_control": {"type": "ephemeral"}  # cache the document
                }
            ]
        },
        {"role": "assistant", "content": "I've read the annual report. What would you like to know?"},
        {"role": "user", "content": question}
    ]
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=messages
    )
    
    return {
        "answer": response.content[0].text,
        "cache_created": response.usage.cache_creation_input_tokens,
        "cache_read": response.usage.cache_read_input_tokens,
    }

# Ask all questions — document cached after first call
for i, q in enumerate(questions, 1):
    result = ask_about_document(q, is_first_call=(i==1))
    cache_info = f"(wrote {result['cache_created']})" if result['cache_created'] else f"(read {result['cache_read']})"
    print(f"Q{i} {cache_info}: {result['answer'][:80]}...")
```

---

## Example 4: Monitor cache performance

```python
import anthropic
from dataclasses import dataclass, field
from typing import List

client = anthropic.Anthropic()

@dataclass
class CacheStats:
    calls: int = 0
    cache_writes: int = 0
    cache_reads: int = 0
    total_input_tokens: int = 0
    
    def record(self, usage):
        self.calls += 1
        self.cache_writes += usage.cache_creation_input_tokens
        self.cache_reads += usage.cache_read_input_tokens
        self.total_input_tokens += usage.input_tokens
    
    def report(self):
        total_cached = self.cache_writes + self.cache_reads
        hit_rate = self.cache_reads / total_cached if total_cached > 0 else 0
        print(f"Calls: {self.calls}")
        print(f"Cache writes: {self.cache_writes} tokens")
        print(f"Cache reads: {self.cache_reads} tokens")
        print(f"Cache hit rate: {hit_rate:.1%}")
        
        # Cost estimate (Sonnet pricing example)
        input_price = 3.0 / 1_000_000  # $3 per MTok
        without_cache = (self.cache_writes + self.cache_reads) * self.calls * input_price
        with_cache = (self.cache_writes * 1.25 + self.cache_reads * 0.10 + self.total_input_tokens) * input_price
        print(f"Estimated savings: ${without_cache - with_cache:.4f}")

stats = CacheStats()

SYSTEM = "You are a helpful assistant. " + "This is additional context. " * 100  # >1024 tokens

for i in range(10):
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=128,
        system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": f"Question {i}: What is {i} + {i}?"}]
    )
    stats.record(resp.usage)

stats.report()
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full concept guide |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Prompt Engineering](../08_Prompt_Engineering/Code_Example.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Batching](../10_Batching/Code_Example.md)
