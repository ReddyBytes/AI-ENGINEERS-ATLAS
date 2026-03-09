# LLM Fundamentals — Cheatsheet

**One-liner:** An LLM is a neural network with billions of parameters, trained on trillions of words to predict text, that emerges with knowledge, reasoning, and language skills.

---

## Key terms

| Term | What it means |
|------|---------------|
| LLM | Large Language Model — a very large neural network for text |
| Parameter | A single trainable number inside the model (there are billions) |
| Token | The basic unit of text — roughly 3/4 of a word |
| Training data | All the text the model learned from |
| Pretraining | Initial training on massive text data (next-token prediction) |
| Base model | Raw pretrained model — not yet fine-tuned for chat |
| Chat model | Base model + instruction tuning + RLHF — gives helpful answers |
| Emergent capability | An ability that appears only at large scale, not designed in |
| Few-shot learning | Model follows examples given in the prompt |
| Open weights | Model weights are public (Llama) — vs closed source (GPT-4) |
| Parameters scale | More parameters = more capacity = usually better performance |
| Inference | Running the model to generate output (different from training) |

---

## Famous models at a glance

| Model | Creator | Open? | Notable for |
|-------|---------|-------|-------------|
| GPT-4 | OpenAI | No | Top benchmark scores, multimodal |
| Claude 3 | Anthropic | No | Long context, safety focus |
| Gemini Ultra | Google | No | Native multimodal (text/image/video) |
| Llama 3 | Meta | Yes (weights) | Run locally, huge community |
| Mistral 7B | Mistral | Yes | Small but punches above weight |
| Falcon | TII | Yes | Research-friendly open model |

---

## Parameter scale and what it buys you

| Size | Example models | What they can do |
|------|---------------|-----------------|
| ~1–7B | Llama 3 8B, Mistral 7B | Basic instruction following, simple Q&A |
| ~13–30B | Llama 2 13B | Better reasoning, code, longer tasks |
| ~70B | Llama 3 70B | Near GPT-3.5 quality, complex tasks |
| ~175B+ | GPT-3 scale | Few-shot, complex coding, expert knowledge |
| ~1T (est) | GPT-4 scale | Multi-step reasoning, exam-passing ability |

---

## When to use what

**Use a large frontier model (GPT-4, Claude 3 Opus) when:**
- Quality is critical
- Task is complex or novel
- You need strong reasoning

**Use a mid-size model (Claude Haiku, GPT-3.5, Llama 70B) when:**
- Cost and speed matter
- Task is well-defined and simpler

**Use an open-weight model (Llama, Mistral) when:**
- Data privacy is required (runs locally)
- You want to fine-tune without API restrictions
- You're doing research

---

## When NOT to use an LLM

- You need 100% factual accuracy (hallucination risk)
- You need deterministic, exact outputs (use a real database or calculator)
- The task is simple pattern matching or lookup (overkill and expensive)
- Real-time requirements under 50ms (inference takes time)

---

## Golden rules

1. Bigger model != always better — match model size to task complexity
2. Base model != chat model. Never deploy a raw base model for user interaction
3. Emergent abilities are real — something that fails at 7B might work at 70B
4. LLMs predict text — they do not "know" things the way a database does
5. Tokens are the unit of cost — understand them to manage API expenses
6. Open weights = you control it. Closed API = someone else controls it

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Timeline.md](./Timeline.md) | Historical timeline of LLMs |

⬅️ **Prev:** [10 Vision Transformers](../../06_Transformers/10_Vision_Transformers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 How LLMs Generate Text](../02_How_LLMs_Generate_Text/Theory.md)
