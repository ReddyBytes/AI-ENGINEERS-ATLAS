# Chunking Strategies — Interview Q&A

## Beginner

**Q1: What is chunking in RAG and why is it necessary?**

<details>
<summary>💡 Show Answer</summary>

Chunking is the process of splitting large documents into smaller text passages before embedding them. It's necessary for two reasons.

First, embedding models have context limits — most handle 256 to 8192 tokens. A 100-page document can't be embedded as a single unit.

Second and more importantly: specificity. If you embed a 50-page annual report as one vector, that vector tries to represent everything in the report — financial data, strategy, org structure, legal disclaimers. When a user asks about revenue figures, the embedding won't match well because it's diluted across all topics. A 400-token chunk specifically about Q3 revenue will embed to a vector that precisely matches the query "what was Q3 revenue?"

In short: better chunks → better embeddings → better retrieval → better answers.

</details>

---

<br>

**Q2: What is chunk overlap and why do we need it?**

<details>
<summary>💡 Show Answer</summary>

Chunk overlap means adjacent chunks share some text. For example, if chunk size is 500 tokens with 50-token overlap, the last 50 tokens of chunk 1 appear again as the first 50 tokens of chunk 2.

Without overlap: a key piece of information might fall exactly at a chunk boundary. Half the sentence is in chunk 1, half in chunk 2. Neither chunk answers the question completely. The embedding of each half-sentence is weak.

With overlap: both chunks contain that boundary information, so at least one chunk will have the full context for retrieval. It's like indexing the seams of a puzzle from both sides.

Typical overlap: 10–20% of chunk size. More overlap = more redundancy (higher storage, more duplicate content in results). Less = more risk of missing boundary information.

</details>

---

<br>

**Q3: What is `RecursiveCharacterTextSplitter` and why is it the recommended default?**

<details>
<summary>💡 Show Answer</summary>

It's a text splitting class in LangChain that tries to split on natural text boundaries before falling back to character counts. It has a priority list of separators: `["\n\n", "\n", " ", ""]` — paragraph breaks, line breaks, word spaces, and individual characters.

For any given chunk, it first tries to split on `\n\n` (paragraph boundary). If a paragraph is still too long, it tries `\n`. Still too long? `" "`. Last resort: split mid-character.

It's the recommended default because it respects the document's natural structure. Paragraphs stay together when they fit. Sentences don't get split in the middle unless absolutely necessary. This produces semantically cleaner chunks than blindly splitting every N characters, without needing a sophisticated semantic understanding like semantic chunking requires.

</details>

---

## Intermediate

**Q4: What is parent-child chunking and when should you use it?**

<details>
<summary>💡 Show Answer</summary>

Parent-child chunking solves a tension: small chunks retrieve precisely, but they lack context for the LLM to generate a good answer. Large chunks have good context but retrieve imprecisely.

The solution: index small child chunks for retrieval. When a child chunk is retrieved, return the larger parent chunk to the LLM.

Example: a legal contract. Child chunk (200 tokens): "Indemnification: The vendor shall hold harmless the client from..." — precise enough to match a query about indemnification. Parent chunk (1500 tokens): the entire indemnification section with definitions, exceptions, and procedures — enough context for the LLM to give a complete answer.

Use when: your documents have natural hierarchical structure (sections and subsections), when small chunks alone don't provide enough context for good answers, or when you want to cite specific passages but provide full section context.

</details>

---

<br>

**Q5: How does semantic chunking work? What are its tradeoffs?**

<details>
<summary>💡 Show Answer</summary>

Semantic chunking groups sentences together while their topic stays consistent, then starts a new chunk when the topic changes. It uses embedding similarity to detect those changes.

Process: (1) Split document into individual sentences. (2) Embed each sentence. (3) Compute cosine similarity between consecutive sentence pairs. (4) When similarity drops sharply below a threshold, start a new chunk.

The result: chunks naturally align with topic boundaries. A paragraph about photosynthesis stays in one chunk. A paragraph about cellular respiration starts a new chunk. No arbitrary cuts mid-concept.

Tradeoffs: requires running an embedding model just for chunking (expensive upfront). Chunk sizes are variable (some topics are 2 sentences, others are 20). The similarity threshold is a hyperparameter to tune. Significantly slower than character-based methods.

