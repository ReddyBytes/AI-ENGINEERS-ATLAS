# PPO — Code Example

## PPO with stable-baselines3 on LunarLander

LunarLander-v2: land a spacecraft between two flags. Continuous or discrete actions.
This uses discrete actions. The agent must fire engines to slow descent and land precisely.

### Install dependencies
```bash
pip install stable-baselines3 gymnasium[box2d]
# If box2d fails: pip install gymnasium[box2d] --extra-index-url ...
# Alternative without Box2D: use CartPole-v1 or MountainCar-v0
```

```python
import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from stable_baselines3.common.evaluation import evaluate_policy
import os


# ─────────────────────────────────────────────────────────────
# 1. BASIC PPO TRAINING — Minimal Example
# ─────────────────────────────────────────────────────────────

def train_basic():
    """The simplest possible PPO training loop with stable-baselines3."""

    # Create a vectorized environment (4 parallel envs for faster data collection)
    env = make_vec_env("LunarLander-v2", n_envs=4)

    # Create PPO agent with default hyperparameters
    # stable-baselines3 chooses sensible defaults — you can override any of them
    model = PPO(
        policy="MlpPolicy",          # multi-layer perceptron policy
        env=env,
        verbose=1,                   # print progress
        learning_rate=3e-4,
        n_steps=1024,                # steps per env per update (total = n_steps * n_envs)
        batch_size=64,               # minibatch size
        n_epochs=4,                  # epochs per update
        gamma=0.999,                 # discount factor
        gae_lambda=0.98,             # GAE lambda
        clip_range=0.2,              # epsilon for clipping
        ent_coef=0.01,               # entropy coefficient
        vf_coef=0.5,                 # value function coefficient
    )

    # Train for 300,000 total environment steps
    model.learn(total_timesteps=300_000)

    # Save the trained model
    model.save("ppo_lunarlander")
    print("Model saved to ppo_lunarlander.zip")

    env.close()
    return model


# ─────────────────────────────────────────────────────────────
# 2. TRAINING WITH CALLBACKS — Auto-stop when solved
# ─────────────────────────────────────────────────────────────

def train_with_callbacks():
    """Train PPO with callbacks for evaluation and early stopping."""

    # Training environment (parallel)
    train_env = make_vec_env("LunarLander-v2", n_envs=4)

    # Separate evaluation environment (single env, deterministic)
    eval_env = gym.make("LunarLander-v2")

    # Callback: stop when mean reward >= 200 over 10 episodes
    stop_callback = StopTrainingOnRewardThreshold(
        reward_threshold=200,
        verbose=1
    )

    # Callback: evaluate every 10,000 steps, save best model
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path="./best_model/",
        log_path="./logs/",
        eval_freq=10_000,           # evaluate every 10k steps
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        callback_on_new_best=stop_callback,
        verbose=1
    )

    model = PPO(
        "MlpPolicy",
        train_env,
        verbose=0,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=64,
        n_epochs=4,
        gamma=0.999,
        gae_lambda=0.98,
        clip_range=0.2,
        ent_coef=0.01,
    )

    print("Training PPO on LunarLander-v2...")
    print("Will stop when mean reward >= 200 over 10 evaluation episodes.")
    print("LunarLander is considered 'solved' at 200+.\n")

    model.learn(
        total_timesteps=500_000,
        callback=eval_callback
    )

    train_env.close()
    eval_env.close()
    return model


# ─────────────────────────────────────────────────────────────
# 3. EVALUATE — Run trained agent and print results
# ─────────────────────────────────────────────────────────────

def evaluate_model(model, n_eval_episodes=20):
    """Evaluate a trained model."""
    eval_env = gym.make("LunarLander-v2")

    mean_reward, std_reward = evaluate_policy(
        model,
        eval_env,
        n_eval_episodes=n_eval_episodes,
        deterministic=True
    )

    print(f"\nEvaluation over {n_eval_episodes} episodes:")
    print(f"  Mean reward: {mean_reward:.2f} ± {std_reward:.2f}")
    print(f"  LunarLander solved threshold: 200")
    print(f"  Status: {'SOLVED' if mean_reward >= 200 else 'Not yet solved'}")

    eval_env.close()
    return mean_reward


# ─────────────────────────────────────────────────────────────
# 4. SAVE AND LOAD MODEL
# ─────────────────────────────────────────────────────────────

def save_and_load_demo(model):
    """Demonstrate saving and loading a PPO model."""

    # Save
    model.save("my_ppo_model")
    print("Saved model to my_ppo_model.zip")

    # Load
    loaded_model = PPO.load("my_ppo_model")
    print("Loaded model from my_ppo_model.zip")

    # You can continue training from where you left off
    # Need to re-attach an environment first
    env = make_vec_env("LunarLander-v2", n_envs=4)
    loaded_model.set_env(env)
    loaded_model.learn(total_timesteps=50_000)   # fine-tune for 50k more steps
    env.close()

    return loaded_model


# ─────────────────────────────────────────────────────────────
# 5. WATCH THE AGENT — Visualize trained policy
# ─────────────────────────────────────────────────────────────

def watch_agent(model, n_episodes=3):
    """Render the trained agent (requires a display)."""
    try:
        env = gym.make("LunarLander-v2", render_mode="human")
    except Exception:
        print("Rendering unavailable in this environment. Skipping visualization.")
        return

    for episode in range(n_episodes):
        obs, _ = env.reset()
        total_reward = 0.0
        done = False

        while not done:
            # Deterministic action: no sampling, pick most probable action
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            total_reward += reward

        print(f"Episode {episode+1}: reward = {total_reward:.1f}")

    env.close()


# ─────────────────────────────────────────────────────────────
# 6. HYPERPARAMETER TUNING — Quick grid search
# ─────────────────────────────────────────────────────────────

def quick_hyperparam_search():
    """Try a few PPO configurations and compare results."""
    configs = [
        {"name": "default",     "lr": 3e-4, "clip": 0.2, "entropy": 0.01},
        {"name": "more_explore", "lr": 3e-4, "clip": 0.2, "entropy": 0.05},
        {"name": "smaller_clip", "lr": 3e-4, "clip": 0.1, "entropy": 0.01},
        {"name": "higher_lr",   "lr": 1e-3, "clip": 0.2, "entropy": 0.01},
    ]

    results = {}
    for cfg in configs:
        print(f"\nTrying config: {cfg['name']}")
        env = make_vec_env("CartPole-v1", n_envs=4)  # use CartPole for speed

        model = PPO(
            "MlpPolicy", env,
            learning_rate=cfg["lr"],
            clip_range=cfg["clip"],
            ent_coef=cfg["entropy"],
            verbose=0
        )
        model.learn(total_timesteps=50_000)

        eval_env = gym.make("CartPole-v1")
        mean_reward, _ = evaluate_policy(model, eval_env, n_eval_episodes=20)
        results[cfg["name"]] = mean_reward
        print(f"  Mean reward: {mean_reward:.1f}")

        env.close()
        eval_env.close()

    print("\n--- Hyperparameter comparison ---")
    for name, reward in sorted(results.items(), key=lambda x: -x[1]):
        print(f"  {name}: {reward:.1f}")


# ─────────────────────────────────────────────────────────────
# 7. MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("PPO with stable-baselines3 on LunarLander-v2")
    print("=" * 50)

    # Option A: Basic training
    print("\nRunning basic PPO training (300k steps)...")
    model = train_basic()

    # Evaluate
    evaluate_model(model, n_eval_episodes=20)

    # Option B: Training with early stopping (uncomment to use)
    # model = train_with_callbacks()

    # Option C: Save and load demo (uncomment to use)
    # model = save_and_load_demo(model)

    # Option D: Watch the agent (uncomment if you have a display)
    # watch_agent(model, n_episodes=3)

    # Option E: Quick hyperparameter search (uncomment to use)
    # quick_hyperparam_search()
```

