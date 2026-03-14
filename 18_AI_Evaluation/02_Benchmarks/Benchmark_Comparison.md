# Major AI Benchmarks — Comparison Table

## Core LLM Benchmarks

| Benchmark | Year | Task type | Format | Primary metric | Dataset size | Human baseline | Status |
|-----------|------|-----------|--------|---------------|-------------|----------------|--------|
| **MMLU** | 2020 | Knowledge, 57 subjects | MCQ 4-way | Accuracy | 14,042 | ~88% (expert) | Widely used, partially saturated |
| **MMLU-Pro** | 2024 | Knowledge + harder reasoning | MCQ 10-way | Accuracy | 12,032 | ~75% | Active, harder variant |
| **HumanEval** | 2021 | Python code generation | Code generation | pass@1 | 164 problems | ~80% | Widely used, small |
| **HumanEval+** | 2023 | Code (more tests) | Code generation | pass@1 | 164 problems | ~80% | Better test coverage |
| **LiveCodeBench** | 2024 | Live coding problems | Code generation | pass@1 | Growing monthly | — | Contamination-resistant |
| **GSM8K** | 2021 | Grade school math | Free-form | Accuracy | 8,500 | ~100% | Saturated (>95% by top models) |
| **MATH** | 2021 | Competition math | Free-form | Accuracy | 12,500 | ~40% | Differentiates frontier models |
| **GPQA** | 2023 | Grad-level science (Phd) | MCQ 4-way | Accuracy | 448 | ~65% (domain experts) | Hard; good frontier differentiator |
| **HellaSwag** | 2019 | Commonsense reasoning | MCQ | Accuracy | 70,000 | ~95% | Saturated |
| **ARC** | 2018 | Grade school science | MCQ | Accuracy | 7,787 | ~100% | Saturated |
| **TruthfulQA** | 2021 | Avoiding false beliefs | Open-ended | % truthful | 817 | ~94% | Safety-relevant |
| **BIG-Bench Hard** | 2022 | 23 diverse hard tasks | Varies | Accuracy | ~5,000 | Varies | Good capability breadth |
| **WinoGrande** | 2019 | Commonsense pronoun resolution | MCQ | Accuracy | 44,000 | ~94% | Partially saturated |
| **PIQA** | 2019 | Physical intuition QA | MCQ | Accuracy | 16,000 | ~95% | Saturated |

---

## Code-Specific Benchmarks

| Benchmark | Tests | Languages | Key metric | Notes |
|-----------|-------|-----------|-----------|-------|
| **HumanEval** | Function completion | Python | pass@1 | 164 problems, widely used |
| **HumanEval+** | Function completion (more rigorous) | Python | pass@1 | More test cases per problem |
| **MBPP** | Simple Python programs from NL spec | Python | pass@1 | 374 problems |
| **LiveCodeBench** | New competitive programming problems | Python | pass@1 | Monthly updates, contamination-resistant |
| **SWE-Bench** | Real GitHub issue resolution | Python | % resolved | Closest to real engineering work |
| **SWE-Bench Verified** | Curated SWE-Bench subset | Python | % resolved | Subset with verified correct solutions |
| **DS-1000** | Data science code | Python (DS libs) | pass@1 | NumPy, pandas, matplotlib, etc. |
| **APPS** | Competitive programming | Python | pass@1 | 10,000 problems, hard |

---

## Math and Reasoning Benchmarks

| Benchmark | Difficulty | Format | Notes |
|-----------|-----------|--------|-------|
| **GSM8K** | Grade 1–6 | Free-form | Saturated. Chain-of-thought standard. |
| **MATH** | AMC competition | Free-form | 7 categories. Top models: ~50–80% |
| **AIME** | American Invitational Math Exam | Free-form | Very hard. Human specialists: ~30–70% |
| **Omni-Math** | Olympiad level | Free-form | Frontier differentiation |
| **MathVista** | Visual math | Image + text | Requires vision + reasoning |
| **FrontierMath** | Research-level math | Free-form | State-of-art models: <10% |

---

## Holistic / Multi-dimensional Benchmarks

| Benchmark | Dimensions | Notes |
|-----------|-----------|-------|
| **HELM** | 42 scenarios × 7 metrics | Accuracy, calibration, robustness, fairness, bias, toxicity, efficiency |
| **LMSYS Chatbot Arena** | Open-ended human preference | Elo from blind pairwise comparisons. Real users, real tasks. |
| **MT-Bench** | Multi-turn conversation quality | LLM-as-judge. 80 high-quality questions. 8 categories. |
| **AlpacaEval** | Instruction following | Win rate vs GPT-4 as reference. 805 instructions. |

---

## Safety Benchmarks

| Benchmark | Tests | Notes |
|-----------|-------|-------|
| **TruthfulQA** | Avoiding hallucinated "true" statements | 817 questions designed to elicit false answers |
| **BBQ** | Social group bias | Checks whether answers differ by demographic group |
| **WinoBias** | Gender bias in coreference | Pronoun resolution with gendered stereotypes |
| **HarmBench** | Jailbreak resistance | 400 harmful behaviors, automated red-teaming |
| **STRONG-REJ** | Safety refusals | Does model appropriately refuse harmful requests? |

---

## Domain-Specific Benchmarks

| Domain | Benchmark | Notes |
|--------|-----------|-------|
| Medical | **MedQA (USMLE)** | US Medical Licensing Exam questions |
| Medical | **MedMCQA** | Indian medical entrance exam |
| Legal | **LegalBench** | 162 legal reasoning tasks |
| Finance | **FinanceBench** | Financial statement Q&A |
| Science | **SciBench** | University STEM problems |
| Multilingual | **MGSM** | Multilingual grade school math |
| Multilingual | **MMMLU** | MMLU translated to 57 languages |

---

## How to Read Benchmark Scores

| Comparison | Interpretation |
|-----------|---------------|
| Model vs random chance | Score should be >> random (25% for 4-way MCQ) |
| Model vs human non-expert | Surpassing means "above average person" |
| Model vs domain expert | Surpassing means genuine expert-level knowledge |
| Model A vs Model B | Only meaningful at same evaluation protocol |
| This model vs last version | Regression testing; any drop is a red flag |

---

## Benchmark Limitations Summary

| Limitation | Which benchmarks affected | Why it matters |
|-----------|--------------------------|----------------|
| Multiple choice is artificial | MMLU, HellaSwag, ARC, GPQA | Real tasks rarely have 4 options |
| Contamination risk | All benchmarks, especially older ones | Scores may reflect memorization |
| Saturation | GSM8K, HellaSwag, ARC, PIQA | Can't differentiate top models |
| Small dataset | HumanEval (164), GPQA (448) | High variance in scores |
| Static | Most benchmarks | Problems don't change; models can overfit |
| English-only | Most benchmarks | Doesn't reflect multilingual capability |
| Doesn't test instruction following | MMLU, HumanEval | A model can know facts but fail to follow instructions |

---

## Where to Find Current Scores

| Resource | URL | Notes |
|----------|-----|-------|
| HuggingFace Open LLM Leaderboard | huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard | Open models only |
| LMSYS Chatbot Arena | lmarena.ai | Human preference Elo |
| Scale AI SEAL Leaderboard | scale.com/leaderboard | Agentic and coding |
| EpochAI | epochai.org/scaling-laws | Scaling analysis |
| Model release papers | arxiv.org | Authoritative scores with methodology |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Benchmark_Comparison.md** | ← you are here |

⬅️ **Prev:** [01 — Evaluation Fundamentals](../01_Evaluation_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 — LLM as Judge](../03_LLM_as_Judge/Theory.md)
