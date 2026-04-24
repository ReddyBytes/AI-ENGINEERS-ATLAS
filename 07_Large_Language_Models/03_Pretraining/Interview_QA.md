# Pretraining — Interview Q&A

## Beginner

**Q1: What is pretraining and why is it needed?**

<details>
<summary>💡 Show Answer</summary>

Pretraining is the initial large-scale training phase where a language model learns from massive amounts of raw text. The training task is self-supervised: given all previous tokens, predict the next one. No human labels are needed because the "correct answer" at each position is just the next word already in the text.

Pretraining is needed because it gives the model a broad foundation. Before any task-specific training, the model learns grammar, world facts, reasoning patterns, code syntax, and writing style by absorbing the patterns in trillions of tokens of human text. Without pretraining, you'd have to teach all of this from scratch for every new task — impossibly expensive.

The result is a "base model" that knows a lot but doesn't yet know how to be helpful or follow instructions. That comes next.

</details>

---

<br>

**Q2: What is self-supervised learning? How is it different from supervised learning?**

<details>
<summary>💡 Show Answer</summary>

In supervised learning, humans provide labeled examples: (input, correct output) pairs. A model learns the mapping. This requires expensive human annotation.

In self-supervised learning, the supervision signal comes from the data itself — no human labeling needed. For LLMs, the signal is: given the tokens before position i, predict the token at position i. The correct token is already in the text.

This is powerful because:
- You can use any raw text as training data
- The internet contains hundreds of terabytes of text
- You don't need to pay annotators for every example
- The model learns a much broader, richer representation than supervised learning on a narrow task could achieve

Other examples of self-supervised learning: masked language modeling (BERT masks tokens and predicts them), image-text contrastive learning (CLIP), and self-supervised visual pretraining.

</details>

---

<br>

**Q3: What is in an LLM's training data? Where does it come from?**

<details>
<summary>💡 Show Answer</summary>

LLM training data comes from many sources, mixed together:

**Web crawls (Common Crawl)**: The largest source. Billions of web pages scraped from the internet. Heavily filtered to remove spam, adult content, and low-quality text. Still the noisiest source but provides enormous breadth.

**Books**: Higher quality than web text. Long-form, coherent writing. Teaches the model to reason across many paragraphs. Sources include BookCorpus, Project Gutenberg, and licensed book datasets.

**Wikipedia**: Encyclopedic knowledge. Well-structured, factual, covers almost every topic. Relatively small in token count but very high quality.

**Code (GitHub)**: Source code across dozens of programming languages. Teaches syntax, logic, and patterns. Code is especially useful because it's precise — either it's valid code or it isn't.

**Academic papers (ArXiv, PubMed)**: STEM reasoning, mathematical notation, technical writing.

**News and web Q&A**: Current events, conversational patterns, factual question-answering.

The mix is carefully balanced. Most frontier models treat Wikipedia and books as higher-quality sources and oversample them relative to raw web crawl.

</details>

---

## Intermediate

**Q4: What are the Chinchilla scaling laws and why did they change how models are trained?**

<details>
<summary>💡 Show Answer</summary>

The Chinchilla paper (Hoffman et al., DeepMind, 2022) showed that the LLM field had been systematically undertraining its models.

Previous scaling guidance (Kaplan et al., 2020) suggested that for a given compute budget, you should scale model size more than training data. This led to models like Gopher (280B parameters) trained on only 300B tokens.

Chinchilla showed this was wrong. They trained hundreds of models at various parameter counts and token counts and found: **for optimal performance, you should train on approximately 20 tokens per parameter**.

- 70B parameters → optimal training on ~1.4T tokens
- 7B parameters → optimal training on ~140B tokens

They trained Chinchilla (70B parameters, 1.4T tokens) and it outperformed Gopher (280B, 300B tokens) on almost every benchmark, despite being 4x smaller.

**Impact**: The entire industry shifted toward training smaller models on more tokens. Llama 3's 8B model trained on 15T tokens (187 tokens per parameter — well over the Chinchilla optimum) dramatically outperforms models 10x its size trained on less data. Better inference efficiency and comparable quality — a strong trade-off.

