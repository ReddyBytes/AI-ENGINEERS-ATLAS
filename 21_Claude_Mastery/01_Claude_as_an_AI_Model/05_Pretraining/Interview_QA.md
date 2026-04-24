# Pretraining — Interview Q&A

## Beginner

**Q1: What is pretraining and how does it give Claude its knowledge?**

<details>
<summary>💡 Show Answer</summary>

Pretraining is the first phase of training a large language model. The model is trained on an enormous corpus of text (trillions of tokens from web pages, books, code, academic papers, etc.) using a single objective: predict what token comes next in a sequence.

This is self-supervised learning — no human labels are needed. The "label" for each training example is simply the next token in the text.

Through this process, the model compresses the statistical patterns of the entire corpus into its billions of parameters. By getting good at predicting the next token across every domain, it effectively learns:
- How language and grammar work
- What facts about the world are commonly stated
- How mathematical reasoning is structured
- How code relates to its behavior
- What metaphors, analogies, and arguments look like

When you ask Claude about medieval history or quantum mechanics, it's drawing on patterns encoded during pretraining — not looking anything up.

</details>

---

<br>

**Q2: What is the Chinchilla scaling law and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

The Chinchilla scaling law (Hoffmann et al., 2022) describes the optimal ratio of training data to model parameters for a given compute budget.

The key finding: previous models (including GPT-3) were dramatically undertrained — they used too many parameters relative to the amount of data they were trained on. The optimal ratio is approximately:

```
optimal training tokens = 20 × model parameters
```

So a 70B parameter model should train on ~1.4 trillion tokens to be compute-optimal.

Why it matters practically:
- A "smaller" model trained on more data often outperforms a "larger" model trained on less data
- This insight drove the development of efficient models like Llama 2 (70B trained on 2T tokens)
- It means throwing more GPUs at a fixed dataset isn't efficient — you need proportionally more data too

</details>

---

<br>

**Q3: What is a knowledge cutoff and how should engineers work around it?**

<details>
<summary>💡 Show Answer</summary>

A knowledge cutoff is the date after which the model has no training data. Events, discoveries, or changes that happened after this date are unknown to the model.

For Claude, the cutoff is typically 6–12 months before the model's public release.

Engineering workarounds:
1. **RAG (Retrieval-Augmented Generation)**: Store current information in a vector database; retrieve relevant chunks per query and inject into context
2. **Tool calling**: Give Claude a web search tool to retrieve live information
3. **Explicit user-provided context**: Paste current information directly into the prompt
4. **Prompt for uncertainty**: Ask Claude to flag when it's uncertain due to potential staleness
5. **Date injection**: Tell Claude the current date in the system prompt so it knows how stale its knowledge might be

Never rely on Claude's parametric knowledge for time-sensitive data — prices, recent events, new software versions, recent research.

</details>

---

## Intermediate

**Q4: What is teacher forcing and what problem does it create?**

<details>
<summary>💡 Show Answer</summary>

Teacher forcing is the training technique where, during pretraining, the model always sees the true previous tokens (from the training data) as context when predicting the next token — never its own previous predictions.

This is efficient: you can compute the loss for every token in a sequence in a single forward pass, and gradients propagate cleanly.

The problem it creates is called **exposure bias**: the model is trained on clean, correct input sequences, but at inference time it must condition on its own (potentially incorrect) outputs. A single early mistake at token 50 means tokens 51+ are conditioned on a sequence the model was never trained on.

This partially explains why LLMs can fall into repetitive loops or nonsensical continuations — once they diverge from a familiar pattern, they're in uncharted territory.

Mitigations: RLHF (trains on full rollouts), chain-of-thought (makes intermediate steps explicit and checkable), self-consistency (multiple samples reduce error correlation).

</details>

---

<br>

**Q5: What is the role of data curation in pretraining quality?**

<details>
<summary>💡 Show Answer</summary>

Data curation is arguably as important as model architecture and scale. A clean, well-curated dataset of 1 trillion tokens typically outperforms a raw, noisy crawl of 10 trillion tokens.

Key curation steps:
1. **Deduplication**: Near-duplicate documents cause memorization rather than generalization. Tools like MinHash find and remove near-duplicates.
2. **Quality filtering**: Heuristics (perplexity scoring against a reference model, word frequency checks, repetition ratios) remove spam, generated content, and low-quality text.
3. **Harmful content filtering**: Remove clear harmful categories based on keyword lists and trained classifiers.
4. **Language identification**: Keep desired languages; filter out incorrectly labeled content.
5. **Data mixing**: The ratio of code to natural language to scientific text to books significantly affects downstream capabilities. Getting this ratio wrong degrades specific skills.

The exact curation pipeline is among the most closely guarded intellectual property at AI labs — the public model weights are the output; the data pipeline is the competitive moat.

