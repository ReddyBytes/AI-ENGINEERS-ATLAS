# RLHF — Cheatsheet

**One-liner:** RLHF trains a reward model from human preference comparisons, then uses reinforcement learning (PPO) to optimize the language model toward outputs humans prefer — making it helpful, safe, and honest.

---

## Key terms

| Term | What it means |
|------|---------------|
| RLHF | Reinforcement Learning from Human Feedback |
| SFT | Supervised Fine-Tuning — Step 1 of RLHF: instruction tune the base model |
| Reward model (RM) | Neural network trained to score (prompt, response) pairs by predicted human preference |
| Policy | The LLM being trained via RL — starts as the SFT model |
| PPO | Proximal Policy Optimization — the RL algorithm used to update the policy |
| KL penalty | Constraint penalizing the policy for diverging too far from the SFT reference model |
| Reward hacking | Model learns to fool the reward model (high score, low quality) |
| RLAIF | RL from AI Feedback — replace human raters with an AI model |
| DPO | Direct Preference Optimization — skip reward model, optimize directly on preferences |
| Constitutional AI | Anthropic's approach: use AI + written principles to replace human raters |
| Preference pairs | Training data for reward model: (prompt, response_A, response_B, which is better) |
| Policy gradient | RL technique: update policy to increase probability of high-reward actions |
| Helpful/Harmless/Honest | The three "H" objectives of Anthropic's alignment approach |

---

## RLHF 3-step pipeline

| Step | What happens | Output |
|------|-------------|--------|
| 1. SFT | Instruction-tune base model on high-quality examples | SFT model (the starting policy) |
| 2. Reward model | Collect human comparisons → train reward model | RM: scores (prompt, response) → scalar |
| 3. PPO | Use RM to reward policy; update policy with RL + KL penalty | Aligned model |

---

## RLHF vs alternatives

| Method | Reward signal | Complexity | Stability | Quality |
|--------|--------------|-----------|-----------|---------|
| RLHF (PPO) | Human comparisons | High | Moderate | High |
| RLAIF | AI comparisons | Medium | Moderate | Good |
| DPO | Human comparisons (no RM needed) | Low | High | Good |
| Constitutional AI | AI + principles | Medium | High | Good |
| SFT only | Example responses | Low | High | Moderate |

---

## What RLHF fixes

| Problem | How RLHF helps |
|---------|----------------|
| Unhelpful verbose responses | Humans prefer concise, direct answers → RM learns this |
| Harmful content | Humans rate harmful content very low → policy avoids it |
| Sycophancy (after too much RLHF) | Ironically can make it worse if not careful |
| False confidence | Humans prefer calibrated hedging → model learns to say "I'm not sure" |
| Refusal to answer benign questions | Humans prefer helpful answers → model learns not to over-refuse |

---

## RLHF limitations

| Limitation | Why it matters |
|------------|----------------|
| Reward hacking | Model games the RM — produces fluent, high-scoring but unhelpful text |
| Human bias | RM inherits annotator biases (e.g., preference for confident-sounding answers) |
| Annotation cost | 50k–200k human comparisons needed |
| Coverage gaps | RM may not generalize to unusual prompts |
| Sycophancy | Models over-optimized with RLHF become "yes-machines" that tell people what they want to hear |
| KL divergence | Too much RL diverges from SFT quality — needs careful balancing |

---

## DPO vs PPO

```
PPO (RLHF):
  preference data → train reward model → RL training loop → policy update

DPO:
  preference data → directly fine-tune policy (no reward model step)

DPO loss: minimize log P(preferred) / P(dispreferred) with a temperature parameter
```

DPO is simpler and increasingly used in open-source models. PPO has a higher ceiling but is harder to stabilize.

---

## Golden rules

1. RLHF builds on SFT — you can't skip instruction tuning and go straight to RLHF
2. Reward hacking is real — always include a KL penalty to the SFT reference model
3. The reward model is only as good as your human annotators — garbage preferences → garbage alignment
4. More RL doesn't always mean better — over-optimization leads to sycophancy and degradation
5. DPO is the simpler alternative — prefer it for open-source / resource-limited settings
6. Constitutional AI / RLAIF allows scalable alignment without bottlenecking on human rater throughput

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | RLHF pipeline architecture |

⬅️ **Prev:** [05 Instruction Tuning](../05_Instruction_Tuning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Context Windows and Tokens](../07_Context_Windows_and_Tokens/Theory.md)
