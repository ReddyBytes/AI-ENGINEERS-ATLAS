# Policy Gradients — Code Example

## REINFORCE on CartPole with PyTorch

REINFORCE is the simplest policy gradient algorithm. This implementation includes
an optional baseline (mean return) to reduce variance.

### Install dependencies
```bash
pip install torch gymnasium
```

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import gymnasium as gym
from torch.distributions import Categorical


# ─────────────────────────────────────────────────────────────
# 1. POLICY NETWORK
# ─────────────────────────────────────────────────────────────

class PolicyNetwork(nn.Module):
    """
    Maps state → action probabilities.
    For CartPole: 4 inputs, 2 outputs (softmax probabilities for left/right).
    """
    def __init__(self, obs_dim, n_actions, hidden_size=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, n_actions)
        )

    def forward(self, x):
        # Output raw logits; Categorical distribution handles softmax internally
        return self.net(x)

    def get_action(self, state):
        """
        Given a state, sample an action from the policy distribution.
        Returns the action and its log probability (needed for the gradient).
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0)  # add batch dim
        logits = self.forward(state_tensor)
        dist = Categorical(logits=logits)  # softmax probability distribution
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob


# ─────────────────────────────────────────────────────────────
# 2. COMPUTE DISCOUNTED RETURNS
# ─────────────────────────────────────────────────────────────

def compute_returns(rewards, gamma=0.99):
    """
    Given a list of rewards from one episode, compute the discounted return
    G_t = r_t + γ·r_{t+1} + γ²·r_{t+2} + ... for each timestep t.

    We compute this backward for efficiency:
    G_T = r_T
    G_{T-1} = r_{T-1} + γ·G_T
    ...
    """
    returns = []
    G = 0.0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)   # prepend so returns[0] = G_0
    return torch.FloatTensor(returns)


# ─────────────────────────────────────────────────────────────
# 3. REINFORCE TRAINING LOOP
# ─────────────────────────────────────────────────────────────

def train_reinforce(n_episodes=1000, gamma=0.99, lr=1e-3, use_baseline=True):
    """
    REINFORCE: collect full episode, compute returns, update policy.

    Args:
        use_baseline: if True, subtract mean return as variance reduction.
    """
    env = gym.make("CartPole-v1")
    obs_dim = env.observation_space.shape[0]   # 4
    n_actions = env.action_space.n             # 2

    policy = PolicyNetwork(obs_dim, n_actions)
    optimizer = optim.Adam(policy.parameters(), lr=lr)

    episode_rewards = []

    for episode in range(n_episodes):
        # ── Collect one full episode ──────────────────────────
        state, _ = env.reset()
        log_probs = []      # log π(a_t | s_t) for each step
        rewards = []        # r_t for each step
        done = False

        while not done:
            action, log_prob = policy.get_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            log_probs.append(log_prob)
            rewards.append(reward)
            state = next_state

        # ── Compute discounted returns ────────────────────────
        returns = compute_returns(rewards, gamma)

        # ── Optional: subtract baseline (mean return) ─────────
        if use_baseline:
            # Subtracting mean reduces variance without changing the gradient direction
            advantages = returns - returns.mean()
        else:
            advantages = returns

        # ── Optional: normalize advantages ────────────────────
        # Dividing by std further stabilizes training
        if len(advantages) > 1:
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # ── Compute REINFORCE loss ────────────────────────────
        # Loss = -Σ_t [ A_t · log π(a_t|s_t) ]
        # Negative because PyTorch minimizes, we want to maximize J(θ)
        log_probs_tensor = torch.stack(log_probs)   # shape: [T]
        loss = -(log_probs_tensor * advantages).sum()

        # ── Gradient update ───────────────────────────────────
        optimizer.zero_grad()
        loss.backward()
        # Clip gradients for stability
        torch.nn.utils.clip_grad_norm_(policy.parameters(), max_norm=1.0)
        optimizer.step()

        total_reward = sum(rewards)
        episode_rewards.append(total_reward)

        # Print progress every 50 episodes
        if (episode + 1) % 50 == 0:
            avg = sum(episode_rewards[-50:]) / 50
            print(f"Episode {episode+1:4d} | "
                  f"Avg reward (50 ep): {avg:6.1f} | "
                  f"Episode length: {len(rewards):3d}")

    env.close()
    return policy, episode_rewards


# ─────────────────────────────────────────────────────────────
# 4. EVALUATION
# ─────────────────────────────────────────────────────────────

def evaluate(policy, n_episodes=10):
    """Evaluate the trained policy greedily (take most probable action)."""
    env = gym.make("CartPole-v1")
    rewards = []

    for episode in range(n_episodes):
        state, _ = env.reset()
        total_reward = 0.0
        done = False

        while not done:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                logits = policy(state_tensor)
                action = logits.argmax().item()  # greedy, no sampling

            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            state = next_state
            total_reward += reward

        rewards.append(total_reward)

    env.close()
    avg = sum(rewards) / len(rewards)
    print(f"\nEvaluation over {n_episodes} episodes:")
    print(f"  Average reward: {avg:.1f}")
    print(f"  Min: {min(rewards):.0f} | Max: {max(rewards):.0f}")
    return rewards


# ─────────────────────────────────────────────────────────────
# 5. BASELINE COMPARISON — WITH vs WITHOUT
# ─────────────────────────────────────────────────────────────

def compare_baseline():
    """Train two agents: one with baseline, one without. Compare learning curves."""
    import random
    torch.manual_seed(42)
    random.seed(42)
    np.random.seed(42)

    print("=== Training WITH baseline ===")
    policy_with, rewards_with = train_reinforce(
        n_episodes=500, use_baseline=True
    )

    torch.manual_seed(42)
    random.seed(42)
    np.random.seed(42)

    print("\n=== Training WITHOUT baseline ===")
    policy_without, rewards_without = train_reinforce(
        n_episodes=500, use_baseline=False
    )

    # Compare final 100 episodes
    avg_with = sum(rewards_with[-100:]) / 100
    avg_without = sum(rewards_without[-100:]) / 100
    print(f"\nFinal avg reward WITH baseline:    {avg_with:.1f}")
    print(f"Final avg reward WITHOUT baseline: {avg_without:.1f}")
    print("The baseline version should show less noisy training and higher final reward.")


# ─────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import torch
    import random
    import numpy as np

    torch.manual_seed(42)
    random.seed(42)
    np.random.seed(42)

    print("Training REINFORCE on CartPole-v1...")
    print("REINFORCE: collect full episode, compute returns, update policy.")
    print("Max reward: 500 steps.\n")

    policy, rewards = train_reinforce(
        n_episodes=600,
        gamma=0.99,
        lr=1e-3,
        use_baseline=True
    )

    final_avg = sum(rewards[-100:]) / 100
    print(f"\nFinal average reward (last 100 episodes): {final_avg:.1f}")

    evaluate(policy, n_episodes=20)
```

---

## Expected Output

REINFORCE is noisier than DQN because it uses Monte Carlo returns:

```
Episode   50 | Avg reward (50 ep):   35.2 | Episode length:  25
Episode  100 | Avg reward (50 ep):   62.7 | Episode length:  58
Episode  150 | Avg reward (50 ep):  124.5 | Episode length: 100
Episode  200 | Avg reward (50 ep):  198.3 | Episode length: 187
Episode  300 | Avg reward (50 ep):  341.6 | Episode length: 330
Episode  400 | Avg reward (50 ep):  432.8 | Episode length: 421
Episode  500 | Avg reward (50 ep):  468.2 | Episode length: 461
Episode  600 | Avg reward (50 ep):  487.1 | Episode length: 480

Evaluation over 20 episodes:
  Average reward: 486.5
  Min: 451 | Max: 500
```

Training is noisier than DQN — expect more variance in the learning curve.

---

## Key Design Choices Explained

**Why `Categorical(logits=logits)` instead of softmax?**
Using logits directly is numerically more stable than computing softmax first. PyTorch's Categorical does the softmax internally in a numerically stable way.

**Why `insert(0, G)` in compute_returns?**
We process rewards backward (T → 0) because G_t = r_t + γ·G_{t+1}. Inserting at index 0 builds the list in forward order.

**Why `loss = -(log_probs * advantages).sum()`?**
PyTorch minimizes, so we negate the policy gradient (which we want to maximize). `.sum()` vs `.mean()` — both work; sum means the learning rate scales with episode length, mean doesn't. Experiment with both.

**Why normalize advantages?**
Without normalization, long episodes have much larger gradient magnitudes than short ones. Normalizing makes the effective learning rate consistent across episodes of different lengths.

---

## What to Try

1. **Disable the baseline** (`use_baseline=False`) — notice the noisier training curve.
2. **Disable advantage normalization** — notice more instability at different episode lengths.
3. **Increase γ to 1.0** — episodes are finite, so this is safe. Does it learn faster?
4. **Lower lr to 1e-4** — slower but more stable.
5. **Try `LunarLander-v2`** — harder environment; REINFORCE may struggle without GAE.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Policy gradient theorem |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [PPO](../06_PPO/Theory.md)
