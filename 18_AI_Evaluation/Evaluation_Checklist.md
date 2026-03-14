# AI Evaluation Checklist

A comprehensive reference for evaluating LLM systems before and after deployment.

---

## Pre-Launch Eval Checklist

### Dataset Readiness
- [ ] At least 100 golden test cases, all manually verified
- [ ] Test cases cover the full distribution of expected user inputs
- [ ] Edge cases included: empty inputs, very long inputs, ambiguous questions
- [ ] Adversarial cases included: jailbreaks, prompt injection, scope violations
- [ ] Dataset stored in version control (git)
- [ ] Owner identified for maintaining and updating the dataset

### Evaluator Readiness
- [ ] Deterministic checks defined for all structured outputs
- [ ] LLM-as-judge configured with validated prompts (κ > 0.7 vs human)
- [ ] Domain-specific checks implemented for critical business rules
- [ ] Eval framework chosen and configured (Promptfoo / LangSmith / custom)
- [ ] Cost per eval run estimated and budgeted

### Quality Targets Set
- [ ] Pass rate threshold defined (e.g., ≥ 85% for general use)
- [ ] Separate thresholds for safety tests (typically 100%)
- [ ] Latency SLA defined (e.g., P95 < 3s)
- [ ] Cost-per-request target defined

### Baseline Established
- [ ] Full eval run completed and results saved as baseline
- [ ] Baseline metrics documented: pass rate, avg score, P95 latency
- [ ] Results reviewed by at least one domain expert

### CI/CD Integration
- [ ] Smoke test runs on every PR (< 2 min)
- [ ] Full eval runs on every merge to main
- [ ] CI fails if pass rate drops below threshold
- [ ] Safety tests always run with 100% threshold

---

## Post-Launch Monitoring Checklist

### Production Data Capture
- [ ] All LLM requests and responses are logged
- [ ] User feedback (thumbs up/down) is captured where possible
- [ ] Error rate is tracked in real-time
- [ ] Latency P50/P95/P99 monitored with alerts

### Ongoing Evaluation
- [ ] Weekly: 20+ production samples reviewed by a human
- [ ] Weekly: LLM judge score checked against human scores on 5 cases
- [ ] Monthly: New test cases added from real failure patterns
- [ ] Monthly: Retired test cases archived (consistently passing edge cases)
- [ ] Quarterly: Full dataset audit with domain expert

### Regression Detection
- [ ] Automated regression detection comparing each eval run to baseline
- [ ] Alert configured for pass rate drop > 3%
- [ ] Alert configured for avg quality score drop > 0.5
- [ ] Newly failed test cases surfaced in Slack/email immediately

### Model and Prompt Versioning
- [ ] Every model or prompt change triggers a full eval before deploy
- [ ] Eval results attached to each deployment record
- [ ] Rollback plan in place if regression detected post-deploy

---

## Red Team Checklist

### Coverage — Attack Categories
- [ ] Direct jailbreaks tested (role-play, hypotheticals, "pretend you are")
- [ ] Indirect prompt injection tested (via documents, web pages, tool outputs)
- [ ] Data extraction attempts tested (asking for training data, system prompts)
- [ ] Social engineering attempts tested (urgency, authority impersonation)
- [ ] Sensitive topic probing tested (self-harm, violence, illegal activities)

### Coverage — Input Variations
- [ ] Multi-language inputs tested
- [ ] Encoded inputs tested (base64, ROT13, pig Latin)
- [ ] Long inputs tested (near context window limit)
- [ ] Inputs with special characters and Unicode tested
- [ ] Multi-turn conversation attacks tested

### Metrics
- [ ] Attack Success Rate (ASR) measured per category
- [ ] ASR target met: < 5% for jailbreaks, < 1% for prompt injection
- [ ] False positive rate checked: safe requests not wrongly blocked
- [ ] Safety filter calibrated: not over-blocking legitimate requests

### Process
- [ ] Red team conducted by people different from system builders
- [ ] Findings documented with reproducible test cases
- [ ] All successful attacks added to adversarial test set
- [ ] Fixes verified by re-running the original attack
- [ ] Re-test after any system prompt or model change

---

## Eval Quality Self-Check

Use this to verify your eval system itself is trustworthy.

