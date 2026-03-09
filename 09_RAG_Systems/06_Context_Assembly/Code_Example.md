# Context Assembly — Code Example

Complete prompt assembly — retrieved chunks + user question → formatted prompt → LLM call → answer with citations.

```python
# pip install anthropic chromadb sentence-transformers
import anthropic
import chromadb
from chromadb.utils import embedding_functions

# ─────────────────────────────────────────────
# SETUP: Connect to the indexed collection
# ─────────────────────────────────────────────

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

chroma_client = chromadb.PersistentClient(path="./rag_index")
collection = chroma_client.get_collection(
    name="company_policies",
    embedding_function=embedding_fn
)

anthropic_client = anthropic.Anthropic()

print(f"Index ready: {collection.count()} documents")


# ─────────────────────────────────────────────
# STEP 1: Retrieval function
# ─────────────────────────────────────────────

def retrieve_chunks(query: str, top_k: int = 3,
                    min_similarity: float = 0.5) -> list[dict]:
    """Retrieve relevant chunks with metadata and similarity scores."""
    results = collection.query(query_texts=[query], n_results=top_k)

    chunks = []
    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        similarity = 1 - distance
        if similarity >= min_similarity:
            chunks.append({
                "text": text,
                "metadata": metadata,
                "similarity": round(similarity, 3)
            })

    return chunks


# ─────────────────────────────────────────────
# STEP 2: Context assembly — format chunks into prompt
# ─────────────────────────────────────────────

def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks as a labeled context block."""
    if not chunks:
        return "No relevant information was found in the knowledge base."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("source", "Unknown source")
        section = chunk["metadata"].get("section", "Unknown section")
        context_parts.append(
            f"[Context {i} | Source: {source} | Section: {section}]\n{chunk['text']}"
        )

    return "\n\n".join(context_parts)


def assemble_prompt(question: str, chunks: list[dict]) -> str:
    """Build the complete RAG prompt from question + retrieved chunks."""
    context = format_context(chunks)

    return f"""You are a helpful customer support assistant. Your job is to answer questions
based ONLY on the information provided in the context below.

Rules:
- Answer ONLY using information from the provided context
- If the answer is not in the context, say "I don't have information about that in our policy documents"
- Include source citations in your answer using [Context X] references
- Be concise and direct

CONTEXT:
{context}

CUSTOMER QUESTION: {question}

ANSWER:"""


# ─────────────────────────────────────────────
# STEP 3: Complete RAG function
# Retrieval + assembly + LLM generation in one call
# ─────────────────────────────────────────────

def rag_answer(question: str, top_k: int = 3,
               verbose: bool = False) -> dict:
    """
    Full RAG pipeline: retrieve → assemble → generate.
    Returns answer + sources used.
    """
    # 1. Retrieve relevant chunks
    chunks = retrieve_chunks(question, top_k=top_k)

    if verbose:
        print(f"\n[Retrieved {len(chunks)} chunks]")
        for c in chunks:
            print(f"  [{c['similarity']:.3f}] {c['text'][:60]}...")

    # 2. Assemble the prompt
    prompt = assemble_prompt(question, chunks)

    if verbose:
        print(f"\n[Prompt ({len(prompt)} chars)]")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)

    # 3. Generate answer
    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        temperature=0,  # deterministic for factual Q&A
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.content[0].text

    # 4. Return answer + sources for citation
    sources = [
        {
            "source": c["metadata"].get("source"),
            "section": c["metadata"].get("section"),
            "similarity": c["similarity"],
            "text_preview": c["text"][:100]
        }
        for c in chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "chunks_used": len(chunks)
    }


# ─────────────────────────────────────────────
# STEP 4: Test with sample questions
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("RAG Q&A DEMO")
print("=" * 60)

test_questions = [
    "What is the return policy and how long do I have?",
    "How can I contact customer support if I have an issue?",
    "What payment methods can I update in my account?",
    "Do you offer free shipping?",
]

for question in test_questions:
    print(f"\nQ: {question}")
    result = rag_answer(question, top_k=3, verbose=False)
    print(f"A: {result['answer']}")
    print(f"\nSources used ({result['chunks_used']}):")
    for s in result["sources"]:
        print(f"  - [{s['similarity']:.3f}] {s['source']} / {s['section']}")
    print("-" * 40)


# ─────────────────────────────────────────────
# STEP 5: Test with out-of-scope question
# (model should say it doesn't know)
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("OUT-OF-SCOPE TEST")
print("=" * 60)

out_of_scope = "What are your company's environmental sustainability initiatives?"
print(f"\nQ: {out_of_scope}")
result = rag_answer(out_of_scope, top_k=3)
print(f"A: {result['answer']}")
```

**Expected output:**
```
Q: What is the return policy and how long do I have?
A: According to our policy documents [Context 1], all product returns must be
initiated within 30 days of the purchase date. To start a return, you'll need
to provide your original order number and the reason for the return [Context 2].
Please note that digital products cannot be returned once accessed [Context 3].

Sources used (3):
  - [0.823] company_policy.pdf / returns
  - [0.756] company_policy.pdf / returns
  - [0.671] company_policy.pdf / returns
```

**Running:**
```bash
# Run after embedding_indexing.py creates the index
pip install anthropic chromadb sentence-transformers
export ANTHROPIC_API_KEY="your-key"
python context_assembly.py
```

**Key design decisions in the prompt:**
- "Answer ONLY using information from the provided context" — prevents model from guessing
- "[Context X] references" instruction — enables citation in the answer
- `temperature=0` — deterministic for factual Q&A
- Graceful fallback: if no chunks retrieved, returns "I don't have information"

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [05 Retrieval Pipeline](../05_Retrieval_Pipeline/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Advanced RAG Techniques](../07_Advanced_RAG_Techniques/Theory.md)
