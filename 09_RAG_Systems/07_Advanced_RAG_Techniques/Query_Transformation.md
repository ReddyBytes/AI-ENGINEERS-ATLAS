# Query Transformation

Query transformation modifies or expands the user's question before it's used for retrieval. The goal: produce a query that will match the relevant document chunks more effectively than the original question.

---

## Why Transform Queries

Users type short, conversational, or ambiguous questions. Documents contain detailed, formal, specific information. These two writing styles produce embeddings that live in different parts of the vector space — even when they're about the same topic.

```
User asks:    "return policy?"          (3 tokens, informal)
Document:     "All product returns must be initiated within 30 days of purchase..."
              (full policy text, formal)
```

A better query for retrieval would be more similar in style to the document: "What is the product return policy including the time window and refund process?"

Query transformation bridges this gap using an LLM — before retrieval, not after.

---

## Technique 1: Query Rewriting

The simplest transformation. Use an LLM to rewrite the user's question into a longer, more specific, more retrieval-friendly form.

```python
import anthropic

client = anthropic.Anthropic()

def rewrite_query(original_query: str) -> str:
    """Rewrite a short/vague query into a more detailed retrieval query."""
    prompt = f"""You are helping improve document search. Rewrite the following user question
into a more detailed, specific search query that will better match relevant documents.

Keep the same intent. Make it longer and more descriptive. Return only the rewritten query.

Original question: {original_query}

Rewritten search query:"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


# Example
original = "return policy?"
rewritten = rewrite_query(original)
print(f"Original:  {original}")
print(f"Rewritten: {rewritten}")
# → "What is the product return policy, including the time window for initiating
#    returns, the refund process, and any restrictions on returnable items?"
```

When to use: short queries (< 5 words), vague questions, when users type keyword searches instead of natural language questions.

---

## Technique 2: Multi-Query Retrieval

Generate multiple variations of the same question. Each variation retrieves a slightly different set of chunks. Merge and deduplicate.

```python
def generate_query_variants(question: str, n: int = 3) -> list[str]:
    """Generate n alternative phrasings of the question."""
    prompt = f"""Generate {n} different ways to phrase this question for document search.
Each phrasing should approach the same question from a slightly different angle.
Return one question per line, no numbers or bullets.

Original: {question}"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    variants = [line.strip() for line in response.content[0].text.strip().split("\n") if line.strip()]
    return variants[:n]


def multi_query_retrieve(question: str, retrieve_fn, top_k: int = 5) -> list[dict]:
    """Retrieve using the original + N variant queries, deduplicate by ID."""
    variants = generate_query_variants(question, n=3)
    all_queries = [question] + variants

    seen_ids = set()
    all_chunks = []

    for q in all_queries:
        for chunk in retrieve_fn(q, top_k=top_k):
            if chunk["id"] not in seen_ids:
                all_chunks.append(chunk)
                seen_ids.add(chunk["id"])

    # Sort by similarity (best match from any variant comes first)
    return sorted(all_chunks, key=lambda c: c["similarity"], reverse=True)


# Example output
question = "How do I get a refund?"
# Original query → finds return policy chunks
# Variant 1: "What is the refund process and timeline?" → finds refund processing chunks
# Variant 2: "What steps do I follow to return a product?" → finds return steps chunks
# Variant 3: "How long does it take to receive a refund?" → finds timeline chunks
# Result: more comprehensive coverage of related chunks
```

When to use: complex questions with multiple components, when users phrase the same question in very different ways, when single-query retrieval consistently misses related but useful information.

---

## Technique 3: HyDE (Hypothetical Document Embeddings)

Instead of embedding the question, generate a hypothetical answer document and embed that.

The insight: a question embedding and a document embedding are stylistically different. A hypothetical answer, written in the same style as real documents, will be much closer in embedding space to the actual relevant documents.

