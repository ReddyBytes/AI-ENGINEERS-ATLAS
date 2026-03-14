# Markov Decision Processes — Cheatsheet

## The Five MDP Components

| Symbol | Name | Meaning |
|---|---|---|
| **S** | State space | All possible situations the agent can be in |
| **A** | Action space | All possible choices the agent can make |
| **P(s'\|s,a)** | Transition function | Probability of landing in s' from s via a |
| **R(s,a,s')** | Reward function | Scalar reward for transitioning s→s' via a |
| **γ** | Discount factor | How much future rewards are down-weighted (0–1) |

---

## The Markov Property (One Line)

```
The future depends only on the current state, not on how you got here.
P(s_{t+1} | s_t, a_t) = P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, ...)
```

---

## The Bellman Equations

**State-value function (V):**
```
V^π(s) = Σ_a π(a|s) · Σ_{s'} P(s'|s,a) · [R(s,a,s') + γ · V^π(s')]
```

**Optimal state-value function:**
```
V*(s) = max_a Σ_{s'} P(s'|s,a) · [R(s,a,s') + γ · V*(s')]
```

**Optimal action-value function:**
```
Q*(s,a) = Σ_{s'} P(s'|s,a) · [R(s,a,s') + γ · max_{a'} Q*(s',a')]
```

**Key relationship:** V*(s) = max_a Q*(s,a)

---

## V vs Q — Quick Comparison

| | V(s) | Q(s,a) |
|---|---|---|
| Input | State only | State + action |
| Meaning | Value of being in state s | Value of taking action a in state s |
| To act | Need to know P to pick best action | Just pick argmax_a Q(s,a) — no P needed |
| Used by | Policy iteration, actor-critic | Q-Learning, DQN |

---

## Discount Factor γ — Effect on Behavior

| γ | Agent type | Use when |
|---|---|---|
| 0 | Completely myopic | Only immediate reward matters |
| 0.5–0.9 | Short-sighted | Near-term tasks |
| 0.99 | Patient | Long-horizon planning |
| 1.0 | No discounting | Only safe in episodic tasks |

---

## Episodic vs Continuing Tasks

| | Episodic | Continuing |
|---|---|---|
| Has terminal state | Yes | No |
| Examples | Chess, Atari, maze | Trading, recommendations |
| Discount required? | Optional | Required (γ < 1) |

---

## MDP Solution Methods

| Method | Needs P, R? | Approach |
|---|---|---|
| Policy Iteration | Yes | Alternate evaluation and improvement |
| Value Iteration | Yes | Iteratively apply Bellman optimality |
| Q-Learning | No | Learn Q* from interactions |
| Policy Gradients | No | Directly optimize policy parameters |

---

## Golden Rules

1. State must satisfy the Markov property — include all relevant history.
2. Q doesn't need P to act (just argmax Q); V does need P.
3. Bellman: value of now = reward now + discounted value of next state.
4. γ < 1 ensures convergence in infinite-horizon problems.
5. Unknown P and R means RL; known P and R means dynamic programming.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Bellman equation from scratch |

⬅️ **Prev:** [RL Fundamentals](../01_RL_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Q-Learning](../03_Q_Learning/Theory.md)
