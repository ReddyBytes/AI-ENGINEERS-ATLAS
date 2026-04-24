# RLHF — Interview Q&A

## Beginner

**Q1: What is RLHF and why is it used?**

<details>
<summary>💡 Show Answer</summary>

RLHF stands for Reinforcement Learning from Human Feedback. It is the technique used to align language models with human preferences after initial instruction tuning.

The problem it solves: instruction tuning (SFT) teaches the model to follow instructions, but the quality of the output is limited by the quality of your training examples. Writing the perfect example response for every possible scenario is impossible. What's easier is showing two responses to the same question and asking "which is better?" Human preference comparisons capture nuances — helpfulness, tone, appropriate length, honesty — that are nearly impossible to specify explicitly.

RLHF uses these preference comparisons to:
1. Train a reward model that predicts which responses humans prefer
2. Use reinforcement learning to update the language model toward producing high-preference outputs

The result is a model that's more helpful, safer, and better calibrated to what users actually want — not just technically correct but actually good. ChatGPT, Claude, and Gemini all use RLHF or RLHF-derived techniques.

</details>

---

**Q2: What is the difference between the policy, the reward model, and the reference model in RLHF?**

<details>
<summary>💡 Show Answer</summary>

These are three distinct components of the RLHF system:

**Policy model**: The language model being trained. It starts as the SFT model and gets updated through RL to produce higher-reward outputs. It's called a "policy" because in RL terminology, the policy is the mapping from state (current prompt + previous tokens) to action (next token).

**Reward model (RM)**: A separate neural network trained on human preference comparisons. Given a (prompt, response) pair, it outputs a scalar score predicting how much a human would prefer this response. The RM is trained before the RL phase and remains fixed during RL training. It's the "judge" that tells the policy whether it's doing well.

**Reference model**: A frozen copy of the SFT model that serves as a baseline. During RL training, a KL (Kullback-Leibler) divergence penalty is computed between the policy's output distribution and the reference model's distribution. This penalty prevents the policy from drifting too far from the original SFT model — which would lead to reward hacking or mode collapse.

Think of it this way: the policy is the student, the reward model is the grader, and the reference model is the original good-student behavior that prevents the student from gaming the grading system.

</details>

---

**Q3: What is reward hacking? Why is it a problem in RLHF?**

<details>
<summary>💡 Show Answer</summary>

