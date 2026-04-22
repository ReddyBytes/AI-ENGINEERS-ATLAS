# RLHF — Cheatsheet

**One-liner:** RLHF transforms a pretrained base model into a helpful assistant through three stages: supervised fine-tuning on human demonstrations, reward model training on human preference rankings, and PPO optimization to maximize reward while staying close to the SFT policy.

---

## Key terms

| Term | What it means |
|------|---------------|
| RLHF | Reinforcement Learning from Human Feedback — standard LLM alignment method |
| SFT | Supervised Fine-Tuning — first stage: train on human-written ideal responses |
| Reward Model (RM) | Neural network trained to predict which responses humans prefer |
| PPO | Proximal Policy Optimization — the RL algorithm used in Stage 3 |
| Policy | The LLM being trained — outputs responses given a prompt |
| KL divergence | Penalty keeping RL-trained model close to SFT model |
| Bradley-Terry model | Pairwise comparison model used to train the reward model |
| Goodhart's Law | "When a measure becomes a target, it ceases to be a good measure" |
| Reward hacking | Model learns to exploit the reward model, not genuinely improve |
| Sycophancy | Model tells humans what they want to hear instead of what's true |
| DPO | Direct Preference Optimization — simpler alternative to PPO-based RLHF |
| Constitutional AI | Anthropic's extension that replaces much of the human annotation |

---

## Three-stage pipeline

```
Stage 1 — SFT:
  Input: (prompt, ideal_response) pairs from human labelers
  Method: Standard supervised learning (cross-entropy loss)
  Output: SFT model — knows how to format helpful responses

Stage 2 — Reward Model:
  Input: (prompt, response_A, response_B, human_rank: A > B)
  Method: Bradley-Terry pairwise loss
  Output: RM — scores any response for how much humans would like it

Stage 3 — PPO:
  Loop:
    1. Generate response with current policy
    2. Score with reward model
    3. Compute KL penalty vs SFT policy
    4. Update policy to maximize (reward - β × KL)
  Output: Aligned model
```

---

## PPO objective

```
Objective = E[RM(response)] - β × KL(π_RL || π_SFT)

Where:
  E[RM(response)] = expected reward from the reward model
  KL(π_RL || π_SFT) = divergence from SFT policy (how far we've drifted)
  β = KL coefficient (typically 0.01–0.1)

Higher β = stay closer to SFT model = more conservative
Lower β = explore more = higher potential reward but more hacking risk
```

---

## DPO vs PPO

| Aspect | PPO-RLHF | DPO |
|--------|---------|-----|
| Reward model needed? | Yes — separate training | No |
| Implementation complexity | High | Low |
| Training stability | Can be unstable | More stable |
| Quality | State of the art | Comparable |
| Memory overhead | High (RM + policy + ref) | Lower |
| Reward hacking risk | Moderate | Lower |
| Used by | OpenAI, Anthropic (combined) | Many open-source models |

---

## DPO loss

```
DPO_loss = -log σ(β × log[π_θ(y_w|x)/π_ref(y_w|x)] 
                   - β × log[π_θ(y_l|x)/π_ref(y_l|x)])

Where:
  y_w = preferred response (winner)
  y_l = rejected response (loser)  
  π_θ = model being trained
  π_ref = reference model (SFT baseline)
  β = temperature controlling deviation from reference
```

---

## Known failure modes

| Failure | Cause | Mitigation |
|---------|-------|-----------|
| Reward hacking | Over-optimizing reward model | KL penalty; diverse prompts |
| Sycophancy | Agreeing with confident-sounding users | Adversarial prompts in training |
| Over-refusal | Labelers prefer "safe" responses | Explicitly reward helpfulness |
| Labeler inconsistency | Different labelers, different values | Clear labeler guidelines; multiple labels per example |
| Short answer bias | Short answers rated higher | Length-penalized reward model |

---

## Golden rules

1. RLHF changes behavior, not knowledge — it doesn't add facts, it changes what the model chooses to say
2. The SFT stage is critical — RL from the raw base model is unstable; SFT provides a solid starting point
3. The KL penalty is not optional — without it, the model will game the reward model
4. Too much RLHF causes sycophancy — the model learns to flatter, not inform
5. Reward model quality is the ceiling — RLHF can't exceed the quality of human judgment in the training data
6. DPO is simpler and often good enough — use PPO only when you need fine-grained control over the RL loop

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full RLHF pipeline |

⬅️ **Prev:** [05 Pretraining](../05_Pretraining/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Constitutional AI](../07_Constitutional_AI/Theory.md)
