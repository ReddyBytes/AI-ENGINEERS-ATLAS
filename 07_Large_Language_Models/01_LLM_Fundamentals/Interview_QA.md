# LLM Fundamentals — Interview Q&A

## Beginner

**Q1: What is a Large Language Model?**

<details>
<summary>💡 Show Answer</summary>

A Large Language Model is a neural network with billions of parameters trained on massive amounts of text data. The training objective is simple: predict the next token given all previous tokens. By doing this at enormous scale — hundreds of billions of parameters, trillions of training tokens — the model learns grammar, facts, reasoning patterns, coding style, and much more. The result is a model that can answer questions, write code, summarize documents, and hold conversations, all from that single training objective.

</details>

---

<br>

**Q2: What is a token, and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

A token is the basic unit of text that an LLM processes. It is not the same as a word. Most tokenizers split text into sub-word units: common words are single tokens ("the", "is"), rare words split into multiple tokens ("tokenization" might be "token" + "ization"), and numbers and punctuation have their own tokens.

A rough rule of thumb: 1 token ≈ 0.75 words. So 100 words ≈ 133 tokens.

Tokens matter because:
- The context window (what the model can "see" at once) is measured in tokens
- API costs are billed per token
- Model speed depends on how many tokens are processed

</details>

---

<br>

**Q3: What is the difference between a base model and a chat model?**

<details>
<summary>💡 Show Answer</summary>

A base model is trained only on next-token prediction across raw internet text. It doesn't know how to answer questions or follow instructions — it just continues whatever text you give it. If you type "The capital of France is", it completes the sentence. But it might not answer "What is the capital of France?" helpfully.

A chat model is a base model that has been further trained through instruction tuning and RLHF (Reinforcement Learning from Human Feedback). This teaches it to follow instructions, answer questions directly, decline harmful requests, and have a conversational style. ChatGPT, Claude, and Gemini are all chat models.

</details>

---

## Intermediate

**Q4: What are emergent capabilities in LLMs? Give an example.**

<details>
<summary>💡 Show Answer</summary>

Emergent capabilities are abilities that appear in large models but are absent or weak in smaller models — even though nobody specifically programmed them. They "emerge" from scale.

The most famous example is few-shot learning. GPT-2 (1.5B parameters) could not reliably do a task after seeing a few examples in the prompt. GPT-3 (175B parameters) could, without any fine-tuning. This ability wasn't trained in explicitly. It emerged from scale.

Other examples:
- **Chain-of-thought reasoning**: asking a large model to "think step by step" dramatically improves accuracy on math problems. This barely works on small models.
- **Code generation**: small models produce broken code. Large models produce working, complex programs.
- **Multilingual transfer**: train mainly on English, and a large model becomes surprisingly good at other languages it saw little of.

Emergence is one reason why scaling LLMs has been so surprising — you can't always predict what new abilities will appear.

</details>

---

<br>

**Q5: Why do LLMs need so much data and compute? What would happen with less?**

<details>
<summary>💡 Show Answer</summary>

LLMs learn by pattern-matching over text. The more patterns they see, the better their internal representations of language, facts, and reasoning. With less data:
- The model overfits — it memorizes training examples rather than learning generalizable patterns
- It has gaps — topics not in the training data are unknown to it
- Reasoning is weaker — multi-step inference requires having seen many varied reasoning examples

Compute is needed because training adjusts billions of parameters using backpropagation. Each pass through the data requires computing gradients across all parameters, which involves enormous matrix multiplications. Training GPT-3 reportedly cost ~$4.6M in compute. GPT-4 training was estimated at $50–100M+.

Less compute = fewer steps through the data = less learned. Scaling compute is one of the most reliable ways to improve model quality, which is why the industry has invested billions in GPU clusters.

</details>

---

<br>

**Q6: How do open-weight models like Llama differ from closed API models like GPT-4?**

<details>
<summary>💡 Show Answer</summary>

| Dimension | Open-weight (Llama) | Closed API (GPT-4) |
|-----------|--------------------|--------------------|
| Access | Download weights, run yourself | Call via REST API |
| Cost | Hardware cost only | Per-token pricing |
| Privacy | Data stays on your hardware | Data sent to provider |
| Customization | Can fine-tune freely | Limited fine-tuning options |
| Maintenance | You manage deployment | Provider handles it |
| Quality ceiling | Usually below frontier | Access to best models |