</details>

---

<br>

**Q5: How is training distributed across hundreds of GPUs? What are the main parallelism strategies?**

<details>
<summary>💡 Show Answer</summary>

Training a 70B+ parameter model on a single GPU is impossible — the model doesn't fit in memory. Several parallelism strategies are used:

**Data parallelism**: The same model is replicated across GPUs. Each GPU processes a different batch of data. Gradients are synchronized (averaged) across all replicas after each step. Simple, but requires each GPU to hold the full model.

**Tensor parallelism (model parallelism)**: Individual weight matrices are split across GPUs. For a 4096×4096 matrix, split into 4 GPUs each holding 1024×4096. Computation is done in pieces and results combined with all-reduce operations. Requires fast inter-GPU communication (NVLink).

**Pipeline parallelism**: Model layers are split across GPUs sequentially. GPU 1 handles layers 1–8, GPU 2 handles layers 9–16, etc. GPUs work in a pipeline — while GPU 2 processes the batch from GPU 1, GPU 1 processes the next batch. Has "pipeline bubbles" (idle time) that need scheduling tricks to minimize.

**Expert parallelism** (for Mixture-of-Experts): Different "expert" sub-networks run on different GPUs. Routing logic sends tokens to the appropriate GPU.

In practice, all strategies are combined. Training Llama 3 405B used tensor + pipeline + data parallelism simultaneously across ~16,000 H100 GPUs.

</details>

---

<br>

**Q6: What is the pretraining loss curve? How do you know if training is going well?**

<details>
<summary>💡 Show Answer</summary>

The pretraining loss is cross-entropy loss on next-token prediction. A well-behaved training run looks like:

1. **Rapid initial drop**: The model quickly learns basic patterns (common words, simple grammar)
2. **Gradual smoothing**: Loss decreases but more slowly as easy patterns are learned and harder ones remain
3. **Power law improvement**: Loss continues decreasing as a smooth power law with more tokens — this is the predictable scaling behavior

Signs training is going well:
- Loss decreases monotonically (with some noise, but no sustained plateaus or spikes)
- Validation loss tracks training loss (no overfitting)
- Benchmark evals improve on schedule with predicted scaling law curves

Signs of problems:
- **Loss spike**: A sudden sharp increase. Usually caused by a bad batch or learning rate issue. Can recover if minor; may require resuming from a checkpoint.
- **Training divergence**: Loss goes to infinity (NaN). Catastrophic — bad hyperparameters.
- **Plateau**: Loss stops decreasing. May indicate learning rate is too low, data is exhausted, or gradient issues.
- **Overfitting**: Training loss decreases but validation loss doesn't. Common when data is deduplicated poorly.

Training GPT-4 scale models involves constant monitoring with automated alerts and teams watching dashboards 24/7.

</details>

---

## Advanced

**Q7: What role does the tokenizer play in pretraining? What happens if you train with a bad tokenizer?**

<details>
<summary>💡 Show Answer</summary>

The tokenizer converts raw text into integer token IDs before training. Every character in the training data must pass through it. The tokenizer's vocabulary directly shapes what the model learns.

**Common tokenization algorithms:**
- **BPE (Byte-Pair Encoding)**: Start with individual characters, iteratively merge the most frequent pair into a new token. Used by GPT-3/4.
- **SentencePiece**: Language-agnostic BPE/unigram variant. Used by Llama.
- **WordPiece**: Similar to BPE, used by BERT.

**What bad tokenization does:**
- **Too many tokens per word**: Rare words split into many pieces (e.g., "unhelpfulness" → 5+ tokens). The model needs more context to understand the word; sequences become artificially longer.
- **Byte fallback vs. unknown token**: Old tokenizers had a special `[UNK]` token for unknown characters. The model learned nothing about these. Modern byte-level tokenizers never produce unknown tokens — every byte is representable.
- **Code inefficiency**: A tokenizer trained only on English text may tokenize Python code very inefficiently. GPT-4's tokenizer tokenizes code much more efficiently than GPT-2's did.
- **Language imbalance**: A tokenizer that merges common English sub-words but splits Chinese characters character-by-character means Chinese text uses 4–6x more tokens than equivalent English text. Chinese users pay more and get worse quality.

