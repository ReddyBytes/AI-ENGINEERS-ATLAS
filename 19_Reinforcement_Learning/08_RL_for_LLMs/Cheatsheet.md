# RL for LLMs — Cheatsheet

## The RLHF Pipeline (Three Stages)

```
Stage 1: SFT
  Pretrained LLM → fine-tune on human demonstrations → SFT Model

Stage 2: Reward Model
  SFT Model → generate multiple responses → humans rank them →
  train Reward Model: RM(prompt, response) → scalar score

Stage 3: RL Fine-Tuning
  SFT Model (starting point) + Reward Model (reward signal) →
  PPO training → Aligned LLM
```

---

## RLHF Objective

```
max_θ  E[r(x, y)] - β · KL( π_θ(·|x) || π_SFT(·|x) )
         ↑                    ↑
   Maximize reward     Stay close to SFT model
```

- `r(x, y)` = reward model score for (prompt x, response y)
- `β` = KL penalty weight (typically 0.1 – 0.5)
- Higher β → safer (more like SFT) but less improvement
- Lower β → more RL optimization but risk of reward hacking

---

## Reward Model Training

```
Loss = -E[ log σ( r(x, y_preferred) - r(x, y_dispreferred) ) ]
```

Bradley-Terry model: reward model learns to rank responses by human preference.

---

## DPO vs RLHF

| | RLHF (PPO) | DPO |
|---|---|---|
| Stages | 3 (SFT + RM + RL) | 2 (SFT + DPO loss) |
| Needs reward model? | Yes | No |
| Needs RL loop? | Yes | No (supervised loss only) |
| Stability | Tricky | Simple |
| Performance | Strong | Comparable |
| Implementation | Complex | ~20 lines |

**DPO loss:**
```python
# Simplified DPO loss
log_ratio_w = log_pi_new(y_win | x) - log_pi_ref(y_win | x)
log_ratio_l = log_pi_new(y_lose | x) - log_pi_ref(y_lose | x)
loss = -F.logsigmoid(beta * (log_ratio_w - log_ratio_l)).mean()
```

---

## Mapping RL Concepts to LLM Training

| RL Concept | LLM Context |
|---|---|
| Agent | The language model being trained |
| Environment | User prompts + human preferences |
| State | Conversation history + prompt + partial response |
| Action | Next token to generate |
| Policy | LM's probability distribution over next tokens |
| Reward | Reward model score (+ KL penalty) |
| Episode | One complete response generation |
| SFT model | Reference policy (π_ref) for KL constraint |

---

## The KL Penalty — Why It's Critical

Without KL penalty:
- LLM drifts far from SFT model in ~100 steps
- Generates repetitive/degenerate text that scores high on RM
- Catastrophic forgetting of original capabilities

With KL penalty:
- Policy stays proximal to SFT model
- Gradual, controlled improvement
- Preserves base model capabilities

**KL divergence between two policies:**
```
KL(π_new || π_ref) = Σ_t E[ log π_new(a_t|s_t) - log π_ref(a_t|s_t) ]
```

---

## Goodhart's Law in RLHF

> "When a measure becomes a target, it ceases to be a good measure."

In RLHF: the reward model is an imperfect proxy for human preferences. Heavy optimization finds ways to score highly that don't match human intent.

**Signs of reward hacking:**
- Reward model score high but human evaluation flat/declining
- Responses become longer without more useful content
- Model becomes sycophantic (always agrees with user)
- Model repeats certain phrases or structures that correlate with high scores

**Mitigations:**
1. KL penalty (keep policy close to SFT)
2. Use multiple reward models
3. Regular human evaluations throughout training
4. Constitutional AI (AI self-critique)
5. Stop training before reward diverges from human judgment

---

## RLHF Variants

| Method | Key feature |
|---|---|
| **InstructGPT / RLHF** | PPO + human preferences; original approach |
| **DPO** | No RL loop; directly maximize preference probability |
| **Constitutional AI** | AI-generated feedback instead of humans |
| **RLAIF** | Replace humans with AI judge entirely |
| **SLiC** | Sequence likelihood calibration — simpler than DPO |
| **ORPO** | Odds Ratio Preference Optimization — no SFT stage needed |
| **GRPO** | Group Relative Policy Optimization (used in DeepSeek-R1) |

---

## Golden Rules

1. Always do SFT before RL — a raw pretrained model is a poor RL starting point.
2. Always use a KL penalty — without it, the model collapses in training.
3. The reward model is a proxy, not ground truth — watch for reward hacking.
4. Run human evaluations during RLHF training — reward model score is not enough.
5. β is your most important hyperparameter — tune it before anything else.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Connection_to_RLHF.md](./Connection_to_RLHF.md) | How PPO applies to LLMs |

⬅️ **Prev:** [RL in Practice](../07_RL_in_Practice/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** Section complete!
