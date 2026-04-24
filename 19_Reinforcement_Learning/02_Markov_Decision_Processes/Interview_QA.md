# Markov Decision Processes — Interview Q&A

## Beginner Level

**Q1: What is a Markov Decision Process?**

<details>
<summary>💡 Show Answer</summary>

A: An MDP is the mathematical framework for describing sequential decision-making problems. It's defined by five things: a set of states (S), a set of actions (A), a transition function P(s'|s,a) that says where you end up, a reward function R that says what you earn, and a discount factor γ. Every RL problem can be formalized as an MDP (or a close relative). Think of it as the "grammar" that RL speaks.

</details>

---

**Q2: What is the Markov property?**

<details>
<summary>💡 Show Answer</summary>

A: The Markov property says: the future depends only on the current state, not on how you got there. Formally: P(s_{t+1} | s_t, a_t, s_{t-1}, …) = P(s_{t+1} | s_t, a_t). In a maze, it means knowing which room you're in is enough to know your options — you don't need to know the path you took to get there. When this holds, the math becomes tractable. When it doesn't hold (partial observability), you need a POMDP instead.

</details>

---

**Q3: What is the difference between the value function V(s) and the action-value function Q(s, a)?**

<details>
<summary>💡 Show Answer</summary>

A: V(s) answers "how good is it to be in state s?" — it gives the expected total future reward from state s, following the current policy. Q(s, a) answers "how good is it to take action a in state s?" — it adds one more level of detail by conditioning on both state and action. Q is more useful for acting: to pick the best action you just compute argmax_a Q(s, a). With V alone, you'd need the transition probabilities P to figure out which action leads to the highest-valued next state.

</details>

---

## Intermediate Level

**Q4: What is the Bellman equation and why is it important?**

<details>
<summary>💡 Show Answer</summary>

A: The Bellman equation is a recursive decomposition of the value function:

```
V^π(s) = E_π[ r_t + γ · V^π(s_{t+1}) | s_t = s ]
```

It says: the value of a state = the immediate expected reward + the discounted value of the next state. Its importance: (1) it turns a complex infinite-horizon optimization into a local consistency condition, (2) nearly every RL algorithm — Q-Learning, TD-learning, policy gradients — is either directly solving the Bellman equation or using it as a learning signal, and (3) it enables dynamic programming solutions when P and R are known.

</details>

---

**Q5: What is the difference between episodic and continuing tasks?**

<details>
<summary>💡 Show Answer</summary>

A: Episodic tasks have a natural end — a terminal state. Each episode starts fresh (e.g., a chess game, an Atari game). Continuing tasks run forever with no terminal state (e.g., a stock trading system, a recommendation engine). The key practical difference: continuing tasks require γ < 1 to ensure the return sum is finite. In episodic tasks you can use γ = 1 safely, since the sum ends at the terminal state.

</details>

---

**Q6: What is the discount factor and what does it control?**

<details>
<summary>💡 Show Answer</summary>

A: The discount factor γ (between 0 and 1) determines how much the agent values future rewards relative to immediate ones. With γ = 0.99, a reward 100 steps in the future is worth e^(-100 * 0.01) ≈ 37% of an immediate reward. With γ = 0.5, it's worth 0.5^100 ≈ 0 — completely ignored. Practically: set γ close to 1 when long-term planning matters (chess, robotics), lower when short-horizon rewards are what matter most.

</details>

---

**Q7: What is the difference between a deterministic and stochastic MDP?**

<details>
<summary>💡 Show Answer</summary>

A: In a deterministic MDP, the transition function P(s'|s,a) always returns 1 for a single next state — the same action from the same state always leads to the same place. In a stochastic MDP, P is a true probability distribution — the same action can lead to different next states with different probabilities (e.g., a robot on a slippery floor, a game with random events). Most real-world problems are stochastic. RL algorithms must handle this by working with expectations over transitions.

</details>

---

## Advanced Level

**Q8: What is the Bellman optimality equation and how does it differ from the Bellman expectation equation?**

<details>
<summary>💡 Show Answer</summary>

A: The **Bellman expectation equation** describes the value function for a *specific* policy π:
```
V^π(s) = Σ_a π(a|s) · Σ_{s'} P(s'|s,a) · [R(s,a,s') + γ · V^π(s')]
```

The **Bellman optimality equation** describes the value function for the *optimal* policy:
```
V*(s) = max_a Σ_{s'} P(s'|s,a) · [R(s,a,s') + γ · V*(s')]
```

The difference is the `max_a` instead of `Σ_a π(a|s)`. The optimality equation doesn't average over actions — it picks the best one. Solving this equation (exactly) gives you V*, from which you can extract the optimal policy. RL algorithms are approximations of solving this when P and R are unknown.

</details>

---

**Q9: What is a POMDP and how does it relate to a standard MDP?**

<details>
<summary>💡 Show Answer</summary>

A: A **Partially Observable MDP (POMDP)** is an extension where the agent cannot directly observe the full state. Instead, it receives an **observation** o that is a noisy or incomplete function of the true state. A self-driving car can't directly observe other drivers' intentions — it only observes sensor readings. Formally, a POMDP adds an observation space O and an observation function Z(o|s,a) to the MDP. The agent must maintain a **belief state** — a probability distribution over possible true states — and update it using Bayes' theorem as new observations arrive. Most real-world RL problems are technically POMDPs; we approximate them as MDPs by including enough observation history in the "state."

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Bellman equation from scratch |

⬅️ **Prev:** [RL Fundamentals](../01_RL_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Q-Learning](../03_Q_Learning/Theory.md)
