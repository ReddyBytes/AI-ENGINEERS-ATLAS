# Reasoning Models — Cheatsheet

## Model Comparison

| Model | Maker | Open Source | Thinking Visible | Best For | Approx Cost |
|---|---|---|---|---|---|
| o1 | OpenAI | No | Summary | Math, science, hard code | $15/$60 per M tokens |
| o3 | OpenAI | No | Summary | Best overall reasoning | Higher than o1 |
| o1-mini | OpenAI | No | Summary | Cheaper reasoning | $3/$12 per M tokens |
| DeepSeek-R1 | DeepSeek | Yes | Full CoT | Open source o1-level | API: cheap / Self-host: free |
| R1-Distill-7B | DeepSeek | Yes | Full CoT | Local inference | Free (Ollama) |
| Claude Extended Thinking | Anthropic | No | Streaming | Configurable budget, multimodal | ~3–5× standard cost |
| Gemini 2.0 Flash Thinking | Google | No | Partial | Fast, multimodal | Competitive |

---

## When to Use

```
Reasoning Model ✓               Standard Model ✓
────────────────────────────     ────────────────────────────
Multi-step math                  Summarization
Complex algorithm design         Simple Q&A
Logic puzzles / proofs           Translation
Scientific reasoning             Chatbots (latency matters)
Tricky debugging                 High-volume, cost-sensitive
Planning with constraints        Creative writing
```

---

## API Quick Reference

### Claude Extended Thinking
```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "..."}]
)
# Access thinking:
thinking_block = response.content[0]   # type="thinking"
answer_block = response.content[1]     # type="text"
```

### OpenAI o1
```python
response = client.chat.completions.create(
    model="o1-preview",
    messages=[{"role": "user", "content": "..."}]
    # No system prompt, no temperature on o1
)
```

### DeepSeek-R1 via Ollama
```bash
ollama pull deepseek-r1:7b
ollama run deepseek-r1:7b
```
```python
import ollama
response = ollama.chat(
    model="deepseek-r1:7b",
    messages=[{"role": "user", "content": "..."}]
)
# <think>...</think> tags contain the reasoning chain
```

---

## Thinking Budget Guide (Claude)

| Task Complexity | Recommended budget_tokens |
|---|---|
| Simple logic | 1,000–2,000 |
| Moderate math | 5,000–8,000 |
| Hard proofs / code | 10,000–15,000 |
| Very complex multi-step | 15,000–32,000 |

---

## Key Benchmarks

| Benchmark | What It Tests | o1 Score | GPT-4o Score |
|---|---|---|---|
| AIME 2024 | Competition math | 74% | 13% |
| MATH | Math word problems | 96% | 76% |
| SWE-bench | Real GitHub issues | 49% | 18% |
| HumanEval | Code generation | 92% | 88% |

---

## Golden Rules

- Set `max_tokens` high — reasoning models need space for both thinking + answer
- Budget for latency: 10–60s is normal, plan your UI accordingly
- o1 does NOT support: system prompts, temperature, top_p, streaming (on some versions)
- For local use: DeepSeek-R1-Distill-7B via Ollama handles many reasoning tasks
- Don't use for simple tasks — standard models are faster and cheaper
