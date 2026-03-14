# Benchmarks — Cheatsheet

## Quick Reference: Key Benchmarks

| Benchmark | Tests | Format | Key metric | Human baseline |
|-----------|-------|--------|-----------|---------------|
| **MMLU** | Knowledge across 57 subjects | Multiple choice (4 options) | Accuracy | ~88% (expert) |
| **HumanEval** | Python code generation | Generate function from docstring | pass@1 | ~80% (programmer) |
| **GSM8K** | Grade school math word problems | Free-form answer | Accuracy | ~100% |
| **MATH** | Competition math | Free-form answer | Accuracy | ~40% (olympiad student) |
| **BIG-Bench Hard** | 23 hard diverse tasks | Varies | Accuracy | Varies |
| **GPQA** | Graduate-level science | Multiple choice | Accuracy | ~65% (domain experts) |
| **HellaSwag** | Commonsense story completion | Multiple choice | Accuracy | ~95% |
| **TruthfulQA** | Avoiding false beliefs | Open-ended | % truthful | ~94% |
| **ARC** | Grade school science | Multiple choice | Accuracy | ~100% |
| **SWE-Bench** | Fix real GitHub issues | Code patches | % resolved | ~13% (junior dev) |
| **LMSYS Arena** | Open-ended quality | Elo from pairwise | Elo rating | — |

---

## Model Scores Reference (approximate, early 2025)

| Model | MMLU | HumanEval | GSM8K |
|-------|------|-----------|-------|
| GPT-4o | 88.7% | 90.2% | 95.8% |
| Claude 3.5 Sonnet | 88.3% | 92.0% | 96.4% |
| Claude 3 Opus | 86.8% | 84.9% | 95.0% |
| Gemini 1.5 Pro | 85.9% | 84.1% | 91.7% |
| Llama 3.1 70B | 86.0% | 80.5% | 95.1% |
| Mistral 7B | 64.2% | 30.5% | 52.2% |

_Scores vary by evaluation settings (few-shot, CoT, etc.). Always verify at source._

---

## Choosing a Benchmark

| If you need to measure... | Use |
|--------------------------|-----|
| General knowledge + reasoning | MMLU |
| Code generation | HumanEval, LiveCodeBench |
| Math (easy) | GSM8K |
| Math (hard) | MATH, AIME |
| Real engineering tasks | SWE-Bench |
| Broad capabilities | BIG-Bench Hard |
| Frontier model differentiation | GPQA, MMLU-Pro |
| Open-ended quality | LMSYS Arena Elo |
| Truthfulness | TruthfulQA |

---

## Evaluation Protocol Terms

| Term | Meaning |
|------|---------|
| **Zero-shot** | No examples in prompt |
| **Few-shot (k-shot)** | k examples before the question |
| **Chain-of-thought (CoT)** | Model reasons step-by-step before answering |
| **pass@1** | First attempt passes all tests |
| **pass@k** | At least 1 of k attempts passes |

---

## Warning Signs of Inflated Scores

- Model released without training data disclosure
- Score dramatically higher than similar-size models
- Only reports best-possible evaluation setting (5-shot CoT) without disclosure
- Doesn't compare to human baseline
- Benchmark is very similar to known training sources

---

## Golden Rules

1. Benchmarks are for model selection starting points, not final evaluation
2. Always compare at the same evaluation protocol (same few-shot setting, same CoT)
3. Your task-specific eval matters more than any benchmark
4. High scores on saturated benchmarks (GSM8K >95%) don't differentiate models
5. Use LMSYS Chatbot Arena Elo for open-ended quality comparisons

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Benchmark_Comparison.md](./Benchmark_Comparison.md) | All benchmarks comparison table |

⬅️ **Prev:** [01 — Evaluation Fundamentals](../01_Evaluation_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 — LLM as Judge](../03_LLM_as_Judge/Theory.md)
