# What is Claude? — Cheatsheet

**One-liner:** Claude is Anthropic's family of safety-first large language models, available in three tiers (Haiku/Sonnet/Opus), built on transformers and trained with Constitutional AI to be helpful, harmless, and honest.

---

## Key terms

| Term | What it means |
|------|---------------|
| Claude | Anthropic's family of large language models |
| Anthropic | AI safety company that created Claude (founded 2021) |
| LLM | Large Language Model — neural network trained on massive text corpora |
| Haiku | Fastest, cheapest Claude tier — best for high-volume simple tasks |
| Sonnet | Balanced tier — best for most production workloads |
| Opus | Most capable Claude tier — best for complex reasoning |
| Constitutional AI | Anthropic's alignment method: self-critique guided by a principle set |
| RLHF | Reinforcement Learning from Human Feedback — aligns model to preferences |
| Context window | Maximum tokens Claude can process in one request |
| Knowledge cutoff | Date after which Claude has no training data |
| System prompt | Instructions that shape Claude's behavior for an entire conversation |
| Hallucination | Generating plausible-sounding but factually wrong content |

---

## Model tiers quick reference

| Model | Best for | Context | Speed | Cost |
|-------|----------|---------|-------|------|
| claude-haiku-4-5 | Classification, routing, quick answers | 200k | Fastest | $ |
| claude-sonnet-4-6 | General development, agents, analysis | 200k | Fast | $$ |
| claude-opus-4 | Complex reasoning, research, hardest tasks | 200k | Slower | $$$$ |

---

## Claude vs other LLMs

| Dimension | Claude | GPT-4o | Gemini |
|-----------|--------|--------|--------|
| Maker | Anthropic | OpenAI (Microsoft) | Google |
| Alignment | Constitutional AI + RLHF | RLHF | RLHF + RLAIF |
| Max context | 200k tokens | 128k tokens | 1M tokens |
| Extended thinking | Yes | o1/o3 only | No |
| Safety focus | Core mission | Product feature | Product feature |

---

## Capabilities at a glance

| Category | What Claude can do |
|----------|-------------------|
| Writing | Drafting, editing, summarizing, translating |
| Reasoning | Multi-step logic, math, analysis |
| Code | Write, debug, explain, refactor (40+ languages) |
| Vision | Analyze images, read text from screenshots |
| Tools | Function calling, agent loops, MCP integration |
| Documents | Process PDFs, long reports, legal/technical docs |

---

## Known limitations

| Limitation | What it means in practice |
|------------|--------------------------|
| Knowledge cutoff | No events after training date — use search tools |
| Hallucination | Verify facts, citations, URLs independently |
| No real-time data | Cannot browse internet without tools |
| No persistent memory | Each session starts fresh — use memory systems |
| Not a calculator | Use code execution for precise math |

---

## Golden rules

1. Choose the right tier — don't pay for Opus when Haiku is sufficient
2. Always verify factual claims — Claude can hallucinate confidently
3. System prompts are your main control lever — use them well
4. Claude is not deterministic by default — same prompt can yield different outputs
5. The context window resets every session — build memory systems for continuity
6. Safety refusals are tunable — the system prompt can adjust within Anthropic's policies

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [Section README](../Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 How Claude Generates Text](../02_How_Claude_Generates_Text/Theory.md)
