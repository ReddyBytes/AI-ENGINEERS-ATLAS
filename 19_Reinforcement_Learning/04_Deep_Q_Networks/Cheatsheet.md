# Deep Q-Networks — Cheatsheet

## DQN = Q-Learning + Neural Network + Two Innovations

```
Standard Q-Learning: Q(s,a) stored in a table
DQN:                 Q(s,a; θ) computed by a neural network
                     + Experience Replay
                     + Target Network
```

---

## The Two Key Innovations

| Innovation | Problem it solves | How it works |
|---|---|---|
| **Experience Replay** | Correlated training samples | Store (s,a,r,s') in buffer; sample random minibatch at each step |
| **Target Network** | Moving training targets | Frozen copy of network; update to match online network every C steps |

---

## DQN Loss Function

```
L(θ) = E[ ( y - Q(s, a; θ) )² ]

where y = r                                if done
      y = r + γ · max_{a'} Q(s', a'; θ⁻)  if not done
```

- `θ` = online network (being trained)
- `θ⁻` = target network (frozen, updated every C steps)
- Gradients only flow through `Q(s,a; θ)`, not through the target

---

## DQN Architecture (for Atari)

```
Input: 4 stacked 84×84 grayscale frames
  → Conv2D(32, 8×8, stride 4) → ReLU
  → Conv2D(64, 4×4, stride 2) → ReLU
  → Conv2D(64, 3×3, stride 1) → ReLU
  → Flatten → Linear(512) → ReLU
  → Linear(n_actions)          ← outputs Q-value per action
```

For CartPole/other continuous-state envs with small observation vectors:
```
Input: observation vector (e.g., 4 floats for CartPole)
  → Linear(128) → ReLU
  → Linear(128) → ReLU
  → Linear(n_actions)
```

---

## Key Hyperparameters

| Parameter | Typical value | Notes |
|---|---|---|
| Replay buffer size | 10,000 – 1,000,000 | Larger = more diverse samples |
| Minibatch size | 32 – 128 | Larger = more stable gradients |
| Target update freq (C) | 100 – 10,000 steps | More frequent = less stable |
| Learning rate | 1e-4 – 1e-3 | Use Adam optimizer |
| Gamma γ | 0.99 | Almost always 0.99 |
| Epsilon start | 1.0 | Full exploration initially |
| Epsilon end | 0.01 – 0.1 | Keep some exploration |
| Epsilon decay | 10,000 – 1,000,000 steps | Anneal over many steps |
| Warmup steps | 1,000 – 10,000 | Fill buffer before training |

---

## DQN Variants (Quick Reference)

| Variant | Key change | Benefit |
|---|---|---|
| **Double DQN** | Use online net to pick best action, target net to evaluate | Reduces overestimation bias |
| **Dueling DQN** | Split into V(s) + A(s,a) streams | Better value estimation |
| **Prioritized Replay** | Sample important experiences more often | Faster learning |
| **Rainbow DQN** | Combines all of the above | State-of-the-art discrete action RL |
| **DDPG** | Continuous actions with actor-critic | For robot control, etc. |

---

## DQN vs Tabular Q-Learning

| | Tabular Q-Learning | DQN |
|---|---|---|
| State space | Small (< 10k states) | Large or continuous |
| Storage | Q-table (n_states × n_actions) | Neural network weights |
| Generalization | None | Yes — similar states → similar Q |
| Convergence guarantee | Yes (theoretically) | No (practical, but not proven) |
| Training stability | Stable | Needs replay + target network |

---

## Golden Rules

1. Always warm up the replay buffer before training.
2. Target network update frequency is critical — too fast = unstable, too slow = slow learning.
3. Normalize observations (pixel values: divide by 255; other values: standardize).
4. Use Adam optimizer with lr ≈ 1e-4.
5. DQN only works for discrete action spaces. For continuous, use DDPG/SAC/PPO.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Architecture diagrams |
| [📄 Code_Example.md](./Code_Example.md) | DQN on CartPole |

⬅️ **Prev:** [Q-Learning](../03_Q_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Policy Gradients](../05_Policy_Gradients/Theory.md)
