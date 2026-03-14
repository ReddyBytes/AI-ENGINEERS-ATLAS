# PPO — Cheatsheet

## PPO in One Paragraph

PPO collects N steps of experience, computes advantages using GAE, then runs K epochs of gradient updates — but clips the probability ratio r_t = π_new/π_old to [1-ε, 1+ε] to prevent large policy changes. It trains the policy and value function together with a combined loss, plus an entropy bonus for exploration.

---

## The Clipped Objective

```
r_t(θ) = π_θ(a_t | s_t) / π_old(a_t | s_t)   ← probability ratio

L_CLIP(θ) = E[ min(
    r_t(θ) · A_t,
    clip(r_t(θ), 1-ε, 1+ε) · A_t
) ]
```

Intuition:
- If A_t > 0 (good action): maximize r_t but cap at 1+ε.
- If A_t < 0 (bad action): minimize r_t but cap at 1-ε.
- The `min` makes the objective pessimistic — prevents overconfident updates.

---

## Full PPO Loss

```
L_total = -L_CLIP  +  c₁ · L_VF  -  c₂ · H(π)
```

| Term | Formula | Typical weight |
|---|---|---|
| `L_CLIP` | Clipped policy gradient (maximize) | weight = 1.0 |
| `L_VF` | (V(s) - G_t)² — value function MSE (minimize) | c₁ = 0.5 |
| `H(π)` | Entropy of policy (maximize for exploration) | c₂ = 0.01 |

Note: we minimize the total loss, so L_CLIP is negated.

---

## PPO Hyperparameters

| Parameter | Typical value | Effect |
|---|---|---|
| **Clip ε** | 0.1 – 0.2 | Policy change cap per update |
| **GAE λ** | 0.95 | Advantage estimation smoothing |
| **Discount γ** | 0.99 | Future reward weighting |
| **N steps per update** | 2,048 – 8,192 | Rollout length before update |
| **K epochs per update** | 3 – 10 | Gradient steps per collected data |
| **Minibatch size** | 64 – 256 | Samples per gradient step |
| **Learning rate** | 2.5e-4 – 3e-4 | Typically constant or linearly decayed |
| **Entropy coefficient c₂** | 0.01 | Exploration encouragement |
| **Value function coeff c₁** | 0.5 | Value loss weight |
| **Max grad norm** | 0.5 | Gradient clipping |

---

## GAE (Generalized Advantage Estimation)

```
δ_t = r_t + γ·V(s_{t+1}) - V(s_t)            ← TD residual
A_t = δ_t + (γλ)·δ_{t+1} + (γλ)²·δ_{t+2} + ...
```

| λ | Estimator | Property |
|---|---|---|
| 0 | One-step TD | Low variance, high bias |
| 1 | Full Monte Carlo | Low bias, high variance |
| 0.95 | GAE default | Good bias-variance trade-off |

---

## PPO Training Loop Summary

```
1. Collect N steps using current policy π_old
2. Compute returns G_t and advantages A_t using GAE
3. Normalize advantages: A_t = (A_t - mean) / std
4. For K epochs:
     - Shuffle experience into minibatches
     - For each minibatch:
         compute ratio r = π_new/π_old
         compute L_CLIP, L_VF, entropy
         backprop and update
5. π_old ← π_new
6. Repeat from step 1
```

---

## PPO vs Other Algorithms

| Algorithm | Action space | Policy | Key strength |
|---|---|---|---|
| DQN | Discrete | Deterministic | Sample efficiency for games |
| REINFORCE | Both | Stochastic | Simple but high variance |
| A2C | Both | Stochastic | Online, synchronous AC |
| PPO | Both | Stochastic | Stable, default choice |
| SAC | Continuous | Stochastic | Off-policy, entropy-based |
| TRPO | Both | Stochastic | Theoretically justified |

---

## When to Use PPO

| Use PPO when | Consider alternatives when |
|---|---|
| Standard starting point for any RL task | Discrete actions, many timesteps → DQN |
| Continuous control (robotics) | Extreme sample efficiency needed → SAC/model-based |
| RLHF for language models | Simple enough for bandit algorithms |
| Stable training is critical | Already using stable-baselines3 which defaults to PPO |

---

## Golden Rules

1. ε = 0.2 is a safe default clip range.
2. K = 4–10 epochs. More than 10 defeats the proximal constraint.
3. Always use GAE (λ = 0.95) — raw MC returns have too much variance.
4. Normalize advantages per minibatch.
5. Monitor the entropy — if it collapses to near 0 early, increase c₂.
6. Monitor the ratio — if max ratio regularly exceeds 1.5, reduce lr or ε.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Clipped objective with numbers |
| [📄 Code_Example.md](./Code_Example.md) | PPO on LunarLander |

⬅️ **Prev:** [Policy Gradients](../05_Policy_Gradients/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [RL in Practice](../07_RL_in_Practice/Theory.md)
