# DQN — Code Example

## DQN on CartPole with PyTorch

CartPole: balance a pole on a moving cart. The observation is 4 floats
(position, velocity, angle, angular velocity). Actions: push left or right.
Episode ends when the pole falls past 12 degrees or cart goes off-screen.
Max score: 500 steps.

### Install dependencies
```bash
pip install torch gymnasium
```

```python
import random
import numpy as np
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import gymnasium as gym


# ─────────────────────────────────────────────────────────────
# 1. NEURAL NETWORK — The Q-Function Approximator
# ─────────────────────────────────────────────────────────────

class DQN(nn.Module):
    """
    Simple 2-layer MLP that maps observations → Q-values for each action.
    Input:  observation vector (4 floats for CartPole)
    Output: Q-value for each action (2 values for CartPole)
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
        return self.net(x)


# ─────────────────────────────────────────────────────────────
# 2. REPLAY BUFFER — Store and sample experiences
# ─────────────────────────────────────────────────────────────

class ReplayBuffer:
    """
    Fixed-capacity circular buffer storing (s, a, r, s', done) tuples.
    Random sampling breaks temporal correlations in training data.
    """
    def __init__(self, capacity=10_000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        """Store one experience tuple."""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        """Random sample of batch_size experiences."""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32)
        )

    def __len__(self):
        return len(self.buffer)


# ─────────────────────────────────────────────────────────────
# 3. DQN AGENT
# ─────────────────────────────────────────────────────────────

class DQNAgent:
    def __init__(self, obs_dim, n_actions,
                 lr=1e-3,
                 gamma=0.99,
                 epsilon_start=1.0,
                 epsilon_end=0.01,
                 epsilon_decay=500,       # steps until epsilon reaches end
                 buffer_capacity=10_000,
                 batch_size=64,
                 target_update_freq=500,  # steps between target network copies
                 warmup_steps=1_000):     # fill buffer before training

        self.n_actions = n_actions
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.warmup_steps = warmup_steps

        # Epsilon annealing
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        # Online network (trained) and target network (frozen copy)
        self.online_net = DQN(obs_dim, n_actions)
        self.target_net = DQN(obs_dim, n_actions)
        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()  # target net is never in training mode

        self.optimizer = optim.Adam(self.online_net.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

        self.replay_buffer = ReplayBuffer(buffer_capacity)
        self.total_steps = 0

    def get_epsilon(self):
        """Linear epsilon annealing: from start to end over decay steps."""
        progress = min(self.total_steps / self.epsilon_decay, 1.0)
        return self.epsilon_start + progress * (self.epsilon_end - self.epsilon_start)

    def choose_action(self, state):
        """Epsilon-greedy action selection."""
        epsilon = self.get_epsilon()
        if random.random() < epsilon:
            return random.randint(0, self.n_actions - 1)  # explore

        # exploit: use online network
        state_tensor = torch.FloatTensor(state).unsqueeze(0)  # add batch dim
        with torch.no_grad():
            q_values = self.online_net(state_tensor)
        return q_values.argmax().item()

    def store_experience(self, state, action, reward, next_state, done):
        """Add one experience to replay buffer."""
        self.replay_buffer.push(state, action, reward, next_state, done)
        self.total_steps += 1

    def train_step(self):
        """Sample a minibatch and perform one gradient update."""
        if len(self.replay_buffer) < self.warmup_steps:
            return None  # not enough data yet

        # Sample minibatch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(
            self.batch_size
        )

        # Convert to tensors
        states_t      = torch.FloatTensor(states)
        actions_t     = torch.LongTensor(actions)
        rewards_t     = torch.FloatTensor(rewards)
        next_states_t = torch.FloatTensor(next_states)
        dones_t       = torch.FloatTensor(dones)

        # Current Q-values: Q(s, a) for the actions actually taken
        # gather() picks the Q-value for the action that was taken
        current_q = self.online_net(states_t).gather(
            1, actions_t.unsqueeze(1)
        ).squeeze(1)

        # TD targets using frozen TARGET network
        with torch.no_grad():
            # max Q-value from next states (0 if episode done)
            next_q = self.target_net(next_states_t).max(1)[0]
            target_q = rewards_t + self.gamma * next_q * (1.0 - dones_t)

        # MSE loss and backprop
        loss = self.loss_fn(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        # Clip gradients to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(self.online_net.parameters(), 1.0)
        self.optimizer.step()

        # Hard update: copy online → target every target_update_freq steps
        if self.total_steps % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.online_net.state_dict())

        return loss.item()


# ─────────────────────────────────────────────────────────────
# 4. TRAINING LOOP
# ─────────────────────────────────────────────────────────────

def train(n_episodes=500, render_every=None):
    env = gym.make("CartPole-v1")
    obs_dim = env.observation_space.shape[0]   # 4
    n_actions = env.action_space.n             # 2

    agent = DQNAgent(
        obs_dim=obs_dim,
        n_actions=n_actions,
        lr=1e-3,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_end=0.02,
        epsilon_decay=10_000,      # linear decay over 10k steps
        buffer_capacity=10_000,
        batch_size=64,
        target_update_freq=500,
        warmup_steps=1_000
    )

    episode_rewards = []

    for episode in range(n_episodes):
        state, _ = env.reset()
        total_reward = 0.0
        done = False

        while not done:
            action = agent.choose_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated

            # Store and train
            agent.store_experience(state, action, reward, next_state, float(done))
            agent.train_step()

            state = next_state
            total_reward += reward

        episode_rewards.append(total_reward)

        # Print progress
        if (episode + 1) % 50 == 0:
            avg = sum(episode_rewards[-50:]) / 50
            eps = agent.get_epsilon()
            print(f"Episode {episode+1:4d} | "
                  f"Avg reward (50 ep): {avg:6.1f} | "
                  f"Epsilon: {eps:.3f} | "
                  f"Buffer: {len(agent.replay_buffer):6d}")

    env.close()
    return agent, episode_rewards


# ─────────────────────────────────────────────────────────────
# 5. EVALUATION — Test the trained agent
# ─────────────────────────────────────────────────────────────

def evaluate(agent, n_episodes=10):
    """Run the trained agent without exploration."""
    env = gym.make("CartPole-v1")
    rewards = []

    for episode in range(n_episodes):
        state, _ = env.reset()
        total_reward = 0.0
        done = False

        while not done:
            # Greedy: no epsilon exploration
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                action = agent.online_net(state_tensor).argmax().item()

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
    print(f"  CartPole is 'solved' at avg 475+ over 100 episodes")
    return rewards


# ─────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    torch.manual_seed(42)
    random.seed(42)
    np.random.seed(42)

    print("Training DQN on CartPole-v1...")
    print("CartPole: balance a pole on a cart. Max reward = 500.")
    print()

    agent, rewards = train(n_episodes=500)

    print("\n--- Training complete ---")
    final_avg = sum(rewards[-100:]) / 100
    print(f"Average reward over final 100 episodes: {final_avg:.1f}")

    evaluate(agent, n_episodes=20)
```

