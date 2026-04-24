# LLM-as-Judge — Interview Q&A

## Beginner Level

**Q1: What is LLM-as-judge and when would you use it?**

<details>
<summary>💡 Show Answer</summary>

**A:** LLM-as-judge is an evaluation technique where a capable LLM (GPT-4, Claude Opus) evaluates the outputs of another AI system. You'd use it when: (1) outputs are open-ended and can't be measured with exact-match rules, (2) you need to evaluate at scale that precludes human review of every output, (3) you need something more nuanced than keyword matching but can't afford full human evaluation. Common use cases: evaluating chatbot response quality, measuring RAG faithfulness, comparing prompt versions in A/B tests.

</details>

**Q2: What is the difference between absolute scoring and pairwise comparison in LLM-as-judge?**

<details>
<summary>💡 Show Answer</summary>

**A:** Absolute scoring rates a single response against defined criteria (e.g., "score helpfulness 1–5"). Pairwise comparison shows the judge two responses (A and B) and asks which is better. Absolute scoring is useful for monitoring quality over time and catching regressions. Pairwise comparison is more reliable (relative judgments are easier than absolute ones) and is better for A/B testing two system versions. The trade-off: pairwise is O(n²) comparisons if you want to rank many options; absolute is O(n).

</details>

**Q3: What is position bias in LLM-as-judge?**

<details>
<summary>💡 Show Answer</summary>

**A:** Position bias is the tendency of LLM judges to prefer whichever response appears first (Response A) in a pairwise comparison — regardless of actual quality. This is a systematic bias that inflates win rates for whichever option you put first. Mitigation: always run the comparison in both orders (A vs B, then B vs A) and average the results. If the judge says A wins in ordering 1 but B wins in ordering 2, call it a tie or a close call.

</details>

---

## Intermediate Level

**Q4: How do you calibrate an LLM judge?**

<details>
<summary>💡 Show Answer</summary>

**A:** Calibration measures how well the LLM judge agrees with human raters:
1. Select 100–200 diverse representative examples
2. Have human annotators rate each example using the same criteria as your judge
3. Run the LLM judge on the same examples
4. Compute: Pearson correlation (for continuous scores), Kendall's Tau (for rankings), or percent agreement within 1 point (for Likert scales)
5. Compute Cohen's Kappa to measure agreement beyond chance
6. Target: κ > 0.6 (substantial agreement), Pearson > 0.7
If calibration is poor, revise the rubric: add more precise definitions, add score examples, break vague criteria into more specific sub-criteria.

</details>

**Q5: What is G-Eval and how does it improve on naive LLM judging?**

<details>
<summary>💡 Show Answer</summary>

**A:** G-Eval (from Geval: NLG Evaluation using GPT-4 with Better Human Alignment, 2023) is a structured evaluation framework that improves on naive "rate this 1–5" prompting. Key components: (1) explicit evaluation criteria with definitions, (2) chain-of-thought reasoning before scoring (ask the judge to think through the criteria first, then score), (3) form-filling format that structures the output, (4) running multiple evaluations and averaging to reduce variance. The chain-of-thought reasoning significantly improves consistency because it forces the judge to articulate its reasoning rather than jumping to a score.

</details>

**Q6: When should you NOT trust LLM-as-judge?**

<details>
<summary>💡 Show Answer</summary>

**A:** Situations where LLM-as-judge is unreliable:
1. **No calibration**: If you haven't verified it agrees with human raters, you don't know if it's measuring what you think
2. **Same model evaluating itself**: GPT-4 judging GPT-4 outputs shows significant self-preference bias
3. **Highly specialized domains**: A general-purpose judge doesn't have domain expertise to evaluate medical accuracy, legal correctness, or financial compliance
4. **Safety-critical decisions**: LLM judges can miss subtle safety issues or have blind spots on certain harmful content types
5. **Very subjective criteria**: "Is this creative?" has high inter-human variance; LLM scores are not more reliable than human disagreement suggests

</details>

---

## Advanced Level

**Q7: How would you build a production-grade LLM evaluation system for a customer support chatbot?**

<details>
<summary>💡 Show Answer</summary>

**A:** System design:
1. **Criteria definition**: Work with support team to define what "good" looks like: (a) Accuracy — is the policy information correct?, (b) Resolution — does it solve the problem?, (c) Tone — is it empathetic and professional?, (d) Completeness — did it address all parts of the question?
2. **Rubric development**: Write 1–5 definitions for each criterion with examples from real support tickets
3. **Human calibration dataset**: Have support supervisors rate 200 real conversations as ground truth
4. **Judge implementation**: Claude Opus as judge (different model family from the chatbot), G-Eval approach with CoT reasoning
5. **Calibration check**: Verify Pearson correlation >0.7 vs human ratings before deploying
6. **Integration**: Run judge on 10% sample of live conversations, daily aggregated scores
7. **Regression testing**: Run full eval suite on 500 test cases before every prompt/model update
8. **Alerts**: If any dimension drops >5% from baseline, trigger immediate review

</details>

**Q8: How would you detect and correct for length bias in LLM-as-judge evaluations?**

<details>
<summary>💡 Show Answer</summary>

**A:** Detection: Check if score correlates with response length — plot score vs character count. If correlation > 0.3, you have length bias. Correction methods:
1. **Explicit instruction**: Add to judge prompt: "A concise, complete answer should score as high as a verbose complete answer. Ignore length and rate content quality only."
2. **Penalize verbosity explicitly**: "If a response is longer than necessary to answer the question, deduct 1 point from Clarity."
3. **Length-normalized test set**: Include pairs of equivalent-quality short vs long answers in your calibration set and check that they score similarly
4. **Post-hoc adjustment**: Fit a regression model (score ~ content_quality + length) and subtract the length component
5. **Swap short/long variants**: For each calibration example, create a condensed version and a verbose version of the same information; check that scores are within 0.5 of each other

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | LLM judge implementation |
| [📄 Prompt_Templates.md](./Prompt_Templates.md) | 5 judge prompt templates |

⬅️ **Prev:** [02 — Benchmarks](../02_Benchmarks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 — RAG Evaluation](../04_RAG_Evaluation/Theory.md)
