# Instruction Tuning — Interview Q&A

## Beginner

**Q1: Why can't you just use a pretrained base model directly as a chatbot?**

<details>
<summary>💡 Show Answer</summary>

A pretrained base model is trained on one thing: given all previous text, predict the next token. It doesn't know what a "question" is in the conversational sense. It doesn't know it's supposed to be a helpful assistant.

If you ask a base model "What is DNA?", it might:
- Write more question text: "What is DNA? What is RNA? What is the central dogma of..."
- Give you a Wikipedia-style paragraph that starts with "DNA, or deoxyribonucleic acid, is..."
- Produce a fragment that sounds like it's mid-article

The model treats your input as text to continue — not as a request to fulfill. It has no concept of "I should answer this helpfully."

Instruction tuning teaches the model that: when a user gives an instruction or asks a question, the right response is a direct, helpful answer that addresses the request. This reorientation from "text completer" to "instruction follower" is what makes the model usable as an assistant.

</details>

---

**Q2: What is instruction tuning? How does it differ from standard fine-tuning?**

<details>
<summary>💡 Show Answer</summary>

Instruction tuning is a specific type of fine-tuning where the dataset consists of (instruction, response) pairs specifically designed to teach the model to follow user commands.

Standard fine-tuning: train on domain-specific (input, output) pairs. The goal is to improve performance on a specific task (e.g., medical Q&A, code generation in a specific language).

Instruction tuning: train on a diverse set of tasks all expressed as instructions. The goal is to teach the model general instruction-following behavior — so it can generalize to instructions it hasn't seen.

Key difference: **generalization across tasks**. A model domain fine-tuned on medical Q&A is better at medical Q&A. A model instruction-tuned on 60 diverse tasks can generalize to task types it never saw in training. FLAN demonstrated this: train on 60 tasks, test on held-out tasks the model never saw — performance improved significantly. Standard fine-tuning on 60 examples of one task doesn't generalize this way.

</details>

---

**Q3: What is the FLAN paper and why was it important?**

<details>
<summary>💡 Show Answer</summary>

FLAN (Fine-tuned Language Models Are Zero-Shot Learners, Google 2021) was one of the first systematic demonstrations of instruction tuning.

The researchers took a large language model and fine-tuned it on over 60 different NLP tasks, but expressed each task as a natural language instruction. For example, instead of training a separate summarization head, they trained on examples like: "Summarize the following article in one paragraph: [article]. [summary]."

The key finding: when you train on many diverse tasks described as instructions, the model learns to follow instructions in general — not just the specific tasks it was trained on. When tested on held-out tasks the model had never seen, the instruction-tuned model dramatically outperformed both the base model and standard fine-tuned models.

Why it matters:
1. It showed that instruction diversity unlocks zero-shot generalization
2. It demonstrated that natural language task specification is powerful
3. It directly led to InstructGPT, ChatGPT, and the modern instruction-tuning paradigm
4. It showed you don't need task-specific model architectures — a general model with good instruction tuning handles all tasks

</details>

---

## Intermediate

**Q4: What is the self-instruct method? What are its advantages and limitations?**

<details>
<summary>💡 Show Answer</summary>

Self-instruct (Wang et al., 2022) is a method for automatically generating instruction tuning datasets using an existing language model, rather than using expensive human annotation.

**Process:**
1. Start with a seed set of 100–200 human-written (instruction, input, output) examples
2. Prompt a large model (e.g., GPT-4) with a few seed examples and ask it to generate new instruction-response pairs
3. Filter the generated data for quality (remove duplicates, low-quality outputs, offensive content)
4. Repeat until you have enough data
5. Fine-tune a smaller model on the collected data

**Advantages:**
- Dramatically cheaper than human annotation ($500–$5k for 50k examples vs. potentially $500k+ for human labels)
- Can scale easily — just prompt more
- Can be targeted to specific domains or styles easily
- Enabled accessible open-source fine-tuning (Stanford Alpaca used this)

