# Policy Gradients — Interview Q&A

## Beginner Level

**Q1: What is a policy gradient method?**

<details>
<summary>💡 Show Answer</summary>

A: A policy gradient method directly optimizes the policy — the function that maps states to actions — using gradient ascent on expected reward. Instead of learning a value function (like Q-Learning does) and deriving actions from it, policy gradient methods parameterize the policy as a neural network and compute gradients that say: "move the policy parameters in this direction to increase expected reward." The most basic algorithm is REINFORCE.

</details>

---

<br>

**Q2: Why would you use policy gradients instead of DQN?**

<details>
<summary>💡 Show Answer</summary>

A: Three main reasons:
1. **Continuous action spaces.** DQN outputs one Q-value per discrete action — you can't have one value per every possible torque level. Policy gradients output a probability distribution over continuous actions naturally.
2. **Stochastic policies.** DQN produces deterministic policies (argmax). Some tasks require randomization (e.g., poker, adversarial environments). Policy gradients produce stochastic policies naturally.
3. **Direct optimization.** Policy gradients optimize the objective you care about (return) directly. DQN optimizes a Q-value approximation and hopes the policy follows.

</details>

---

<br>

**Q3: What is the REINFORCE algorithm?**

<details>
<summary>💡 Show Answer</summary>

A: REINFORCE is the simplest policy gradient algorithm:
1. Run a complete episode using the current policy.
2. For each step t, compute the return G_t (discounted total future reward from that step).
3. For steps where G_t was high, increase the probability of that action in that state.
4. For steps where G_t was low, decrease it.

The update rule: θ ← θ + α · Σ_t [G_t · ∇_θ log π_θ(a_t | s_t)].

The key insight: if an action led to high return, reinforce it. If it led to low return, suppress it. The `log π` term is a mathematical trick that lets us compute gradients through the randomness.

</details>

---

## Intermediate Level

**Q4: What is the baseline in policy gradients and why doesn't it bias the gradient?**

<details>
<summary>💡 Show Answer</summary>

A: A baseline b(s_t) is a value subtracted from the return before multiplying by the gradient:
```
θ ← θ + α · Σ_t [(G_t - b(s_t)) · ∇_θ log π_θ(a_t | s_t)]
```

The baseline reduces variance by centering the updates — instead of "action a led to return 8" (is that good or bad?), we say "action a led to return 3 above baseline" (now we know it's good).

Why doesn't it bias the gradient? Because E[b(s_t) · ∇_θ log π_θ(a_t|s_t)] = 0 — the baseline times the log-gradient has zero expected value, so it doesn't change the direction of the gradient on average. This is a consequence of the score function identity.

</details>

---

<br>

**Q5: What is Actor-Critic and how does it improve on REINFORCE?**

<details>
<summary>💡 Show Answer</summary>

A: REINFORCE uses Monte Carlo returns: you must wait until the episode ends to compute G_t. This is unbiased but has high variance (different episodes give very different returns).

Actor-Critic uses two networks: an actor (the policy) and a critic (a value function V(s)). The critic can compute an estimate of future return at every step without waiting for the episode to end. The advantage A_t = r_t + γ·V(s_{t+1}) - V(s_t) (the TD residual) is used instead of G_t.

Benefits: lower variance (critic provides a stable baseline), online updates (no waiting for episode end), and faster learning.

</details>

---

<br>

**Q6: What is the advantage function and why is it used?**

<details>
<summary>💡 Show Answer</summary>

A: The advantage A(s, a) = Q(s, a) - V(s) measures how much better action a is compared to the average action in state s. It answers: "Was this action better or worse than what I'd normally expect in this situation?"

It's used because raw returns G_t vary enormously across episodes. The advantage is a more stable signal: it's centered around 0 (average advantage is 0 by definition) and measures relative quality. Multiplying by advantage makes the gradient update focus on "which actions were better than average" rather than "which actions were in episodes with high total return."

</details>

---

## Advanced Level

**Q7: What is the policy gradient theorem and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

A: The policy gradient theorem provides the exact form of ∇_θ J(θ):
```
∇_θ J(θ) = E_π[ Q^π(s,a) · ∇_θ log π_θ(a|s) ]
```

Why it matters: computing ∇_θ J(θ) naively would require differentiating through the entire MDP, including transition dynamics P — which we don't know. The theorem shows that this complex gradient equals a much simpler quantity: an expectation over the log-gradient of the policy weighted by Q-values. No P required. This makes policy gradient methods practical — you can estimate the gradient from sampled trajectories.

</details>

---

<br>

**Q8: What are the trade-offs between on-policy and off-policy methods in the context of policy gradients?**

<details>
<summary>💡 Show Answer</summary>

A: Policy gradient methods like REINFORCE and PPO are **on-policy**: they can only use data generated by the current policy. Once you update the policy, old data becomes invalid (it came from a different distribution). This makes them sample-inefficient — each collected trajectory is used once and discarded.

The benefit of on-policy: the gradient estimate is unbiased. The cost: you need lots of fresh data.

Off-policy methods (DQN, SAC) can reuse old data via replay buffers, making them more sample-efficient. The challenge: using old data from a different policy to estimate the current policy's gradient requires importance sampling corrections, which can have high variance. Algorithms like SAC and TD3 manage this for actor-critic settings.

</details>

---

<br>

**Q9: What is Generalized Advantage Estimation (GAE) and why is it used in PPO?**

<details>
<summary>💡 Show Answer</summary>

A: GAE (Schulman et al., 2015) provides a family of advantage estimators parameterized by λ ∈ [0,1]:

```
A_t^GAE(λ) = Σ_{l=0}^{∞} (γλ)^l · δ_{t+l}
where δ_t = r_t + γV(s_{t+1}) - V(s_t)
```

When λ = 0: A_t = r_t + γV(s_{t+1}) - V(s_t) — the one-step TD residual (low variance, high bias).
When λ = 1: A_t = G_t - V(s_t) — the full return minus baseline (low bias, high variance).

λ interpolates between these extremes. λ = 0.95 is the standard PPO setting — it provides a good bias-variance trade-off. It's used in PPO because it produces more stable and reliable advantage estimates than either pure MC or pure TD.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Policy gradient theorem |
| [📄 Code_Example.md](./Code_Example.md) | REINFORCE on CartPole |

⬅️ **Prev:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [PPO](../06_PPO/Theory.md)
