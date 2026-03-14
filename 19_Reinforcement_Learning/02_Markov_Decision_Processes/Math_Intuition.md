# Markov Decision Processes — Math Intuition

## Building the Bellman Equation from Scratch

This file builds the Bellman equation step by step using one concrete example — a four-room maze. No background required beyond basic arithmetic.

---

## The Maze

```
[START] → [HALL A] → [HALL B] → [EXIT]
  s=0        s=1        s=2       s=3
```

Rules:
- The agent can move **forward** (toward exit) or **backward** (toward start).
- From the EXIT, only **backward** is available (or the episode ends — let's say it ends).
- Reward: **+10** when entering the EXIT, **0** everywhere else.
- Discount factor: **γ = 0.9**
- Policy: always move forward (a deterministic policy).

---

## Step 1: What Are We Trying to Compute?

We want V(s) for each state — the **total expected reward the agent will collect** starting from that state, following the "always move forward" policy.

This seems easy: just add up the rewards on the path. But the discount factor complicates things. A reward further in the future is worth less.

---

## Step 2: Compute V(s) Directly by Unrolling

Start from the EXIT and work backward.

**V(EXIT) = V(s=3)**
The agent is at the exit. The episode ends. No more rewards.
```
V(s=3) = 0
```
(We already collected the +10 reward when *entering* s=3. Now we're done.)

**V(HALL B) = V(s=2)**
From HALL B, the agent moves forward to EXIT and collects +10.
```
V(s=2) = r + γ · V(s=3)
       = 10 + 0.9 · 0
       = 10
```

**V(HALL A) = V(s=1)**
From HALL A, the agent moves forward to HALL B (reward = 0), then eventually to EXIT.
```
V(s=1) = r + γ · V(s=2)
       = 0 + 0.9 · 10
       = 9
```

**V(START) = V(s=0)**
```
V(s=0) = r + γ · V(s=1)
       = 0 + 0.9 · 9
       = 8.1
```

So the values are: V(0) = 8.1, V(1) = 9, V(2) = 10, V(3) = 0.

---

## Step 3: The Pattern Is the Bellman Equation

Look at what we computed each time:
```
V(s) = reward_received + γ · V(next_state)
V(s) = R(s, a, s') + γ · V(s')
```

This IS the Bellman equation. We just derived it naturally from the definition of discounted return.

Formal statement:
```
V^π(s) = E_π[ R(s, a, s') + γ · V^π(s') ]
```

---

## Step 4: What If Transitions Are Stochastic?

Real environments aren't deterministic. What if our agent sometimes slips? Say from HALL B, there's:
- 80% chance of reaching EXIT (reward +10)
- 20% chance of sliding back to HALL A (reward 0)

Now V(s=2) becomes an **expectation**:
```
V(s=2) = 0.8 · [10 + 0.9 · V(EXIT)] + 0.2 · [0 + 0.9 · V(HALL A)]
       = 0.8 · [10 + 0.9 · 0]  + 0.2 · [0 + 0.9 · 9]
       = 0.8 · 10              + 0.2 · 8.1
       = 8.0 + 1.62
       = 9.62
```

The general stochastic Bellman equation:
```
V^π(s) = Σ_a π(a|s) · Σ_{s'} P(s'|s,a) · [R(s,a,s') + γ · V^π(s')]
```

Read it as: for each action I might take (weighted by my policy), for each place I might land (weighted by transition probabilities), collect reward + discounted value of the next state.

---

## Step 5: The Optimal Bellman Equation

What if we could *choose* the best action at each state? Instead of averaging over the policy, we take the maximum:

```
V*(s) = max_a Σ_{s'} P(s'|s,a) · [R(s,a,s') + γ · V*(s')]
```

In our maze: at HALL B with the stochastic transition, suppose we have a second action "wait" that keeps us in HALL B with reward 0. Is it worth waiting?

```
V*(s=2) with action "forward": 9.62 (computed above)
V*(s=2) with action "wait":
  = 1.0 · [0 + 0.9 · V*(s=2)]
  = 0.9 · V*(s=2)
  → solving: V = 0.9V → V = 0 (waiting forever earns nothing discounted)
```

So the optimal action is still "forward." V*(s=2) = 9.62.

---

## Step 6: The Q-Function Relationship

The **Q-function** Q(s, a) is the value of *first taking action a* from state s, then following the optimal policy:

```
Q*(s,a) = Σ_{s'} P(s'|s,a) · [R(s,a,s') + γ · V*(s')]
```

And:
```
V*(s) = max_a Q*(s, a)
```

This is the key relationship. If you know Q*, you don't need P to act — you just pick the action with the highest Q-value. This is why Q-Learning is so powerful.

---

## Step 7: Why This Is Hard to Solve Directly

In our tiny 4-state maze, we computed V(s) in seconds. In a real problem:
- Atari games: ~10^18 possible states (all possible screen arrangements)
- Chess: ~10^43 positions
- Real robot control: continuous state space (infinitely many states)

You can't enumerate all states and solve the Bellman equation exactly. Instead, RL algorithms approximate it through repeated interaction:

```
Start with random V(s) estimates
  → Take actions, observe rewards
  → Update V(s) toward the Bellman target: r + γ · V(s')
  → Repeat until estimates converge
```

This is the core of **Temporal Difference (TD) learning**, which is the foundation of Q-Learning.

---

## Summary: The Bellman Equation in Three Forms

| Form | Equation | Use |
|---|---|---|
| For a policy π | V^π(s) = E[r + γ·V^π(s')] | Evaluate how good a policy is |
| For optimal policy | V*(s) = max_a E[r + γ·V*(s')] | Find the best policy |
| Q-function form | Q*(s,a) = E[r + γ·max_{a'} Q*(s',a')] | Foundation of Q-Learning |

The entire field of value-based RL is, at heart, finding ways to solve or approximate these three equations at scale.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Intuition.md** | ← you are here |

⬅️ **Prev:** [RL Fundamentals](../01_RL_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Q-Learning](../03_Q_Learning/Theory.md)