**Limitations:**
- Quality ceiling: the training data is only as good as the model generating it. If GPT-4 generates training data, the fine-tuned small model can approach but not exceed GPT-4 quality.
- Bias propagation: biases in the generator model are passed to the training data and amplified in the fine-tuned model
- Diversity is constrained by the generator's tendencies — it may generate data from the same distribution it's already familiar with, missing important edge cases
- Cannot teach the model things the generator doesn't know
- Requires API access to a capable model — not free at scale

Self-instruct is best for rapid prototyping and resource-constrained settings. Production-quality models (GPT-4, Claude) use human-curated instruction datasets for the most critical training examples.

</details>

---

**Q5: What is the difference between instruction tuning and RLHF? Why is both needed?**

<details>
<summary>💡 Show Answer</summary>

They solve different problems:

**Instruction tuning** (SFT):
- Teaches the model to follow instructions and be helpful
- Training signal: "for this instruction, this is a good response"
- Works from examples: model learns to match the format and approach of example responses
- Limitation: the quality ceiling is your training data. If training data has mediocre examples, the model learns to produce mediocre outputs. It optimizes for producing text that looks like your training data, not text that humans actually prefer.

**RLHF** (Reinforcement Learning from Human Feedback):
- Teaches the model to produce outputs that humans actually prefer
- Training signal: comparisons between responses ("Response A is better than B")
- Works from preferences: model learns what makes humans prefer one response over another
- Advantage: captures hard-to-specify qualities — "this is the right fact but the phrasing is condescending" is hard to put in an SFT example but easy to express in a preference rating

**Why both are needed:**
InstructGPT showed that a model instruction-tuned with SFT was much better than a base model, but still made errors that were easy for humans to identify. Adding RLHF on top of the SFT model significantly improved helpfulness and reduced harmful outputs.

SFT teaches the model how to respond. RLHF teaches the model what humans actually prefer about responses. The two are complementary: SFT provides the behavioral foundation, RLHF refines toward human values.

</details>

---

**Q6: How do you create a high-quality instruction dataset? What makes the difference between good and bad training data?**

<details>
<summary>💡 Show Answer</summary>

Dataset quality is the single biggest lever in instruction tuning quality. Here's what matters:

**1. Diversity of instructions**
The dataset should cover many types of instructions: factual Q&A, creative writing, code generation, summarization, translation, math, reasoning, classification, format conversion. A model trained only on Q&A will struggle with "write a poem about X."

**2. Complexity distribution**
Include simple, medium, and hard tasks. A dataset of only simple instructions produces a model that fails on complex tasks. Including some step-by-step reasoning examples (chain-of-thought) dramatically improves reasoning ability.

**3. Response quality**
Bad response examples teach the model to give bad responses. Each training example should show the ideal response — direct, accurate, appropriately formatted, complete. One poor example has outsized negative impact because the model may overfit to it.

**4. Deduplication**
Near-duplicate instructions bias the model toward those patterns. Aggressive deduplication improves generalization.

**5. Appropriate length distribution**
If all training responses are short, the model learns to give short responses. Vary length to match task requirements.

**6. Coverage of edge cases**
Include examples of how to handle: questions the model shouldn't answer, unclear instructions, ambiguous cases. Without these, the model improvises — often badly.

**Practical quality checklist:**
- Would a human expert approve of this response?
- Is the instruction clear and unambiguous?
- Does the response fully address the instruction?
- Is the format appropriate for the task?
- Are there any factual errors in the response?
- Would you be comfortable showing this to a user?

</details>

---

## Advanced

**Q7: What is task contamination in instruction tuning? How do you detect it?**

<details>
<summary>💡 Show Answer</summary>

Task contamination is when examples from benchmark test sets appear in the instruction tuning training data. This inflates benchmark scores — the model appears to generalize, but it has actually memorized the test examples.

**Example**: If Alpaca's 52k examples include questions similar to GSM8k math problems (used as a benchmark), a model fine-tuned on Alpaca will score higher on GSM8k not because it's better at math reasoning, but because it has seen similar problems.

