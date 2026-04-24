# Hallucination and Alignment — Interview Q&A

## Beginner

**Q1: What is LLM hallucination? Why does it happen?**

<details>
<summary>💡 Show Answer</summary>

LLM hallucination is when a language model generates text that is factually incorrect or made up, but presents it with the same fluency and confidence as correct information.

Examples: citing papers that don't exist, stating wrong dates for historical events, inventing URLs or statistics.

Why it happens: LLMs are statistical pattern matchers. They learn to generate text that looks like the text they were trained on. They don't "look things up" — they generate what is most statistically likely given the context. For common facts the model saw many times in training ("The capital of France is Paris"), the highest-probability continuation is correct. For obscure facts the model rarely saw, the highest-probability continuation is often a plausible-sounding guess.

There's no internal mechanism that says "I don't know this — refuse to answer." The model generates tokens either way. The probability distribution looks similar whether the model actually knows something or is filling in with a plausible pattern.

</details>

---

<br>

**Q2: What is alignment? What does "Helpful, Harmless, Honest" mean?**

<details>
<summary>💡 Show Answer</summary>

Alignment is the challenge of making AI systems behave in ways that match human values and intentions. An "aligned" model does what you actually want, not just what you technically asked for, and avoids causing harm.

"Helpful, Harmless, Honest" (HHH) is Anthropic's framework for alignment:

**Helpful**: The model actually assists users with their tasks. Not just technically compliant — genuinely useful. A model that refuses every request is not helpful, even if it's very safe.

**Harmless**: The model avoids producing content that could cause harm — dangerous instructions, hate speech, harassment, deception. Not so cautious that it's useless, but refuses clear harms.

**Honest**: The model doesn't make things up, doesn't pretend to know things it doesn't, acknowledges uncertainty, and doesn't deceive users. This includes hallucination — an honest model would say "I'm not sure" rather than fabricate an answer.

The challenge: these three objectives sometimes conflict. Being maximally helpful might mean giving information that could be harmful. Being maximally harmless might mean refusing so many things the model becomes useless. Alignment is the art of balancing all three well.

</details>

---

<br>

**Q3: What is Constitutional AI and how is it different from RLHF?**

<details>
<summary>💡 Show Answer</summary>

Constitutional AI (CAI) is Anthropic's approach to alignment that uses a written set of principles (a "constitution") and AI feedback instead of relying entirely on human raters.

Standard RLHF: human annotators compare responses and rate which is better. Expensive, slow, and limited by annotator consistency.

Constitutional AI:
1. Takes a model that is "helpful but not yet safe"
2. Asks the model to generate responses to potentially harmful prompts
3. Asks the model to critique its own responses using principles from the constitution
4. Asks the model to revise its responses based on the critique
5. Uses another AI model (like Claude Opus) to compare response pairs according to the constitution's principles
6. Trains a preference model from these AI-generated comparisons
7. Runs RL against this preference model

Key differences:
- **Scalable**: AI feedback is much cheaper than human feedback
- **Transparent**: The constitution is a readable document. You can see exactly what values are being instilled.
- **Consistent**: AI raters apply principles consistently (no daily variation like human annotators)
- **Auditable**: If behavior is wrong, you can check if it violates the constitution and revise the principles

Claude (all versions) was trained using Constitutional AI. It's a significant alternative to pure RLHF.

</details>

---

## Intermediate

**Q4: What is calibration in the context of hallucination? Why is it important?**

<details>
<summary>💡 Show Answer</summary>

Calibration refers to the relationship between a model's expressed confidence and its actual accuracy. A perfectly calibrated model that says "I'm 80% sure" would be right 80% of the time on such statements.

Why LLMs are poorly calibrated:
- Pretraining rewards fluency — confident text often scored higher in next-token prediction
- RLHF sometimes rewarded confident-sounding responses (human raters preferred them)
- Models learn to match the confident writing style of their training data, not to accurately represent their own uncertainty

**Manifestations of poor calibration:**
- Stating a made-up fact with the same tone as a well-established one
- Saying "certainly" when the model is actually uncertain
- Not saying "I don't know" because that phrase rarely appeared in training data as a good answer

**Why calibration matters:**
If a model says "the paper by Smith et al. (2019) found X" with full confidence, you can't tell if it actually exists. A calibrated model would say "I believe there was a paper, though I'd recommend verifying" for uncertain citations — giving you the signal to check.

