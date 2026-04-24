# RLHF — Interview Q&A

## Beginner

**Q1: What problem does RLHF solve? Why isn't pretraining alone enough?**

<details>
<summary>💡 Show Answer</summary>

A pretrained language model is good at continuing text in the style it was trained on. If you ask it "How do I do X?", it might output a continuation that looks like a how-to document — but that's not the same as actually answering helpfully, honestly, and safely.

Pretrained models:
- Can continue harmful content in harmful styles (since harmful content exists in training data)
- Optimize for "sounds like plausible training data" not "is genuinely helpful"
- Have no concept of what humans prefer — they just predict next tokens

RLHF solves this by introducing a feedback loop: actual humans rate the model's responses, and the model is updated to produce responses that humans rate higher. This teaches the model what "good" means in practice — not just textbook plausibility.

</details>

---

<br>

**Q2: What is a reward model and how is it trained?**

<details>
<summary>💡 Show Answer</summary>

A reward model is a neural network that takes a (prompt, response) pair as input and outputs a score predicting how much a human would prefer that response.

Training process:
1. Run the SFT model on many prompts to generate multiple responses
2. Human labelers rank the responses: "Response A > Response B > Response C"
3. Convert rankings into pairwise comparisons: (A, B, A preferred), (A, C, A preferred), (B, C, B preferred)
4. Train the reward model to predict these rankings using a Bradley-Terry pairwise loss

The reward model is essential because running the RL loop requires scoring millions of model-generated responses. Human labelers can't evaluate millions of responses — the reward model acts as an automated proxy.

</details>

---

<br>

**Q3: What is PPO and why is it used in RLHF?**

<details>
<summary>💡 Show Answer</summary>

PPO (Proximal Policy Optimization) is a reinforcement learning algorithm that updates the policy (the LLM) to maximize the expected reward while preventing updates that are too large.

The "proximal" part is key: PPO clips the policy update to ensure the new policy doesn't diverge too far from the previous one. In the RLHF context, there's an additional KL divergence penalty that keeps the model close to the SFT baseline.

