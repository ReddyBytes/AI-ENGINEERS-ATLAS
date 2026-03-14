# Q-Learning — Interview Q&A

## Beginner Level

**Q1: What does Q stand for in Q-Learning?**

A: Q stands for "Quality" — the quality of taking a particular action in a particular state. Q(s, a) represents how good it is (in terms of expected future reward) to take action a when you're in state s. Formally it's the action-value function, but "quality" is the intuition.

---

**Q2: What is a Q-table?**

A: A Q-table is a lookup table with one row per state and one column per action. Each cell Q(s, a) stores the current estimate of the expected future reward from taking action a in state s. At the start, all values are 0 (or small random numbers). As the agent explores, the values get updated to reflect experience. When training is done, the agent acts by looking up the row for its current state and picking the action with the highest value.

---

**Q3: What is epsilon-greedy and why is it used?**

A: Epsilon-greedy is a strategy for balancing exploration (trying new things) and exploitation (using what you know). With probability ε, the agent picks a random action (explores). With probability 1-ε, it picks the action with the highest Q-value (exploits). It's used because a purely greedy agent would never discover actions it hasn't tried — it would get stuck in a suboptimal policy. A purely random agent would never improve. Epsilon-greedy gives a simple way to do both.

---

**Q4: What is the Q-learning update rule in plain English?**

A: "After taking action a in state s and landing in s' with reward r, update your belief about Q(s,a) by nudging it toward a better estimate." The better estimate (called the TD target) is: r + γ · max Q(s', ·) — immediate reward plus the best future value from the next state. The learning rate α controls how big the nudge is.

---

## Intermediate Level

**Q5: What does "off-policy" mean in the context of Q-Learning?**

A: Off-policy means the algorithm learns the optimal Q-function independently of what actions the agent actually takes during training. Q-Learning's update uses `max Q(s', a')` — the best possible action from the next state — not the action the agent actually chose. So the agent can wander randomly (for exploration) and still learn the optimal policy. This is useful because you can even learn from old data collected by a different (e.g., random) policy.

---

**Q6: What are the convergence conditions for Q-Learning?**

A: Q-Learning converges to Q* under three conditions: (1) every state-action pair must be visited infinitely often — ensured by keeping ε > 0; (2) the learning rate must satisfy Σ α_t = ∞ and Σ α_t² < ∞ — satisfied by decaying α appropriately; (3) the MDP must satisfy the Markov property. In practice, a small fixed α (0.1) and ε annealed from 1.0 to 0.01 works well, even if it doesn't satisfy the theoretical conditions exactly.

---

**Q7: What is the difference between Q-Learning and SARSA?**

A: Both algorithms update Q-values using experience. The difference is in the update target:

- **Q-Learning**: Q(s,a) += α · [r + γ · **max_{a'} Q(s', a')** - Q(s,a)]
- **SARSA**: Q(s,a) += α · [r + γ · **Q(s', a_actual)** - Q(s,a)]

Q-Learning uses the best possible next action (off-policy). SARSA uses the action the agent actually took (on-policy). In practice, near cliffs or risky areas, SARSA is safer because it accounts for the agent's actual (potentially random) behavior. Q-Learning is more aggressive — it assumes optimal future behavior even when the agent is still exploring.

---

## Advanced Level

**Q8: What are the practical limitations of tabular Q-Learning?**

A: Three main limitations:

1. **Memory** — The Q-table has n_states × n_actions entries. An Atari game has ~10^18 possible screen states — a table would be impossibly large.
2. **Generalization** — The table treats every state independently. If the agent has never been in state s=42, Q(42, a) is still 0 regardless of similar states it has visited. No generalization across similar situations.
3. **Continuous state spaces** — States like joint angles or pixel images are continuous (infinite possible values). You can't have a row for every real number.

The fix: replace the table with a function approximator (neural network) that maps (state) → Q-values for all actions. That's DQN.

---

**Q9: How does Q-Learning relate to the Bellman optimality equation?**

A: Q-Learning is essentially an iterative, sample-based method for solving the Bellman optimality equation:

```
Q*(s,a) = E[ r + γ · max_{a'} Q*(s', a') ]
```

Dynamic programming solves this exactly using the known transition model P. Q-Learning solves it approximately, without knowing P, by replacing the expectation E[…] with sample-based updates: each time the agent experiences (s, a, r, s'), it treats r + γ·max Q(s',·) as a noisy sample of the true expectation and nudges Q(s,a) toward it. With enough samples, the estimates converge to Q*.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Q-update derivation with numbers |
| [📄 Code_Example.md](./Code_Example.md) | Q-Learning on a gridworld |

⬅️ **Prev:** [Markov Decision Processes](../02_Markov_Decision_Processes/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md)
