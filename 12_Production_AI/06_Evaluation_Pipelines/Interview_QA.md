# Interview QA — Evaluation Pipelines

## Beginner

**Q1: What is the difference between offline and online evaluation for AI systems?**

<details>
<summary>💡 Show Answer</summary>

**A:** **Offline evaluation** happens before deployment. You run the model on a fixed curated test set of (input, expected_output) pairs and measure quality metrics. It's like running unit tests in software development — you do it before shipping. Offline eval catches regressions and validates that a new model/prompt version is at least as good as the current one. Fast, controlled, repeatable.

**Online evaluation** happens in production on live traffic. You can't control the inputs (real users send anything), you often don't have ground truth expected outputs, and you can't block a request to wait for an eval. Instead, you sample a fraction of live requests, evaluate them asynchronously (using LLM judge or human review), and track quality metrics over time. Online eval detects distribution drift (when users start asking different questions), catches edge cases your test set missed, and gives you ground truth about real-world quality.

Both are necessary. Offline eval is your safety gate before deployment. Online eval is your smoke detector in production.

</details>

---

**Q2: What is LLM-as-judge and what are its limitations?**

<details>
<summary>💡 Show Answer</summary>

**A:** LLM-as-judge means using a powerful language model (e.g., GPT-4 or Claude Opus) to automatically evaluate the quality of responses from another model. You give the judge a rubric (accuracy, helpfulness, clarity, safety), the original question, and the response to evaluate. The judge returns a score and reasoning.

Why it's useful: Human evaluation is expensive and slow (human labelers charge per annotation). LLM judges can evaluate thousands of responses per hour, are available 24/7, provide consistent scoring, and correlate well with human judgment (0.7-0.9 Pearson correlation on most tasks).

Limitations:
1. **Self-serving bias**: Models tend to prefer outputs in their own style. GPT-4 scores GPT-4 outputs higher than Claude outputs on average, even when both are equally good. Always use a different model family as your judge.
2. **Position bias**: LLM judges prefer responses in position A when shown (A, B) in a comparative evaluation. Mitigate by randomizing order.
3. **Verbosity bias**: LLM judges tend to rate longer responses higher, even if the short response is actually better. This is a known limitation.
4. **Not reliable for safety**: An LLM judge can miss subtle harmful content. For safety evaluation, use specialized safety classifiers.
5. **Cost**: Running GPT-4 on every response for evaluation adds significant cost. Sample strategically (1-5% of production traffic, full eval set pre-deployment).

</details>

---

**Q3: What metrics would you use to evaluate a RAG (Retrieval Augmented Generation) system?**

<details>
<summary>💡 Show Answer</summary>

**A:** RAG systems have two stages — retrieval and generation — each requiring different metrics.

**Retrieval quality:**
- **Context Precision**: Of all the retrieved chunks, what fraction are actually relevant to the question? High precision means you're not flooding the LLM with irrelevant context.
- **Context Recall**: Of all the information needed to answer the question, what fraction did we retrieve? High recall means we found all the necessary facts.

**Generation quality:**
- **Faithfulness**: Does the generated answer contradict the retrieved context? A faithful answer is grounded in the provided documents and doesn't hallucinate.
- **Answer Relevance**: Does the answer actually address the question that was asked? A long response about tangentially related topics scores low.

**End-to-end:**
- **Answer Correctness**: How accurate is the final answer compared to the ground truth? Combines factual accuracy with completeness.

The **RAGAS** library (ragas.io) implements all of these metrics and uses LLM calls to compute them automatically. It's the standard evaluation framework for RAG systems.

</details>

---

## Intermediate

**Q4: How would you build a CI/CD-integrated evaluation pipeline that blocks bad model updates?**

<details>
<summary>💡 Show Answer</summary>

**A:** The goal is to make evaluation as automatic as running unit tests.

**Pipeline structure:**
1. **Test set storage**: Maintain a versioned dataset of (input, expected_output, metadata) in your repo or a dataset registry. Version it with git-LFS or DVC.