**How to improve calibration:**
- Add "express your uncertainty appropriately" to system prompts
- Fine-tune on examples that model good uncertainty language
- Ask "how confident are you?" as a follow-up
- Use techniques like "predict, then verify" prompting patterns

</details>

---

<br>

**Q5: How does RAG (Retrieval-Augmented Generation) mitigate hallucination?**

<details>
<summary>💡 Show Answer</summary>

RAG reduces hallucination by grounding model outputs in specific retrieved documents rather than having the model rely solely on its parametric memory (what it learned during training).

**The core insight**: If the answer is in the context window (retrieved document), the model's job is to extract/summarize it, not generate it from memory. Extraction is much less prone to hallucination than generation from scratch.

**How RAG works for hallucination reduction:**
1. User asks a question
2. A retrieval system (vector database + embedding model) finds the most relevant documents
3. Those documents are inserted into the model's context
4. The model answers using the retrieved content
5. Optionally: the model is prompted to cite specific passages

**Why it works:**
- The model can see the actual source material — no need to "remember"
- You can prompt: "Answer only based on the provided documents. If the answer isn't there, say so."
- Citations become verifiable — user can check the original source

**Limitations:**
- Retrieval can fail to find the right document (retrieval miss)
- Model can still hallucinate even with sources (ignore or misread them)
- Adversarial documents in the knowledge base can cause the model to reproduce incorrect information
- Doesn't help for tasks where no external documents exist (open-ended reasoning, math)

RAG is the most practical and widely deployed hallucination mitigation strategy in production systems.

</details>

---

<br>

**Q6: What is chain-of-thought prompting? How does it reduce hallucination?**

<details>
<summary>💡 Show Answer</summary>

Chain-of-thought (CoT) prompting asks the model to "think step by step" and show its reasoning before giving a final answer.

**Without CoT:**
```
Q: A bat and ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost?
A: The ball costs $0.10.   (wrong — this is the intuitive but incorrect answer)
```

**With CoT:**
```
Q: A bat and ball cost $1.10. The bat costs $1 more than the ball. How much does the ball cost? Think step by step.
A: Let's call the ball's cost x. The bat costs x + $1. Together: x + (x + 1) = 1.10. So 2x = 0.10, x = $0.05. The ball costs $0.05.  (correct)
```

**Why CoT reduces hallucination:**

1. **Explicit intermediate steps**: Each reasoning step is a token the model generates and can condition the next step on. Errors become visible and can be caught.

2. **Forces deliberation**: The model has to "work through" the problem rather than jumping to the most statistically likely answer. This surface slower, more careful reasoning.

3. **Verification opportunity**: The user (or another model) can check each step, not just the final answer.

4. **Self-consistency**: Run CoT multiple times. If different reasoning paths reach different answers, that signals uncertainty. Take the majority vote.

**Limitations**: CoT helps with reasoning and math but doesn't help with pure factual recall (if the model doesn't know a date, having it "think step by step" doesn't produce the correct date).

</details>

---

## Advanced

**Q7: What is the difference between closed-book and open-book hallucination? How do production systems address each?**

<details>
<summary>💡 Show Answer</summary>

The terms come from an analogy to exams:

**Closed-book**: The model must answer from its parametric memory (what it learned during training). No external documents available.

**Open-book**: The model has access to retrieved documents in its context window (RAG). Answers should be grounded in those documents.

These have different hallucination failure modes:

**Closed-book failure modes:**
- Factual recall errors: the model "misremembers" facts from training
- Knowledge gaps: topics not well-represented in training data
- Temporal displacement: using outdated information as current
- Confidence without knowledge: same tone for known vs unknown facts

**Open-book failure modes:**
- Retrieval failure: the right document wasn't retrieved, model falls back on parametric memory
- Faithful but wrong: the retrieved document itself is incorrect
- Selective attention: model ignores relevant parts of retrieved documents
- Context contamination: model mixes retrieved content with parametric memory
- Attribution errors: model attributes information to wrong document in context

**Production system design:**

| Failure mode | Mitigation |
|-------------|-----------|
| Factual recall | Use RAG, cite sources, mandate document grounding |
| Retrieval failure | Multiple retrieval strategies, fallback to "I don't know" |
| Outdated knowledge | Include date context, filter retrieved docs by date |
| Confident ignorance | Few-shot examples showing hedged answers, add "say I don't know" to system prompt |
| Attribution errors | Structured output with explicit [Document N] citations |

