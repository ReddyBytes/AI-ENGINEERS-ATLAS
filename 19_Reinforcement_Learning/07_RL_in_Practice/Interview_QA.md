# RL in Practice — Interview Q&A

## Beginner Level

**Q1: What is Gymnasium (formerly OpenAI Gym) and why is it important?**

A: Gymnasium is a Python library that provides a standardized interface for RL environments. Every environment exposes the same API: `reset()` returns an initial observation, `step(action)` takes one action and returns (observation, reward, terminated, truncated, info). This means any RL algorithm written for Gymnasium works with any Gymnasium environment — CartPole, LunarLander, Atari games, MuJoCo robots. It's the "MNIST for RL" — the common ground that makes research reproducible and code reusable.

---

**Q2: What is reward shaping and why is it needed?**

A: Reward shaping is the practice of supplementing the original environment reward with additional reward signals to help the agent learn faster. It's needed because many real tasks have **sparse rewards** — the agent only gets feedback at the end of a long sequence of actions (like receiving +1 only when winning a chess game after 40 moves). With sparse rewards, the agent wanders randomly for thousands of episodes without any learning signal.

Shaping adds informative intermediate signals (like "you're getting closer to the goal") that guide learning without changing what the optimal behavior ultimately is.

---

**Q3: What is stable-baselines3 and when should you use it?**

A: stable-baselines3 (SB3) is a Python library with clean, reliable implementations of major RL algorithms: PPO, DQN, SAC, A2C, TD3. Use it when:
- You want to apply RL to a problem without implementing algorithms from scratch.
- You're prototyping and need reliable baselines quickly.
- You're a practitioner, not an algorithm researcher.

Don't use SB3 when you need to modify the algorithm internals deeply (e.g., for research), or when you need extreme performance at scale (use Ray RLlib instead).

---

## Intermediate Level

**Q4: What is reward hacking and how do you prevent it?**

A: Reward hacking (also called specification gaming) occurs when the agent finds an unintended strategy that maximizes the reward function without achieving the intended goal. Classic examples:
- A boat racing agent scores points by spinning in circles collecting bonuses instead of finishing the race.
- A walking robot learns to be tall (to maximize height reward) rather than to walk.
- An LLM learns to output very long text because length correlates with human preference ratings.

Prevention strategies:
1. **Watch replay videos** — visualize what your agent actually does.
2. **Use multiple reward components** — hard to hack all simultaneously.
3. **Potential-based shaping** — safe by construction.
4. **Human oversight** — spot-check agent behavior regularly.
5. **Goodhart's Law awareness** — "When a measure becomes a target, it ceases to be a good measure."

---

**Q5: Why is running multiple random seeds important in RL experiments?**

A: RL training is extremely sensitive to random initialization. The same algorithm with the same hyperparameters but a different random seed can produce dramatically different results — sometimes converging to the optimal policy, sometimes getting stuck in a suboptimal one. This variance is inherent to the exploration/exploitation trade-off and the non-convex nature of policy optimization.

Running a single seed and reporting those results is not scientifically valid. Best practice: run 3–10 seeds, report mean ± std (or mean ± std error), and plot the full distribution. Many RL papers in the early 2010s were later found to report cherry-picked seeds, which inflated apparent performance.

---

**Q6: What is the exploration-exploitation trade-off in practice, and what techniques address it?**

A: In practice, the trade-off manifests as: explore enough to find good strategies, but exploit what you've learned to actually improve performance. Too much exploration → slow learning (you keep trying bad actions). Too little → premature convergence (you lock in a mediocre policy before finding better ones).

Practical techniques:
- **Epsilon-greedy with decay** (DQN): start ε = 1.0, decay to 0.01 over training.
- **Entropy bonus** (PPO, SAC): add a term to the loss that rewards action diversity.
- **Curiosity-driven exploration**: add intrinsic reward for visiting novel states.
- **Noisy networks**: add learned noise to network weights rather than epsilon-greedy.
- **Optimistic initialization**: initialize Q-values high to encourage trying everything.

---

## Advanced Level

**Q7: When is RL NOT the right approach?**

A: RL is often the wrong tool. Better alternatives:

- **Supervised learning**: if you have labeled data (correct actions), imitate them rather than discovering them through RL. Imitation learning (behavioral cloning) is much more sample-efficient.
- **Search algorithms**: if the environment is deterministic and fully known, A*, MCTS, or dynamic programming find optimal solutions without learning.
- **Rule-based systems**: if the task is well-understood and consistent, hand-coded rules outperform learned policies in terms of reliability and interpretability.
- **Optimization methods**: for continuous optimization problems (e.g., hyperparameter tuning, circuit design), evolutionary algorithms or Bayesian optimization can be more sample-efficient than RL.

RL is justified when: (1) the environment is too complex to specify rules, (2) no labeled data exists, (3) you have a simulator, and (4) sequential decisions with delayed rewards are core to the problem.

---

**Q8: What is curriculum learning in RL and when is it used?**

A: Curriculum learning starts the agent on simple versions of a task and gradually increases difficulty as the agent improves. This is analogous to how humans learn — you learn addition before multiplication.

Why it helps: if the full task is too hard (sparse rewards, long horizons), the agent never finds any positive signal and doesn't learn. Simpler initial tasks provide a strong learning signal that builds a foundation.

Examples:
- Train a robot to walk in a wind-free environment first, then add wind.
- Train a maze-solving agent in small mazes, then progressively larger ones.
- In RLHF: fine-tune on easy instructions first, then complex multi-step tasks.

Implementation: adjust environment difficulty based on the agent's performance metric. If the agent is doing well, increase difficulty; if struggling, decrease it.

---

**Q9: What is the sim-to-real gap and how is it addressed?**

A: The sim-to-real gap is the performance degradation when a policy trained in simulation is deployed on real hardware. Simulation is imperfect — friction, motor dynamics, sensor noise, and visual appearance all differ from reality.

Techniques to bridge the gap:
1. **Domain randomization**: randomize simulation parameters (friction, mass, lighting, textures) during training. The policy learns to be robust to variation.
2. **System identification**: measure the real robot's parameters and tune the simulation to match.
3. **Domain adaptation**: use a small amount of real-world data to fine-tune the simulation-trained policy.
4. **Sim-to-real transfer benchmarks**: track how well policies transfer across multiple environments.

AlphaGo has no sim-to-real gap (it's all digital). Robot locomotion is the hardest sim-to-real challenge.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | RL debugging checklist |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Train, eval, save, load |
| [📄 Frameworks_Guide.md](./Frameworks_Guide.md) | Library comparison |

⬅️ **Prev:** [PPO](../06_PPO/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [RL for LLMs](../08_RL_for_LLMs/Theory.md)