2. **Evaluation script**: A Python script that takes a model/prompt version, runs all test cases, scores each with your chosen metric (exact match, LLM judge, ROUGE), and outputs a JSON report with pass rate and individual scores.

3. **CI/CD integration**: Run the eval script on every PR that touches prompts, model config, or core LLM code. Example in GitHub Actions:
   ```yaml
   - name: Run eval
     run: python eval.py --model $PR_MODEL --threshold 4.0
     if: steps.changed_files.outputs.llm_changed == 'true'
   ```

4. **Gate on threshold**: If pass rate < 90% or average score < 4.0, fail the CI check and block the merge. Surface the failing test cases as a PR comment so engineers know what to fix.

5. **Baseline comparison**: Store the current production model's scores. Block deployment if the new model's scores are more than 0.2 points lower on any category, even if they're above the absolute threshold (prevents gradual drift).

6. **Fast eval subset**: Full eval might take 5 minutes. Keep a "fast eval" subset (20-30 most important test cases) that runs in 30 seconds for quick developer feedback. Run full eval nightly or on merge to main.

</details>

---

**Q5: How do you evaluate open-ended creative or conversational AI responses where there's no single correct answer?**

<details>
<summary>💡 Show Answer</summary>

**A:** When there's no ground truth, you need evaluation criteria that don't require a reference answer. Several approaches:

**Rubric-based LLM judge:**
Define clear criteria for your use case. For a creative writing assistant:
- Creativity (1-5): Is the response original and interesting?
- Relevance (1-5): Does it address the prompt?
- Coherence (1-5): Is it logically structured?
- Safety (1-5): Is it free of harmful content?

Have an LLM judge score each dimension. Track scores over time. A regression in average score is a signal, even without ground truth.

**Pairwise comparison:**
Instead of absolute scoring, compare two model outputs side by side. "Which response is better?" has higher inter-rater agreement than absolute 1-5 scoring. Used heavily by OpenAI/Anthropic for RLHF. For production eval, randomly sample 5% of traffic, generate two responses (current model vs candidate), have an LLM judge pick the winner. Statistical test to determine if the candidate is significantly better/worse.

**Reference-free metrics:**
- **Distinctness**: Does the model repeat itself or produce generic outputs? Measure n-gram diversity.
- **Hallucination detection**: Even without ground truth, you can check if the model invents specific facts (names, dates, numbers) using a fact-checking LLM call.
- **Style consistency**: For brand voice consistency, train a classifier on examples of good/bad style and score new outputs.

**User signals as proxy:**
Ultimately the ground truth for "is this creative response good?" is whether users like it. Track regeneration rate (did they hit "try again"?), session length, and explicit ratings.

</details>

---

**Q6: What is regression testing for AI models, and how is it different from regression testing in traditional software?**

<details>
<summary>💡 Show Answer</summary>

**A:** In traditional software, regression testing checks that new code doesn't break existing functionality. A regression is when a previously passing test now fails — a clear binary outcome.

In AI, regression testing is similar in intent but harder because model outputs are probabilistic and partially subjective:

**Similarity**: You have a fixed test set, you run the model on it, and you check that quality metrics haven't dropped below a threshold compared to the previous version.

**Key differences:**
1. **Probabilistic outputs**: Run the same test case multiple times and you may get slightly different answers. Regression metrics must be averages over enough samples to be statistically meaningful.

2. **No binary pass/fail**: Instead of "does it compile?", you're measuring "is average quality ≥ 4.1/5?" A model that was 4.2 and drops to 4.0 is a regression, but the threshold is a judgment call, not a logical guarantee.

3. **Silent regressions**: An AI model can regress on specific subsets (demographic groups, specific languages, edge cases) while average quality stays flat. Test set stratification is important — check metrics per-category, not just overall.

4. **Difficult to root cause**: When a software test fails, there's a specific line of code to blame. When an AI model regresses, the root cause could be: a prompt change, a model update by the provider, a change in user query distribution, or a data quality issue. Investigation requires prompt ablation studies and error analysis.

