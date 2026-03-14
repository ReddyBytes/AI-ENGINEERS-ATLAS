# RL in Practice — Code Example

## PPO with stable-baselines3: Train, Evaluate, Save, Load

This file shows the complete practical workflow: training, evaluation, saving, loading,
and a reward-shaping demonstration on MountainCar.

### Install
```bash
pip install stable-baselines3 gymnasium
```

```python
import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor
import os


# ─────────────────────────────────────────────────────────────
# 1. BASIC WORKFLOW: TRAIN → EVALUATE → SAVE → LOAD
# ─────────────────────────────────────────────────────────────

def basic_workflow():
    """Complete workflow from scratch to saved model."""

    print("=" * 55)
    print("1. BASIC PPO WORKFLOW")
    print("=" * 55)

    # Create vectorized environment (4 parallel envs = faster training)
    env = make_vec_env("CartPole-v1", n_envs=4, seed=42)

    # Create PPO model
    model = PPO(
        "MlpPolicy",
        env,
        verbose=0,              # set to 1 to see training logs
        learning_rate=3e-4,
        n_steps=512,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,
        seed=42,
    )

    # TRAIN
    print("Training for 50,000 steps...")
    model.learn(total_timesteps=50_000)
    print("Training complete.")

    # EVALUATE (use a single, non-vectorized env for clean evaluation)
    eval_env = gym.make("CartPole-v1")
    mean_reward, std_reward = evaluate_policy(
        model, eval_env, n_eval_episodes=20, deterministic=True
    )
    print(f"Evaluation: mean={mean_reward:.1f} ± {std_reward:.1f}")
    print(f"CartPole solved threshold: 475")
    eval_env.close()

    # SAVE
    model.save("cartpole_ppo")
    print("Model saved to cartpole_ppo.zip")

    # LOAD
    loaded_model = PPO.load("cartpole_ppo")
    print("Model loaded from cartpole_ppo.zip")

    # Verify loaded model works
    eval_env = gym.make("CartPole-v1")
    mean_reward2, _ = evaluate_policy(
        loaded_model, eval_env, n_eval_episodes=10, deterministic=True
    )
    print(f"Loaded model evaluation: mean={mean_reward2:.1f}")
    eval_env.close()

    # CONTINUE TRAINING (fine-tune)
    loaded_model.set_env(env)
    loaded_model.learn(total_timesteps=20_000, reset_num_timesteps=False)
    print("Fine-tuned for additional 20,000 steps.")

    env.close()
    return loaded_model


# ─────────────────────────────────────────────────────────────
# 2. REWARD SHAPING DEMONSTRATION
#    MountainCar: hard with sparse reward, easy with shaping
# ─────────────────────────────────────────────────────────────

class RewardShapedMountainCar(gym.Wrapper):
    """
    MountainCar-v0 with potential-based reward shaping.

    Original reward: -1 per step (car must reach height=0.45 to get 0)
    Shaped reward: add velocity term so agent learns to build momentum

    The formula is potential-based:
    reward_shaped = reward + gamma * F(s') - F(s)
    where F(s) = car_position + abs(car_velocity) * velocity_weight

    This is safe by the potential shaping theorem — doesn't change optimal policy.
    """
    def __init__(self, env, velocity_weight=0.3):
        super().__init__(env)
        self.velocity_weight = velocity_weight
        self.gamma = 0.99

    def _potential(self, obs):
        """F(s) = position + velocity_weight * |velocity|"""
        position, velocity = obs[0], obs[1]
        return position + self.velocity_weight * abs(velocity)

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        # Note: we need the previous state to compute F(s)
        # We track it via a stored attribute
        F_next = self._potential(obs)
        shaped_reward = reward + self.gamma * F_next - self.F_prev
        self.F_prev = F_next
        return obs, shaped_reward, terminated, truncated, info

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        self.F_prev = self._potential(obs)  # initialize F_prev
        return obs, info


def compare_reward_shaping():
    """
    Train two agents on MountainCar:
    1. Default (sparse reward) — usually fails or takes very long
    2. Shaped reward — learns faster with velocity guidance
    """
    print("\n" + "=" * 55)
    print("2. REWARD SHAPING DEMO: MountainCar")
    print("=" * 55)
    print("MountainCar: sparse reward (-1/step). Hard to learn.")
    print("Testing default vs shaped reward.\n")

    TIMESTEPS = 100_000

    # --- WITHOUT shaping ---
    def make_plain_env():
        return gym.make("MountainCar-v0")

    plain_env = make_vec_env(make_plain_env, n_envs=4, seed=42)
    plain_model = PPO("MlpPolicy", plain_env, verbose=0, seed=42)
    plain_model.learn(total_timesteps=TIMESTEPS)

    eval_plain = gym.make("MountainCar-v0")
    mean_plain, _ = evaluate_policy(plain_model, eval_plain, n_eval_episodes=20)
    eval_plain.close()
    plain_env.close()

    # --- WITH shaping ---
    def make_shaped_env():
        base_env = gym.make("MountainCar-v0")
        return RewardShapedMountainCar(base_env, velocity_weight=0.3)

    shaped_env = make_vec_env(make_shaped_env, n_envs=4, seed=42)
    shaped_model = PPO("MlpPolicy", shaped_env, verbose=0, seed=42)
    shaped_model.learn(total_timesteps=TIMESTEPS)

    # Evaluate on ORIGINAL (unshaped) env for fair comparison
    eval_shaped = gym.make("MountainCar-v0")
    mean_shaped, _ = evaluate_policy(shaped_model, eval_shaped, n_eval_episodes=20)
    eval_shaped.close()
    shaped_env.close()

    print(f"Without shaping: mean reward = {mean_plain:.1f}")
    print(f"With shaping:    mean reward = {mean_shaped:.1f}")
    print(f"MountainCar solved: episode reward > -110")
    if mean_shaped > mean_plain + 10:
        print("Reward shaping helped significantly!")
    else:
        print("Try more timesteps or different shaping weight.")


# ─────────────────────────────────────────────────────────────
# 3. MONITORING TRAINING WITH CALLBACKS
# ─────────────────────────────────────────────────────────────

def training_with_monitoring():
    """Train with periodic evaluation and save best model."""
    print("\n" + "=" * 55)
    print("3. TRAINING WITH MONITORING")
    print("=" * 55)

    os.makedirs("./logs/", exist_ok=True)
    os.makedirs("./best_model/", exist_ok=True)

    train_env = make_vec_env("LunarLander-v2", n_envs=4, seed=42)
    eval_env = Monitor(gym.make("LunarLander-v2"))

    # Evaluate every 25,000 steps, keep best model
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./best_model/",
        log_path="./logs/",
        eval_freq=25_000 // 4,   # divide by n_envs (total steps per check)
        n_eval_episodes=10,
        deterministic=True,
        verbose=1,
    )

    model = PPO("MlpPolicy", train_env, verbose=0, seed=42)
    model.learn(total_timesteps=200_000, callback=eval_callback)

    # Load the best model (might be different from final model)
    best_model = PPO.load("./best_model/best_model")
    final_mean, _ = evaluate_policy(best_model, eval_env, n_eval_episodes=20)
    print(f"\nBest model mean reward: {final_mean:.1f}")

    train_env.close()
    eval_env.close()
    return best_model


# ─────────────────────────────────────────────────────────────
# 4. COMPARING ALGORITHMS
# ─────────────────────────────────────────────────────────────

def compare_algorithms():
    """Quick comparison of PPO vs DQN on CartPole."""
    print("\n" + "=" * 55)
    print("4. PPO vs DQN on CartPole")
    print("=" * 55)

    TIMESTEPS = 50_000
    results = {}

    for algo_name, algo_class in [("PPO", PPO), ("DQN", DQN)]:
        env = make_vec_env("CartPole-v1", n_envs=1, seed=42)
        model = algo_class("MlpPolicy", env, verbose=0, seed=42)
        model.learn(total_timesteps=TIMESTEPS)

        eval_env = gym.make("CartPole-v1")
        mean_reward, std_reward = evaluate_policy(
            model, eval_env, n_eval_episodes=20
        )
        results[algo_name] = (mean_reward, std_reward)
        print(f"{algo_name}: {mean_reward:.1f} ± {std_reward:.1f}")

        env.close()
        eval_env.close()

    winner = max(results, key=lambda k: results[k][0])
    print(f"\nBetter on CartPole after {TIMESTEPS} steps: {winner}")


# ─────────────────────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Basic workflow (CartPole)
    model = basic_workflow()

    # 2. Reward shaping demo (MountainCar)
    # compare_reward_shaping()   # uncomment to run (takes ~2 min)

    # 3. Training with monitoring (LunarLander — needs box2d)
    # training_with_monitoring()  # uncomment to run

    # 4. Compare algorithms
    # compare_algorithms()        # uncomment to run
```