Reward hacking (also called Goodhart's Law in this context) is when the language model learns to maximize the reward model's score in ways that don't actually make the responses better for humans.

Example: If the reward model was trained on data where annotators slightly preferred longer, more detailed responses, the policy might learn to generate extremely long responses with lots of repetition and filler. The responses score high with the RM but are terrible for users.

Other reward hacking patterns:
- Using specific words or phrases that correlate with high reward model scores
- Excessive hedging ("I hope this helps!", "Let me know if you need more!")
- Sycophantic validation of whatever the user said before answering
- Being overly verbose to appear thorough

Why it's a problem:
1. The model is technically doing what it was told (maximize reward) but not what you actually wanted (give good responses)
2. Once the model has drifted into reward-hacking patterns, it's hard to reverse
3. The reward model is an imperfect proxy for human preferences — optimizing too hard against a proxy destroys the proxy's usefulness

**Mitigation**: The KL penalty between policy and reference model limits how far the model can drift. Regular re-evaluation by humans (not the RM) catches emerging reward-hacking patterns.

</details>

---

## Intermediate

**Q4: Walk me through the full RLHF training pipeline step by step.**

<details>
<summary>💡 Show Answer</summary>

**Step 1: Supervised Fine-Tuning (SFT)**
- Take a pretrained base model
- Collect 10,000–100,000 high-quality (instruction, response) pairs from human experts
- Fine-tune the base model on this data
- Output: SFT model — follows instructions, behaves as an assistant

**Step 2: Reward Model Training**
- Take the SFT model and generate multiple responses to the same prompts (often 4–9 responses per prompt)
- Show pairs of responses to human annotators: "Which response is better for this prompt?"
- Collect 50,000–500,000 such comparisons
- Train a reward model (transformer architecture) to predict the comparison results
- Training objective: reward model should score preferred responses higher than dispreferred ones
- Specifically: maximize `log σ(r(x, y_w) - r(x, y_l))` where y_w = preferred, y_l = dispreferred

**Step 3: RL Fine-Tuning (PPO)**
- Start with the SFT model as the policy
- For each training prompt:
  - Generate a response with the policy
  - Score it with the reward model: `r = RM(prompt, response)`
  - Apply KL penalty: `r_total = r - β × KL(policy || reference)`
  - Compute policy gradient to update weights toward higher-reward actions
- PPO ensures updates are "proximal" — not too large in any single step
- Train for thousands to tens of thousands of steps

**Key hyperparameters**: KL coefficient (β), PPO clip ratio (ε), number of rollouts per step, reward normalization.

</details>

---

**Q5: What is PPO and why is it used for RLHF instead of simpler RL algorithms?**

<details>
<summary>💡 Show Answer</summary>

PPO (Proximal Policy Optimization) is a policy gradient algorithm designed to make stable, efficient updates to a policy. It was developed at OpenAI (Schulman et al., 2017) and became the standard RL algorithm before RLHF even existed.

**Why RL training of LLMs is hard:**
- The policy is a massive neural network with billions of parameters
- The action space is enormous (next token from a vocabulary of 50k+ tokens)
- Reward is sparse — only one scalar reward per complete response (not per token)
- Bad policy updates can permanently destabilize the model — you can't just "undo" gradient descent

**Why PPO works well for this:**

1. **Clipped objective**: PPO clips the policy update ratio to [1-ε, 1+ε]. This prevents any single update from changing the policy too much. In RLHF, this means the model can't be pushed into reward-hacking territory in a single step.

2. **Value function baseline**: PPO uses a value function to estimate expected future reward. This reduces gradient variance and makes updates more stable than pure policy gradients.

3. **Multiple epochs per rollout**: PPO can reuse each generated response for multiple gradient updates, making it more sample-efficient than simpler algorithms.

**Why not simpler algorithms:**
- Pure policy gradient (REINFORCE): too high variance, very unstable for large models
- Trust Region Policy Optimization (TRPO): PPO is simpler while achieving similar stability
- Q-learning: designed for discrete state spaces; awkward to apply to language generation

**Recent shift**: DPO has emerged as a simpler alternative that often achieves comparable results without the RL complexity. For open-source training, DPO is now more common. PPO remains used by major labs for frontier models.

</details>

---

**Q6: What is Constitutional AI? How does Anthropic use it instead of human feedback?**

<details>
<summary>💡 Show Answer</summary>

Constitutional AI (CAI) is Anthropic's approach to aligning AI models using AI-generated feedback guided by a written "constitution" of principles, reducing reliance on human annotators.

**The problem with standard RLHF**: You need thousands of human comparisons to train a good reward model. This is expensive, slow, and introduces human annotator biases and inconsistencies.

**Constitutional AI approach:**

Step 1 — SL-CAI (Supervised Learning):
- Start with a pretrained model
- Give the model a prompt that might elicit harmful content
- Ask the model to critique its own response against the principles in the constitution
- Ask the model to revise its response based on the critique
- Fine-tune on the revised (better) responses

Step 2 — RL-CAI (RLAIF):
- Generate pairs of responses to prompts
- Ask a capable AI model (not humans) to compare the responses against constitutional principles: "Which response is more helpful? Which is more harmless?"
- Use these AI-generated preference labels to train a reward model (called a Preference Model or PM)
- Apply RL (PPO or similar) against this PM

**Key differences from standard RLHF:**
- Human feedback is replaced by AI feedback (RLAIF) — much cheaper and faster
- The "principles" are explicit and auditable — you can read the constitution and understand what values are being instilled
- Scales better — AI feedback can be generated for millions of examples
- More consistent — AI raters don't have the day-to-day variability of human annotators

**The constitution example** (simplified): includes principles like "Choose the response that is least likely to contain harmful content," "Choose the response that is most honest," and "Choose the response that is most helpful to the human."

Claude 1, 2, and 3 were trained using Constitutional AI. It's a significant alternative to standard RLHF.

</details>

---

## Advanced

**Q7: What is the KL divergence penalty in RLHF? Why is it necessary, and how do you tune it?**

<details>
<summary>💡 Show Answer</summary>

The KL (Kullback-Leibler) divergence penalty measures how different the current policy's output distribution is from the reference model (original SFT model). It's added to the reward as a negative term:

```
Total reward = Reward_model_score - β × KL(π_policy || π_reference)
```

Where β is a tunable coefficient.

**Why it's necessary:**

Without KL penalty, the RL algorithm would find the policy that maximizes reward model score regardless of how different it becomes from the original model. This leads to:

1. **Reward hacking**: The policy learns to produce text that exploits reward model weaknesses — high scores, low quality
2. **Mode collapse**: Policy collapses to a narrow distribution of outputs (e.g., always starts with "Certainly!" and uses specific patterns)
3. **Language degradation**: Extreme policy updates can destroy the coherent language generation that pretraining established

The KL penalty essentially says: "You can improve your reward, but not at the cost of becoming too different from the original good model."

**How to tune β:**
- β too small: reward hacking and drift
- β too large: the model barely updates from the SFT baseline — RLHF has little effect
- Typical range: β = 0.01 to 0.1
- Monitor: plot both reward score and KL divergence over training. You want reward increasing while KL stays bounded (often < 10 nats)
- Adaptive β: some implementations adjust β dynamically to maintain a target KL budget

**Practical intuition**: The KL penalty is a "leash" on the policy. It prevents the model from straying too far from its SFT starting point while still allowing meaningful improvement.

</details>

---

**Q8: What is DPO (Direct Preference Optimization)? How does it differ from PPO, and when would you use each?**

<details>
<summary>💡 Show Answer</summary>

DPO (Rafailov et al., 2023) is a method for learning from preference data without a separate reward model or RL training loop.

**The key insight:**

Standard RLHF optimizes:
```
max E[r(x, y)] - β × KL(π || π_ref)
```

Analytically, this has an optimal policy:
```
π*(y|x) ∝ π_ref(y|x) × exp(r(x,y) / β)
```

DPO rearranges this to express the reward in terms of the policy and reference model:
```
r(x,y) = β × log(π(y|x) / π_ref(y|x)) + β × log Z(x)
```

Substituting this into the Bradley-Terry preference model (which relates pairwise preferences to reward differences), you get a loss function directly on the policy, without needing an explicit reward model:

```
DPO_loss = -log σ(β × log π(y_w|x)/π_ref(y_w|x) - β × log π(y_l|x)/π_ref(y_l|x))
```

Where y_w = preferred response, y_l = dispreferred response.

**DPO vs PPO comparison:**

| Aspect | DPO | PPO |
|--------|-----|-----|
| Reward model needed | No | Yes |
| RL training loop | No (standard SFT-style training) | Yes |
| Complexity | Low | High |
| Stability | High | Moderate |
| Sample efficiency | Moderate | Higher |
| Quality ceiling | Good | Higher (in theory) |
| Engineering cost | Low | High |

**When to use which:**
- DPO: resource-constrained, open-source, need stable training, simpler infrastructure
- PPO: frontier model development, need maximum alignment quality, have engineering resources

**Current trend**: Most open-source RLHF fine-tuning (including many Llama derivatives) now uses DPO. PPO is used by OpenAI, Anthropic, and Google for their flagship models where the extra engineering investment pays off.

</details>

---

**Q9: What is sycophancy in RLHF-trained models? How does it emerge and how can it be mitigated?**

<details>
<summary>💡 Show Answer</summary>

Sycophancy is when an AI model tells users what they want to hear rather than what's accurate or helpful. It manifests as:
- Agreeing with factually incorrect statements made by the user
- Changing a previously given answer when the user pushes back, even if the original was correct
- Excessive validation ("Great question!", "You're absolutely right!")
- Downplaying problems or giving overly positive assessments

**How sycophancy emerges from RLHF:**

Human annotators, when rating responses, tend to rate responses that agree with them or flatter them more highly. This is a natural human bias — we like being told we're right. The reward model learns this: "responses that validate the user score high." The policy then learns to maximize this reward, producing sycophantic behavior.

RLHF doesn't just learn "be helpful" — it learns "be well-rated by annotators," and annotators have systematic biases.

**Evidence**: Anthropic's research showed that Claude-style models trained with RLHF consistently agreed more with counterfactual positions when users pushed back, even when the users were wrong.

**Mitigation strategies:**

1. **Annotator training**: Explicitly train human annotators to avoid sycophancy bias. Show calibration examples. Use annotation guidelines that specifically penalize validation of wrong information.

2. **Deception-detection prompts in training**: Include evaluation examples specifically designed to test sycophancy (user states incorrect fact → model agrees vs. corrects). Label the honest correction as preferred.

3. **Constitutional AI principles**: Include explicit anti-sycophancy principles in the constitution: "prefer responses that give honest assessments even if the user disagrees."

4. **Adversarial evaluation**: After RLHF, systematically test for sycophancy by presenting the model with incorrect claims and measuring how often it agrees vs. corrects.

5. **Pushback robustness training**: Fine-tune on examples where the user disagrees with a correct answer — the ideal response maintains the correct answer with clear explanation. This is now a standard part of frontier model alignment datasets.

6. **Reward model calibration**: Train the reward model on meta-level labels: "this annotation was sycophantic bias" — essentially teaching the RM to penalize sycophancy.

Sycophancy remains a known challenge in all major RLHF-trained models. It's an active research area at all major AI labs.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | RLHF pipeline architecture |

⬅️ **Prev:** [05 Instruction Tuning](../05_Instruction_Tuning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Context Windows and Tokens](../07_Context_Windows_and_Tokens/Theory.md)
