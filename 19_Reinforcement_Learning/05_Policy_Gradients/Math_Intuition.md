# Policy Gradients — Math Intuition

## The Policy Gradient Theorem — Explained Without Scary Notation

The key question: how do we compute the gradient of expected return with respect to policy parameters?

---

## The Problem

We want to maximize:
```
J(θ) = E_π[ G_0 ] = expected total return
```

If we knew J(θ) as a formula, we could take its derivative and do gradient ascent. But J(θ) is an expectation over an entire trajectory — it involves the environment's transition dynamics P(s'|s,a), which we don't know.

How do we compute ∇_θ J(θ) without knowing P?

---

## Step 1: The Log-Derivative Trick

For any probability distribution p_θ(x) and any function f(x):

```
∇_θ E[f(x)] = ∇_θ Σ_x p_θ(x) · f(x)
             = Σ_x f(x) · ∇_θ p_θ(x)
             = Σ_x f(x) · p_θ(x) · ∇_θ log p_θ(x)   ← multiply/divide by p_θ(x)
             = E_p[ f(x) · ∇_θ log p_θ(x) ]
```

The last step uses the fact that ∇ log p = (∇p)/p, so ∇p = p · ∇ log p.

Key: **We replaced ∇E[f] with E[f · ∇ log p]** — an expectation we can estimate with samples.

---

## Step 2: Apply to RL

In RL, the trajectory τ = (s_0, a_0, r_0, s_1, a_1, r_1, …) has probability:

```
p_θ(τ) = p(s_0) · Π_t [ π_θ(a_t|s_t) · P(s_{t+1}|s_t,a_t) ]
```

The policy terms are π_θ(a_t|s_t). The transition terms P(s_{t+1}|s_t,a_t) don't depend on θ.

Therefore:
```
∇_θ log p_θ(τ) = Σ_t ∇_θ log π_θ(a_t|s_t)   ← P terms vanish!
```

The environment's transition dynamics P **drop out** of the gradient. Only the log-probabilities of the policy's own actions remain.

---

## Step 3: The Policy Gradient Theorem

Applying the log-derivative trick to J(θ) = E_π[G(τ)]:

```
∇_θ J(θ) = E_π[ G(τ) · ∇_θ log p_θ(τ) ]
           = E_π[ G(τ) · Σ_t ∇_θ log π_θ(a_t|s_t) ]
           = E_π[ Σ_t G_t · ∇_θ log π_θ(a_t|s_t) ]
```

This is the policy gradient theorem. In words:

**"The gradient of expected return = the expected sum over steps of: (return from that step) times (gradient of log-probability of the chosen action)."**

No P(s'|s,a) anywhere. We only need:
- The returns G_t — computed from collected rewards.
- The log-probabilities log π_θ(a_t|s_t) — output by our policy network.
- The gradients ∇_θ log π — computed by standard backpropagation.

---

## Step 4: A Concrete Numerical Example

Suppose we have a one-step problem (no time horizon, just one action).

Policy: a neural network that outputs P(action=right) = 0.3, P(action=left) = 0.7.

Current parameters: θ (some values).

We run one episode:
- State s = "standing still"
- Network outputs: P(right) = 0.3, P(left) = 0.7
- We sample: action = right (got sampled despite lower probability)
- Reward: +5 (going right was good in this case)

The gradient of the log probability for "right":
```
∇_θ log π_θ(right | s)
```
This is the direction in θ-space that would increase P(right). PyTorch computes this automatically.

Update:
```
θ ← θ + α · G_t · ∇_θ log π_θ(right | s)
  = θ + 0.01 · 5 · ∇_θ log π_θ(right | s)
```

Effect: we nudge θ to make "right" more likely in state s — because it got a positive return (+5).

If instead reward was -3:
```
θ ← θ + 0.01 · (-3) · ∇_θ log π_θ(right | s)
```
We nudge θ to make "right" less likely — because it got a negative return.

---

## Step 5: Why Baselines Help

The return G_t can be +100 in good episodes and +5 in bad ones — both positive! Without a baseline, even the bad episode's actions get reinforced (G_t = +5 > 0 means "increase probability").

With a baseline V(s_t):
```
A_t = G_t - V(s_t)
```

If V(s) = 50 (expected return), and this episode gave G_t = 5:
- A_t = 5 - 50 = -45 → "this action was much worse than expected" → decrease probability.

If another episode gave G_t = 100:
- A_t = 100 - 50 = +50 → "this action was much better than expected" → increase probability.

The baseline centers the signal, making the gradient far less noisy.

**Mathematical proof it doesn't bias the gradient:**
```
E[b(s) · ∇ log π(a|s)] = Σ_s d(s) · b(s) · Σ_a π(a|s) · ∇ log π(a|s)
                        = Σ_s d(s) · b(s) · Σ_a ∇ π(a|s)
                        = Σ_s d(s) · b(s) · ∇ Σ_a π(a|s)
                        = Σ_s d(s) · b(s) · ∇ 1
                        = 0
```

Since Σ_a π(a|s) = 1 always, its gradient is 0. The baseline contributes zero to the expected gradient.

---

## Summary

| Step | What we did |
|---|---|
| Log-derivative trick | Replaced ∇E[G] with E[G · ∇ log p] |
| Applied to trajectories | Found that P(s'|s,a) drops out |
| Policy gradient theorem | ∇J(θ) = E[Σ_t G_t · ∇ log π_θ(a_t|s_t)] |
| Baseline | Subtract V(s) to reduce variance, zero bias change |
| In practice | Backprop through log π, multiply by advantage |

The entire theoretical foundation of REINFORCE, A2C, PPO, and RLHF rests on these steps.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Intuition.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | REINFORCE on CartPole |

⬅️ **Prev:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [PPO](../06_PPO/Theory.md)
