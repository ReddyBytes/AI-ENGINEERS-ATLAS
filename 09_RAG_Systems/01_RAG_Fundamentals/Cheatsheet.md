# RAG Fundamentals — Cheatsheet

**One-liner:** RAG (Retrieval-Augmented Generation) makes an LLM look up relevant documents first, then generate an answer grounded in those documents — giving accurate, citable, up-to-date responses from any knowledge base.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **RAG** | Retrieval-Augmented Generation — retrieve then generate |
| **Retrieval** | Finding relevant document chunks from a vector database |
| **Generation** | LLM producing an answer based on retrieved context |
| **Chunk** | A small passage of text (256–512 tokens) indexed for retrieval |
| **Context** | The retrieved chunks passed to the LLM in the prompt |
| **Grounded answer** | A response generated from retrieved text, not from model memory |
| **Hallucination** | Model inventing facts not in its knowledge or the retrieved context |
| **Source citation** | Returning the source document alongside the answer |
| **Naive RAG** | Basic retrieve-then-generate with no advanced optimization |
| **Advanced RAG** | RAG with reranking, hybrid search, or query transformation |

---

## RAG Pipeline Summary

```
Documents → chunk → embed → store in vector DB     [one-time indexing]

User question → embed → search → retrieve top-K     [per query]
  → build prompt (question + chunks)
  → LLM generates grounded answer
```

---

## RAG vs Fine-tuning Quick Decision

| Situation | Use |
|-----------|-----|
| Knowledge is in documents | RAG |
| Knowledge updates frequently | RAG |
| Need source citations | RAG |
| Need specific tone/style | Fine-tuning |
| Need specific task behavior | Fine-tuning |
| Low budget | RAG (much cheaper) |

---

## When to Use / Not Use

| Use RAG when... | Don't use RAG when... |
|----------------|----------------------|
| You have private/proprietary data | Questions don't need specific knowledge |
| Knowledge changes (e.g., weekly updates) | You need to change the model's behavior |
| You need audit trails / citations | Corpus is too small (< 50 docs — just put in context) |
| Answers need to be factually grounded | The task is creative (writing, brainstorming) |

---

## Golden Rules

1. **Retrieval quality is everything** — if you retrieve the wrong chunks, no amount of prompt engineering fixes the answer.
2. **Chunk size matters** — 256–512 tokens is a good starting point. Too small = no context. Too large = diluted embeddings.
3. **Cite your sources** — always return the source chunk with the answer so users can verify.
4. **Don't trust the model to answer from its own knowledge** — explicitly instruct it to use only the provided context.
5. **Evaluate regularly** — build a test set of (question, expected_answer) pairs. Measure recall and faithfulness.
6. **Start simple** — naive RAG often works surprisingly well. Add complexity (hybrid search, reranking) only when you measure a problem.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 When_to_Use_RAG.md](./When_to_Use_RAG.md) | When to use RAG vs fine-tuning |

⬅️ **Prev:** [08 Streaming Responses](../../08_LLM_Applications/08_Streaming_Responses/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Document Ingestion](../02_Document_Ingestion/Theory.md)