---

## Expected Results

LunarLander-v2 is considered solved when mean reward ≥ 200 over 100 episodes.

```
Training progress (verbose output from stable-baselines3):
| rollout/             |          |
|    ep_len_mean       | 412      |
|    ep_rew_mean       | 189      |
| time/                |          |
|    fps               | 1234     |
|    iterations        | 73       |
|    time_elapsed      | 242      |
|    total_timesteps   | 299008   |
| train/               |          |
|    approx_kl         | 0.00823  |
|    clip_fraction     | 0.108    |
|    clip_range        | 0.2      |
|    entropy_loss      | -0.569   |
|    explained_variance| 0.972    |
|    learning_rate     | 0.0003   |
|    loss              | 27.1     |
|    policy_gradient_loss | -0.00647 |
|    value_loss        | 59.8     |

Evaluation over 20 episodes:
  Mean reward: 214.56 ± 42.31
  LunarLander solved threshold: 200
  Status: SOLVED
```

---

## Key stable-baselines3 Diagnostic Metrics

| Metric | What it means | Healthy range |
|---|---|---|
| `approx_kl` | KL divergence between old and new policy | < 0.02 |
| `clip_fraction` | Fraction of samples where ratio was clipped | 0.05–0.2 |
| `entropy_loss` | Policy entropy (negative = high entropy) | Should not collapse to 0 |
| `explained_variance` | How well critic explains returns | > 0.8 is good |
| `ep_rew_mean` | Mean episode reward | Should increase over time |
| `value_loss` | Critic MSE | Should decrease over time |

---

## CartPole Alternative (No Box2D Required)

If LunarLander installation fails, replace `LunarLander-v2` with `CartPole-v1` everywhere. CartPole trains in ~50k steps and requires no extra dependencies.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Clipped objective explained |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Policy Gradients](../05_Policy_Gradients/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [RL in Practice](../07_RL_in_Practice/Theory.md)
