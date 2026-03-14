# Q-Learning — Code Example

## Q-Learning on a Gridworld (Pure Python, No Dependencies)

This example implements Q-Learning on a 5×5 gridworld from scratch.
No gymnasium, no numpy required — runs with only Python's standard library.

### The Environment

```
+--+--+--+--+--+
|S |  |  |H |  |   S = Start (0,0)
+--+--+--+--+--+   H = Hole (penalty)
|  |  |H |  |  |   G = Goal (+10 reward)
+--+--+--+--+--+
|  |  |  |  |H |
+--+--+--+--+--+
|H |  |  |  |  |
+--+--+--+--+--+
|  |  |  |  |G |
+--+--+--+--+--+
```

Actions: 0=Up, 1=Down, 2=Left, 3=Right

```python
import random
import math


# ─────────────────────────────────────────────────────────────
# 1. ENVIRONMENT
# ─────────────────────────────────────────────────────────────

class GridWorld:
    """
    5x5 grid. Agent starts at (0,0), must reach (4,4).
    Holes at (0,3), (1,2), (2,4), (3,0) — step in one and get -5 reward + episode ends.
    Every step costs -0.1 (encourages efficiency).
    Reaching the goal gives +10.
    """

    def __init__(self, size=5):
        self.size = size
        self.holes = {(0, 3), (1, 2), (2, 4), (3, 0)}
        self.goal = (4, 4)
        self.start = (0, 0)
        self.state = self.start

    def reset(self):
        """Reset to start position, return initial state index."""
        self.state = self.start
        return self._state_to_index(self.state)

    def step(self, action):
        """
        Take action: 0=Up, 1=Down, 2=Left, 3=Right
        Returns: (next_state_index, reward, done)
        """
        row, col = self.state
        if action == 0:    # Up
            row = max(0, row - 1)
        elif action == 1:  # Down
            row = min(self.size - 1, row + 1)
        elif action == 2:  # Left
            col = max(0, col - 1)
        elif action == 3:  # Right
            col = min(self.size - 1, col + 1)

        self.state = (row, col)
        next_state = self._state_to_index(self.state)

        # Check outcomes
        if self.state in self.holes:
            return next_state, -5.0, True   # fell in hole
        elif self.state == self.goal:
            return next_state, 10.0, True   # reached goal
        else:
            return next_state, -0.1, False  # normal step

    def _state_to_index(self, state):
        """Convert (row, col) to a single integer index."""
        row, col = state
        return row * self.size + col

    @property
    def n_states(self):
        return self.size * self.size

    @property
    def n_actions(self):
        return 4


# ─────────────────────────────────────────────────────────────
# 2. Q-LEARNING AGENT
# ─────────────────────────────────────────────────────────────

class QLearningAgent:
    """
    Tabular Q-Learning agent.
    Maintains a Q-table of shape [n_states x n_actions].
    Uses epsilon-greedy action selection.
    """

    def __init__(self, n_states, n_actions, alpha=0.1, gamma=0.99,
                 epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        self.n_states = n_states
        self.n_actions = n_actions
        self.alpha = alpha          # learning rate
        self.gamma = gamma          # discount factor
        self.epsilon = epsilon      # current exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Initialize Q-table to zeros
        # q_table[state][action] = expected future reward
        self.q_table = [[0.0] * n_actions for _ in range(n_states)]

    def choose_action(self, state):
        """Epsilon-greedy action selection."""
        if random.random() < self.epsilon:
            return random.randint(0, self.n_actions - 1)  # explore
        else:
            # exploit: pick action with highest Q-value
            return self._best_action(state)

    def _best_action(self, state):
        """Return the action with the highest Q-value for this state."""
        q_values = self.q_table[state]
        max_q = max(q_values)
        # If multiple actions tie, pick randomly among them
        best_actions = [a for a, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def update(self, state, action, reward, next_state, done):
        """
        Q-Learning update:
        Q(s,a) += alpha * [r + gamma * max Q(s',a') - Q(s,a)]
        """
        current_q = self.q_table[state][action]

        if done:
            # No future reward if episode ended
            target = reward
        else:
            best_next_q = max(self.q_table[next_state])
            target = reward + self.gamma * best_next_q

        td_error = target - current_q
        self.q_table[state][action] += self.alpha * td_error

    def decay_epsilon(self):
        """Reduce epsilon after each episode (explore less over time)."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)


# ─────────────────────────────────────────────────────────────
# 3. TRAINING LOOP
# ─────────────────────────────────────────────────────────────

def train(n_episodes=1000):
    env = GridWorld()
    agent = QLearningAgent(
        n_states=env.n_states,
        n_actions=env.n_actions,
        alpha=0.1,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.995
    )

    episode_rewards = []
    episode_lengths = []

    for episode in range(n_episodes):
        state = env.reset()
        total_reward = 0.0
        steps = 0
        done = False

        while not done and steps < 200:  # 200 step cap to avoid infinite loops
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)

            agent.update(state, action, reward, next_state, done)

            state = next_state
            total_reward += reward
            steps += 1

        agent.decay_epsilon()
        episode_rewards.append(total_reward)
        episode_lengths.append(steps)

        # Print progress every 100 episodes
        if (episode + 1) % 100 == 0:
            avg_reward = sum(episode_rewards[-100:]) / 100
            avg_steps = sum(episode_lengths[-100:]) / 100
            print(f"Episode {episode+1:4d} | "
                  f"Avg reward (last 100): {avg_reward:6.2f} | "
                  f"Avg steps: {avg_steps:5.1f} | "
                  f"Epsilon: {agent.epsilon:.3f}")

    return agent, episode_rewards


# ─────────────────────────────────────────────────────────────
# 4. EVALUATION — WATCH THE TRAINED AGENT
# ─────────────────────────────────────────────────────────────

def evaluate(agent, n_episodes=5):
    """Run the trained agent greedily (no exploration) and print paths."""
    env = GridWorld()
    action_names = ["Up", "Down", "Left", "Right"]

    print("\n--- Evaluating Trained Agent (no exploration) ---")

    for episode in range(n_episodes):
        state = env.reset()
        total_reward = 0.0
        steps = 0
        path = [env.state]
        done = False

        while not done and steps < 30:
            # Act greedily — no exploration
            action = agent._best_action(state)
            next_state, reward, done = env.step(action)
            path.append(env.state)
            total_reward += reward
            state = next_state
            steps += 1

        success = env.state == env.goal
        print(f"Episode {episode+1}: {'SUCCESS' if success else 'FAILED '} | "
              f"Steps: {steps:2d} | Reward: {total_reward:6.2f} | "
              f"Path: {' → '.join(str(p) for p in path[:8])}"
              + (" ..." if len(path) > 8 else ""))


# ─────────────────────────────────────────────────────────────
# 5. PRINT Q-TABLE (OPTIONAL — FOR SMALL GRIDS)
# ─────────────────────────────────────────────────────────────

def print_best_actions(agent, grid_size=5):
    """Print the best action for each cell in the grid."""
    action_symbols = ["↑", "↓", "←", "→"]
    print("\n--- Best Action Per Cell ---")
    print("(H=Hole, G=Goal)")
    holes = {(0,3), (1,2), (2,4), (3,0)}
    goal = (4, 4)

    for row in range(grid_size):
        row_str = ""
        for col in range(grid_size):
            if (row, col) in holes:
                row_str += " H "
            elif (row, col) == goal:
                row_str += " G "
            else:
                state_idx = row * grid_size + col
                best_a = agent._best_action(state_idx)
                row_str += f" {action_symbols[best_a]} "
        print(row_str)


# ─────────────────────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    random.seed(42)

    print("Training Q-Learning agent on 5x5 GridWorld...")
    print("Grid: S=Start(0,0), G=Goal(4,4), H=Holes")
    print()

    agent, rewards = train(n_episodes=1000)

    # Check overall success rate in last 100 episodes
    # (A good agent should consistently reach the goal)
    final_avg = sum(rewards[-100:]) / 100
    print(f"\nFinal average reward (episodes 901-1000): {final_avg:.2f}")
    print("(Goal reward is +10 minus step penalties. Expect ~8-9 if agent succeeds.)")

    evaluate(agent, n_episodes=5)
    print_best_actions(agent)
```

