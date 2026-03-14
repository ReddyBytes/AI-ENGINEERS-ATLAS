# RL in Practice — Cheatsheet

## RL Debugging Checklist

Use this checklist when your agent isn't learning.

### Step 1: Verify the Basics

- [ ] Environment resets correctly (`env.reset()` returns valid obs)
- [ ] Reward is non-zero at least occasionally (run random agent, check if any reward received)
- [ ] Observation shape matches what the network expects
- [ ] Actions are in valid range (check `env.action_space`)
- [ ] Episode terminates within reasonable steps (not running forever)

### Step 2: Check Data Pipeline

- [ ] Observations are normalized (pixel values ÷ 255, or running mean/std normalization)
- [ ] Rewards are not on wildly different scales (normalize if needed)
- [ ] No NaN values in observations or rewards
- [ ] Done/terminated flags are correct

### Step 3: Check Training Stability

- [ ] Loss is not exploding or NaN → reduce learning rate, add gradient clipping
- [ ] Value function loss is decreasing → if not, critic has wrong architecture or lr
- [ ] Policy entropy is not collapsing to 0 → increase entropy coefficient
- [ ] KL divergence per update is < 0.02 (PPO) → if not, reduce K epochs or lr

### Step 4: Check Exploration

- [ ] Agent is exploring (random actions being tried) → check epsilon schedule / entropy
- [ ] Not always taking the same action → low entropy is bad early in training
- [ ] Replay buffer is diverse (DQN) → check buffer size

### Step 5: Check Performance

- [ ] Run 3–5 random seeds and check variance — one bad run may not mean failure
- [ ] Watch a rendered episode — does behavior look reasonable?
- [ ] Compare to a random baseline — if random agent gets similar reward, the task may be easy or reward is bugged

---

## Quick Reference: Algorithm Selection

```
Discrete actions, large state space?      → DQN or PPO
Continuous actions?                        → PPO or SAC
Need off-policy (replay)?                  → DQN or SAC
Need stability above all?                  → PPO
Robotics / MuJoCo benchmarks?             → SAC or TD3
RLHF / language models?                   → PPO
Learning from demonstrations?             → GAIL / behavioral cloning + RL
```

---

## Gymnasium Quick Reference

```python
import gymnasium as gym
env = gym.make("CartPole-v1")
obs, info = env.reset(seed=42)

while True:
    action = env.action_space.sample()      # or agent.predict(obs)
    obs, reward, term, trunc, info = env.step(action)
    done = term or trunc
    if done:
        obs, info = env.reset()
        break

env.close()
```

### Common Wrappers

```python
from gymnasium.wrappers import (
    RecordEpisodeStatistics,   # track ep_return, ep_len in info
    NormalizeObservation,       # running-mean normalize obs
    NormalizeReward,            # normalize rewards
    TimeLimit,                  # cap episode length
    RecordVideo,               # save rendered episodes to video
)

env = gym.make("CartPole-v1")
env = RecordEpisodeStatistics(env)
env = NormalizeObservation(env)
```

---

## stable-baselines3 Quick Reference

```python
from stable_baselines3 import PPO, DQN, SAC, A2C, TD3
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy

# Train
env = make_vec_env("CartPole-v1", n_envs=4)
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100_000)

# Evaluate
mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=20)

# Save / Load
model.save("my_model")
model = PPO.load("my_model")

# Continue training
model.set_env(env)
model.learn(total_timesteps=50_000, reset_num_timesteps=False)
```

---

## Reward Shaping Checklist

| Before shaping | After shaping |
|---|---|
| Only terminal reward | Step-level dense reward |
| Binary (0/1) | Continuous (distance, velocity) |
| No progress signal | Progress toward goal rewarded |
| Reward hacking possible | Multiple objectives balanced |

**Safe shaping formula:**
```
r_shaped = r_original + γ·F(s') - F(s)

where F(s) is any "potential" function (e.g., negative distance to goal)
```

This guarantees the shaped reward doesn't change the optimal policy.

---

## Key Metrics to Monitor

| Metric | What to watch for |
|---|---|
| `ep_rew_mean` | Should increase over time |
| `entropy_loss` | Should not collapse to 0 early |
| `value_loss` | Should decrease |
| `explained_variance` | Should be > 0.8 |
| `approx_kl` (PPO) | Should stay < 0.02 |
| `clip_fraction` (PPO) | 0.05–0.2 is healthy |

---

## Common Environment Benchmarks

| Environment | Random | Solved at | Steps to solve |
|---|---|---|---|
| CartPole-v1 | ~25 | 475 | ~50k |
| MountainCar-v0 | ~-200 | -110 | ~100k (needs shaping) |
| LunarLander-v2 | ~-200 | 200 | ~200k |
| BipedalWalker-v3 | ~-100 | 300 | ~1M |
| HalfCheetah-v4 | ~-100 | 3000 | ~1M |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Train, eval, save, load |
| [📄 Frameworks_Guide.md](./Frameworks_Guide.md) | Library comparison |

⬅️ **Prev:** [PPO](../06_PPO/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [RL for LLMs](../08_RL_for_LLMs/Theory.md)
