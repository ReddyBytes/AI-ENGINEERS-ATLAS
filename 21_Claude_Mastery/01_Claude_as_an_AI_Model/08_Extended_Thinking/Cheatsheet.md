# Extended Thinking — Cheatsheet

**One-liner:** Extended thinking gives Claude a reasoning scratchpad of up to 100k tokens before generating its final response — dramatically improving accuracy on complex multi-step problems at the cost of higher latency and token price.

---

## Key terms

| Term | What it means |
|------|---------------|
| Extended thinking | Claude feature: dedicated reasoning phase before final response |
| Thinking tokens | Tokens used in the scratchpad — generated autoregressively but treated as internal |
| budget_tokens | Max tokens for thinking — set in the API request |
| Thinking block | The API response block containing reasoning text |
| Text block | The API response block containing the final answer |
| Chain-of-thought (CoT) | The general technique of explicit step-by-step reasoning |
| Streaming thinking | Receiving thinking tokens in real time via SSE |

---

## API parameters

```python
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",  # model must support thinking
    max_tokens=16000,                     # must cover thinking + response
    thinking={
        "type": "enabled",
        "budget_tokens": 10000            # max tokens for thinking phase
    },
    messages=[{"role": "user", "content": "..."}]
)

# Response structure
for block in response.content:
    if block.type == "thinking":
        thinking_text = block.thinking   # the reasoning scratchpad
    elif block.type == "text":
        answer = block.text              # the final response
```

---

## Budget sizing guide

| Task type | Recommended budget |
|-----------|-------------------|
| Simple reasoning | 1,000–2,000 |
| Moderate complexity (multi-step) | 3,000–8,000 |
| Hard math / algorithm design | 10,000–20,000 |
| Research synthesis / complex code | 20,000–50,000 |
| Hardest problems (competition math, PhDs) | 50,000–100,000 |

Minimum effective budget: ~1,024 tokens (below this, thinking doesn't engage meaningfully).

---

## Cost formula with thinking

```
Total cost = (input_tokens × input_rate)
           + (thinking_tokens + output_tokens) × output_rate

Thinking tokens are billed as OUTPUT tokens.
At Sonnet pricing ($15/M output):
  10k thinking tokens = $0.15 per call
  vs. standard 500-token response = $0.0075 per call
```

Extended thinking is typically 5–20x more expensive per call.

---

## When to use vs skip

| Use extended thinking | Skip extended thinking |
|-----------------------|------------------------|
| Multi-step math problems | Simple factual lookup |
| Complex code architecture | Creative writing |
| Ambiguous multi-constraint analysis | High-frequency API calls |
| When reasoning needs to be audited | Cost-sensitive pipelines |
| Competition-level problems | Latency-sensitive features |

---

## Key implementation notes

- `max_tokens` must be set to cover both thinking and response: `max_tokens = budget_tokens + expected_response`
- Check `stop_reason` as usual — thinking can hit max_tokens before completing
- Thinking text is only included if you access `block.thinking` — it's separate from the response
- The model may use fewer tokens than `budget_tokens` if it reaches a conclusion early
- Thinking content cannot be injected in prefilled assistant turns

---

## Golden rules

1. Extended thinking helps with complexity, not with knowledge — if the fact isn't in training, thinking won't find it
2. Set max_tokens generously — budget_tokens + expected output + 500 safety buffer
3. Always check stop_reason — truncated thinking produces incomplete reasoning
4. Don't display raw thinking to users without filtering — "trying wrong paths" can confuse
5. Reserve for problems where accuracy > cost — 10-20x price increase is significant at scale
6. Minimum 1,024 budget tokens — below this, the thinking phase doesn't meaningfully engage

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | API usage examples |

⬅️ **Prev:** [07 Constitutional AI](../07_Constitutional_AI/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Claude Model Families](../09_Claude_Model_Families/Theory.md)
