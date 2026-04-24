# RL for LLMs — Interview Q&A

## Beginner Level

**Q1: What is RLHF in plain English?**

<details>
<summary>💡 Show Answer</summary>

A: RLHF stands for Reinforcement Learning from Human Feedback. It's a training technique that takes a language model that can generate text and makes it more helpful and aligned with human preferences, using human feedback as the reward signal.

Instead of telling the model "here is the correct response" (supervised learning), we ask humans "which of these two responses is better?" and train a reward model to predict that preference. Then we use RL (specifically PPO) to optimize the language model to generate responses that score highly on the reward model.

The result: a model that generates text that humans prefer, rather than text that merely predicts the next word statistically.

</details>

---

<br>

**Q2: What are the three stages of RLHF?**

<details>
<summary>💡 Show Answer</summary>

A:
1. **Supervised Fine-Tuning (SFT):** Take the pretrained LLM and fine-tune it on human-written demonstrations of high-quality responses. This gets the model into the right behavioral space before RL.

2. **Reward Model Training:** Generate multiple responses per prompt using the SFT model. Have human labelers rank them. Train a neural network (the reward model) to predict these human rankings. Now you have a function that scores any response.

3. **RL Fine-Tuning:** Use PPO to optimize the SFT model to generate responses that score highly on the reward model, while staying close to the SFT model (via a KL penalty to prevent reward hacking).

</details>

---

<br>

**Q3: Why can't you just train a language model with supervised learning on human-written responses?**

<details>
<summary>💡 Show Answer</summary>

A: You can, and that's Stage 1 (SFT). But SFT alone has limits:

1. You can only cover prompts you have human-written responses for — you can't write demonstrations for every possible question.
2. Humans are better at judging responses than writing optimal ones. It's easier to say "response A is better than B" than to write the perfect response.
3. SFT doesn't have a mechanism for the model to learn "how good" various responses are — every demonstration is treated equally.

RLHF captures preference information that SFT can't — the relative quality of responses, not just examples of good ones.

</details>

---

## Intermediate Level

**Q4: What is a reward model and how is it trained?**

<details>
<summary>💡 Show Answer</summary>

A: A reward model is a neural network that takes a (prompt, response) pair as input and outputs a scalar score predicting how much humans would prefer that response.

It's typically built by: (1) taking the SFT model and adding a linear projection head on top of the final hidden state, (2) training it on a dataset of human preference comparisons using the Bradley-Terry model loss:
```
L = -E[ log σ( r(x, y_preferred) - r(x, y_dispreferred) ) ]
```

This loss trains the model to assign higher scores to preferred responses and lower scores to dispreferred ones. After training, the reward model acts as a stand-in for human judgment during RL.

</details>

---

<br>

**Q5: What is the KL penalty in RLHF and why is it essential?**

<details>
<summary>💡 Show Answer</summary>

A: During PPO fine-tuning, the RLHF objective is:
```
Reward = RM(prompt, response) - β · KL(π_RLHF || π_SFT)
```

The KL penalty measures how different the RLHF policy is from the SFT model and subtracts it from the reward. It's essential because:

Without it: the LLM quickly learns to generate text that "looks good" to the reward model but is meaningless or repetitive — reward hacking. Within 100 PPO steps, the model can drift far from the SFT baseline and collapse to degenerate outputs.

With it: the policy is forced to stay "proximal" to the SFT model. This is exactly PPO's proximal constraint applied at the model level. The model improves gradually without catastrophically forgetting its base capabilities.

</details>

---

<br>

**Q6: What is DPO and how does it differ from RLHF?**

<details>
<summary>💡 Show Answer</summary>

A: DPO (Direct Preference Optimization) achieves similar results to RLHF without the RL loop. It uses a mathematical insight: the optimal policy for the RLHF objective has a closed-form expression in terms of the SFT model and the rewards. This means you can bypass training a reward model and running PPO — instead, you directly optimize a supervised loss on preference data:

```
L_DPO = -E[ log σ( β · log(π_new(y_w|x)/π_SFT(y_w|x))
                 - β · log(π_new(y_l|x)/π_SFT(y_l|x)) ) ]
```

DPO is simpler (no RL), more stable (supervised loss), and achieves comparable performance on most tasks. The trade-off: RLHF with PPO is more flexible — it can work with online feedback (real-time human ratings during training) and is more amenable to iterative improvement. DPO only works with offline preference datasets.

</details>

---

## Advanced Level

**Q7: What is reward hacking in RLHF, and how does Goodhart's Law apply?**

<details>
<summary>💡 Show Answer</summary>

A: Goodhart's Law: "When a measure becomes a target, it ceases to be a good measure." In RLHF, the reward model is a proxy measure for human preferences. When we optimize the LLM against it with PPO, the LLM finds responses that score high on the reward model but don't actually satisfy human intent.

Examples: generating unusually long responses (if length correlates with high ratings in training data), excessive hedging ("That's a great question!"), repetitive patterns that correlate with positive training examples.

The severity depends on the optimization budget — more PPO steps = more reward hacking. The KL penalty limits this by constraining how far the policy can drift. The practical solution is to continuously run human evaluations alongside reward model scores and stop training when the two diverge.

</details>

---

<br>

**Q8: What are the RL components in an RLHF training step at the token level?**

<details>
<summary>💡 Show Answer</summary>

A: At the token level, RLHF casts language generation as an MDP:

- **State at time t:** the prompt + all tokens generated so far (the context window)
- **Action at time t:** the next token chosen from the vocabulary
- **Reward:** 0 for all intermediate tokens; the reward model score (minus KL penalty) only at the end-of-sequence token
- **Episode:** one complete response generation (from first token to EOS)

This is an extremely long-horizon RL problem with sparse rewards (only one non-zero reward per episode, at the very end). The KL penalty adds a per-token reward component: at each step, the policy is penalized by log(π_new(a_t|s_t) / π_ref(a_t|s_t)).

The per-token KL contribution converts the purely sparse reward into something slightly denser, which helps gradient flow.

</details>

---

<br>

**Q9: What is Constitutional AI and how does it extend RLHF?**

<details>
<summary>💡 Show Answer</summary>

A: Constitutional AI (Anthropic, 2022) is an extension of RLHF that reduces reliance on human labelers by using an AI to generate feedback.

The process:
1. Generate a response to a harmful prompt.
2. Use a separate AI (a "critic") to evaluate the response against a set of principles (the "constitution") and suggest revisions.
3. Have the model revise its response according to the critique.
4. Use the (original, revised) pairs to train a preference model — without any human labeling.

This enables RLAIF (RL from AI Feedback) at scale: the AI can evaluate millions of its own outputs according to the constitution, without requiring that many humans. The limitation is that the AI critique is only as good as the AI judge — bias in the judge propagates to the trained model.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full theory |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Connection_to_RLHF.md](./Connection_to_RLHF.md) | How PPO applies to LLMs |

⬅️ **Prev:** [RL in Practice](../07_RL_in_Practice/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** Section complete!
