# Fine-Tuning — Cheatsheet

**One-liner:** Fine-tuning continues training a pretrained model on a smaller, task-specific dataset to specialize its behavior — LoRA/QLoRA makes this affordable without full compute.

---

## Key terms

| Term | What it means |
|------|---------------|
| Fine-tuning | Continued training of a pretrained model on task-specific data |
| SFT (Supervised Fine-Tuning) | Fine-tuning on (input, output) example pairs |
| Instruction tuning | SFT with (instruction, response) format to teach instruction-following |
| Domain adaptation | Fine-tuning on domain-specific text (medical, legal, code) |
| Full fine-tuning | Update all model parameters — best quality, most expensive |
| LoRA | Low-Rank Adaptation — add small trainable matrices, freeze base model |
| QLoRA | LoRA + 4-bit quantization of the base model — runs on consumer GPUs |
| Rank (r) | LoRA hyperparameter — controls adapter size (typically 4–64) |
| Adapter | Small pluggable module added to a model for task-specific training |
| Catastrophic forgetting | Fine-tuning degrades base knowledge — mitigated by mixing data |
| PEFT | Parameter-Efficient Fine-Tuning — umbrella term for LoRA, adapters, etc. |
| HuggingFace Trainer | Python API for fine-tuning transformer models |
| Learning rate | Typically 1e-4 to 2e-4 for LoRA; smaller for full fine-tuning (2e-5) |

---

## Fine-tuning methods compared

| Method | Trainable params | GPU needed | Quality | Use when |
|--------|-----------------|-----------|---------|----------|
| Full fine-tuning | 100% | 8× A100 80GB+ | Best | You have compute + large dataset |
| LoRA (r=16) | ~0.5–1% | 1× A100 40GB | Very good | Most production cases |
| QLoRA (r=16) | ~0.5–1% | 1× consumer GPU | Good | Budget, single GPU setup |
| Adapter layers | ~1–3% | 1–2× A100 | Good | When you need modular swapping |
| Prompt tuning | ~0.01% | Small GPU | Moderate | Very low resource scenarios |

---

## LoRA hyperparameters

| Parameter | What it does | Typical values |
|-----------|-------------|---------------|
| r (rank) | Size of adapters — higher = more expressive | 4, 8, 16, 32, 64 |
| alpha | Scaling factor (usually set to 2×r) | 8, 16, 32, 64 |
| dropout | Regularization on adapters | 0.0 – 0.1 |
| target_modules | Which layers to apply LoRA to | q_proj, v_proj (attention) |
| bias | Whether to train bias terms | "none" usually |

---

## Dataset format for SFT

**Standard instruction format (Alpaca style):**
```json
{
  "instruction": "Summarize the following text in one sentence.",
  "input": "The Eiffel Tower is a wrought-iron lattice tower...",
  "output": "The Eiffel Tower is a famous 330-meter iron structure in Paris built in 1889."
}
```

**Chat format (used by modern chat models):**
```json
[
  {"role": "system", "content": "You are a helpful assistant."},
  {"role": "user", "content": "What is the Eiffel Tower?"},
  {"role": "assistant", "content": "The Eiffel Tower is..."}
]
```

---

## How much data you need

| Goal | Min examples | Recommended |
|------|-------------|-------------|
| Style/format change | 100–500 | 1,000 |
| Domain Q&A | 1,000–5,000 | 10,000+ |
| Full chat fine-tune | 50,000+ | 100,000+ |

Quality >> quantity. 1,000 expert examples beat 50,000 low-quality ones.

---

## When to fine-tune vs prompt engineer

Fine-tune when:
- Same task runs thousands of times (cost efficiency)
- Latency is critical (avoid long system prompts)
- Style must be consistent across all outputs
- You have 1,000+ high-quality examples
- Domain knowledge isn't in the base model

Prompt engineer when:
- Prototyping (move fast, iterate)
- Task definition changes frequently
- Data is scarce (fewer than 500 examples)
- Frontier model quality is required immediately
- No ML infra available

---

## Golden rules

1. Always start with prompting. Fine-tune only when prompting hits a wall.
2. Data quality > data quantity. Garbage in, garbage out — but at a higher cost.
3. Eval before you fine-tune. Establish a baseline so you know if fine-tuning helped.
4. LoRA first. Full fine-tuning rarely justifies the cost difference for most use cases.
5. Combine domain adaptation + instruction tuning for best domain-specific assistants.
6. Watch for catastrophic forgetting. If base model tasks degrade, mix in general data.
7. Fine-tuning doesn't fix hallucinations. Use RAG + grounding for factual accuracy.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 When_to_Use.md](./When_to_Use.md) | When to fine-tune vs other approaches |

⬅️ **Prev:** [03 Pretraining](../03_Pretraining/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Instruction Tuning](../05_Instruction_Tuning/Theory.md)
