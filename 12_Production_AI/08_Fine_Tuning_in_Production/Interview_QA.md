# Interview QA — Fine-Tuning in Production

## Beginner

**Q1: What is fine-tuning and how is it different from prompting?**

<details>
<summary>💡 Show Answer</summary>

**A:** Both fine-tuning and prompting are ways to get an LLM to behave in a specific way, but they work at different levels.

**Prompting** instructs the model at inference time using text in the context window: "You are a product classifier. Return JSON with category, subcategory, and color fields. Here are 3 examples: [...]". The model reads these instructions every time it processes a request. The model's weights are unchanged — it's using general instruction-following capability.

**Fine-tuning** changes the model's weights by continuing training on your specific task data. After fine-tuning, the model has internalized the pattern. You don't need to remind it with lengthy instructions every request — it just "naturally" produces the format you want.

Key differences:
- Prompting is instant to iterate; fine-tuning takes hours/days
- Prompting uses tokens (costs money per request for the instructions); fine-tuned models need shorter prompts
- Prompting is general; fine-tuning is specialized
- Fine-tuning can achieve better consistency for format-heavy tasks
- Fine-tuning can learn domain-specific knowledge not in the base model

Rule of thumb: Try prompting first. Only fine-tune when prompting has been exhausted and you have enough quality data.

</details>

---

**Q2: What is LoRA and why is it the preferred fine-tuning method for most production use cases?**

<details>
<summary>💡 Show Answer</summary>

**A:** LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning technique that adds small trainable "adapter" matrices to the existing frozen model weights, rather than updating all the model's parameters.

The key idea: any change to a weight matrix W can be expressed as a low-rank decomposition W + ΔW = W + BA, where B and A are small matrices (rank r << original dimension). Instead of updating all of W (7 billion parameters for a 7B model), you only train B and A (a few million parameters — ~0.1% of total).

Why LoRA is the practical default:
1. **Memory efficiency**: A 7B model fully fine-tuned needs ~120GB VRAM. With LoRA, ~16GB. This makes fine-tuning possible on affordable hardware (e.g., a single A100 40GB).
2. **No catastrophic forgetting**: The original weights are frozen. The model retains all its general capabilities while the adapters add task-specific behavior.
3. **Easily switchable**: You can maintain multiple LoRA adapters for different tasks and hot-swap them without reloading the base model.
4. **Quality**: For most tasks, LoRA fine-tuned models perform nearly as well as fully fine-tuned models.

For most production fine-tuning: LoRA with rank 8-64 is sufficient. QLoRA (LoRA on a 4-bit quantized base model) when VRAM is the constraint.

</details>

---

**Q3: How much training data do you need for fine-tuning to be effective?**

<details>
<summary>💡 Show Answer</summary>

**A:** The amount varies by task complexity and quality of the data:

**Minimum thresholds (approximate):**
- Simple format/style tasks (always return specific JSON): 50-100 high-quality examples
- Moderate tasks (classification into 10-20 categories): 500-1,000 examples per category
- Complex tasks (nuanced writing, domain expertise): 2,000-10,000 examples
- Very complex tasks (medical, legal expertise): 10,000+ examples

**More important than quantity is quality:**
- 500 perfect, expert-labeled examples often outperform 5,000 mediocre crowdsourced ones
- Training data must be perfectly consistent in format and quality
- Diversity matters: cover the full range of inputs your model will see in production
- Edge cases matter: include the hard examples that the base model struggles with

**Practical guideline**: Start with what you have. If you have 100 examples, fine-tune and evaluate. If you see clear improvement, you likely have enough for the task. If not, collect more — specifically examples where the current model fails.

</details>

---

## Intermediate

**Q4: What is catastrophic forgetting and how do you prevent it in fine-tuning?**

<details>
<summary>💡 Show Answer</summary>

**A:** Catastrophic forgetting happens when a model, trained extensively on a new specific task, "forgets" capabilities it learned during pre-training. For example, a model fine-tuned heavily on medical texts might lose its ability to reason about general topics, write code, or follow general instructions.

Why it happens: gradient updates that push the model toward the new task also move it away from the representations that supported old capabilities.

**Prevention strategies:**

