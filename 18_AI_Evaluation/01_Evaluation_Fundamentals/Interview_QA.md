# AI Evaluation Fundamentals — Interview Q&A

## Beginner Level

**Q1: What is an AI eval and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

**A:** An AI eval (evaluation) is a structured test that measures how well an AI system performs on defined tasks using specific metrics. It matters because: (1) AI outputs are probabilistic — without measurement you can't tell if quality is 60% or 90%, (2) AI can degrade silently without triggering obvious errors, (3) you can't improve what you don't measure. Teams that treat evals as first-class engineering dramatically outperform those that rely on intuition.

</details>

**Q2: What are the four dimensions of AI evaluation?**

<details>
<summary>💡 Show Answer</summary>

**A:**
1. **Quality** — Does it produce correct, relevant, helpful outputs?
2. **Safety** — Does it avoid harmful, inappropriate, or dangerous outputs?
3. **Latency** — How fast does it respond?
4. **Cost** — How much does it cost per query to operate?
All four matter for production systems. A perfectly accurate model that takes 30 seconds per response is not production-ready.

</details>

**Q3: What is the difference between automated evaluation and human evaluation?**

<details>
<summary>💡 Show Answer</summary>

**A:** Automated evaluation uses code to measure AI outputs — comparing against reference answers, applying regex patterns, or using LLM-as-judge. It's fast, cheap, and scalable. Human evaluation uses people to rate AI outputs, which is slower and more expensive but captures nuance that automated metrics miss (like whether an answer is actually helpful or just technically correct). In practice you use both: automate what you can, use humans for calibration and high-stakes decisions.

</details>

---

## Intermediate Level

**Q4: What is eval contamination and why is it so dangerous?**

<details>
<summary>💡 Show Answer</summary>

**A:** Eval contamination happens when test cases from your evaluation set are used during model training, prompt development, or fine-tuning. When this happens, the model has "seen the answers" and will score artificially high on those test cases — giving you inflated confidence that doesn't reflect real-world performance. It's dangerous because it's invisible; your metrics look great but your production performance is poor. Fix: maintain a strict test set that is never used for anything except evaluation, and regenerate test sets periodically.

</details>

**Q5: How do you define a good test case for an AI system?**

<details>
<summary>💡 Show Answer</summary>

**A:** A good test case has:
1. **A realistic input** — drawn from actual or representative production queries
2. **A defined expected output or criteria** — either an exact expected answer (for factual tasks) or a rubric of what a good answer should include
3. **Coverage of edge cases** — unusual inputs, ambiguous questions, boundary conditions
4. **Diversity** — different topic areas, difficulty levels, and input styles
Bad test cases: only happy-path examples, identical structure repeated with different words, or inputs that don't resemble what real users will send.

</details>

**Q6: Why is having a baseline critical for evaluation?**

<details>
<summary>💡 Show Answer</summary>

**A:** A score in isolation means nothing. "72% accuracy" — is that good? You can't tell without context. A baseline provides context:
- Compared to the previous version: is this better or worse?
- Compared to a simpler system: is this expensive LLM actually better than a basic rule-based approach?
- Compared to human performance: are we close to human-level or still far off?
Always report scores relative to at least one baseline, and always ask "better than what?"

</details>

---

## Advanced Level

**Q7: How do you implement evaluation-driven development for an AI feature?**

<details>
<summary>💡 Show Answer</summary>

**A:** The process mirrors TDD (test-driven development):
1. **Define the task**: What should the AI do? What does success look like?
2. **Write test cases before building**: Create 50–200 test cases covering normal use, edge cases, and failure modes
3. **Build the simplest possible baseline**: A naive implementation against which to compare
4. **Build and evaluate**: Implement the real system, run the eval
5. **Analyze failures**: Look at every failing test case. What pattern do they share?
6. **Improve and re-eval**: Change the system, run the eval again
7. **Never modify test cases to fit your system**: Only add new test cases, never change existing ones to match current behavior
The key discipline: your eval score only improves when the AI actually gets better, not when you massage the test set.

</details>

**Q8: How do you handle evaluating subjective quality at scale?**

<details>
<summary>💡 Show Answer</summary>

**A:** Subjective quality (helpfulness, tone, clarity) can't be measured with exact match. Options at scale:
1. **LLM-as-judge**: Use a capable LLM (GPT-4, Claude Opus) with a detailed rubric to rate outputs on a 1–5 scale. Measure correlation with human ratings to calibrate.
2. **Pairwise preference**: Show two outputs (A vs B), ask which is better. More reliable than absolute ratings. Aggregate into a ranking.
3. **Human on a sample**: Rate 5% of outputs with humans, use LLM-as-judge for the rest. Use human ratings to calibrate and monitor the judge.
4. **Crowd-sourced ratings**: Use annotation platforms (Scale AI, Labelbox) for large-scale human evaluation.
Key insight: you need human evaluation to calibrate automated methods, but you can't rely on humans alone at scale.

</details>

**Q9: System design: How would you build an evaluation system for a production chatbot?**

<details>
<summary>💡 Show Answer</summary>

**A:** Three-tier eval system:
1. **Automated regression suite** (runs on every deploy):
   - 500 test cases with expected outputs or criteria
   - Automated LLM-as-judge scoring on quality dimensions
   - Latency and cost measurements
   - Pass/fail threshold: if quality drops >2% from baseline, block deploy
2. **Continuous production sampling**:
   - Sample 1% of live conversations
   - Run LLM-as-judge on sampled outputs
   - Alert if quality score drops below threshold
   - Weekly human review of 50 sampled conversations
3. **Deep evaluation** (weekly/on-demand):
   - Full human evaluation on 200 examples
   - Adversarial test cases (red team inputs)
   - Coverage analysis: which query types are underperforming?
   - Input: analysis into improvement priorities for next iteration

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Section 17 — Multimodal AI](../../17_Multimodal_AI/) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 — Benchmarks](../02_Benchmarks/Theory.md)