</details>

---

<br>

**Q6: What are emergent capabilities and why are they surprising?**

<details>
<summary>💡 Show Answer</summary>

Emergent capabilities are abilities that appear suddenly in language models at certain scales, rather than improving gradually. On a graph of model performance vs. scale, emergent capabilities look like a step function rather than a smooth curve.

Examples: A model at 10B parameters might score near-random (25-30%) on multi-step arithmetic. A model at 100B parameters might score 70-80%. The jump happens relatively abruptly.

Why it's surprising: you'd expect performance to improve smoothly as you add parameters. The discontinuous nature suggests these tasks require multiple simpler sub-capabilities, each of which improves gradually — but the task only "works" when all required sub-capabilities cross their individual thresholds simultaneously.

Why it matters to engineers: you can't always predict what a larger model will be able to do just by testing a smaller one. Capabilities can appear that weren't present at any smaller scale — making frontier model releases genuinely surprising even to their creators.

</details>

---

## Advanced

**Q7: How does compute-optimal training change the economics of model development?**

<details>
<summary>💡 Show Answer</summary>

Pre-Chinchilla, the assumption was: bigger model = better model. Labs competed on parameter count (GPT-3 at 175B was a landmark).

Post-Chinchilla: for any fixed compute budget C, the optimal allocation is to train a model of size N on D tokens where both N and D scale as C^0.5. This has economic implications:

1. **Smaller models trained longer outperform larger models trained shorter**: Llama-2-70B (70B params, 2T tokens) often outperforms earlier 200B models trained on 300B tokens
2. **Inference cost matters**: A compute-optimally trained smaller model costs less to serve at inference — costs that multiply with every query in production
3. **Overfitting on compute-optimal curves**: The Chinchilla paper optimized for a single training run. Meta's Llama 3 trained a 8B model on 15T tokens — far beyond compute-optimal — because cheap inference costs outweigh expensive training for a widely deployed model
4. **Multi-epoch training**: Training on the same data multiple times can be viable for smaller datasets but degrades performance — most frontier labs assume single-epoch training on their data

The insight for engineers: don't just compare model sizes — compare model size and training token count together. A 7B model trained on 2T tokens may outperform a 70B model trained on 100B tokens on many benchmarks.

</details>

---

<br>

**Q8: What is the relationship between pretraining data diversity and model capabilities?**

<details>
<summary>💡 Show Answer</summary>

The diversity of the pretraining corpus directly determines which domains the model excels in:

1. **Code capability**: Models with high proportions of code data (GitHub, StackOverflow) are dramatically better at programming tasks. Adding 15% code to training can 3-5x code benchmark scores without hurting language performance significantly.

2. **Mathematical reasoning**: Models trained on mathematical papers, textbooks, and worked solutions show much stronger math performance. Chain-of-thought ability is amplified by exposure to step-by-step problem solving in training data.

3. **Multilingual capability**: A model's performance in language X is approximately proportional to the square root of the fraction of language X in training data. 1% Spanish training data gives ~10x better Spanish performance than 0.01%.

4. **Instruction following**: Documents that demonstrate instructional formats (how-to guides, tutorials, Q&A forums) help the model naturally adopt helpful conversational patterns, reducing the work required by SFT.

5. **Long-form coherence**: Training on well-structured long documents (books, papers) versus short social media posts affects the model's ability to maintain coherent long-form outputs.

Anthropic's data mixture for Claude is proprietary, but the general principle is that high-quality, diverse data across all the target capability domains is worth more than raw scale.

</details>

---

<br>

**Q9: How does pretraining relate to in-context learning (ICL)?**

<details>
<summary>💡 Show Answer</summary>

In-context learning (ICL) is the ability to learn a new task from examples provided in the prompt, without any weight updates. This is an emergent capability that only appears robustly at certain scales.

Connection to pretraining:

The transformer attention mechanism, trained on diverse data, learns to distinguish patterns in the context. When you provide few-shot examples in the prompt, the model recognizes the input-output pattern and generalizes it.

Research hypothesis: during pretraining, the model sees many documents of the form "here are examples, here is a new case, here is the answer." Learning to continue these documents is functionally the same as in-context learning.

Why scale matters: at small scale, the model doesn't have enough capacity to represent diverse pattern types. At large scale, the model can represent many patterns simultaneously and generalize to patterns seen at most once during pretraining.

Practical implication: few-shot prompting with carefully chosen examples is a powerful way to steer Claude's behavior without any fine-tuning. The model was trained on enough diverse demonstrations that it can learn a new format or domain from 3-5 examples.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [04 Transformer Architecture](../04_Transformer_Architecture/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 RLHF](../06_RLHF/Theory.md)