1. **Use LoRA instead of full fine-tuning**: LoRA freezes the original weights — catastrophic forgetting is largely impossible because the base model weights are unchanged. Only the small adapter matrices are updated.

2. **Regularization (L2 / weight decay)**: Penalizes large weight updates, keeping the model's parameters close to their pre-trained values. Common in full SFT: `weight_decay=0.01` in training args.

3. **Low learning rate**: A smaller learning rate (1e-5 to 5e-5) makes smaller gradient steps, reducing the risk of dramatic weight changes.

4. **Mix in general instruction data**: Include 10-20% "general" instruction-following examples in your training data alongside your domain-specific examples. This reminds the model to retain general capabilities.

5. **Few epochs**: 1-3 epochs is often enough for SFT. Over-training amplifies forgetting.

6. **Elastic Weight Consolidation (EWC)**: A more sophisticated regularization technique that identifies which parameters are most important for previous tasks and penalizes changing them. Used in research, less common in production.

</details>

---

**Q5: Walk me through the process of preparing training data for fine-tuning, including common data quality issues.**

<details>
<summary>💡 Show Answer</summary>

**A:** Data preparation is often the most time-consuming and most critical part of fine-tuning. Good data produces good models; bad data produces bad models.

**Data collection:**
1. Start with real production examples: actual user inputs that your system should handle well
2. Have domain experts (not just engineers) generate or review the training outputs
3. For style/format tasks: export successful human-curated examples from your existing product

**Data formatting:**
```jsonl
// Each line is one training example
{"messages": [
  {"role": "system", "content": "You classify product reviews by sentiment."},
  {"role": "user", "content": "This product broke after one week. Very disappointed."},
  {"role": "assistant", "content": "{\"sentiment\": \"negative\", \"confidence\": \"high\"}"}
]}
```

**Common data quality issues:**
1. **Inconsistent format**: Some examples return JSON, some return plain text. The model will learn to randomly switch formats.
2. **Inconsistent content**: Some examples are thorough, some are terse. The model will produce unpredictably variable responses.
3. **Mislabeled examples**: 5-10% wrong labels in training data causes measurable quality degradation.
4. **Insufficient diversity**: All training examples are easy cases. The model learns nothing about hard cases it will see in production.
5. **Training-production mismatch**: Training data was generated with different prompting than what production uses. The model specializes for the wrong input format.
6. **Data leakage**: Eval examples that accidentally appear in training data, making eval metrics falsely high.

**Data validation checklist:**
- Format consistency check: programmatically verify every example follows the exact format
- Label review: have domain experts review 10% random sample
- Diversity check: look at the distribution of example types, lengths, difficulty levels
- Deduplication: remove near-duplicate examples (they add weight but not information)
- Train/eval split: 80/20 split, stratified by category if classification

</details>

---

**Q6: How do you decide between RAG and fine-tuning for a knowledge-intensive task?**

<details>
<summary>💡 Show Answer</summary>

**A:** This is one of the most important architectural decisions in AI product development. The key dimensions to consider:

**Use RAG when:**
- Information changes frequently (current events, product prices, new policies)
- Information is personalized (user-specific data, account information)
- Information comes from specific authoritative documents (a specific contract, a specific manual)
- You need to cite sources (RAG can quote the exact retrieved text)
- You have limited labeled training data (< a few hundred examples)

**Use fine-tuning when:**
- You need a specific response format/style that is hard to prompt reliably
- The "knowledge" is actually a skill or pattern, not factual information
- You are trying to reduce prompt length and token costs
- You have a large labeled dataset of (input, expert_output) pairs
- The task is consistent and well-defined (not open-ended)

**Use both (RAG + fine-tuning) when:**
- The domain knowledge is extensive AND format/style matters
- A fine-tuned model that retrieves and uses context in a specific format

**Practical test**:
1. Try prompting with few-shot examples first
2. If quality isn't good enough: add RAG if it's a knowledge problem
3. If RAG quality is good but format/consistency is the issue: fine-tune
4. If it's both: RAG + fine-tuning

Example: A medical coding assistant
- Uses RAG: to look up current ICD-10 codes from an authoritative database (changes yearly)
- Uses fine-tuning: to learn the exact output format and the specialist's decision logic
- Together: retrieves relevant codes, applies domain expertise to select the right one

