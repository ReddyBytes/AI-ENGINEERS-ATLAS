# RL Fundamentals — Cheatsheet

## Key Terms at a Glance

| Term | Plain-English Definition |
|---|---|
| **Agent** | The learner / decision-maker |
| **Environment** | Everything the agent interacts with |
| **State (s)** | A snapshot of the world at time t |
| **Action (a)** | A choice the agent makes |
| **Reward (r)** | A scalar feedback signal (+/- /0) |
| **Policy (π)** | The agent's strategy: state → action |
| **Value function V(s)** | Expected total future reward from state s |
| **Q-function Q(s,a)** | Expected total future reward from doing a in state s |
| **Return (G_t)** | Sum of discounted future rewards from time t |
| **Discount factor (γ)** | How much future rewards are down-weighted (0–1) |
| **Episode** | One complete run (start → terminal state) |
| **Trajectory** | A sequence of (s, a, r, s') tuples from one episode |
| **Exploration** | Trying new actions to gather information |
| **Exploitation** | Choosing the best-known action to maximize reward |

---

## The RL Loop (One Step)

```
s_t  →  Agent (policy π)  →  a_t
                                ↓
                          Environment
                                ↓
                     r_t, s_{t+1}  →  back to Agent
```

---

## The Return Formula

```
G_t = r_t + γ·r_{t+1} + γ²·r_{t+2} + γ³·r_{t+3} + …
```

- γ close to 1 → agent is patient, cares about long-term reward
- γ close to 0 → agent is greedy, cares only about immediate reward
- γ = 0.99 is a common default

---

## The Bellman Equation (Plain English)

```
V(s) = E[ immediate reward + γ · value of next state ]
V(s) = E[ r + γ · V(s') ]
```

"The value of where I am = what I'll get now + the discounted value of where I'll end up."

---

## RL vs Supervised Learning — Quick Comparison

| | Supervised | Reinforcement |
|---|---|---|
| Data source | Labeled dataset | Agent's own interactions |
| Feedback | Label per sample | Reward per step (often sparse) |
| Goal | Minimize prediction error | Maximize cumulative reward |
| Teacher | Human annotators | The environment |
| Sample efficiency | High | Usually low |

---

## Types of RL Algorithms

| Category | Examples | Learns |
|---|---|---|
| Value-based | Q-Learning, DQN | Q-function or V-function |
| Policy-based | REINFORCE, PPO | Policy directly |
| Actor-Critic | A2C, SAC, PPO | Both policy and value function |
| Model-based | Dyna, MuZero | A model of the environment |

---

## Common Reward Function Patterns

| Scenario | Reward design |
|---|---|
| Reach a goal | +1 on reaching goal, 0 otherwise |
| Avoid crashes | -1 on crash, 0 otherwise |
| Speed task | +1 per step survived (incentivizes speed) |
| Continuous control | Negative distance to target each step |
| Game score | Direct game score as reward |

---

## Golden Rules

1. The reward function IS the goal — design it carefully.
2. Maximize **return** (total future reward), not just immediate reward.
3. Use γ < 1 to ensure convergence in infinite-horizon problems.
4. Exploration vs exploitation is always a tension — never purely exploit.
5. RL requires vastly more data than supervised learning — plan for it.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | 5 everyday RL examples |

⬅️ **Prev:** Section intro &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Markov Decision Processes](../02_Markov_Decision_Processes/Theory.md)