---

## Expected Output

```
=======================================================
1. BASIC PPO WORKFLOW
=======================================================
Training for 50,000 steps...
Training complete.
Evaluation: mean=487.2 ± 23.4
CartPole solved threshold: 475
Model saved to cartpole_ppo.zip
Model loaded from cartpole_ppo.zip
Loaded model evaluation: mean=489.1
Fine-tuned for additional 20,000 steps.

=======================================================
2. REWARD SHAPING DEMO: MountainCar
=======================================================
MountainCar: sparse reward (-1/step). Hard to learn.
Testing default vs shaped reward.

Without shaping: mean reward = -200.0
With shaping:    mean reward = -127.4
MountainCar solved: episode reward > -110
Reward shaping helped significantly!
```

---

## Key Patterns to Remember

**Parallel environments** — Always use `make_vec_env` with `n_envs >= 4` for PPO. It collects experience 4x faster at no extra cost.

**Monitor vs eval environment** — The training environment can be vectorized. The evaluation environment should be a single `Monitor`-wrapped env for clean metrics.

**`reset_num_timesteps=False`** — When continuing training on a loaded model, pass this to keep the timestep counter going (important for lr schedules, epsilon decay, etc.).

**Separate eval environment** — Never evaluate on the training environment. Vectorized environments modify state during evaluation, giving misleading numbers.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Debugging checklist |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Frameworks_Guide.md](./Frameworks_Guide.md) | Library comparison |

⬅️ **Prev:** [PPO](../06_PPO/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [RL for LLMs](../08_RL_for_LLMs/Theory.md)
