# RAG Fundamentals — Interview Q&A

## Beginner

**Q1: What is RAG and why was it invented?**

<details>
<summary>💡 Show Answer</summary>

RAG stands for Retrieval-Augmented Generation. It was invented to solve a fundamental limitation of LLMs: they only know what was in their training data, which has a knowledge cutoff date and contains no private information.

RAG works in two phases. First, it retrieves relevant documents from a knowledge base based on the user's question. Second, it passes those documents as context to the LLM, which generates an answer grounded in the retrieved information.

It was invented because fine-tuning models on new knowledge was expensive, slow, and didn't enable source citation. RAG is faster (hours not weeks), cheaper (no training), updatable (just add docs), and auditable (every answer links back to a source).

</details>

---

<br>

**Q2: Walk me through the basic RAG pipeline step by step.**

<details>
<summary>💡 Show Answer</summary>

The pipeline has two phases:

**Indexing (done once):**
1. Load documents from your sources (PDFs, databases, web pages)
2. Split each document into smaller chunks (typically 256–512 tokens)
3. Embed each chunk using an embedding model — convert text to a vector
4. Store vectors (with metadata) in a vector database

**Query (on every user question):**
1. Receive the user's question
2. Embed the question with the same model used to embed documents
3. Search the vector database for chunks with similar embeddings (top-K results)
4. Build a prompt: "Based on the following context, answer: [question]. Context: [retrieved chunks]"
5. Send the prompt to the LLM
6. Return the answer (and optionally, the source chunks)

</details>

---

<br>

**Q3: What is the difference between RAG and prompt stuffing?**

<details>
<summary>💡 Show Answer</summary>

Prompt stuffing means putting all your documents directly into the prompt context. RAG means retrieving only the relevant parts.

Prompt stuffing works when: your knowledge base is small (a few pages), the model has a large enough context window, and you can afford the token cost.

Prompt stuffing fails when: your knowledge base is larger than the context window, the cost of sending all tokens every time is too high, or performance degrades from too much irrelevant context.

RAG selectively retrieves only the relevant 3–10 chunks for each query. This scales to millions of documents, is cost-efficient, and often produces more focused answers (less irrelevant context noise).

</details>

---

## Intermediate

**Q4: When should you use RAG vs fine-tuning? What are the key decision factors?**

<details>
<summary>💡 Show Answer</summary>

RAG and fine-tuning solve different problems.

Use RAG when: you have knowledge that changes (company docs, recent news), you need source citations, your data is private, or you need to be up and running quickly. RAG is deployed in hours.

Use fine-tuning when: you need the model to behave differently (e.g., always respond in a specific tone, format), you need domain-specific reasoning patterns, you're making millions of API calls and need to bake in a long system prompt to save tokens, or the task consistently fails even with perfect RAG.

The key insight: RAG for knowledge, fine-tuning for behavior. They're not mutually exclusive — production systems often fine-tune a model AND add RAG on top. But if you're choosing one, RAG is almost always the right starting point for knowledge-intensive tasks.

</details>

---

<br>

**Q5: What are the main failure modes of a RAG system?**

<details>
<summary>💡 Show Answer</summary>

Three major failure categories:

**Retrieval failure:** the right chunk isn't returned. Causes: poor chunking (relevant info spans chunk boundaries), wrong chunk size, incorrect embedding model, weak query. Fix: improve chunking, use hybrid search, try query transformation.

**Context window failure:** too many chunks retrieved, the most important one gets "lost" in the middle of a large context, or the total context exceeds the limit. Fix: reduce top-K, use re-ranking, limit chunk size.

