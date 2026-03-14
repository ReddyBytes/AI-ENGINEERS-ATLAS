# Deep Q-Networks — Interview Q&A

## Beginner Level

**Q1: What is DQN and how does it differ from tabular Q-Learning?**

A: DQN (Deep Q-Network) is Q-Learning where the Q-table is replaced by a neural network. In tabular Q-Learning, you store Q(s, a) values in a table with one row per state. This works for small problems (like a 5×5 gridworld) but is impossible for large state spaces (like video game screens with millions of possible configurations). DQN uses a neural network that takes a state as input and outputs Q-values for all actions — it can generalize across similar states, which a table cannot.

---

**Q2: What is experience replay and why is it needed?**

A: Experience replay is a technique where the agent's experiences `(state, action, reward, next_state)` are stored in a **replay buffer**. At each training step, a random minibatch is sampled from this buffer to train the network.

It's needed because consecutive game frames are highly correlated — frames 1 and 2 look nearly identical. Training on them in sequence is like training a neural network on the same example over and over, which causes it to forget earlier lessons. Random sampling breaks this correlation. As a bonus, each experience can be reused many times, improving data efficiency.

---

**Q3: What is the target network and why is it needed?**

A: DQN maintains two neural networks with identical architecture: an **online network** that's trained at every step, and a **target network** that's a frozen copy, updated to match the online network only every few hundred or thousand steps.

The target network is needed because without it, the training target `r + γ·max Q(s',·)` changes every step as the network updates. You're training the network toward a target that moves every step, which creates a feedback loop that destabilizes training. The frozen target network provides a stable training signal for a while, making learning converge.

---

## Intermediate Level

**Q4: Describe the complete DQN training loop.**

A:
1. Agent observes state s.
2. With probability ε, take random action; otherwise take argmax_a Q(s, a; online network).
3. Execute action, observe reward r and next state s'.
4. Store (s, a, r, s', done) in replay buffer.
5. If buffer has enough samples, sample a random minibatch.
6. For each sample, compute TD target: y = r if done, else y = r + γ·max Q(s', a'; target network).
7. Compute loss = MSE(Q(s, a; online network), y).
8. Backpropagate and update online network weights.
9. Every C steps, copy online network weights to target network.
10. Repeat.

---

**Q5: What is the overestimation problem in DQN and how does Double DQN fix it?**

A: Standard DQN uses `max Q(s', a'; θ⁻)` as the next-state value. The `max` operation is optimistic — it tends to select the action with the highest Q-value even if that value is noisy or overestimated. Over time, these overestimates compound and the Q-values become inflated.

**Double DQN** decouples action selection from action evaluation:
- Use the **online network** to select which action is best: `a* = argmax_a Q(s', a; θ)`
- Use the **target network** to evaluate that action: `Q(s', a*; θ⁻)`

This simple change significantly reduces overestimation bias and improves performance on most Atari games.

---

**Q6: What is the difference between DQN and policy gradient methods?**

A: DQN learns a value function (Q-values) and derives actions from it — pick the action with the highest Q-value. It's a **value-based** method. Policy gradient methods (like REINFORCE, PPO) directly parameterize and optimize the policy — the network directly outputs action probabilities. Key practical differences:
- DQN only works for discrete action spaces; policy gradients can handle continuous.
- DQN is off-policy (can learn from old data); many policy gradient methods are on-policy.
- Policy gradients tend to be more stable; DQN can be more sample efficient for discrete action problems.

---

## Advanced Level

**Q7: Why does DQN use convolutional layers for Atari, and how is the input preprocessed?**

A: Atari game screens are 210×160 pixels in RGB. Preprocessing: (1) convert to grayscale, (2) downsample to 84×84, (3) stack the last 4 frames into a single input of shape (4, 84, 84). Stacking frames is essential because a single frame doesn't convey velocity — you can't tell which direction the ball is moving. Four stacked frames give the network implicit access to recent motion.

Convolutional layers are used because the Q-value should be spatially invariant to some extent — what matters is the relative positions of objects, not their absolute pixel locations. Conv layers learn spatial features efficiently.

---

**Q8: What are prioritized experience replay and its trade-offs?**

A: **Prioritized Experience Replay (PER)** samples experiences proportional to their TD error — experiences the agent found surprising (high error) are replayed more often. The intuition: experiences that are more surprising are more informative.

Trade-offs:
- **Benefit:** Faster learning — the agent focuses on the most useful experiences.
- **Cost 1:** Bias — non-uniform sampling changes the distribution the network trains on. Fix: use importance sampling weights to correct the bias.
- **Cost 2:** Complexity — requires a priority data structure (e.g., a sum-tree) that's efficient to update and sample from.
- **Cost 3:** Stale priorities — priorities are set when the experience is first stored, based on the network at that time. As the network improves, old priorities become less accurate.

---

**Q9: What are the main failure modes of DQN training?**

A: Common failure modes:
1. **Divergence** — Q-values grow without bound. Often caused by a learning rate too high, target network updating too frequently, or missing experience replay.
2. **Policy collapse** — The agent finds a suboptimal strategy early and stops exploring. Fix: keep ε from decaying too fast.
3. **Overestimation spiral** — Q-values consistently overestimate, leading to poor policy. Fix: use Double DQN.
4. **Slow learning** — Replay buffer is too small or the reward is too sparse. Fix: larger buffer, reward shaping, or prioritized replay.
5. **Catastrophic forgetting** — The network forgets how to handle early-game situations as it learns late-game situations. Fix: larger replay buffer, lower learning rate.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Architecture diagrams |
| [📄 Code_Example.md](./Code_Example.md) | DQN on CartPole |

⬅️ **Prev:** [Q-Learning](../03_Q_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Policy Gradients](../05_Policy_Gradients/Theory.md)