The best production systems combine: closed-book knowledge for common facts, open-book retrieval for specific claims, and explicit system prompts that encourage "I don't know" responses when unsure.

</details>

---

<br>

**Q8: What causes the factuality vs fluency tradeoff in language models? Is it possible to achieve both?**

<details>
<summary>💡 Show Answer</summary>

The core tension: language models are trained to generate fluent, probable text. Fluent, probable text doesn't always align with factual text.

**Why the tradeoff exists:**

1. **Training objective**: Next-token prediction rewards generating text that looks like training data. Training data contains confident, fluent writing — academic papers, news articles, books all write factual claims confidently. Models learn this style.

2. **Fluency feedback in RLHF**: Human raters often prefer fluent, confident answers. They may unknowingly rate well-written hallucinations higher than accurate but hedged responses. The reward model learns: "confident fluency → high score."

3. **Uncertainty is anti-fluent**: Phrases like "I'm not certain, but...", "It's possible that...", "you should verify this" break reading fluency. Models that generate these frequently may be rated worse by raters who prioritize coherence.

4. **No training signal for "I don't know"**: The model rarely saw "I don't know" as the correct continuation in pretraining. Wikipedia doesn't say "I don't know" — it just doesn't cover the topic.

**Can you achieve both?**

Partially:
- **Calibration fine-tuning**: Fine-tune specifically on examples that model appropriate uncertainty. "I'm confident X is the capital of France, but I'd recommend verifying that the CEO you mentioned is still in that role."
- **RLHF with calibration reward**: Include calibration metrics in the reward signal. Rate responses where the model expresses high confidence about correct facts AND expresses uncertainty about uncertain facts highly.
- **Factuality benchmarks in alignment**: Explicitly test and reward on factuality benchmarks (TruthfulQA, HaluEval) during alignment training.
- **Output structure**: Force the model to separate "what I know" from "what I'm inferring" via structured output format.

Current frontier models are significantly better calibrated than early versions, but perfect calibration remains elusive. The tradeoff is reduced but not eliminated.

</details>

---

<br>

**Q9: How do you evaluate and measure hallucination in production systems? What are the key metrics and testing approaches?**

<details>
<summary>💡 Show Answer</summary>

Measuring hallucination is harder than preventing it. You need systematic evaluation:

**Automated benchmarks:**

- **TruthfulQA**: 817 questions where the intuitive answer is often wrong. Measures whether models generate truthful answers or default to common misconceptions. Scored by GPT-4 judge + human overlap.
- **HaluEval**: Dataset of hallucinated vs. non-hallucinated document summaries, QA answers, and conversations. Tests if the model can detect hallucinations in others — proxy for its own.
- **FactScore**: Breaks model responses into individual factual claims, then verifies each claim against Wikipedia. Gives a percentage of verifiable claims.
- **FreshQA**: Time-sensitive questions about recent events. Tests temporal hallucination.

**Domain-specific evaluation:**

For production systems, build domain-specific hallucination test sets:
1. Collect 100–500 "ground truth" facts specific to your domain
2. Create questions that require these facts
3. Run the model and verify answers against ground truth
4. Measure hallucination rate (facts stated incorrectly / total facts stated)

**LLM-as-judge:**
Use a separate strong model (Claude 3 Opus, GPT-4) to evaluate responses:
```
Prompt: "Given the following source document and model response, identify any factual claims in the response that are not supported by the document or that contradict it."
```

Automates hallucination detection at scale, though the judge can also hallucinate.

**Adversarial red-teaming:**
Deliberately try to make the model hallucinate:
- Ask about fictional people/events as if real
- Ask about topics near but not in training distribution
- Provide slightly wrong premises and see if model corrects or agrees
- Ask very specific statistics or dates

**Key production metrics:**

| Metric | How to measure |
|--------|----------------|
| Factual accuracy | Automated fact-check against knowledge base |
| Citation validity | Retrieve cited URLs/papers — do they exist? |
| Retrieval faithfulness | % of claims in response grounded in retrieved documents |
| Hallucination rate | Human or LLM audit on random sample |
| Over-refusal rate | % of benign queries refused (false positive safety) |

Running these systematically before and after model updates is the only reliable way to track hallucination in production.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Mitigation_Strategies.md](./Mitigation_Strategies.md) | Hallucination mitigation strategies |

⬅️ **Prev:** [07 Context Windows and Tokens](../07_Context_Windows_and_Tokens/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Using LLM APIs](../09_Using_LLM_APIs/Theory.md)
