# Context Assembly — Cheatsheet

**One-liner:** Format your retrieved chunks into a structured prompt — with source labels, ordering rules, and grounding instructions — so the LLM can answer accurately and cite its sources.

---

## Key Terms

| Term | What it means |
|---|---|
| **Context assembly** | The step that formats retrieved chunks into a prompt the LLM can use |
| **Grounding instruction** | Tells the LLM to answer ONLY from the provided context |
| **Source citation** | A `[Context 1]` or `[Source: X]` label that lets the LLM reference specific chunks |
| **Context window** | The maximum tokens the model can process in one call |
| **Lost in the middle** | LLMs pay more attention to the start and end of context than the middle |
| **Fallback** | What to return when no relevant chunks were found |
| **Chunk ordering** | Which chunk goes first in the prompt — matters for relevance |

---

## The Basic Prompt Template

```
You are a helpful assistant. Answer based ONLY on the context below.
If the answer isn't in the context, say "I don't have that information."

CONTEXT:
[Source: handbook.pdf, Section: Returns]
All product returns must be initiated within 30 days of purchase.

[Source: handbook.pdf, Section: Returns]
Refunds are processed within 5-7 business days after receipt.

QUESTION: {user_question}

ANSWER (cite your sources):
```

---

## Chunk Ordering Rule

LLMs remember the start and end better than the middle ("lost in the middle" effect):

```
Most relevant chunk → FIRST
Second most relevant → LAST
Third relevant → MIDDLE
```

Sort by similarity score descending — the top chunk goes first.

---

## Context Window Budget

```
Total tokens = system_prompt + (num_chunks × avg_chunk_tokens) + question + max_answer

Example:
  system_prompt:    ~200 tokens
  3 chunks × 400:  1,200 tokens
  question:         ~50 tokens
  max_answer:       512 tokens
  ─────────────────────────────
  Total:           ~1,962 tokens  ← well within any modern model
```

Rule: keep to **3–5 chunks × 400–600 tokens each**. If you're hitting limits, reduce K or chunk size.

---

## When to Use / Not Use Context Assembly Formatting

| Use structured formatting when... | Simpler formatting is fine when... |
|---|---|
| You need source citations in the answer | Single-chunk retrieval |
| Multiple chunks from different sources | All chunks are from the same document |
| Users need to verify answers | Internal/prototype use |
| High-stakes domain (legal, medical, policy) | Exploratory Q&A |

---

## Handling No Good Match

```python
if not chunks or max(c["similarity"] for c in chunks) < 0.5:
    context = "No relevant information found in the knowledge base."
    # The LLM will use the grounding instruction to say it doesn't know
else:
    context = format_chunks(chunks)
```

Always include the fallback path — never pass an empty context silently.

---

## The `assemble_prompt()` Pattern

```python
def assemble_prompt(question: str, chunks: list[dict]) -> str:
    if not chunks:
        context = "No relevant information found."
    else:
        context = "\n\n".join([
            f"[Context {i} | Source: {c['metadata']['source']} | Section: {c['metadata']['section']}]\n{c['text']}"
            for i, c in enumerate(chunks, 1)
        ])

    return f"""You are a helpful assistant. Answer based ONLY on the context below.
If the answer isn't in the context, say you don't have that information.
Include [Context X] citations in your answer.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
```

---

## Golden Rules

1. **Context before question** — the model reads context as background; seeing it first improves accuracy.
2. **Explicit grounding instruction** — "Answer ONLY from context" prevents the model using training memory.
3. **Label every chunk** — `[Context 1]`, `[Source: ...]` enables citation and debugging.
4. **Most relevant chunk first** — never bury the best result in the middle.
5. **`temperature=0` for factual Q&A** — deterministic answers for policy/support use cases.
6. **Always handle the empty case** — if no chunks retrieved, say so explicitly rather than passing empty context.
7. **Ask for citations** — "Include [Context X] references" in your instruction produces better-cited answers.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [05 Retrieval Pipeline](../05_Retrieval_Pipeline/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Advanced RAG Techniques](../07_Advanced_RAG_Techniques/Theory.md)