Use when: your documents have clear topic boundaries (research papers, technical documentation, encyclopedia articles) and you have the compute budget for embedding twice.

</details>

---

<br>

**Q6: What is the optimal chunk size? How do you choose it for your use case?**

<details>
<summary>💡 Show Answer</summary>

There's no universal answer — it depends on your documents, queries, and embedding model. But there are useful heuristics.

Start at 512 characters (roughly 120–150 tokens). This works for most English knowledge bases.

Smaller chunks (200–300 chars): better for precise factual lookups ("what's the refund deadline?"), collections of short FAQs, or documents where every sentence is independently important.

Larger chunks (800–1200 chars): better for conceptual questions that need more context ("explain the company's approach to diversity"), technical documentation where procedures span multiple steps, or documents where context within a section matters.

The empirical approach: build a test set of 20–50 representative (query, expected_answer) pairs. Try chunk sizes of 200, 500, and 800 characters. Measure recall@5 for each. Pick the chunk size with the highest recall on your test set.

Never choose chunk size by intuition alone. Always measure.

</details>

---

## Advanced

**Q7: How does chunking strategy affect embedding model choice?**

<details>
<summary>💡 Show Answer</summary>

They're intertwined. Different embedding models have different context length limits and different sensitivities to input length.

Short context models (all-MiniLM-L6-v2: 256 tokens max): require small chunks. Excellent quality within their limit. If your chunk exceeds 256 tokens, the excess is truncated — potentially cutting the most important part.

Longer context models (text-embedding-3-small: 8K tokens, jina-embeddings-v2: 8K tokens): can handle larger chunks without truncation. Enable parent-child retrieval where parent chunks are large.

Dimension matters too: a 384-dim model (MiniLM) has less representational capacity than a 1536-dim model (text-embedding-3-small). Larger chunks need more dimensions to represent diverse content within a single vector.

Rule of thumb: make sure your chunk size is well within the embedding model's context limit (aim for less than 80% of the limit). For models with small limits, you must chunk small. For models with large limits, you have freedom to choose.

</details>

---

<br>

**Q8: What is the "lost in the middle" problem and how does chunking help or hurt?**

<details>
<summary>💡 Show Answer</summary>

The "lost in the middle" problem: when an LLM receives multiple context chunks, information in the middle of the context tends to be used less than information at the start or end. Research shows LLMs have a U-shaped attention curve over long contexts.

Chunking affects this: if you retrieve 10 large chunks and concatenate them into a huge context, the important chunk in the middle might be effectively ignored. If you retrieve 3 focused small chunks, the most relevant information is less diluted and gets more model attention.

Mitigations: (1) Reduce the number of retrieved chunks — top-3 is often better than top-10. (2) Re-rank retrieved chunks and put the most relevant ones at the start of the context. (3) Use smaller chunks so the total context is shorter. (4) Use a model with strong long-context performance (Claude, Gemini).

Chunking size is the easiest lever: smaller chunks = less "noise" in context = less lost-in-the-middle effect.

</details>

---

<br>

**Q9: How would you chunk a technical API reference documentation that has function signatures, code examples, and prose descriptions all mixed together?**

<details>
<summary>💡 Show Answer</summary>

Technical docs with mixed content require a more thoughtful strategy than general text splitting.

Approach 1: Section-based chunking. API docs typically have clear headers per function/endpoint. Use headers as natural split points — each function/endpoint becomes one chunk. This is semantically ideal: users search for specific functions.

Approach 2: Separate chunk types. Create three chunk types: (a) signature chunks: just the function signature and parameter list — for "how do I call X?", (b) description chunks: the prose explanation — for "what does X do?", (c) example chunks: the code examples — for "show me how to use X". Tag chunks with `chunk_type` metadata and potentially retrieve from each type separately.

Approach 3: Preserve code blocks intact. Never split mid-code. Use the code block boundaries as mandatory split boundaries, then recursively split the prose sections.

In practice: a combination works best. Preserve code block integrity, split prose recursively with small chunks (300–400 chars), and tag each chunk with its function name, module, and content type in metadata.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Comparison.md](./Comparison.md) | Chunking strategies comparison |

⬅️ **Prev:** [02 Document Ingestion](../02_Document_Ingestion/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Embedding and Indexing](../04_Embedding_and_Indexing/Theory.md)