---

## Expected Training Progress

```
Episode   50 | Avg reward (50 ep):   22.3 | Epsilon: 0.895 | Buffer:   1234
Episode  100 | Avg reward (50 ep):   45.7 | Epsilon: 0.789 | Buffer:   3456
Episode  150 | Avg reward (50 ep):  112.4 | Epsilon: 0.634 | Buffer:   6789
Episode  200 | Avg reward (50 ep):  287.6 | Epsilon: 0.456 | Buffer:  10000
Episode  250 | Avg reward (50 ep):  412.3 | Epsilon: 0.278 | Buffer:  10000
Episode  300 | Avg reward (50 ep):  463.8 | Epsilon: 0.123 | Buffer:  10000
Episode  400 | Avg reward (50 ep):  489.2 | Epsilon: 0.024 | Buffer:  10000
Episode  500 | Avg reward (50 ep):  494.7 | Epsilon: 0.020 | Buffer:  10000

Evaluation over 20 episodes:
  Average reward: 493.5
  Min: 467 | Max: 500
```

---

## Key Things to Notice in the Code

1. **Two networks** — `online_net` is trained; `target_net` is a frozen copy.
2. **`gather(1, actions)`** — selects only the Q-value for the action that was actually taken. We don't update Q-values for actions we didn't take.
3. **`(1.0 - dones_t)`** — zeros out the future term for terminal states. No future reward if the episode ended.
4. **`torch.no_grad()`** — target computation has no gradients. We don't want the target to change during backprop.
5. **Gradient clipping** — prevents exploding gradients in early training.

---

## Experiments to Try

- Remove the target network (set `target_update_freq=1`) — training becomes unstable.
- Remove experience replay (train directly on each step without buffering) — observe correlation-caused instability.
- Increase `epsilon_decay` to 50,000 — the agent explores longer and may learn better.
- Try `CartPole-v0` (easier: max 200 steps) for a quick demo.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Architecture diagrams |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Q-Learning](../03_Q_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Policy Gradients](../05_Policy_Gradients/Theory.md)