**Best practices for AI regression testing:**
- Always compare to a baseline (current production model's scores), not just an absolute threshold
- Stratify your test set by query type, language, domain, etc. — check per-segment metrics
- Keep failing examples from past regressions permanently in your test set
- Run regression tests on every meaningful change: prompts, model version, chunking, retrieval strategy

</details>

---

## Advanced

**Q7: Design a comprehensive evaluation framework for a multi-step AI agent that uses tools (web search, code execution, database queries).**

<details>
<summary>💡 Show Answer</summary>

**A:** Evaluating agents is significantly harder than evaluating single-turn models because the quality of the final answer depends on a chain of decisions.

**What to evaluate at each level:**

**Step-level evaluation:**
- For each tool call, did the agent choose the right tool?
- For each tool call, did it pass correct parameters? (JSON schema validation)
- After receiving tool results, did it use them correctly in the next step?

**Trajectory evaluation:**
- Did the agent take the most efficient path? (fewer steps = better, if same outcome)
- Did it recover from tool failures gracefully?
- Did it know when to stop (avoiding unnecessary extra steps)?

**Outcome evaluation:**
- Is the final answer correct? (LLM judge + ground truth when available)
- Is the answer supported by the tool outputs? (faithfulness check)
- Did the agent stay on task, or wander?

**Evaluation implementation:**
```python
def evaluate_agent_run(trace: AgentTrace, ground_truth: str) -> AgentEvalResult:
    return AgentEvalResult(
        # Outcome metrics
        final_answer_score=llm_judge(trace.final_answer, ground_truth),
        answer_faithfulness=check_faithfulness(trace.final_answer, trace.tool_results),

        # Trajectory metrics
        step_count=len(trace.steps),
        unnecessary_steps=count_redundant_steps(trace.steps),
        tool_error_recovery=count_handled_errors(trace.steps),

        # Step-level metrics
        tool_selection_accuracy=evaluate_tool_choices(trace.steps),
        parameter_correctness=evaluate_tool_params(trace.steps),
    )
```

**Test case design for agents:**
- Create test cases with known optimal trajectories (expert demonstrations)
- Include "trap" test cases that tempt the wrong tool choice
- Include test cases where tools fail — test error recovery
- Test with different levels of context completeness

**Key challenge**: Agent evaluation requires tracing every decision step, not just the final answer. Use LLM-specific tracing (Langfuse, Phoenix) that can capture multi-step traces.

</details>

---

**Q8: How do you detect and handle distribution shift in production AI systems, and how does this relate to evaluation?**

<details>
<summary>💡 Show Answer</summary>

**A:** Distribution shift means the inputs your model receives in production differ from what it was trained or tuned on. This causes quality degradation that your offline eval doesn't detect (because it uses a fixed test set).

**Types of distribution shift:**
- **Covariate shift**: Input distribution changes (users start asking new types of questions)
- **Label shift**: Expected output distribution changes (what's considered a "good" answer changes)
- **Concept drift**: The underlying relationship changes (facts that were true become false — e.g., laws change, products change)

**Detection via evaluation:**
1. **Embedding drift**: Embed recent production queries and compare their distribution to your test set embeddings. If the centroid or spread shifts significantly (KL divergence, Wasserstein distance), you may have distribution shift.

2. **Quality metric drift**: Track online LLM judge scores over time. A declining trend (not a sudden spike) often indicates distribution shift rather than a bug.

3. **Out-of-distribution detection**: Build a classifier trained on your test set queries. Flag production queries that it classifies as "OOD" (out of distribution). These are high-risk queries where the model may underperform.

**Response to detected shift:**
1. **Short-term**: Sample flagged OOD queries, have humans review them, understand the new query types
2. **Medium-term**: Add examples of the new query type to your test set; this makes future evaluations detect regressions on the new distribution
3. **Long-term**: Fine-tune or adjust the prompt on the new query distribution

The evaluation pipeline and distribution monitoring are tightly linked — your test set must evolve to represent the current production distribution, not just the original launch distribution.

</details>

---

## 📂 Navigation