Why PPO specifically:
- Stable training — more reliable than older RL methods like vanilla policy gradient
- Can handle the high-dimensional action space (vocabulary of 100k tokens)
- The clip and KL mechanisms prevent catastrophic forgetting or reward gaming
- Proven to work at LLM scale (originally validated by OpenAI's work on InstructGPT)

</details>

---

## Intermediate

**Q4: What is Goodhart's Law and how does it apply to reward hacking in RLHF?**

<details>
<summary>💡 Show Answer</summary>

Goodhart's Law states: "When a measure becomes a target, it ceases to be a good measure."

In RLHF, the reward model is a proxy for human preferences. When the language model optimizes hard against this proxy, it can learn behaviors that score well on the reward model without actually being what humans want.

Examples of reward hacking:
- Generating longer responses (if human labelers unconsciously preferred longer answers)
- Adopting overly formal or deferential tone (which might correlate with "safe" in the training data)
- Confident, fluent-sounding responses that are factually wrong (confidence scored well)
- Adding disclaimers everywhere because labelers preferred "responsible" sounding outputs

Mitigation strategies:
- KL divergence penalty (prevents the policy from diverging too far from SFT)
- Diverse prompt distributions (makes it harder to hack a specific pattern)
- Ensemble of reward models (harder to simultaneously game multiple models)
- Periodic human evaluation as a check on the proxy reward

</details>

---

<br>

**Q5: What is DPO and how does it differ from PPO-based RLHF?**

<details>
<summary>💡 Show Answer</summary>

Direct Preference Optimization (DPO) is a simpler approach that achieves similar results to RLHF without a separate reward model or RL loop.

The key insight: the optimal RLHF policy has a mathematical relationship to the reference (SFT) policy. DPO rearranges the optimization objective so you can directly optimize the language model on preference pairs.

Comparison:
- RLHF with PPO: train reward model → run RL loop → update LLM (three separate stages, high complexity)
- DPO: directly update LLM using preference pairs, similar to supervised learning (one stage, much simpler)

In practice:
- DPO is what most open-source fine-tuning pipelines use (Hugging Face TRL library has DPO trainer)
- Many research papers show DPO competitive with or better than PPO on standard benchmarks
- Commercial labs (Anthropic, OpenAI) use more complex setups that may combine both approaches

</details>

---

<br>

**Q6: What is sycophancy in LLMs and how does RLHF cause it?**

<details>
<summary>💡 Show Answer</summary>

Sycophancy is when a model tells people what they want to hear rather than what is accurate or useful. It manifests as:
- Agreeing with the user's incorrect statement when they express it confidently
- Changing its answer when a user pushes back, even without new evidence
- Over-complimenting user work rather than giving honest feedback
- Adapting its position to match cues about the user's preferences

The RLHF cause: human labelers tend to rate responses that agree with them more highly. If you ask a labeler to choose between "you're right, the capital is Vienna" and "actually, the capital is Prague," the agreeable response might score higher — even when the user was wrong.

The reward model learns this pattern. The RL optimization then pushes the LLM toward sycophantic outputs because they maximize reward.

Mitigations:
- Include adversarial prompts in training data where agreeing is clearly wrong
- Reward "sticks to its position when challenged without new evidence"
- Include factual accuracy checking in the reward signal

</details>

---

## Advanced

**Q7: How does the KL divergence term in PPO prevent reward model gaming, and what happens if it's too small or too large?**

<details>
<summary>💡 Show Answer</summary>

The PPO objective in RLHF is:

```
Objective = E[RM(response)] - β × KL(π_RL || π_SFT)
```

The KL term penalizes the distance between the RL-fine-tuned policy (π_RL) and the SFT reference policy (π_SFT). Intuitively: "maximize reward, but don't drift too far from where we started."

If β is too small (KL penalty too weak):
- The model aggressively optimizes for reward
- Discovers exploits: e.g., generating all-capital-letters text, extreme verbosity, repetitive safe phrases
- Forgets what it learned during SFT (catastrophic forgetting)
- Outputs become fluent but detached from actual helpfulness

If β is too large (KL penalty too strong):
- The model barely moves from the SFT starting point
- RLHF has little effect on behavior
- Safety and helpfulness improvements from the RL stage are minimal

Typical β values: 0.01–0.1. The right value is found empirically and depends on the quality of the reward model and the desired degree of alignment change. Anthropic and others treat this as a sensitive hyperparameter in production training runs.

</details>

---

<br>

**Q8: How does multi-stage RLHF training relate to Constitutional AI, and which limitations of RLHF does CAI address?**

<details>
<summary>💡 Show Answer</summary>

RLHF has two key bottlenecks:

1. **Human annotation throughput**: You can only generate preference data as fast as humans can evaluate responses. At frontier model scale, this is the limiting factor.

2. **Inconsistency**: Different human labelers have different values, cultural backgrounds, and interpretations of "good." The reward model absorbs these inconsistencies.

Constitutional AI (CAI) addresses both:

1. **Throughput**: Instead of humans evaluating responses, the model itself critiques and revises its own outputs against a written constitution. Millions of (critique, revision) pairs can be generated without human annotation.

2. **Consistency**: The constitution is a fixed document. All "labeling" is done by the model applying the same principles — no inter-labeler variance.

The resulting AI Feedback (AIFF) can replace much of the Human Feedback (HF) in RLHF → CAI is sometimes called RLAIF (Reinforcement Learning from AI Feedback).

Anthropic uses a combination: RLHF for helpfulness and general quality, CAI for harmlessness specifically. The constitution covers principles like "don't help with bioweapons" that would be difficult to get consistent labeling on.

</details>

---

<br>

**Q9: How would you evaluate whether a RLHF-trained model has improved compared to the SFT baseline?**

<details>
<summary>💡 Show Answer</summary>

Evaluation of RLHF improvement requires multiple approaches because a single benchmark is gameable:

1. **Held-out human evaluation**: Have a separate pool of human evaluators (not involved in training) rate SFT vs RLHF responses on a diverse prompt set. This is the gold standard but expensive.

2. **Win rate on preference pairs**: Use a held-out reward model (different from the training RM) to compare SFT vs RLHF responses. Win rate > 50% indicates improvement.

3. **Targeted capability benchmarks**:
   - Helpfulness: does the model answer questions more accurately? (TruthfulQA)
   - Harmlessness: does it refuse more appropriately? (custom red-teaming datasets)
   - Honesty: does it calibrate uncertainty correctly?

4. **Red-teaming**: Does the RLHF model still jailbreak on the same prompts? Are new jailbreaks discovered?

5. **Regression testing**: Does the RLHF model retain capability on standard benchmarks (MMLU, HumanEval, GSM8K)? RLHF sometimes hurts raw capability — this needs monitoring.

6. **Sycophancy test**: Present the model with a factual question and then "I think the answer is [wrong answer]." Does the RLHF model agree more than the SFT model? (It often does — sycophancy regression is a common RLHF failure.)

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full RLHF pipeline |

⬅️ **Prev:** [05 Pretraining](../05_Pretraining/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Constitutional AI](../07_Constitutional_AI/Theory.md)
