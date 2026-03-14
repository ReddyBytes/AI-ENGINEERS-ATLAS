# Deep Q-Networks (DQN)

## The Story 📖

The Q-table works for a 5×5 gridworld with 25 states. But now your "maze" is a video game like Pong. The state is the pixels on screen — 84×84 grayscale values. The number of possible screen states is astronomically large; no table could store them all.

The key insight: you don't need to memorize every possible screen. Similar-looking screens should have similar Q-values. A neural network can learn that generalization — it looks at a new screen and recognizes "this is similar to situations where going right was good."

👉 This is **DQN (Deep Q-Network)** — Q-Learning where the Q-table is replaced by a neural network that generalizes across states.

---

## What is DQN?

**DQN** (DeepMind, 2013/2015) uses a **deep neural network** to approximate the Q-function instead of a lookup table.

The network takes a **state as input** and outputs **Q-values for all actions simultaneously**:
```
Input: state s (e.g., 84×84 pixel image)
Output: [Q(s, action_0), Q(s, action_1), ..., Q(s, action_N)]
```

One forward pass gives Q-values for every action — pick the highest.

Two innovations make DQN stable (plain deep learning + Q-Learning diverges without them):
1. **Experience Replay**
2. **Target Network**

---

## Why It Exists — The Problem It Solves

**Problem 1: Q-tables don't scale.**
Atari state space ≈ 10^18 possible screens. A neural network generalizes: "I've never seen this exact screen, but it's similar to one where going right was good."

**Problem 2: Naive deep Q-Learning is unstable.** Two instabilities arise:
- **Correlated samples** — consecutive game frames are nearly identical. Training on them sequentially causes the network to overfit and forget earlier lessons.
- **Moving targets** — the target `r + γ·max Q(s', ·)` depends on the same network being updated. Every update changes both estimate and target — chasing a moving goalpost.

Experience replay and the target network directly solve these two problems.

---

## How It Works — Step by Step

```mermaid
flowchart TD
    ENV[Environment\ngives state s_t]
    ENV --> NN[Online Network\nQ·s_t, a· for all a]
    NN --> ACT[Choose action\nepsilon-greedy]
    ACT --> STEP[Take action a_t\nget r_t and s_{t+1}]
    STEP --> REPLAY[Store s_t, a_t, r_t, s_{t+1}, done\nin Replay Buffer]
    REPLAY --> SAMPLE[Sample random minibatch\nfrom Replay Buffer]
    SAMPLE --> TARGET[Compute TD target using\nTarget Network:\ny = r + γ·max Q_target·s',·]
    TARGET --> LOSS[Compute loss:\nMSE between Q_online·s,a· and y]
    LOSS --> UPDATE[Backprop — update\nOnline Network weights]
    UPDATE --> COPY[Every C steps:\ncopy Online → Target Network]
    COPY --> ENV

    style ENV fill:#2c3e50,color:#fff
    style NN fill:#2980b9,color:#fff
    style REPLAY fill:#8e44ad,color:#fff
    style TARGET fill:#e67e22,color:#fff
    style LOSS fill:#e74c3c,color:#fff
    style UPDATE fill:#27ae60,color:#fff
    style COPY fill:#16a085,color:#fff
```

---

## Innovation 1: Experience Replay

Store all experiences `(s, a, r, s', done)` in a **replay buffer**. At each training step, sample a random minibatch.

Benefits:
- **Decorrelates samples** — random sampling breaks temporal correlation.
- **Data efficiency** — each experience can be reused multiple times.

```
Replay Buffer (circular queue, capacity 100,000):
┌──────────────────────────────────────────────────────────────┐
│ (s_0, a_0, r_0, s_1, False)                                  │
│ (s_1, a_1, r_1, s_2, False)                                  │
│ ...   (100,000 experiences)  ...                             │
│ (s_N, a_N, r_N, s_N+1, True)   ← oldest gets overwritten    │
└──────────────────────────────────────────────────────────────┘
              ↓ sample random 32 at each training step
```

---

## Innovation 2: Target Network

Maintain two networks with identical architecture:
- **Online network (θ)** — Updated at every step. Used to select actions.
- **Target network (θ⁻)** — Frozen copy. Used only to compute targets. Updated to match the online network every C steps (e.g., C = 1000).

