# Q-Learning — Math Intuition

## The Q-Update Rule Derived with Real Numbers

Let's build intuition for Q(s,a) ← Q(s,a) + α · [r + γ·max Q(s',·) - Q(s,a)] from scratch.

---

## Setup: A Tiny Maze

```
[A] → [B] → [EXIT]
 s=0    s=1    s=2
```

Actions: `forward` (move toward exit) or `backward` (move toward start).
Rewards: +10 when entering EXIT, 0 otherwise.
γ = 0.9, α = 0.5

The true optimal Q-values (what we want to converge to):
```
Q*(A, forward)  = 8.1   (0 + 0.9 × 9)
Q*(A, backward) ≈ 0     (goes nowhere useful)
Q*(B, forward)  = 10    (0 + 0.9 × 10... wait, reward is +10 entering EXIT)
Q*(B, forward)  = 10    (immediate +10, then nothing)
Q*(B, backward) ≈ 0
```

---

## Step 1: Initialize

All Q-values start at 0.

```
Q-table:
         forward  backward
State A:   0         0
State B:   0         0
State EXIT: (terminal)
```

---

## Step 2: Episode 1 — Random Exploration

ε = 1.0, so all actions are random.

**Step 1:** s = A. Roll dice → choose `forward`. Land in B, reward = 0.

Apply the update:
```
Q(A, forward) ← Q(A, forward) + α · [r + γ · max Q(B, ·) - Q(A, forward)]
              ← 0 + 0.5 · [0 + 0.9 · max(0, 0) - 0]
              ← 0 + 0.5 · [0 - 0]
              = 0
```
Nothing changed yet — because all values are 0, we don't have signal to propagate.

**Step 2:** s = B. Roll dice → choose `forward`. Land in EXIT, reward = +10.

```
Q(B, forward) ← Q(B, forward) + α · [r + γ · max Q(EXIT, ·) - Q(B, forward)]
              ← 0 + 0.5 · [10 + 0.9 · 0 - 0]
              ← 0 + 0.5 · 10
              = 5.0
```

Now the Q-table has signal:
```
         forward  backward
State A:   0         0
State B:   5.0       0
```

---

## Step 3: Episode 2 — The Signal Propagates Back

ε starts decaying. Suppose we're still mostly exploring but happen to take `forward` again.

**Step 1:** s = A. Choose `forward`. Land in B, reward = 0.

```
Q(A, forward) ← 0 + 0.5 · [0 + 0.9 · max(5.0, 0) - 0]
              ← 0 + 0.5 · [4.5 - 0]
              = 2.25
```

Now state A has learned that going forward is valuable — because B's Q-value got propagated back.

```
         forward  backward
State A:   2.25      0
State B:   5.0       0
```

---

## Step 4: Episode 3 — Values Converge

**Step 1:** s = A, choose `forward`, land in B, reward = 0.

```
Q(A, forward) ← 2.25 + 0.5 · [0 + 0.9 · 5.0 - 2.25]
              ← 2.25 + 0.5 · [4.5 - 2.25]
              ← 2.25 + 0.5 · 2.25
              = 2.25 + 1.125
              = 3.375
```

**Step 2:** s = B, choose `forward`, land in EXIT, reward = +10.

```
Q(B, forward) ← 5.0 + 0.5 · [10 + 0 - 5.0]
              ← 5.0 + 0.5 · 5.0
              = 7.5
```

After more episodes, the values converge toward the true optimal values:
```
Q*(B, forward) = 10
Q*(A, forward) = 0 + 0.9 × 10 = 9
```

---

## The Key Insight: Backward Credit Propagation

Notice the pattern: the reward signal starts at the EXIT (+10) and propagates **backward** through the Q-table, one step per episode.

- Episode 1: B gets the signal (adjacent to EXIT).
- Episode 2: A gets the signal (B propagates back to A).
- Episode N: The signal has propagated N steps back from the reward.

This is why Q-Learning needs many episodes to learn long-horizon tasks. In a 100-step maze, the reward signal needs ~100 episodes just to reach the starting state. This is the **credit assignment** problem in practice.

---

## The TD Error

The term `r + γ · max Q(s', ·) - Q(s, a)` is called the **Temporal Difference (TD) error**.

- **Positive TD error** → reality was better than expected → increase Q(s,a).
- **Negative TD error** → reality was worse than expected → decrease Q(s,a).
- **TD error = 0** → Q(s,a) is already perfectly calibrated for this transition.

When the TD error is 0 for all (s,a) pairs, the Q-table has converged — it satisfies the Bellman equation exactly.

---

## Effect of Learning Rate α

| α | Effect | Risk |
|---|---|---|
| 0.01 | Very slow, stable updates | Takes forever to converge |
| 0.1 | Moderate speed and stability | Good default |
| 0.5 | Fast updates | Values may oscillate |
| 1.0 | Completely replace old estimate | Unstable in stochastic environments |

With α = 1.0 in a deterministic environment, Q-Learning converges in one pass through each (s,a) pair — because it replaces the estimate with the exact target. In stochastic environments, α = 1.0 means the estimate jerks around with every noisy sample.

---

## Effect of Discount Factor γ

Start from B: one step from EXIT (+10 reward).

| γ | Q(B, forward) = | Meaning |
|---|---|---|
| 0.0 | 0 + 0.0 × 0 = 0 (reward is in next state, not here) | Completely myopic |
| 0.5 | 0 + 0.5 × 10 = 5 | Only half credit for next-state reward |
| 0.9 | 0 + 0.9 × 10 = 9 | Most credit flows back |
| 0.99 | 0 + 0.99 × 10 = 9.9 | Almost full credit |

With γ = 0, no value propagates backward at all — the agent can never learn about rewards more than one step away. With γ close to 1, rewards propagate far back but training may be slow to converge.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Intuition.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Q-Learning on a gridworld |

⬅️ **Prev:** [Markov Decision Processes](../02_Markov_Decision_Processes/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md)
