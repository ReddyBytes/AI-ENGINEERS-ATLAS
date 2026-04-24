# Context Windows and Tokens — Interview Q&A

## Beginner

**Q1: What is a token? Why isn't it the same as a word?**

<details>
<summary>💡 Show Answer</summary>

A token is the basic unit of text that a language model processes. It's not the same as a word because the tokenization algorithm (usually Byte Pair Encoding) splits text at subword boundaries, not word boundaries.

How it works: BPE starts with individual characters and merges the most frequent pairs of tokens until it reaches a target vocabulary size (~32k–128k tokens). This means:

- Common short words become single tokens: "the", "is", "cat" → 1 token each
- Common longer words stay whole: "running", "python", "table" → 1 token
- Rare or long words split into pieces: "tokenization" → "token" + "ization" (2 tokens)
- Numbers and punctuation have their own tokens: "2024" → 1 token, "!!!" → 3 tokens

The rough rule of thumb: 1 token ≈ 0.75 words, or 4 characters.

Why it matters practically:
- API costs are per token, not per word
- Context windows are measured in tokens
- Non-English text often uses more tokens per word (less common sub-word patterns)
- Counting words ≠ counting tokens — always use a tokenizer for accurate counts

</details>

---

<br>

**Q2: What is a context window and what happens when you exceed it?**

<details>
<summary>💡 Show Answer</summary>

The context window (also called context length) is the maximum number of tokens the model can process in a single forward pass. Everything in the window is "visible" to the model — it can attend to any part of it when generating each response token.

What goes into the context window:
- System prompt (instructions for the model)
- Full conversation history (all previous user and assistant messages)
- Current user message
- The model's response (as it's being generated)

When you exceed the context window, something must be dropped. Different systems handle this differently:

1. **Hard truncation**: Simply cut the oldest tokens. The oldest messages disappear. The model has no memory of them.
2. **Sliding window**: Keep only the most recent N tokens, dropping from the beginning as new tokens arrive.
3. **Summarization**: Compress older parts of the conversation using the model itself, then add the summary to context.
4. **Error**: Some APIs simply return an error if you exceed the limit.

The practical consequence: very long chat sessions can "forget" things you said early in the conversation. For production systems, context window management is a real engineering problem.

</details>

---

<br>

**Q3: Why do output tokens cost more than input tokens in LLM APIs?**

<details>
<summary>💡 Show Answer</summary>

In most LLM APIs, output tokens cost 3–5x more per token than input tokens. The reason is compute:

**Input tokens** are processed in a single forward pass. All input tokens are processed simultaneously using the transformer's parallel attention mechanism. Processing 1,000 input tokens is barely more expensive than processing 100 — it's parallel.

**Output tokens** are generated one at a time (autoregressive generation). Each new output token requires:
1. A full forward pass through the transformer
2. Computing attention over all previous tokens (input + previously generated)
3. Sampling from the output distribution

Generating 200 output tokens means 200 sequential forward passes. This is significantly more compute than the single forward pass used for input processing.

The compute cost difference directly translates to price difference. This is why:
- You should write concise prompts to reduce input cost
- You should limit max_tokens to avoid unnecessary long responses
- Summarization use cases (long input, short output) are cheaper than generation tasks (short input, long output)

</details>

---

## Intermediate

**Q4: What is the KV cache? How does it work and why is it important?**

<details>
<summary>💡 Show Answer</summary>

During the transformer's attention mechanism, each token computes Key (K) and Value (V) matrices that encode its representation for use in attention calculations. For a generated sequence of n tokens, generating token n+1 would naively require recomputing K and V for all n previous tokens — an O(n²) operation.

The KV cache solves this: after each token is generated, its K and V matrices are stored in a cache. When generating the next token, only the new token's K and V need to be computed; the rest are loaded from cache.

