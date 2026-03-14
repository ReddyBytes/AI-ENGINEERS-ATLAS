# RL Fundamentals — Interview Q&A

## Beginner Level

**Q1: What is reinforcement learning in plain English?**

A: Reinforcement learning is a way for a computer program (called an agent) to learn by trying things in an environment and getting feedback on how well it did. When the agent does something good, it gets a reward. When it does something bad, it gets a penalty (or no reward). Over many trials, the agent learns which actions tend to lead to more reward. Think of training a dog with treats — no one writes down the rules, the dog figures them out from feedback.

---

**Q2: What are the main components of an RL system?**

A: The five core components are:
- **Agent** — the learner/decision-maker
- **Environment** — everything the agent interacts with
- **State** — the current situation (what the agent observes)
- **Action** — what the agent can do
- **Reward** — the feedback signal (a number) the environment gives after each action

Two additional components round out the framework:
- **Policy** — the agent's strategy for choosing actions
- **Value function** — the agent's estimate of how good a state (or action in a state) is for long-term reward

---

**Q3: What is the difference between reward and return?**

A: **Reward** is what the agent gets right now — a single number for the most recent action. **Return** is the sum of all future rewards, usually discounted: G_t = r_t + γ·r_{t+1} + γ²·r_{t+2} + … The agent's goal is to maximize return, not just the immediate reward. This distinction matters enormously — an agent optimizing only immediate reward might sacrifice a great long-term outcome for a small short-term gain.

---

**Q4: What is a policy?**

A: A policy is the agent's strategy — a mapping from states to actions (or to probability distributions over actions). A **deterministic policy** always picks the same action in a given state: π(s) = a. A **stochastic policy** outputs probabilities: π(a|s) = probability of taking action a in state s. The whole point of RL training is to find a policy that produces high cumulative reward.

---

## Intermediate Level

**Q5: How does RL differ from supervised learning?**

A: Three key differences:

1. **Data source** — Supervised learning uses a pre-collected labeled dataset. RL generates its own data by interacting with an environment.
2. **Feedback** — Supervised learning gets a correct label per sample. RL gets a scalar reward that may be delayed and sparse (e.g., only at the end of a game).
3. **Sequential decisions** — In supervised learning, samples are independent. In RL, actions affect the future state, creating dependencies across time.

The deeper difference: in supervised learning the teacher knows the right answer. In RL the teacher only says "you did well" or "you did poorly" — the agent must figure out *what* to do differently.

---

**Q6: What is the discount factor and why is it needed?**

A: The discount factor γ (between 0 and 1) down-weights future rewards. G_t = r_t + γ·r_{t+1} + γ²·r_{t+2} + …

It serves two purposes:
1. **Mathematical convergence** — Without discounting, the sum of rewards in an infinite-horizon task could grow without bound. Discounting ensures the sum stays finite.
2. **Preference modeling** — A lower γ makes the agent prefer immediate rewards over distant ones (like how people prefer money now over money later). γ = 0.99 is common for tasks where long-term planning matters.

---

**Q7: What is the exploration vs exploitation trade-off?**

A: Exploration means trying actions you haven't tried (or haven't tried enough) to gather information. Exploitation means using what you already know to get the best reward. The trade-off: exploit too much and you might miss better options; explore too much and you waste time on actions you know are bad. The **epsilon-greedy** strategy handles this by choosing a random action with probability ε and the best-known action otherwise. Over training, ε is typically annealed (reduced) from high to low.

---

**Q8: What is the difference between model-based and model-free RL?**

A: **Model-free RL** learns directly from raw experience — it doesn't build a representation of how the environment works. It's simpler to implement and works well when you have lots of interaction budget. Q-Learning and PPO are model-free.

**Model-based RL** learns a model of the environment (predicting what state you'll land in and what reward you'll get for each action), then uses that model to plan. It's more sample-efficient (you can simulate experience with the model) but harder to get right — a bad model can mislead the agent badly.

---

## Advanced Level

**Q9: What is the credit assignment problem in RL?**

A: The credit assignment problem is the challenge of figuring out which past actions were responsible for a reward received now. If you win a chess game on move 60, which of your previous 59 moves contributed to the win? The reward signal doesn't come labeled with "move 23 was particularly good." The agent must attribute credit backward through time. This is why RL is fundamentally harder than supervised learning. Techniques like **temporal difference (TD) learning**, **eligibility traces**, and **advantage estimation** all exist to solve credit assignment more efficiently.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Intuition_First.md](./Intuition_First.md) | 5 everyday RL examples |

⬅️ **Prev:** Section intro &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Markov Decision Processes](../02_Markov_Decision_Processes/Theory.md)
