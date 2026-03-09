# Instruction Tuning — Cheatsheet

**One-liner:** Instruction tuning is supervised fine-tuning on (instruction, response) pairs that transforms a text-completing base model into an assistant that follows user instructions.

---

## Key terms

| Term | What it means |
|------|---------------|
| Instruction tuning | SFT on (instruction, response) dataset to teach instruction following |
| Base model | Raw pretrained model — completes text, doesn't follow instructions |
| Chat model | Base model + instruction tuning (+ optionally RLHF) |
| SFT (Supervised Fine-Tuning) | Training on labeled (input, output) pairs |
| FLAN | Google's instruction tuning approach — 60+ tasks as natural language |
| Alpaca | Stanford's 52k instruction dataset generated via self-instruct from GPT-3.5 |
| InstructGPT | OpenAI's SFT + RLHF model — direct predecessor to ChatGPT |
| Self-instruct | Using an existing LLM to generate instruction training data for a smaller model |
| Zero-shot | Model performs a task without any examples (just the instruction) |
| Few-shot | Model follows task from a few examples in the prompt |
| Chat format | System/user/assistant role-based conversation format |
| Alpaca format | Instruction/input/output 3-field flat format |
| Task diversity | Training on many different task types generalizes better than depth in one |

---

## Dataset formats

**Alpaca (flat format):**
```json
{
  "instruction": "Classify the sentiment of this review as positive or negative.",
  "input": "This product broke after two days. Total waste of money.",
  "output": "Negative"
}
```

**Chat format (preferred for modern models):**
```json
[
  {"role": "system", "content": "You are a helpful assistant."},
  {"role": "user", "content": "Classify: This product broke after two days."},
  {"role": "assistant", "content": "Negative sentiment."}
]
```

---

## Key datasets at a glance

| Dataset | Size | Source | Notable for |
|---------|------|--------|-------------|
| FLAN | ~1M examples across 60+ tasks | Human annotated | First systematic instruction tuning |
| Alpaca | 52k | GPT-3.5 generated | Cheap self-instruct pipeline |
| ShareGPT | ~90k conversations | Real ChatGPT users | Real conversational style |
| Dolly (Databricks) | 15k | Human-written | Commercially licensed open data |
| Open Platypus | 25k | Curated from 11 datasets | High quality, deduplicated |
| FLAN-v2 | ~15M | Combined tasks + CoT | Best diversity, includes reasoning |

---

## Effect of instruction tuning on model behavior

| Before | After |
|--------|-------|
| Continues text | Answers questions directly |
| No structure | Uses headers, lists, formatting when appropriate |
| No role awareness | Maintains assistant persona |
| Ignores format hints | Follows format instructions (e.g., "give 5 bullet points") |
| May start with "Also..." | Starts with a direct response |

---

## What instruction tuning does NOT fix

- Hallucination (model still makes things up — needs RAG or RLHF)
- Safety (model may still produce harmful content — needs RLHF/Constitutional AI)
- Knowledge gaps (fine-tuning doesn't add new knowledge reliably)
- Context length (structural limit of the architecture)
- Reasoning depth (instruction tuning doesn't make reasoning better — that's RLHF + CoT)

---

## Self-instruct pipeline

```
1. Seed instructions (100 human-written examples)
       ↓
2. Prompt frontier model (GPT-4): "Generate 10 diverse instruction-response pairs"
       ↓
3. Quality filter (remove low quality, near-duplicates)
       ↓
4. Add to training set
       ↓
5. Fine-tune smaller open model on result
       ↓
6. Evaluate and iterate
```

Cost: ~$500–$5,000 to generate 50k–500k pairs via API. Much cheaper than human annotation.

---

## Golden rules

1. Diversity > quantity. 60 different task types beats 1 task type × 60,000 examples.
2. Instruction tuning is cheap compared to pretraining. 52k examples can meaningfully improve a 7B model.
3. Self-instruct works but the student can't exceed the teacher's quality ceiling.
4. Format matters. Models learn the format of good responses, not just the content.
5. The system prompt is where instruction tuning "shows up" in deployment — it calibrates the model to its trained behavior.
6. Instruction tuning without RLHF still produces a model that can say harmful things. Safety requires the RLHF step.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [04 Fine Tuning](../04_Fine_Tuning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 RLHF](../06_RLHF/Theory.md)
