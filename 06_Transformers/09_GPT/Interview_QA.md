# GPT — Interview Q&A

## Beginner

**Q1. What is GPT and how does it generate text?**

GPT (Generative Pretrained Transformer) is a decoder-only transformer trained to predict the next token in a text sequence. It generates text autoregressively — one token at a time.

To generate a sentence from a prompt:
1. Feed the prompt tokens into the model
2. The model outputs a probability distribution over the vocabulary for the next token
3. Sample one token from this distribution
4. Append it to the sequence
5. Repeat from step 2 until you hit an end-of-sequence token or a length limit

Because each generation step uses the model's own previous output as context, mistakes can compound — but fluency is generally maintained because the model was trained on coherent human text.

---

**Q2. Why is GPT described as "autoregressive"?**

Autoregressive means each output element is conditioned on all previous outputs. GPT generates token t+1 from tokens 1 through t. Then generates t+2 from tokens 1 through t+1.

This is the same structure as classical autoregressive language models (n-grams, RNNs) — GPT just uses a much more powerful model.

The "auto" in autoregressive means "self" — the model feeds its own outputs back as inputs. This is different from models that generate outputs in one shot (like BERT's masked token prediction or an encoder that processes everything at once).

---

**Q3. What is the difference between zero-shot and few-shot learning in GPT?**

Both are forms of in-context learning — no gradient updates, no fine-tuning. Just a carefully constructed prompt.

**Zero-shot:** Give the model a description of the task and ask it to do it. No examples.
```
"Translate the following English text to French: 'Hello, how are you?'"
```

**Few-shot:** Give the model a few examples of the task, then a new instance.
```
"English: Hello → French: Bonjour
English: Thank you → French: Merci
English: Goodbye → French: "
```

Few-shot typically performs better because the examples help the model understand the exact format and nature of the task. Zero-shot is more convenient. Both work better as model size increases.

---

## Intermediate

**Q4. What is temperature in GPT generation and how does it affect output?**

When GPT predicts the next token, it produces logit scores for every token in the vocabulary. Softmax converts these to probabilities. Temperature T modifies this:

```
probability_i = exp(logit_i / T) / sum(exp(logit_j / T))
```

- **T = 0 (or near-zero):** The highest-probability token is always selected. Deterministic and repetitive.
- **T = 1.0:** Standard softmax. Samples proportional to model probabilities.
- **T > 1.0:** Flattens the distribution — more random tokens become likely. Creative but less coherent.
- **T < 1.0 (e.g., 0.3):** Sharpens the distribution — focuses on top tokens. More focused and predictable.

Use low temperature for factual, precise tasks. Use higher temperature for creative writing or when diversity is desired.

---

**Q5. How did GPT-3 achieve few-shot learning without any fine-tuning?**

GPT-3 (175B parameters, trained on ~300B tokens) demonstrates an emergent property: in-context learning. Given a few examples in the prompt, it generalizes the pattern to new inputs without any weight updates.

Why it works: during pretraining, GPT-3 saw countless examples of text where patterns appear in sequence — instructions followed by examples followed by answers, articles structured similarly to each other, code with comments before it. The model learned to continue these patterns.

When you give GPT-3 a few-shot prompt, it "pattern-matches" to the format it learned during pretraining and continues appropriately. Smaller models can't do this reliably because they haven't seen enough training data to internalize the necessary meta-learning capability.

---

**Q6. What is RLHF and why was it needed for GPT-3 to become InstructGPT?**

GPT-3 can generate text, but it wasn't reliably instruction-following. Asking "Explain black holes simply" might produce a Wikipedia-style essay, a rambling answer, or a continuation that ignores the instruction entirely.

RLHF (Reinforcement Learning from Human Feedback) fine-tunes GPT-3 to follow instructions:

1. **Supervised fine-tuning:** Show the model examples of good instruction-response pairs written by humans
2. **Reward model:** Train a separate model to predict human preference between two responses
3. **RL fine-tuning:** Use the reward model to fine-tune GPT via PPO (Proximal Policy Optimization) — optimize for responses the reward model rates highly

The result (InstructGPT) behaves like an assistant, not just a text completer. This is also the basis for ChatGPT, Claude, and all modern AI assistants.

---

## Advanced

**Q7. What is the KV cache and why is it critical for GPT inference efficiency?**

During autoregressive generation, GPT runs the full model for every new token. At each step, it computes K (key) and V (value) matrices for all past tokens in the sequence. This is wasteful — the K/V for previous tokens don't change.

The KV cache stores the K and V matrices from previous steps. When generating token t+1, you only compute K/V for the new token and retrieve all previous K/V from cache.

Impact:
- Without KV cache: generating 100 tokens requires 100 × N computations for the full sequence
- With KV cache: generating 100 tokens requires N computations for position 1, 2N for position 2... — linear total instead of quadratic

KV cache memory scales as: batch_size × num_layers × 2 × sequence_length × d_model. For GPT-3 generating 1000 tokens per request at batch size 1: ~600MB. High-throughput serving of large models requires careful memory management around KV caches.

---

**Q8. What is the difference between GPT-style pretraining and instruction fine-tuning?**

**Pretraining (causal LM):** Train on raw text to predict the next token. The model learns language, facts, and reasoning from patterns in trillions of tokens. The objective is purely predictive — "what word comes next in this text?"

**Instruction fine-tuning (SFT + RLHF):** Fine-tune the pretrained model on curated (prompt, response) pairs where responses represent desired assistant behavior. The model learns to follow instructions, be helpful, and refuse harmful requests.

The distinction matters:
- A pretrained GPT might complete "Tell me how to make a bomb" with actual instructions (it just continues text)
- An instruction-tuned model (ChatGPT, Claude) refuses harmful requests and provides helpful responses

Instruction fine-tuning doesn't erase pretraining knowledge — it changes the model's behavior pattern while keeping the factual and reasoning capabilities from pretraining intact.

---

**Q9. How do you prevent GPT from repeating itself, and what causes repetition?**

Repetition in GPT generation is caused by the model assigning high probability to already-generated tokens in certain contexts. Common causes:
- Temperature too low → model always picks highest-probability tokens, which tend to be the same
- No repetition penalty
- Short or generic prompts give insufficient context

Solutions:

1. **Repetition penalty:** Divide logits of recently generated tokens by a penalty factor (e.g., 1.3), reducing their probability. HuggingFace: `repetition_penalty=1.3`.

2. **Temperature tuning:** Increase temperature slightly (0.7–0.9) to increase diversity without losing coherence.

3. **Top-p or top-k sampling:** Prevents the model from always defaulting to the same small set of high-probability tokens.

4. **Better prompts:** More specific, detailed prompts give more context for the model to follow, reducing the tendency to fall into repetitive patterns.

5. **Frequency penalty (OpenAI API):** Penalizes tokens proportional to how many times they've appeared in the generation so far.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [08 BERT](../08_BERT/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 Vision Transformers](../10_Vision_Transformers/Theory.md)