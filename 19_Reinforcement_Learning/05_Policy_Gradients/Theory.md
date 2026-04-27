# Policy Gradients

## The Story 📖

Imagine you're learning to throw a basketball. You don't first build a mental model of every possible shot angle and speed and score them all (that's the value-based approach). Instead, you just throw the ball, see if it goes in, and if it does, you think: "Do more of that." You're directly adjusting your throwing technique — the policy — based on outcomes.

DQN learns the value of every (state, action) pair and then derives a policy from it. Policy gradients skip the value function entirely and optimize the policy directly — like adjusting your throwing technique based on whether the ball went in.

👉 This is **Policy Gradients** — directly optimizing the policy using gradients of expected reward.

---

## 📌 Learning Priority

**Must Learn** — core concepts, needed to understand the rest of this file:
[What is Policy Gradient](#what-is-a-policy-gradient-method) · [REINFORCE Algorithm](#reinforce--the-simplest-policy-gradient-algorithm) · [Advantage and Baselines](#the-high-variance-problem-and-baselines)

**Should Learn** — important for real projects and interviews:
[Actor-Critic Architecture](#actor-critic-combining-policy-and-value) · [Policy Gradient Theorem](#the-policy-gradient-theorem-intuition-only) · [Real AI Systems](#where-youll-see-this-in-real-ai-systems)

**Good to Know** — useful in specific situations, not needed daily:
[Value-Based vs Policy Gradient](#policy-gradients-vs-value-based-methods) · [Common Mistakes](#common-mistakes-to-avoid-)

**Reference** — skim once, look up when needed:
[Connection to Other Concepts](#connection-to-other-concepts-)

---

## What is a Policy Gradient Method?

A **policy gradient method** parameterizes the policy as a neural network with parameters θ, and directly adjusts those parameters to maximize expected return using gradient ascent.

The policy network outputs **action probabilities** given a state:
```
π_θ(a | s) = probability of taking action a in state s
```

Training goal: find θ that maximizes:
```
J(θ) = E_π[ G_t ] = expected total return under policy π_θ
```

We do this by computing the gradient ∇_θ J(θ) and ascending it.

---

## Why It Exists — The Problem It Solves

Value-based methods (Q-Learning, DQN) have three limitations:

1. **Discrete actions only.** Q-values are defined per action, so you need a finite list of actions. For a robot with continuous joint torques, there's no action list — you need to output a real number.
2. **Deterministic policies.** Argmax Q(s,·) always picks the same action in a given state. Some problems require **stochastic policies** (randomization is optimal — e.g., in poker you shouldn't be predictable).
3. **No direct policy optimization.** DQN learns Q-values and hopes that leads to a good policy. Policy gradients directly optimize what we care about: the policy.

Policy gradients handle continuous and discrete actions, naturally produce stochastic policies, and optimize the objective directly.

---

## How It Works — Step by Step

```mermaid
flowchart TD
    INIT[Initialize policy network π_θ\nwith random weights θ]
    INIT --> EP[Run one full episode\nusing π_θ]
    EP --> TRAJ[Collect trajectory:\ns_0,a_0,r_0 · s_1,a_1,r_1 · ... · s_T,a_T,r_T]
    TRAJ --> RETURN[Compute return G_t for each step:\nG_t = r_t + γ·r_{t+1} + γ²·r_{t+2} + ...]
    RETURN --> GRAD[Compute gradient:\n∇_θ J ≈ Σ_t G_t · ∇_θ log π_θ·a_t|s_t·]
    GRAD --> UPDATE[Update: θ ← θ + α · ∇_θ J]
    UPDATE --> CHECK{Converged?}
    CHECK -- No --> EP
    CHECK -- Yes --> DONE[Done]

    style INIT fill:#2c3e50,color:#fff
    style TRAJ fill:#8e44ad,color:#fff
    style RETURN fill:#e67e22,color:#fff
    style GRAD fill:#e74c3c,color:#fff
    style UPDATE fill:#27ae60,color:#fff
```

---

## REINFORCE — The Simplest Policy Gradient Algorithm

**REINFORCE** (Williams, 1992) is the foundational policy gradient algorithm:

1. Run a complete episode using the current policy.
2. For each step t, compute the return G_t (total future reward from that step).
3. For each step, compute the gradient: G_t · ∇_θ log π_θ(a_t | s_t).
4. Sum over all steps and update θ.

The intuition:
- If G_t is high (good outcome), we **increase** the probability of action a_t in state s_t.
- If G_t is low (bad outcome), we **decrease** that probability.
- The `log π` part is just the gradient of the log probability — it tells us which direction to move θ.

The update rule:
```
θ ← θ + α · Σ_t [ G_t · ∇_θ log π_θ(a_t | s_t) ]
```

---

## The Policy Gradient Theorem (Intuition Only)

The policy gradient theorem proves that:
```
∇_θ J(θ) = E_π[ G_t · ∇_θ log π_θ(a_t | s_t) ]
```

Why `log π` instead of `π`? Taking the gradient of log π is a mathematical trick (the "log-derivative trick" or "score function estimator") that lets us compute the gradient even though G_t involves future states we haven't seen yet. It's covered in `Math_Intuition.md`.

---

## The High Variance Problem and Baselines

REINFORCE has one big practical problem: **high variance**. The return G_t varies enormously between episodes. This means the gradient estimate is noisy — the parameters jump around wildly and training is slow.

**Solution: subtract a baseline b(s_t).**

Instead of multiplying by G_t, multiply by (G_t - b(s_t)) — the **advantage**: how much better was this action than what we'd normally expect?

```
θ ← θ + α · Σ_t [ (G_t - b(s_t)) · ∇_θ log π_θ(a_t | s_t) ]
```

The baseline doesn't change the expected gradient (a mathematical fact) but dramatically reduces variance. The most common baseline is V(s_t) — the estimated value of the current state.

When the baseline is V(s), the term (G_t - V(s_t)) is called the **advantage** A_t: "This action turned out to be A_t better (or worse) than I expected."

---

## Actor-Critic: Combining Policy and Value

REINFORCE waits until the end of an episode to compute returns. This is called **Monte Carlo** — unbiased but high variance.

**Actor-Critic** methods use two networks:
- **Actor** (π_θ) — the policy network; decides what action to take.
- **Critic** (V_φ) — a value function network; estimates how good each state is.

The critic provides a baseline after every step, not just at episode end. This enables:
- **Lower variance** — the baseline is always available.
- **Online updates** — no need to wait for episode completion.
- **Temporal difference learning** — the critic can be updated with TD targets.

```mermaid
flowchart LR
    S[State s_t]
    S --> ACTOR[Actor π_θ\nOutputs action probabilities]
    S --> CRITIC[Critic V_φ\nOutputs state value V·s·]
    ACTOR -->|action a_t| ENV[Environment]
    ENV -->|r_t, s_{t+1}| ADV[Advantage\nA_t = r_t + γV·s_{t+1}· - V·s_t·]
    CRITIC --> ADV
    ADV -->|update gradient| ACTOR
    ADV -->|TD error| CRITIC

    style ACTOR fill:#2980b9,color:#fff
    style CRITIC fill:#8e44ad,color:#fff
    style ENV fill:#e67e22,color:#fff
```

---

## The Math / Technical Side (Simplified)

**The update:**
```
Actor loss:   L_actor = -Σ_t A_t · log π_θ(a_t | s_t)
Critic loss:  L_critic = Σ_t (G_t - V_φ(s_t))²
```

Why negative sign in actor loss? Because PyTorch minimizes losses, but we want to maximize expected return. Negating turns ascent into descent.

**Advantage estimation:**
```
Simple:    A_t = G_t - V(s_t)               (returns - baseline)
TD(0):     A_t = r_t + γ·V(s_{t+1}) - V(s_t)  (one-step TD residual)
GAE:       A_t = weighted mixture of n-step returns (used in PPO)
```

---

## Where You'll See This in Real AI Systems

- **OpenAI's game-playing agents** — A3C and PPO (both actor-critic) power most of OpenAI's RL achievements.
- **Robotics** — Policy gradients naturally handle continuous action spaces (joint torques, gripper forces).
- **RLHF** — PPO (a policy gradient algorithm) is the optimizer used to fine-tune language models on human feedback.
- **Dialogue systems** — Policy gradient agents that directly optimize for conversation quality.
- **Continuous control benchmarks** — MuJoCo environments (HalfCheetah, Ant, Humanoid) are the standard testbed, all requiring continuous actions.

---

## Policy Gradients vs Value-Based Methods

| | Value-Based (DQN) | Policy Gradients (PPO/REINFORCE) |
|---|---|---|
| Learns | Q-function → derives policy | Policy directly |
| Action space | Discrete only | Discrete or continuous |
| Policy type | Deterministic (argmax) | Stochastic (probabilities) |
| On/off policy | Off-policy | Usually on-policy |
| Variance | Lower | Higher (mitigated by baselines) |
| Sample efficiency | Higher | Lower (typically) |

---

## Common Mistakes to Avoid ⚠️

**Running REINFORCE without a baseline.** Raw REINFORCE has extremely high variance. Always use at least a simple baseline (the mean return of the episode, or a learned value function).

**Using a too-large learning rate.** Policy gradient updates can be large. A single bad update can completely destroy the policy. Start with α = 1e-3 or smaller.

**Confusing policy gradient with policy evaluation.** The policy gradient updates the policy. Evaluating the policy (computing J(θ)) is a different, separate operation.

**Forgetting that REINFORCE is on-policy.** You can only use experiences generated by the current policy. Unlike DQN, you can't reuse old experiences directly.

**Not normalizing advantages.** Normalizing advantages per batch (subtract mean, divide by std) is a critical practical trick for stable training.

---

## Connection to Other Concepts 🔗

- **DQN** — The value-based alternative; better for discrete actions, less so for continuous.
- **PPO** — The modern, production-grade policy gradient algorithm; adds a clipping mechanism to prevent unstable updates.
- **Actor-Critic** — The family of methods combining a policy network (actor) and value network (critic).
- **RLHF** — Uses PPO (a policy gradient method) to fine-tune language models on human preference data.
- **Advantage function** — The key quantity used by most modern policy gradient methods: A(s,a) = Q(s,a) - V(s).

---

✅ **What you just learned:**
- Policy gradients directly optimize the policy by gradient ascent on expected return.
- REINFORCE: collect a full episode, compute returns, nudge action probabilities toward high-reward actions.
- High variance is the main problem — baselines and actor-critic methods address this.
- Policy gradients work for continuous action spaces; value-based methods don't.

🔨 **Build this now:**
Run the REINFORCE code in `Code_Example.md` on CartPole. Watch the training curve. Then disable the baseline (set `use_baseline=False`) and compare the variance. Notice how much noisier the training curve becomes without the baseline.

➡️ **Next step:** `../06_PPO/Theory.md` — learn PPO, the practical algorithm that fixes the remaining instabilities in policy gradients.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Policy gradient theorem explained |
| [📄 Code_Example.md](./Code_Example.md) | REINFORCE on CartPole |

⬅️ **Prev:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [PPO](../06_PPO/Theory.md)
