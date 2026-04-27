# Proximal Policy Optimization (PPO)

## The Story 📖

Imagine you're learning to ski. You're making progress — small improvements each run. Then one day you try to take a massive shortcut: you point your skis straight down the steepest slope, hoping to learn a lot at once. You crash spectacularly and forget everything you'd learned.

Early policy gradient algorithms had this problem. A large gradient update could completely destroy a policy that had taken thousands of episodes to learn. One bad update and you're back to random behavior.

PPO is like a ski instructor who won't let you make a turn that's too steep. It says: "You can improve your technique this run, but I'm going to clip how extreme any single adjustment is. Small, safe steps every time."

👉 This is **PPO (Proximal Policy Optimization)** — a policy gradient algorithm with a built-in guardrail that prevents catastrophically large policy updates.

---

## 📌 Learning Priority

**Must Learn** — core concepts, needed to understand the rest of this file:
[What is PPO](#what-is-ppo) · [Clipped Objective](#the-clipped-objective) · [Probability Ratio](#the-probability-ratio-explained)

**Should Learn** — important for real projects and interviews:
[Full PPO Loss](#the-full-ppo-loss) · [PPO and RLHF](#ppo-and-rlhf) · [Real AI Systems](#where-youll-see-this-in-real-ai-systems)

**Good to Know** — useful in specific situations, not needed daily:
[PPO vs TRPO](#ppo-vs-trpo) · [GAE](#generalized-advantage-estimation-gae)

**Reference** — skim once, look up when needed:
[Common Mistakes](#common-mistakes-to-avoid-) · [Connection to Other Concepts](#connection-to-other-concepts-)

---

## What is PPO?

**PPO** (Schulman et al., 2017) is an on-policy actor-critic algorithm that stabilizes policy gradient training through a **clipped surrogate objective**. It ensures that the updated policy doesn't deviate too far from the old policy in any single training step.

PPO became the default choice for RL in 2017 and remains the most widely used algorithm today. It is the optimizer used in RLHF pipelines to fine-tune language models.

Three key ideas:
1. **Clipped objective** — caps how much the policy can change per update.
2. **Multiple epochs** — reuses collected data for several gradient steps (more sample efficient than pure REINFORCE).
3. **Combined loss** — optimizes policy, value function, and entropy together.

---

## Why It Exists — The Problem It Solves

Vanilla policy gradients (REINFORCE, basic actor-critic) suffer from **training instability**:

**Problem 1: Large updates destroy the policy.** If the learning rate is too high, a single gradient step can change the policy dramatically. A policy that previously walked successfully might suddenly run in circles.

**Problem 2: Finding the right learning rate is hard.** Too small → slow learning. Too large → policy catastrophe. The "right" size changes throughout training.

**Problem 3: TRPO works but is too complex.** Trust Region Policy Optimization (the predecessor) solved instability by constraining the KL divergence between old and new policy. But TRPO requires second-order optimization (computing the Hessian), which is slow and hard to implement. PPO achieves similar stability with a simple first-order method.

---

## How It Works — Step by Step

```mermaid
flowchart TD
    COL[Collect N steps of experience\nusing current policy π_old]
    COL --> GAE[Compute advantages A_t\nusing GAE with λ=0.95]
    GAE --> EPOCH[For K epochs:\nShuffle into minibatches]
    EPOCH --> RATIO[Compute probability ratio:\nr_t·θ· = π_θ·a_t|s_t· / π_old·a_t|s_t·]
    RATIO --> CLIP[Compute clipped objective:\nL_CLIP = min·r_t·θ··A_t, clip·r_t·θ·,1-ε,1+ε··A_t·]
    CLIP --> LOSS[Combined loss:\nL = -L_CLIP + c1·L_VF - c2·entropy]
    LOSS --> UPDATE[Gradient update on policy and value network]
    UPDATE --> CHECK{Done\nN steps?}
    CHECK -- No --> EPOCH
    CHECK -- Yes --> COL

    style COL fill:#2c3e50,color:#fff
    style RATIO fill:#8e44ad,color:#fff
    style CLIP fill:#e74c3c,color:#fff
    style UPDATE fill:#27ae60,color:#fff
```

---

## The Key Innovation: The Clipped Objective

The standard policy gradient objective (REINFORCE-style) is:
```
L_PG(θ) = E[ r_t(θ) · A_t ]
```

where `r_t(θ) = π_θ(a_t|s_t) / π_old(a_t|s_t)` is the **probability ratio** between the new and old policy.

If r_t > 1, the new policy is more likely to take this action than the old policy.
If r_t < 1, the new policy is less likely.

**The problem:** if A_t is positive and we maximize by increasing r_t, there's no limit — the policy can change arbitrarily.

**PPO's clipped objective:**
```
L_CLIP(θ) = E[ min( r_t(θ)·A_t,  clip(r_t(θ), 1-ε, 1+ε)·A_t ) ]
```

The `clip` function limits r_t to the range [1-ε, 1+ε] (typically ε = 0.2).

The `min` of the two terms means:
- **When A_t > 0** (good action): increase r_t, but stop at 1+ε. Don't reinforce too aggressively.
- **When A_t < 0** (bad action): decrease r_t, but stop at 1-ε. Don't suppress too aggressively.

In both cases, the objective is **pessimistic** — it takes the minimum, which prevents overconfident updates.

---

## The Probability Ratio Explained

```
r_t(θ) = π_θ(a_t | s_t) / π_old(a_t | s_t)
```

- r_t = 1: new policy assigns the same probability to this action as old policy — no change.
- r_t = 1.5: new policy is 50% more likely to take this action.
- r_t = 0.5: new policy is 50% less likely to take this action.

PPO clips r_t to [0.8, 1.2] when ε = 0.2. The new policy can't become more than 20% more or less likely to take any particular action per update.

---

## The Full PPO Loss

```
L_PPO(θ) = L_CLIP(θ) - c₁·L_VF(θ) + c₂·S[π_θ](s_t)
```

Three components:

| Term | What it is | Why it's included |
|---|---|---|
| `L_CLIP` | Clipped policy gradient | Update policy safely |
| `-c₁·L_VF` | Value function loss (MSE) | Train the critic to estimate V(s) better |
| `+c₂·S[π_θ]` | Entropy bonus | Encourage exploration; prevent premature convergence |

Typical values: c₁ = 0.5, c₂ = 0.01.

The entropy bonus adds `H(π) = -Σ_a π(a|s) · log π(a|s)` to the objective. Maximizing entropy encourages the policy to remain diverse (not collapse to a deterministic strategy prematurely).

---

## PPO vs TRPO

| | TRPO | PPO |
|---|---|---|
| Constraint | Hard KL divergence constraint | Soft clip on probability ratio |
| Optimization | Second-order (Hessian) | First-order (Adam) |
| Implementation | Complex (conjugate gradients, line search) | Simple (just clip and minimize) |
| Performance | Slightly better in theory | Comparable in practice, much simpler |
| Use today | Rarely used | Default RL algorithm |

PPO's genius is achieving TRPO-like stability with first-order gradients, making it 10x simpler to implement.

---

## PPO and RLHF

PPO is the algorithm that fine-tunes language models in RLHF (Reinforcement Learning from Human Feedback). The connection:

- **Policy** = the language model (e.g., GPT-4, Claude)
- **Action** = next token to generate
- **State** = conversation history
- **Reward** = score from a reward model trained on human preferences
- **Old policy** = the supervised fine-tuned (SFT) model

The clipped objective is critical here: without it, the LLM would drift far from the SFT model in a few gradient steps, losing all the behavior learned during pretraining. The clip keeps the LLM "proximal" to the SFT model — hence the name.

---

## The Math / Technical Side (Simplified)

**Generalized Advantage Estimation (GAE):**
```
δ_t = r_t + γ·V(s_{t+1}) - V(s_t)           (TD residual)
A_t = δ_t + (γλ)·δ_{t+1} + (γλ)²·δ_{t+2} + ...
```

λ = 0.95 is the standard. It interpolates between one-step TD (λ=0) and Monte Carlo (λ=1).

**Policy update (one step):**
```
ratio = π_new(a|s) / π_old(a|s)
clipped_ratio = clip(ratio, 1-ε, 1+ε)
L_CLIP = min(ratio * A, clipped_ratio * A)
θ ← θ + α · ∇_θ L_CLIP
```

---

## Where You'll See This in Real AI Systems

- **RLHF pipelines** — InstructGPT, ChatGPT, Claude all trained with PPO or PPO variants.
- **OpenAI gym benchmarks** — MuJoCo continuous control (Ant, HalfCheetah, Humanoid).
- **Game playing** — OpenAI Five (Dota 2) used PPO for all agents.
- **Robotics** — Standard choice for continuous robot control.
- **Default in stable-baselines3** — The most recommended library's default algorithm.

---

## Common Mistakes to Avoid ⚠️

**Setting ε too large.** ε = 0.5 defeats the purpose — the clip range is too wide to provide stability. ε = 0.1 to 0.2 is standard.

**Too few rollout steps before update.** PPO needs enough data for meaningful advantage estimation. Typical: 2,048 steps per update for continuous control tasks.

**Too many epochs (K).** If you train for 20 epochs on the same data, the policy drifts far from the old policy despite clipping, which breaks the clipping guarantee. K = 3 to 10 is typical.

**Not using GAE.** Using raw Monte Carlo returns for advantage estimation introduces much higher variance. GAE with λ = 0.95 is standard.

**Forgetting the entropy bonus.** Without entropy regularization, PPO policies often become deterministic too quickly, especially on simple environments, leading to suboptimal policies.

---

## Connection to Other Concepts 🔗

- **Policy Gradients** — PPO is a policy gradient method; it builds directly on REINFORCE and actor-critic.
- **TRPO** — PPO's predecessor; PPO achieves similar stability with simpler implementation.
- **Actor-Critic** — PPO is an actor-critic method; it has both a policy network and a value network.
- **RLHF** — PPO is the RL algorithm in RLHF; the "proximal" constraint prevents LLM collapse.
- **DPO** — Direct Preference Optimization, a simpler alternative to PPO for RLHF that avoids RL entirely.

---

✅ **What you just learned:**
- PPO prevents catastrophically large policy updates through a clipped objective.
- The clip constrains the probability ratio r_t(θ) = π_new/π_old to [1-ε, 1+ε].
- PPO outperforms TRPO in practical terms while being far simpler to implement.
- PPO is the default RL algorithm and the optimizer behind RLHF in modern LLMs.

🔨 **Build this now:**
Run the stable-baselines3 PPO code in `Code_Example.md` on LunarLander. It should learn to land successfully in about 200,000 steps. Compare to the DQN result on the same environment to see the training curve difference.

➡️ **Next step:** `../07_RL_in_Practice/Theory.md` — learn the practical skills needed to actually make RL work: debugging, reward shaping, and choosing the right algorithm.


---

## 📝 Practice Questions

- 📝 [Q93 · ppo](../../ai_practice_questions_100.md#q93--interview--ppo)


---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference + hyperparameters |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Clipped objective with numbers |
| [📄 Code_Example.md](./Code_Example.md) | PPO on LunarLander |

⬅️ **Prev:** [Policy Gradients](../05_Policy_Gradients/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [RL in Practice](../07_RL_in_Practice/Theory.md)
