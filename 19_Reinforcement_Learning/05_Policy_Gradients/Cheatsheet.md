# Policy Gradients — Cheatsheet

## Core Idea

```
Value-based: Learn Q(s,a) → pick action = argmax Q
Policy-based: Directly learn π_θ(a|s) → action = sample from π
```

---

## Key Algorithms

| Algorithm | Type | Key feature |
|---|---|---|
| **REINFORCE** | Monte Carlo policy gradient | Simple; high variance; uses full episode returns |
| **REINFORCE + baseline** | REINFORCE with variance reduction | Subtracts V(s) from returns |
| **A2C / A3C** | Actor-Critic | Online updates; critic provides baseline |
| **PPO** | Clipped Actor-Critic | Stable training; used in RLHF |
| **SAC** | Off-policy Actor-Critic | Adds entropy; great for continuous control |

---

## REINFORCE Update Rule

```
θ ← θ + α · Σ_t [ G_t · ∇_θ log π_θ(a_t | s_t) ]
```

With baseline:
```
θ ← θ + α · Σ_t [ (G_t - b(s_t)) · ∇_θ log π_θ(a_t | s_t) ]
```

Where b(s_t) = V(s_t) = estimated state value.

---

## The Log Trick (Score Function Estimator)

```
∇_θ E[f(x)] = E[ f(x) · ∇_θ log p_θ(x) ]
```

In RL terms:
```
∇_θ J(θ) = E_π[ G_t · ∇_θ log π_θ(a_t|s_t) ]
```

The `log π` gradient tells us: "which direction to move θ to make action a_t more likely in state s_t."

---

## Actor-Critic Structure

```
State s_t
   ├─→ Actor π_θ(a|s)  → action probabilities → sample action a_t
   └─→ Critic V_φ(s)   → scalar value estimate V(s_t)

Advantage: A_t = r_t + γ·V(s_{t+1}) - V(s_t)   (TD residual)

Actor update:  θ ← θ + α · A_t · ∇_θ log π_θ(a_t|s_t)
Critic update: φ ← φ - β · ∇_φ (A_t)²
```

---

## Loss Functions in Code

```python
# Actor loss (minimize → maximize J)
actor_loss = -torch.mean(log_probs * advantages)

# Critic loss
critic_loss = torch.mean((returns - values) ** 2)

# Combined loss (common in actor-critic)
total_loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy
```

Why entropy term? Encourages the policy to remain exploratory (not collapse to deterministic).

---

## Variance Reduction Techniques

| Technique | Mechanism | Benefit |
|---|---|---|
| Baseline | Subtract V(s) from returns | Reduces variance, no bias change |
| Advantage normalization | Normalize advantages per batch | Stabilizes training |
| Multiple rollouts | Average gradient over many trajectories | Reduces noise |
| GAE (Generalized Advantage Estimation) | Blend n-step returns | Bias-variance trade-off |

---

## On-Policy vs Off-Policy

| | Policy Gradients (REINFORCE, PPO) | Q-Learning (DQN) |
|---|---|---|
| Uses old data? | No — on-policy only | Yes — off-policy |
| Replay buffer? | No (PPO uses small buffer within update) | Yes |
| Action space | Discrete or continuous | Discrete only |
| Stochastic policy | Natural | Must add noise manually |

---

## Quick Hyperparameter Guide

| Parameter | Typical value |
|---|---|
| Learning rate (actor) | 1e-4 – 3e-4 |
| Learning rate (critic) | 1e-4 – 1e-3 |
| Discount γ | 0.99 |
| Entropy coefficient | 0.01 |
| GAE λ | 0.95 |
| Gradient clip | 0.5 |

---

## Golden Rules

1. Always use a baseline — raw REINFORCE is too noisy for practical use.
2. Normalize advantages per batch (subtract mean, divide by std).
3. Clip gradients — policy gradient updates can explode.
4. Policy gradient methods are on-policy — don't mix data from different policies.
5. For continuous actions: output mean and std, sample from Gaussian.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Policy gradient theorem |
| [📄 Code_Example.md](./Code_Example.md) | REINFORCE on CartPole |

⬅️ **Prev:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [PPO](../06_PPO/Theory.md)
