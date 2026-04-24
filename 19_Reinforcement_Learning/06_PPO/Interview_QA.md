# PPO — Interview Q&A

## Beginner Level

**Q1: What problem does PPO solve?**

<details>
<summary>💡 Show Answer</summary>

A: PPO solves the training instability of vanilla policy gradient methods. In algorithms like REINFORCE, a single large gradient update can completely destroy a policy that took thousands of episodes to build — the agent reverts to near-random behavior. PPO prevents this with a clipped objective that limits how much the policy changes in any single update step. The "Proximal" in PPO means "close to" — the new policy must stay close (proximal) to the old one.

</details>

---

**Q2: What is the probability ratio in PPO?**

<details>
<summary>💡 Show Answer</summary>

A: The probability ratio r_t(θ) = π_θ(a_t|s_t) / π_old(a_t|s_t) compares how likely the current (new) policy is to take a specific action vs how likely the old policy was. If r_t = 1, no change. If r_t = 1.5, the new policy is 50% more likely to take that action. If r_t = 0.7, it's 30% less likely. PPO clips this ratio to [1-ε, 1+ε] (usually [0.8, 1.2]) so the policy can't change too drastically in one update.

</details>

---

**Q3: What does "clipping" do in PPO?**

<details>
<summary>💡 Show Answer</summary>

A: When computing the policy gradient, we'd normally reward actions proportionally to their advantage (how much better they were than expected). Without clipping, this could cause us to massively increase the probability of a lucky action in one update, completely destabilizing the policy.

Clipping caps the probability ratio at [1-ε, 1+ε]. For ε = 0.2, the new policy can only become 20% more or less likely to take any action per update. The `min` in the objective ensures the update is pessimistic — it never lets the policy confidently over-commit to any direction.

</details>

---

## Intermediate Level

**Q4: What are the three components of the PPO loss?**

<details>
<summary>💡 Show Answer</summary>

A:
1. **L_CLIP** — the clipped policy gradient loss. Maximizing this improves the policy while staying near the old policy.
2. **L_VF** — the value function loss (MSE between predicted and actual returns). Training the critic so advantage estimates improve over time.
3. **Entropy bonus** — a term that maximizes the policy's entropy (action distribution spread). Prevents the policy from becoming deterministic too quickly, which would stop exploration.

Combined: L = -L_CLIP + c₁·L_VF - c₂·H(π)

</details>

---

**Q5: How does PPO differ from TRPO?**

<details>
<summary>💡 Show Answer</summary>

A: Both PPO and TRPO constrain the policy update to prevent large changes. TRPO uses a hard constraint: the KL divergence between old and new policy must not exceed a fixed threshold δ. Enforcing this constraint requires second-order optimization (computing the Fisher information matrix, conjugate gradient, backtracking line search) — complex and slow.

PPO uses a soft approximation: it clips the probability ratio instead of directly constraining KL divergence. This is a first-order method (works with standard Adam optimizer) and is much simpler to implement. In practice, PPO achieves similar performance to TRPO with far less complexity. TRPO is mostly of historical interest now.

</details>

---

**Q6: What is GAE and why is it used in PPO?**

<details>
<summary>💡 Show Answer</summary>

A: GAE (Generalized Advantage Estimation) is a way to compute advantage estimates that balances bias and variance. The advantage A_t = G_t - V(s_t) can be estimated multiple ways:

- One-step: A_t = r_t + γ·V(s_{t+1}) - V(s_t) — low variance, but biased if V is wrong.
- Full Monte Carlo: A_t = G_t - V(s_t) — unbiased, but high variance.

GAE interpolates between these using λ ∈ [0,1]:
```
A_t^GAE = Σ (γλ)^k · δ_{t+k}   where δ_t = r_t + γV(s_{t+1}) - V(s_t)
```

λ = 0.95 is the PPO default — it gives low variance advantage estimates with mild bias, which is the sweet spot for stable training.

</details>

---

## Advanced Level

**Q7: Why does PPO use multiple epochs on the same data, and what limit should you set?**

<details>
<summary>💡 Show Answer</summary>

A: PPO collects N steps of data (the rollout), then runs K epochs of gradient updates on that same data. This reuse makes PPO more sample-efficient than pure REINFORCE (which uses each sample once).

However, there's a tension: after the first epoch, the policy changes. By epoch K, the policy π_new might be significantly different from π_old, meaning the data (collected under π_old) is increasingly "off-policy." The clipping mechanism limits this drift, but it's not unlimited. If K is too large, the clipping bound is violated repeatedly and the proximal guarantee breaks down.

The typical limit is K = 3–10 epochs. A useful diagnostic: monitor the KL divergence between old and new policy during updates. If it consistently exceeds ~0.015–0.02, reduce K or reduce the learning rate.

</details>

---

**Q8: How is PPO applied to RLHF for language models?**

<details>
<summary>💡 Show Answer</summary>

A: In RLHF, PPO fine-tunes a language model (LM) using human preference data. The mapping:
- **Policy** = the LM being trained (parameter θ)
- **State** = the prompt + partial response so far
- **Action** = the next token to generate
- **Reward** = score from a separate reward model (trained on human comparisons) + KL penalty

The KL penalty (KL(π_θ || π_SFT)) penalizes the LM for diverging from the supervised fine-tuned (SFT) reference model. This serves as a form of PPO's proximal constraint — keeping the RLHF model from drifting too far from the base model's behavior. Without this constraint, the LM would "reward hack" by generating text that scores high on the reward model but is nonsensical or pathological.

</details>

---

**Q9: What are the most common failure modes in PPO training?**

<details>
<summary>💡 Show Answer</summary>

A:
1. **Entropy collapse** — the entropy bonus is too small; the policy becomes deterministic prematurely. Fix: increase c₂ (0.01 → 0.05) or use entropy scheduling.
2. **Value function lagging** — if the value network learns too slowly, advantage estimates are noisy. Fix: increase learning rate for critic or give it more updates per rollout.
3. **Gradient explosion** — policy gradient loss spikes; NaN values. Fix: ensure gradient clipping (max_norm = 0.5).
4. **Too many epochs** — KL divergence grows; clipping no longer effective. Fix: reduce K or add early stopping when KL exceeds threshold.
5. **Reward scale mismatch** — rewards range from -1000 to +1000 while value estimates are in [-10, 10]. Fix: normalize rewards or scale by a running mean/std.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Clipped objective with numbers |
| [📄 Code_Example.md](./Code_Example.md) | PPO on LunarLander |

⬅️ **Prev:** [Policy Gradients](../05_Policy_Gradients/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [RL in Practice](../07_RL_in_Practice/Theory.md)