</details>

---

## Advanced

**Q7: Design a continuous fine-tuning pipeline for a production model. How do you avoid data quality issues and regressions?**

<details>
<summary>💡 Show Answer</summary>

**A:** Continuous fine-tuning is re-training the model periodically as new labeled data accumulates. This is how production AI systems stay current and improve over time.

**Pipeline design:**

```
1. Data collection (ongoing):
   - Log all model inputs and outputs in production
   - Route a sample (1-5%) to human review queue
   - Capture explicit user feedback (thumbs up/down)
   - Tag high-quality outputs for potential training inclusion

2. Data curation (weekly/monthly):
   - Human reviewers approve/reject sampled examples
   - Automated quality checks: format consistency, length distribution
   - Deduplication with existing training set
   - Stratified sampling to maintain class balance

3. Training trigger:
   - New training run when: 1,000+ new quality-approved examples OR quality metric drift detected
   - Combine new data with existing training data (don't replace)
   - Maintain historical training data — curriculum matters

4. Training run:
   - Same architecture as previous version
   - Start from previous fine-tuned checkpoint (incremental, not from scratch)
   - Validate training/eval loss curves for overfitting signals
   - Compare eval set performance vs previous model version

5. Evaluation gate:
   - Automatic eval on fixed holdout set
   - Must beat previous model on: primary task metric, no regression on secondary metrics
   - Block deployment if any category drops > 3%

6. Staged deployment:
   - 5% canary → 24 hours monitoring → 50% → 24 hours → 100%
   - Auto-rollback if production quality metrics degrade

7. Model versioning:
   - Tag every model with: training_date, training_data_version, eval_metrics
   - Keep last 3 versions warm (ready to roll back)
```

**Key risks and mitigations:**
- **Training data poisoning**: Malicious users craft inputs to steer the model. Mitigate: human review of flagged examples, anomaly detection on example distributions.
- **Feedback loop bias**: If good outputs are collected for training, bad outputs (which users never see after guardrails block them) are underrepresented. Mitigate: include adversarial examples and correction examples.
- **Label quality drift**: Human reviewers' standards change over time. Mitigate: anchor reviews with calibration examples, periodic inter-rater agreement checks.

</details>

---

**Q8: What is RLHF and how is it related to production fine-tuning?**

<details>
<summary>💡 Show Answer</summary>

**A:** RLHF (Reinforcement Learning from Human Feedback) is the training technique used to align large language models with human preferences. It's how models like ChatGPT, Claude, and Gemini are made helpful, harmless, and honest — and it's relevant to fine-tuning because the same principles apply when you want to fine-tune toward quality preferences rather than just format.

**RLHF in training (simplified):**
1. Fine-tune the base model on demonstration data (good responses) — this is standard SFT
2. Collect human preference data: show two model responses, human picks which is better
3. Train a "reward model" to predict human preferences from these comparisons
4. Use reinforcement learning (PPO) to fine-tune the model to maximize the reward model's score
5. Result: model that produces outputs humans prefer, not just outputs that match training examples

**Why it matters for production fine-tuning:**
For most production use cases, you do supervised fine-tuning (SFT), not full RLHF — RLHF is expensive and complex. But you can use a simplified version:

**Direct Preference Optimization (DPO)** — a simpler, more stable alternative to RLHF that:
- Takes (prompt, chosen_response, rejected_response) triplets instead of a separate reward model
- Directly optimizes the model to prefer the chosen response
- No separate reward model needed; more stable than PPO
- Increasingly common in production fine-tuning

When you'd use DPO in production:
- You have human comparison data (A is better than B)
- You want to fine-tune for quality, not just format
- You have cases where multiple valid responses exist and you want to guide toward the better ones

```python
# DPO training data format
{"prompt": "Explain quantum computing",
 "chosen": "Quantum computing uses quantum bits (qubits) that can exist in multiple states...",
 "rejected": "Quantum computing is just a faster version of regular computers..."}
```

Libraries: `trl` (Transformer Reinforcement Learning) from HuggingFace implements DPO, PPO, and SFT with minimal boilerplate.

</details>

---

## 📂 Navigation