```python
def hyde_retrieve(question: str, retrieve_fn, top_k: int = 5) -> list[dict]:
    """
    1. Generate a hypothetical answer document
    2. Embed the hypothetical document
    3. Use its embedding for retrieval
    """
    # Step 1: Generate hypothetical answer
    hyde_prompt = f"""Write a brief, factual answer to the following question as if it were
extracted from an official policy document. Write in the style of formal documentation.
Do not say you are generating a hypothetical — just write the answer directly.
Keep it to 2-3 sentences.

Question: {question}

Answer:"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": hyde_prompt}]
    )
    hypothetical_doc = response.content[0].text.strip()

    print(f"Hypothetical document: {hypothetical_doc}")

    # Step 2 & 3: Retrieve using the hypothetical document text as the query
    # The embedding model encodes this richer text instead of the short question
    return retrieve_fn(hypothetical_doc, top_k=top_k)


# Example
question = "What is the return window for electronics?"
# Hypothetical doc generated: "Electronics purchased online may be returned within
#   30 days of the purchase date. Items must be in original condition with all
#   packaging included. Digital products are non-returnable once accessed."
# This embeds much closer to the actual policy chunk than the original question.
```

When to use: abstract or conceptual questions, knowledge bases with dense factual documents, when questions are in a different writing style than the documents.

When NOT to use: the hypothetical document might contain hallucinated specific details (wrong numbers, wrong names) that could mislead retrieval. Use with care when your knowledge base is very specific (legal documents, medical references).

---

## Technique 4: Step-Back Prompting

For multi-step or complex questions, ask the LLM to identify the underlying general concept, then retrieve on that.

```python
def step_back_retrieve(question: str, retrieve_fn, top_k: int = 5) -> list[dict]:
    """Extract the underlying concept, retrieve on it, then retrieve on original too."""
    prompt = f"""What is the general concept or principle behind this question?
Return a single more general question that captures the underlying topic.

Specific question: {question}

General concept question:"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=80,
        messages=[{"role": "user", "content": prompt}]
    )
    general_question = response.content[0].text.strip()

    # Retrieve on both the original and the general concept
    specific_chunks = retrieve_fn(question, top_k=top_k)
    general_chunks = retrieve_fn(general_question, top_k=top_k)

    # Merge, deduplicate
    seen_ids = set()
    merged = []
    for chunk in specific_chunks + general_chunks:
        if chunk["id"] not in seen_ids:
            merged.append(chunk)
            seen_ids.add(chunk["id"])

    return merged


# Example:
# Specific: "Can I return a laptop I bought during a sale event?"
# General:  "What are the return policy rules and exceptions?"
# Both queries retrieve relevant chunks → better coverage
```

---

## Choosing a Transformation Strategy

```
Is the query < 5 words?
  → Query rewriting

Does the question have multiple aspects or components?
  → Multi-query

Is the question abstract and the knowledge base factual/specific?
  → HyDE

Is the question very specific but part of a larger topic?
  → Step-back prompting

Is the query fine and just needs better keyword matching?
  → Hybrid search (not a query transformation, but often the right fix)
```

---

## Cost Consideration

Every query transformation technique adds an LLM call (or multiple) before retrieval. This adds latency and cost.

| Technique | Extra LLM calls | Extra retrieval calls | Typical added latency |
|---|---|---|---|
| Query rewriting | 1 | 0 | +500ms |
| Multi-query (3 variants) | 1 | 3x | +600ms |
| HyDE | 1 | 0 | +500ms |
| Step-back | 1 | 1 extra | +600ms |

Recommendation: apply transformations selectively. Use a cheap fast model (not Claude Opus) for the transformation call itself. Measure whether the quality improvement justifies the latency cost for your use case.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Hybrid_Search.md](./Hybrid_Search.md) | Hybrid search techniques |
| 📄 **Query_Transformation.md** | ← you are here |
| [📄 Reranking.md](./Reranking.md) | Reranking approaches |

⬅️ **Prev:** [06 Context Assembly](../06_Context_Assembly/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 RAG Evaluation](../08_RAG_Evaluation/Theory.md)