**Impact on pretraining**: A better tokenizer means the model sees more semantic content per context window, leading to better quality at the same sequence length.

</details>

---

<br>

**Q8: What is "catastrophic forgetting" in the context of continual pretraining? How do you handle it?**

<details>
<summary>💡 Show Answer</summary>

Catastrophic forgetting is the phenomenon where a neural network "forgets" previously learned information when trained on new data. The new gradient updates overwrite the weight configurations that encoded old knowledge.

For pretraining, this matters when you want to update a model with new data (e.g., adding knowledge from 2025 events to a model trained through 2023).

If you fine-tune on only new data:
- The model rapidly improves on new data
- Performance on old tasks degrades dramatically
- The valuable pretraining is partially destroyed

**Mitigations:**

1. **Data replay / experience replay**: Mix new data with samples from the original training distribution. The model reinforces old patterns while learning new ones. Expensive because you need access to original training data.

2. **Elastic Weight Consolidation (EWC)**: Identify which parameters are most important for previous tasks (using Fisher information) and penalize large changes to them. Computationally intensive at LLM scale.

3. **Low learning rate continual pretraining**: Use a very small learning rate when adding new domain data. The model nudges toward new knowledge without catastrophically overwriting old patterns. Common in practice (e.g., medical domain adaptation).

4. **Adapter layers / LoRA**: Add new parameters for new knowledge, freeze most old parameters. The base knowledge is preserved by not touching those weights.

5. **Full retraining**: If the new data is large enough and the capability gap is severe, just retrain from scratch with the new data mixed in. What Meta did with Llama 3 — incorporated much more recent data into a fresh training run rather than patching Llama 2.

</details>

---

<br>

**Q9: What is the difference between GPT-style (decoder-only) and BERT-style (encoder-only) pretraining? When would you choose each?**

<details>
<summary>💡 Show Answer</summary>

The two dominant pretraining architectures use different attention patterns and different objectives:

**GPT-style (decoder-only, causal language model):**
- Architecture: Causal (left-to-right) attention — each token only attends to tokens before it
- Objective: Next-token prediction (autoregressive)
- At inference: Can generate new text naturally — just keep predicting next tokens
- Examples: GPT-4, Claude, Llama, Gemini

**BERT-style (encoder-only, masked language model):**
- Architecture: Bidirectional attention — each token attends to all other tokens
- Objective: Masked Language Modeling (MLM) — randomly mask 15% of tokens, predict the masked ones. Plus Next Sentence Prediction (NSP).
- At inference: Cannot generate text natively — outputs fixed-size contextual embeddings for each token
- Examples: BERT, RoBERTa, DeBERTa, ELECTRA

**Comparison:**

| Dimension | Decoder-only (GPT) | Encoder-only (BERT) |
|-----------|-------------------|---------------------|
| Training objective | Next-token prediction | Masked token prediction |
| Attention | Causal (left-to-right) | Bidirectional |
| Good for | Text generation, chat, code | Classification, NER, semantic similarity |
| Context usage | Sees past only | Sees full context both ways |
| Fine-tuning for classification | Add classification head, works OK | Natural fit — bidirectional is better |
| Generative use | Native | Not possible without modification |

**When to use each:**
- Need to generate text? → Decoder-only (GPT/Llama style)
- Need embeddings for classification, search, NER, sentence similarity? → Encoder-only (BERT style)
- Need both? → Encoder-decoder (T5, BART style) — or just use a frontier LLM

In 2024, decoder-only models have largely taken over even classification tasks because large enough GPT-style models with RLHF can do everything. But for production classification systems where speed and cost matter, BERT-style models are still faster and cheaper per query.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Pretraining architecture deep dive |

⬅️ **Prev:** [02 How LLMs Generate Text](../02_How_LLMs_Generate_Text/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Fine Tuning](../04_Fine_Tuning/Theory.md)