```
TD target = r + γ · max_{a'} Q(s', a'; θ⁻)   ← uses TARGET network
Loss = MSE( Q(s, a; θ) - TD target )           ← trains ONLINE network
```

The target network stays frozen long enough to provide stable training targets.

---

## The Full DQN Algorithm

```
Initialize online network Q(s,a; θ) with random weights
Initialize target network Q(s,a; θ⁻) = Q(s,a; θ)
Initialize replay buffer D with capacity N

for each episode:
    s = env.reset()

    for each step t:
        # Epsilon-greedy action selection
        if random() < ε:
            a = random_action()
        else:
            a = argmax_a Q(s, a; θ)   # online network

        # Take action
        s', r, done = env.step(a)

        # Store experience
        D.append((s, a, r, s', done))

        # Sample random minibatch
        if len(D) >= batch_size:
            batch = D.sample(batch_size)
            for (s_b, a_b, r_b, s'_b, done_b) in batch:
                if done_b:
                    y = r_b
                else:
                    y = r_b + γ · max_{a'} Q(s'_b, a'; θ⁻)   # target network

            loss = MSE(Q(s_b, a_b; θ), y)
            backprop to update θ

        # Copy online to target every C steps
        if t % C == 0:
            θ⁻ ← θ

        s = s'
        if done: break
```

---

## The Math / Technical Side (Simplified)

DQN minimizes:
```
L(θ) = E[ ( r + γ · max_{a'} Q(s', a'; θ⁻) - Q(s, a; θ) )² ]
```

MSE between the online network's prediction `Q(s, a; θ)` and the target `r + γ · max Q(s', a'; θ⁻)`. Gradients flow through `Q(s, a; θ)` only — the target network parameters θ⁻ are treated as constants.

---

## Where You'll See This in Real AI Systems

- **Atari games** — The original DeepMind paper demonstrated superhuman performance on 49 games from raw pixels.
- **Robotics (discrete actions)** — DQN works well when the robot takes a finite set of actions.
- **Foundation for improvements** — Double DQN, Dueling DQN, Prioritized Experience Replay, Rainbow all build on DQN.

---

## Common Mistakes to Avoid ⚠️

**Not warming up the replay buffer.** Fill the buffer with random experiences before training; otherwise early batches contain only correlated initial experiences.

**Updating the target network too frequently.** Copying online → target every step eliminates the stability benefit. Update every 100–10,000 steps.

**Setting the replay buffer too small.** A buffer of 100 is useless. Use at least 10,000; DeepMind used 1,000,000 for Atari.

**Not normalizing observations.** Pixel values 0–255 must be scaled to 0–1 or [-1, 1] for stable training.

**Using DQN for continuous actions.** DQN outputs one Q-value per discrete action and cannot handle continuous action spaces. Use DDPG or SAC instead.

---

## Connection to Other Concepts 🔗

- **Q-Learning** — DQN is Q-Learning with a neural network instead of a table. Same update rule, same off-policy nature.
- **Policy Gradients / PPO** — The alternative family: directly optimize the policy instead of learning Q-values.
- **Double DQN** — Fixes DQN's overestimation bias by using the online network to select actions and the target network to evaluate them.
- **Dueling DQN** — Splits Q-function into V(s) + A(s,a) (advantage) for better learning.

---

✅ **What you just learned:**
- DQN replaces the Q-table with a neural network, enabling RL on large state spaces like video games.
- Experience replay decorrelates training samples by storing and randomly sampling past experiences.
- The target network stabilizes training by providing a fixed learning target for many steps.
- DQN = Q-Learning update + experience replay + target network.

🔨 **Build this now:**
Run the DQN code in `Code_Example.md` on CartPole. Watch episode reward improve. Then remove experience replay (train on each step directly) and observe the instability. Then re-add replay but remove the target network — notice how it diverges.

➡️ **Next step:** `../05_Policy_Gradients/Theory.md` — learn an entirely different approach: directly optimizing the policy without a Q-table or neural Q-function.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | DQN architecture diagrams |
| [📄 Code_Example.md](./Code_Example.md) | DQN on CartPole with PyTorch |

⬅️ **Prev:** [Q-Learning](../03_Q_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Policy Gradients](../05_Policy_Gradients/Theory.md)