**Why it's a problem:**
- Benchmark scores become meaningless for measuring real-world generalization
- The field can't compare models fairly if contamination is unknown
- Researchers building on contaminated models make incorrect conclusions about what works

**Detecting contamination:**
1. **N-gram overlap**: Check for high n-gram overlap (e.g., 8-gram) between training data and benchmark problems
2. **Exact match search**: Hash test examples and search training data
3. **Paraphrase detection**: More sophisticated — check for semantic similarity (embedding-based)
4. **Held-out performance analysis**: If fine-tuning improves a model much more on specific benchmarks than on held-out tasks, contamination is likely

**Current state**: Many public instruction datasets have some contamination. Llama 2's evaluation paper explicitly discusses benchmark contamination checks. This is still an active research problem — there's no standardized decontamination process.

</details>

---

**Q8: How does training on chain-of-thought examples improve reasoning in instruction-tuned models?**

<details>
<summary>💡 Show Answer</summary>

Chain-of-thought (CoT) prompting asks the model to "think step by step" before giving a final answer. When CoT examples are included in the instruction tuning dataset, the model learns to generate reasoning traces, not just answers.

**Why CoT in training data helps:**

1. **Explicit intermediate state**: Complex reasoning requires multiple steps. If the model just predicts the final answer, it has to encode the entire reasoning chain implicitly in a single generation. CoT externalizes the reasoning — each step is a token the model generates and can condition the next step on.

2. **Error correction**: If step 3 of a reasoning chain is wrong, subsequent steps built on step 3 will also be wrong. But because step 3 is explicit text, the model can (in principle) detect and correct the error rather than carrying a hidden wrong assumption forward.

3. **Generalization**: Models trained on CoT examples generalize to similar reasoning patterns they haven't seen. Training on "If all A are B and all B are C, then all A are C" style examples helps the model handle novel syllogisms.

**FLAN-CoT / T5 CoT findings:**
Including CoT examples in the instruction tuning dataset improved performance on math word problems and logical reasoning benchmarks by large margins. Larger models benefited more — small models (< 7B) see less benefit from CoT, while large models (70B+) see dramatic improvements.

**Practical guidance**: If your fine-tuning dataset needs to support reasoning tasks, include at least some chain-of-thought examples. Format: "Let me think step by step. First... Second... Therefore, the answer is..."

</details>

---

**Q9: What happened with InstructGPT? How did it demonstrate that a smaller instruction-tuned model can beat a larger base model?**

<details>
<summary>💡 Show Answer</summary>

InstructGPT (Ouyang et al., OpenAI, 2022) was a landmark paper with a surprising finding: a 1.3B parameter instruction-tuned model was preferred by human evaluators over the raw 175B GPT-3 base model.

**What they did:**
1. Took GPT-3 (175B) as the base model
2. Collected ~13,000 (instruction, response) pairs via human labelers writing ideal responses
3. Fine-tuned GPT-3 on these pairs (SFT step)
4. Trained a reward model from human comparisons
5. Used PPO (reinforcement learning) to align the model with the reward model (RLHF step)

The final model: InstructGPT at 1.3B (with RLHF) was preferred by human evaluators over 175B raw GPT-3.

**Why this happened:**
- 175B GPT-3 continues text — helpful for some tasks, unhelpful and verbose for others
- 1.3B InstructGPT answers questions directly, helpfully, in an appropriate format
- Humans prefer helpful and direct responses over technically "better" text continuations
- The alignment with human preferences > raw parameter count

**The key insight**: Parameters measure capability. Alignment measures whether that capability is applied usefully. A well-aligned smaller model can appear much better to users than a powerful but misaligned larger model.

This finding shaped the entire industry's approach: don't just scale parameters — align with human preferences. ChatGPT, Claude, and all major chat products are built on this insight.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [04 Fine Tuning](../04_Fine_Tuning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 RLHF](../06_RLHF/Theory.md)