**Generation failure:** the right chunks are retrieved, but the LLM generates an answer that contradicts or ignores them. Causes: weak prompt (doesn't clearly instruct to use the context), model "overconfident" in its own knowledge. Fix: strong prompting ("Answer ONLY based on the provided context"), evaluate faithfulness.

</details>

---

<br>

**Q6: What is "naive RAG" vs "advanced RAG"?**

<details>
<summary>💡 Show Answer</summary>

Naive RAG: the basic pipeline. Chunk documents → embed → store → embed query → retrieve top-K → stuff into prompt → generate. Simple, often surprisingly effective.

Advanced RAG adds optimization layers to fix specific failure modes:

- **Pre-retrieval**: query transformation (rewrite the query to be clearer), query expansion (generate multiple variant queries)
- **During retrieval**: hybrid search (semantic + keyword), metadata filtering, parent-child retrieval
- **Post-retrieval**: re-ranking (reorder retrieved chunks by relevance), context compression (summarize chunks), self-RAG (model evaluates its own retrieved context)

Start with naive RAG. Measure quality. Only add advanced techniques where you observe specific failures. Over-engineering RAG without measuring is a common mistake.

</details>

---

## Advanced

**Q7: How would you design a RAG system for a large enterprise with 10 million documents?**

<details>
<summary>💡 Show Answer</summary>

Scale requirements drive architecture choices. Key decisions:

**Indexing**: batch embedding pipeline (process in parallel, cache embeddings). Use a fast embedding model (text-embedding-3-small, not large). Store in a scalable vector DB (Pinecone, Weaviate, Qdrant — not ChromaDB).

**Multi-tenancy**: each department or user group gets its own namespace/collection. All queries must include tenant_id metadata filter — enforced at the data layer.

**Retrieval**: hybrid search (semantic + BM25) increases recall. Re-ranking with a cross-encoder improves precision. Target latency: < 200ms for retrieval, < 2s for full response.

**Caching**: semantic cache for frequent queries. Embedding cache (don't re-embed the same text twice). CDN for static responses.

**Evaluation pipeline**: automated RAGAS metrics on a representative query set. Regression testing on every pipeline change. Human evaluation on a weekly sample.

**Data freshness**: incremental updates — when a document changes, re-embed only the changed chunks. Soft deletes with TTL for outdated content.

</details>

---

<br>

**Q8: Explain the concept of faithfulness in RAG and why it's the most important metric.**

<details>
<summary>💡 Show Answer</summary>

Faithfulness measures whether the generated answer is factually consistent with the retrieved context. A faithful answer only makes claims that are supported by the retrieved chunks.

Why it's the most important: the entire value proposition of RAG is that answers are grounded in your documents. If the model generates content not in the retrieved context — even if technically correct from its training — you've lost traceability and trust. Users can't verify the answer. Compliance teams can't audit it.

A RAG system with low faithfulness is just a regular LLM with extra steps. Faithfulness is measured by asking: "Does this claim appear in the retrieved context?" Low faithfulness suggests the prompt doesn't sufficiently constrain the model to use the context, or the model's training knowledge is overriding the retrieved context.

Enforcement: add to your prompt "Answer ONLY based on the provided context. If the context doesn't contain the answer, say so." Never say "use the context" — say "ONLY use the context."

</details>

---

<br>

**Q9: What is self-RAG and corrective RAG? When would you use them?**

<details>
<summary>💡 Show Answer</summary>

Standard RAG always retrieves, regardless of whether retrieval helps. It retrieves whatever scores highest, regardless of quality.

**Self-RAG**: the LLM evaluates whether retrieval is needed for a given query (some questions can be answered from memory — "what is 2+2"). It also evaluates retrieved chunks for relevance before using them, and evaluates its own output for faithfulness. Adds critical thinking to the pipeline.

**Corrective RAG (CRAG)**: if the retrieval quality score is low (retrieved docs aren't relevant), CRAG triggers a fallback — typically a web search to supplement local retrieval. It also filters irrelevant retrieved chunks before passing to the LLM.

Use these when: you have diverse query types (some need retrieval, some don't), your retrieval quality is inconsistent across query types, or you need the system to gracefully handle queries your knowledge base can't answer.

Both add latency and complexity. Only add them after measuring that standard RAG has specific, consistent failure modes in these areas.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 When_to_Use_RAG.md](./When_to_Use_RAG.md) | When to use RAG vs fine-tuning |

⬅️ **Prev:** [08 Streaming Responses](../../08_LLM_Applications/08_Streaming_Responses/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Document Ingestion](../02_Document_Ingestion/Theory.md)