Open-weight models are ideal when: privacy matters, costs at scale are high, or you need fine-tuning control. Closed APIs are ideal when: you want frontier quality without infrastructure, or you're prototyping quickly.

</details>

---

## Advanced

**Q7: Explain the scaling laws for LLMs. What do they predict?**

<details>
<summary>💡 Show Answer</summary>

Scaling laws (Kaplan et al. 2020, Hoffman et al. 2022 "Chinchilla") describe mathematical relationships between model performance, model size, dataset size, and compute budget.

Key findings:
- Model loss follows a power law as you scale any of these three dimensions
- **Kaplan scaling laws** suggested that given a compute budget, you should prioritize model size (bigger model, fewer tokens)
- **Chinchilla scaling laws** (2022) corrected this: optimal training uses roughly 20 tokens per parameter. So a 70B parameter model should be trained on ~1.4T tokens. Many models prior to Chinchilla were "undertrained"

Practical implication: Llama 2's 70B model trained on 2T tokens significantly outperformed GPT-3's 175B model trained on only 300B tokens, despite having fewer parameters. Token-efficient training beat raw parameter count.

The frontier has since shifted further — Llama 3's 8B model trained on 15T tokens outperforms models many times its size trained on less data.

</details>

---

<br>

**Q8: What is the "bitter lesson" and how does it apply to LLMs?**

<details>
<summary>💡 Show Answer</summary>

The "bitter lesson" (Rich Sutton, 2019) is the observation that in AI, methods that leverage computation and scale consistently beat methods that encode human knowledge. Every time researchers built clever, domain-specific AI, it eventually got beaten by a simpler method run at larger scale.

For LLMs, this manifests clearly: researchers tried for decades to build language understanding through hand-crafted parsers, knowledge graphs, and linguistic rules. GPT-3 — a simple transformer trained at scale — surpassed all of them on almost every NLP benchmark.

The lesson for practitioners: when in doubt, scale. Cleverness in architecture matters less than raw scale. This is why the industry's response to every capability gap is often "train a bigger model on more data."

That said, the bitter lesson has limits: alignment, safety, and factuality don't automatically improve with scale. Those require targeted techniques beyond just scaling.

</details>

---

<br>

**Q9: What are the key differences between GPT-4, Claude 3, and Gemini architecturally and in terms of design philosophy?**

<details>
<summary>💡 Show Answer</summary>

All three are transformer-based LLMs with instruction tuning and RLHF/RLAIF. The differences are in design philosophy, safety approach, and capabilities:

**GPT-4 (OpenAI)**
- Architecture: likely Mixture of Experts (MoE), allowing a large total parameter count with only a subset active per inference
- Multimodal from the ground up (text + images)
- Optimized for broad capability benchmark performance
- Safety approach: RLHF with human raters; moderation via content filters

**Claude 3 (Anthropic)**
- Architecture not disclosed, but known for exceptionally long context (up to 200k tokens in Claude 3)
- Safety approach: Constitutional AI (CAI) — model is trained using AI feedback against a written "constitution" of principles, reducing reliance on human raters for every example
- Design philosophy: "Helpful, Harmless, Honest" as core objectives
- Tends to be more verbose and detailed in explanations

**Gemini Ultra (Google)**
- Built natively multimodal — unlike GPT-4 which integrated vision later, Gemini was trained on text, images, video, and audio together from the start
- Deep integration with Google's infrastructure and products (Search, Workspace)
- Safety approach: responsible scaling policy with staged deployment
- Strong on multilingual tasks given Google's global data assets

The fundamental architecture (transformer + attention) is the same. The differences are in training data curation, safety methodology, context length engineering, and multimodal integration strategy.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Timeline.md](./Timeline.md) | Historical timeline of LLMs |

⬅️ **Prev:** [10 Vision Transformers](../../06_Transformers/10_Vision_Transformers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 How LLMs Generate Text](../02_How_LLMs_Generate_Text/Theory.md)
