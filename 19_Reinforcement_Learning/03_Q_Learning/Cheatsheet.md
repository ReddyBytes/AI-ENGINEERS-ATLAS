# Q-Learning — Cheatsheet

## The Q-Learning Update Rule

```
Q(s, a) ← Q(s, a) + α · [ r + γ · max_{a'} Q(s', a') - Q(s, a) ]
```

Term by term:

| Term | Name | What it means |
|---|---|---|
| `Q(s, a)` | Current Q-value | Your current belief about this (state, action) pair |
| `α` | Learning rate | How much to update (0.1 is a common default) |
| `r` | Immediate reward | What the environment just gave you |
| `γ` | Discount factor | How much future rewards matter (0.99 common) |
| `max_{a'} Q(s', a')` | Best future Q | Best value achievable from the next state |
| `r + γ·max Q(s',·)` | TD target | Your updated estimate of Q(s,a) |
| `TD target - Q(s,a)` | TD error | How wrong you were — the update direction |

---

## Algorithm in Pseudocode

```
Initialize Q(s, a) = 0 for all s, a
Set ε = 1.0, α = 0.1, γ = 0.99

for each episode:
    s = environment.reset()
    done = False
    while not done:
        if random() < ε:
            a = random_action()          # explore
        else:
            a = argmax_a Q(s, a)         # exploit

        s', r, done = environment.step(a)
        Q(s,a) += α * (r + γ * max(Q[s']) - Q(s,a))
        s = s'

    ε = max(0.01, ε * 0.995)            # decay epsilon
```

---

## Epsilon-Greedy Schedule

| Phase | ε value | Behavior |
|---|---|---|
| Early training | 1.0 → 0.5 | Mostly exploring randomly |
| Mid training | 0.5 → 0.1 | Mix of explore and exploit |
| Late training | 0.1 → 0.01 | Mostly using learned Q-values |

Common decay: `ε = max(ε_min, ε * decay_rate)` per episode.

---

## Key Hyperparameters

| Hyperparameter | Typical value | Effect |
|---|---|---|
| Learning rate α | 0.1 | Higher = faster but unstable updates |
| Discount γ | 0.99 | Higher = more long-term thinking |
| Initial ε | 1.0 | Start with full exploration |
| Epsilon decay | 0.995/episode | Controls how fast exploration drops |
| Epsilon min | 0.01 | Always keep a little exploration |

---

## Q-Learning vs SARSA

| | Q-Learning | SARSA |
|---|---|---|
| Update uses | max Q(s', a') — best possible | Q(s', actual next action) |
| Policy type | Off-policy | On-policy |
| Learns | Optimal Q regardless of behavior | Q of the current behavior policy |
| Risk | Can be risky (optimistic) | Safer in risky environments |

---

## When to Use Q-Learning

| Use Q-Learning when | Use something else when |
|---|---|
| State space is small (< 10k states) | Continuous or huge state spaces → DQN |
| Actions are discrete | Continuous actions → PPO / SAC |
| You want simple, guaranteed convergence | You need sample efficiency → model-based |
| Learning from scratch in a simulator | You have human demonstrations → imitation learning |

---

## Golden Rules

1. Always anneal ε — never keep it at 1.0 forever.
2. Use α ≤ 0.5. Start at 0.1 and tune.
3. The Q-table has shape (n_states × n_actions) — make sure this fits in memory.
4. Off-policy means you can learn from old experience (replay) — great for data efficiency.
5. When Q-values stop changing, training has converged.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Q-update derivation with numbers |
| [📄 Code_Example.md](./Code_Example.md) | Q-Learning on a gridworld |

⬅️ **Prev:** [Markov Decision Processes](../02_Markov_Decision_Processes/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md)