### Test Set Quality
- [ ] Test cases are independent (no copying from training data)
- [ ] Test cases are unambiguous (experts agree on the correct answer)
- [ ] Test set is balanced (not dominated by any one category)
- [ ] Test set evolves (new cases added; old ones retire)
- [ ] Contamination checked (test data not in model training data)

### Evaluator Validity
- [ ] LLM judge agreement with humans measured (κ > 0.7)
- [ ] Judge prompts tested for position bias (swap A/B order, check for flip)
- [ ] Judge prompts tested for length bias (longer outputs should not auto-score higher)
- [ ] Judge calibrated: known-bad outputs should score < 5

### Process Integrity
- [ ] Eval person is different from prompt engineer (avoid confirmation bias)
- [ ] Eval results are not cherry-picked for favorable presentation
- [ ] Test thresholds were set before seeing results (not tuned post-hoc)
- [ ] Eval run reproducibility confirmed (same inputs → same results within variance)

---

## Quick Reference: Metric Targets

| Metric | Minimum | Target | Excellent |
|--------|---------|--------|-----------|
| Pass rate (general) | 75% | 85% | 95%+ |
| Pass rate (safety) | 95% | 99% | 100% |
| Avg judge score (1–10) | 6.0 | 7.5 | 9.0 |
| LLM judge vs human (κ) | 0.5 | 0.7 | 0.85+ |
| P95 latency (chatbot) | 8s | 3s | 1s |
| Error rate | 5% | 1% | < 0.1% |
| Attack success rate | 10% | 5% | < 1% |
| False positive (safety) | 5% | 1% | < 0.5% |

---

## Diagnostic Guide: What to Do When Metrics Are Bad

```
Pass rate < 75%
  ├── Are failures clustered in one category? → Focus improvement there
  ├── Is the model hallucinating facts? → Add retrieval or cite sources
  ├── Is the model ignoring instructions? → Strengthen system prompt
  └── Are test cases ambiguous? → Fix the test set

Quality score declining over time
  ├── Was the model or API updated? → Check model version changelog
  ├── Did user query distribution shift? → Update test set to match
  └── Is the judge model drifting? → Recalibrate judge vs human

Latency P95 > 5s
  ├── Are prompts getting longer? → Compress context
  ├── Are tools taking too long? → Add timeouts; parallelize
  └── Is token usage high? → Switch to faster/smaller model for simpler queries

Safety ASR > 5%
  ├── Identify which attack category succeeds → Add specific guardrails
  ├── Is it prompt injection via external data? → Sanitize inputs; add delimiters
  └── Is the system prompt weak? → Add explicit refusal instructions with examples

High false positive rate (blocking good requests)
  ├── Safety classifier too aggressive → Lower threshold
  ├── System prompt over-refuses → Add positive examples of allowed behavior
  └── Add known-safe cases to test set to track improvements
```

---

## Section 18 — Full Navigation

| Subsection | What It Covers |
|------------|---------------|
| [01_Evaluation_Fundamentals](01_Evaluation_Fundamentals/) | Why evals matter, types of evals, test set design |
| [02_Benchmarks](02_Benchmarks/) | MMLU, HumanEval, GSM8K, contamination |
| [03_LLM_as_Judge](03_LLM_as_Judge/) | G-Eval, pairwise comparison, bias mitigation |
| [04_RAG_Evaluation](04_RAG_Evaluation/) | RAGAS: faithfulness, relevance, recall |
| [05_Agent_Evaluation](05_Agent_Evaluation/) | Task completion, tool accuracy, trajectory |
| [06_Red_Teaming](06_Red_Teaming/) | Attack categories, ASR, automated red teaming |
| [07_Eval_Frameworks](07_Eval_Frameworks/) | Promptfoo, LangSmith, OpenAI Evals |
| [08_Build_an_Eval_Pipeline](08_Build_an_Eval_Pipeline/) | End-to-end pipeline: data → CI → monitoring |

---

## 📂 Navigation

- Section root: [18_AI_Evaluation](.)
- Start here: [01_Evaluation_Fundamentals](01_Evaluation_Fundamentals/)
- Build a pipeline: [08_Build_an_Eval_Pipeline](08_Build_an_Eval_Pipeline/)
- Previous section: [17_Multimodal_AI](../17_Multimodal_AI/)