**Effect on performance:**
- Without KV cache: generating a 1,000-token response would require progressively longer forward passes
- With KV cache: each generation step takes roughly constant time (just one token's computation + cache lookups)

**Effect on memory:**
The KV cache grows linearly with context length. For each token in context:
- KV cache memory ≈ 2 × num_layers × hidden_dim × sizeof(float16)
- For a 70B model processing 128k tokens: ~128 GB KV cache alone
- This is often more than the model weights themselves

**Engineering implications:**
- For very long contexts, KV cache is the memory bottleneck, not model weights
- Some systems use techniques like quantized KV cache (store in int8) to save memory
- "Paged KV cache" (used in vLLM) manages KV cache like virtual memory pages for efficient batching
- The KV cache is why long-context inference is expensive even at companies with good hardware

</details>

---

<br>

**Q5: What is the "lost in the middle" problem? How does it affect how you should structure prompts?**

<details>
<summary>💡 Show Answer</summary>

The "Lost in the Middle" problem (Liu et al., 2023) is an empirical finding: language models recall information from the beginning and end of their context window much better than information buried in the middle.

**The experiment**: Present a model with many documents in its context window, one of which contains the answer to a question. Vary where the relevant document is placed — beginning, middle, or end. Measure accuracy.

**Finding**: Accuracy was highest when the relevant document was at position 1 (beginning) or position n (end). Accuracy dropped significantly when the document was in the middle, even for models with large context windows.

**Why this happens**: Attention patterns in transformers naturally weight recent tokens more heavily (recent = end of sequence) and the very first tokens have persistent influence as the "primacy" anchor. Middle positions receive less consistent attention.

**Practical implications for prompt design:**

1. Put your most important instructions in the system prompt (beginning of context)
2. Put any critical reference material early or as the last user message
3. Don't bury key information in a long document list — put relevant documents first
4. For multi-document RAG, rank documents by relevance and put highest-ranked first
5. If you need the model to remember something from a long context, repeat it near the end
6. For very long documents, extract and prepend the key sections rather than including the full document

</details>

---

<br>

**Q6: How do different positional encoding schemes affect context length capabilities?**

<details>
<summary>💡 Show Answer</summary>

Transformers require positional information because attention has no inherent notion of order. Different positional encoding approaches have very different extrapolation properties.

**Sinusoidal (original Transformer, 2017):**
- Fixed sinusoidal functions of position
- Cannot generalize beyond training sequence length at all
- If trained on length 512, performance collapses at 513+

**Learned absolute positions (early BERT, GPT-2):**
- Learns an embedding for each position from 1 to max_length
- Hard limit: can't process position 4097 if max is 4096
- Performance degrades before the limit due to out-of-distribution positions

**RoPE (Rotary Position Embedding, Su et al., 2021):**
- Encodes position as rotation of the query/key vectors
- Relative positions are preserved across all lengths
- Used in: Llama 1/2/3, Mistral, Gemini, Qwen
- Can extrapolate somewhat beyond training length
- Extended via "RoPE scaling" techniques for longer contexts

**ALiBi (Attention with Linear Biases, Press et al., 2021):**
- Adds a linear attention bias based on token distance (no special embedding)
- Clean extrapolation properties — just add larger penalties for longer distances
- Used in: MPT, BLOOM
- Very memory-efficient

**YaRN (Yet another RoPE extensioN, Peng et al., 2023):**
- Rescales RoPE frequencies to extend context beyond training length
- Allows 2–4x context extension with minimal quality loss
- Used to extend Llama 2 from 4k to 128k context

**Practical result**: Modern models use RoPE or ALiBi and are trained with explicit long-context fine-tuning to handle 128k–1M tokens. The encoding choice matters but training with the target context length is equally important.

</details>

---

## Advanced

**Q7: How does tokenization affect model performance on different languages and tasks?**

<details>
<summary>💡 Show Answer</summary>

Tokenization has a large, often underappreciated effect on model performance across languages and tasks.

**English-centric tokenizers:**
Most tokenizers are built primarily on English text. Common English words become single tokens, while text in other scripts may tokenize very inefficiently:

- English: "hello world" → 2 tokens
- Chinese: "你好世界" → 4–8 tokens (character-by-character often)
- Arabic: similar issue — right-to-left script, frequent ligatures
- Code in non-Latin scripts: large performance gap

Effect: Chinese or Arabic users of a model with an English tokenizer:
- Use 3–6x more tokens to express the same information
- Pay 3–6x more for the same text
- Have 3–6x less effective context window
- Often get lower quality responses (model's representation of these tokens is weaker)

**Tokenization and arithmetic:**
Numbers tokenize inconsistently. "123" might be 1 token. "1234" might be 2 tokens. "12345" might be 3 tokens. This inconsistency makes arithmetic harder — the model can't reliably "see" individual digits.

Models trained with digit-by-digit tokenization of numbers (treating "1", "2", "3" as separate tokens) are significantly better at arithmetic because each digit is independently visible and manipulable.

**Code tokenization:**
Code has unusual patterns: indentation (spaces/tabs), special characters, exact syntax requirements. Models trained with tokenizers not designed for code use many tokens to represent common constructs. GPT-4's tokenizer, trained with code in mind, is much more efficient at Python/JavaScript than earlier models.

**Practical lesson**: When evaluating an LLM for your use case, check how the tokenizer handles your specific input domain. If you're building for a non-English language, look for models with multilingual tokenizers (Llama 3, Qwen, etc.) that have better non-English token efficiency.

</details>

---

<br>

**Q8: What is "needle in a haystack" evaluation for context windows? What does it reveal?**

<details>
<summary>💡 Show Answer</summary>

"Needle in a haystack" (NIAH) is a standard evaluation methodology for long-context models. It directly tests whether a model can find and use information anywhere in a very long context.

**Setup:**
1. Take a long document (the "haystack") — often the full text of a novel or Paul Graham essays
2. Insert a specific piece of information (the "needle") at a precise position: "The secret password is 'golden-trumpet-42'"
3. Ask the model a question that requires finding the needle: "What is the secret password?"
4. Vary: (1) the total document length and (2) the needle's position (0%–100% through the document)
5. Plot a heatmap: x-axis = needle position, y-axis = total context length, color = accuracy

**What it reveals:**

Good long-context model: high accuracy across all positions and all lengths (solid green heatmap).

Typical failure patterns:
- Bright spots at beginning and end, dark in the middle (lost in the middle)
- Degradation as total length increases (positional encoding limitation)
- Certain positions consistently fail (attention pattern artifacts)
- Certain lengths work well, others don't (context length training gaps)

**Industry results (2024):**
- GPT-4: good up to ~128k tokens but degrades in middle
- Claude 3: excellent up to 200k tokens with less middle degradation
- Gemini 1.5 Pro: tested at 1M tokens; maintains reasonable performance

**Limitations of NIAH:**
- Tests retrieval of a specific fact, not reasoning over the full context
- Synthetic setup may not reflect real use patterns
- A model that passes NIAH might still fail at multi-hop reasoning across a long document

</details>

---

<br>

**Q9: How does context window size affect RAG system design? When is a large context not enough?**

<details>
<summary>💡 Show Answer</summary>

Context window size and RAG (Retrieval-Augmented Generation) interact in important ways, and many practitioners think they're alternatives when they're actually complementary.

**When large context replaces RAG:**
- If your entire document set fits in context: load it all, no retrieval needed
- Example: 20-page technical manual (~10k tokens) in a 128k context → just include the whole manual
- Simpler architecture, no retrieval errors, full context visibility

**When large context is NOT enough (and RAG is still needed):**

1. **Scale beyond any context window**: A company knowledge base with 50,000 documents (~500M tokens) can't fit in any model's context, even 1M tokens. You need retrieval.

2. **Cost**: Filling a 200k context window costs $0.60 per call in input tokens alone (at $3/1M). With RAG, retrieve 5 relevant documents (~10k tokens = $0.03/call). 20x cheaper per call.

3. **Freshness**: Context windows are filled once per request. A RAG system can pull from a database updated in real-time. If your knowledge base changes daily, context-stuffing requires rebuilding prompts constantly.

4. **Latency**: Processing 200k tokens takes seconds longer than processing 10k tokens. For low-latency applications, RAG's targeted retrieval is faster.

5. **Lost in the middle at scale**: Even with 1M context windows, retrieval quality degrades when you stuff everything in. The model gets "confused" by irrelevant documents. RAG pre-filters to only relevant chunks.

**The emerging best practice (2024):**
Use large context windows for local reasoning (analyze this 50-page document), combined with RAG for broad retrieval across large corpora. The two are complementary:
- RAG retrieves the relevant chunks (breadth)
- Large context holds those chunks + conversation history + task context (depth)

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [06 RLHF](../06_RLHF/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Hallucination and Alignment](../08_Hallucination_and_Alignment/Theory.md)