---

## Expected Output

After 1000 episodes you should see something like:

```
Episode  100 | Avg reward (last 100):  -1.23 | Avg steps: 45.2 | Epsilon: 0.607
Episode  200 | Avg reward (last 100):   2.45 | Avg steps: 32.1 | Epsilon: 0.368
Episode  300 | Avg reward (last 100):   6.12 | Avg steps: 18.7 | Epsilon: 0.223
Episode  400 | Avg reward (last 100):   7.89 | Avg steps: 12.4 | Epsilon: 0.135
Episode  500 | Avg reward (last 100):   8.21 | Avg steps:  9.8 | Epsilon: 0.082
...
Episode 1000 | Avg reward (last 100):   8.67 | Avg steps:  8.1 | Epsilon: 0.010

--- Evaluating Trained Agent (no exploration) ---
Episode 1: SUCCESS | Steps:  8 | Reward:   9.20 | Path: (0,0) → (1,0) → ...
```

The best-action grid will show arrows pointing toward the goal, avoiding holes.

---

## Key Things to Try

1. **Change α (learning rate):** Try 0.5 — does it converge faster but less stably?
2. **Change γ (discount):** Try 0.5 — does the agent become more short-sighted?
3. **Change ε decay:** Try 0.99 (slower decay) — does the agent explore longer?
4. **Add more holes:** Does the agent find alternative routes?
5. **Change grid size to 10×10:** Watch how many more episodes it needs.

---

## What This Demonstrates

- The Q-table starts empty (all zeros) — the agent knows nothing.
- Early episodes: random exploration, poor performance.
- Middle episodes: values propagate backward from the goal, performance improves.
- Late episodes: agent reliably finds near-optimal paths to the goal.
- This is exactly how DQN works, but with a neural network instead of the table.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Q-update derivation |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [Markov Decision Processes](../02_Markov_Decision_Processes/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Deep Q-Networks](../04_Deep_Q_Networks/Theory.md)
