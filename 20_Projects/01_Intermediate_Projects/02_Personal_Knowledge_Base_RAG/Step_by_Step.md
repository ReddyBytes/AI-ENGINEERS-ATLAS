# Project 2 — Personal Knowledge Base RAG: Step-by-Step Guide

## Overview

| Stage | What you build | Time estimate |
|---|---|---|
| 1 | Environment, documents, ChromaDB setup | 30 min |
| 2 | Document ingestion (PDF + text) | 45 min |
| 3 | Chunking with overlap | 30 min |
| 4 | Embedding and indexing into ChromaDB | 30 min |
| 5 | Retrieval pipeline | 30 min |
| 6 | Context assembly + Claude generation | 45 min |
| 7 | Citations and evaluation | 30 min |

Total: approximately 4 hours

---

## Stage 1 — Environment Setup

### Step 1: Install dependencies

```bash
pip install anthropic chromadb pdfplumber tiktoken python-dotenv openai
```

- `chromadb`: local vector database with persistence
- `pdfplumber`: reliable PDF text extraction (better than PyPDF2 for most PDFs)
- `tiktoken`: count tokens accurately before sending to an LLM
- `openai`: for the embeddings API (Anthropic delegates embeddings to Voyage)

### Step 2: Environment variables

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...      # for embeddings only
```

### Step 3: Collect documents

Put 5–15 documents in the `documents/` folder. Mix PDFs and `.txt` files. Good sources:
- Papers you have already read (save as PDF)
- Notes you have taken on AI concepts (copy from this repo's Theory files as .txt)
- Any technical documentation you have

At least 3 documents should share a topic (so retrieval is non-trivial — there are multiple relevant sources to rank).

**Theory connection:** Read `09_RAG_Systems/01_RAG_Fundamentals/Theory.md` and `09_RAG_Systems/02_Document_Ingestion/Theory.md` before Stage 2.

---

## Stage 2 — Document Ingestion

### Step 4: Implement PDF extraction

Use `pdfplumber` to extract text from PDFs page by page. Store the page number as metadata — you will need it for citations.

```python
import pdfplumber

def extract_pdf(file_path: str) -> list[dict]:
    """Returns list of {"page": int, "text": str} dicts."""
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append({"page": i, "text": text.strip()})
    return pages
```

Watch for: scanned PDFs return empty text. If `page.extract_text()` returns `None` or empty for most pages, the PDF is image-based and requires OCR (outside scope of this project — just skip those files).

### Step 5: Implement plain-text ingestion

Simpler — read the whole file, treat it as one "page 1":

```python
def extract_text_file(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return [{"page": 1, "text": f.read().strip()}]
```

### Step 6: Build a unified document loader

Write `load_all_documents(documents_dir)` that iterates over all files, dispatches to the correct extractor by extension, and returns a unified list.

**Theory connection:** Read `09_RAG_Systems/02_Document_Ingestion/Theory.md` — pay attention to the section on metadata. The source filename and page number you attach here travel with the chunk all the way to the final citation.

---

## Stage 3 — Chunking

### Step 7: Implement fixed-size chunking with overlap

The most common chunking approach: split text into chunks of `chunk_size` characters, with each chunk overlapping the previous by `chunk_overlap` characters.

Why overlap? The end of one chunk and the start of the next might contain a sentence broken across the boundary. Overlap ensures that boundary sentences appear in at least one complete chunk.

```python
def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text string.
        chunk_size: Target size of each chunk in characters.
        overlap: Number of characters to repeat between consecutive chunks.

    Returns:
        List of chunk strings.
    """
    # Your implementation here
```

### Step 8: Token-aware chunking (extension)

Character count is an approximation. LLMs charge by tokens, and context windows are measured in tokens, not characters. After your character-based version works, add a token-counting variant using `tiktoken`:

```python
import tiktoken

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    enc = tiktoken.get_encoding(model)
    return len(enc.encode(text))
```

Use this to verify your chunks are actually within your target token count.

**Theory connection:** Read `09_RAG_Systems/03_Chunking_Strategies/Theory.md` — it covers fixed-size, sentence-based, and semantic chunking. Implement fixed-size for now; the comparison guide explains when to upgrade.

### Step 9: Assign metadata to each chunk

Each chunk needs metadata that travels with it into ChromaDB:

```python
{
    "source_file": "attention_mechanism.pdf",
    "page": 2,
    "chunk_index": 4,      # 4th chunk in this document
    "char_start": 1600,    # character offset in original page text
    "char_end": 2000,
}
```

This metadata is what enables citations. Store it now, use it later.

---

## Stage 4 — Embedding and Indexing

### Step 10: Initialize ChromaDB

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}  # use cosine distance
)
```

The `PersistentClient` saves to disk automatically. Your index survives restarts.

### Step 11: Embed and add chunks to ChromaDB

ChromaDB can call an embedding function itself, or you can pass pre-computed embeddings. Using pre-computed embeddings gives you more control:

```python
from openai import OpenAI
embedding_client = OpenAI()

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns list of vectors."""
    response = embedding_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]
```

Add chunks to the collection:
```python
collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=[c["text"] for c in chunks],
    embeddings=embed_texts([c["text"] for c in chunks]),
    metadatas=[c["metadata"] for c in chunks],
)
```

**Important:** ChromaDB IDs must be unique. If you re-run ingestion, you will get duplicate ID errors. Either clear the collection first (`collection.delete(...)`) or check if a chunk already exists.

**Theory connection:** Read `09_RAG_Systems/04_Embedding_and_Indexing/Theory.md`.

### Step 12: Skip already-indexed files

Add a check: if a file's chunks are already in ChromaDB (use the source filename as a filter), skip it. This makes re-running safe and fast.

```python
existing = collection.get(where={"source_file": filename})
if existing["ids"]:
    print(f"  Skipping {filename} — already indexed.")
    continue
```

---

## Stage 5 — Retrieval Pipeline

### Step 13: Query ChromaDB

```python
def retrieve(query: str, collection, top_k: int = 5) -> list[dict]:
    """
    Embed query, search ChromaDB, return top_k chunks with metadata.
    """
    query_embedding = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    # results["documents"][0] is a list of chunk texts
    # results["metadatas"][0] is a list of metadata dicts
    # results["distances"][0] is a list of distances (lower = more similar)
    return results
```

### Step 14: Convert distances to similarity scores

ChromaDB with cosine space returns distances in `[0, 2]` where 0 = identical. Convert to similarity score `[0, 1]` for display:

```python
similarity = 1 - (distance / 2)
```

**Theory connection:** Read `09_RAG_Systems/05_Retrieval_Pipeline/Theory.md`.

---

## Stage 6 — Context Assembly and Generation

### Step 15: Assemble the context window

Take your retrieved chunks and format them as a context block for Claude. Number each source for citation:

```python
def assemble_context(retrieved_chunks: list[dict]) -> tuple[str, list[dict]]:
    """
    Format retrieved chunks as a context string with source markers.

    Returns:
        context_str: The formatted context to insert into the prompt.
        sources: List of source metadata for citation display.
    """
```

Example output format:
```
[SOURCE 1] File: attention_mechanism.txt | Page: 1 | Chunk: 3
The attention mechanism allows the model to focus on relevant parts of the input...

[SOURCE 2] File: transformers_overview.pdf | Page: 2 | Chunk: 7
In the original Transformer architecture, attention is computed three ways...
```

**Theory connection:** Read `09_RAG_Systems/06_Context_Assembly/Theory.md` — it covers prompt templates, source ordering, and staying within the context window.

### Step 16: Count tokens before sending

Before calling Claude, count the tokens in your assembled prompt:

```python
total_tokens = count_tokens(system_prompt + context + question)
if total_tokens > 180_000:   # Claude's context window is 200K
    # trim chunks from the end until you fit
    pass
```

In practice, your 5 chunks will be much smaller than 180K. This matters at scale.

### Step 17: Generate with Claude

```python
import anthropic

claude_client = anthropic.Anthropic()

def generate_answer(question: str, context: str) -> str:
    system = """You are a helpful assistant answering questions from a personal knowledge base.

Use ONLY the information in the provided sources to answer.
If the answer is not in the sources, say so clearly.
When you use information from a source, cite it as [SOURCE N]."""

    user_message = f"""Sources:
{context}

Question: {question}

Answer (with citations):"""

    response = claude_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text
```

---

## Stage 7 — Citations and Evaluation

### Step 18: Display citations

After the answer, print the source list:
```
Sources used:
  [1] attention_mechanism.txt — Page 1, Chunk 3 (chars 800–1200)
  [2] transformers_overview.pdf — Page 2, Chunk 7 (chars 2100–2500)
```

### Step 19: Evaluate faithfulness manually

For 5 test questions where you know the answer, check:
1. Did the system retrieve chunks that actually contain the answer?
2. Did Claude's response accurately reflect what the chunks said?
3. Did it hallucinate facts not in the retrieved context?

Log these evaluations. You will formalize this in Project 5.

**Theory connection:** Read `09_RAG_Systems/08_RAG_Evaluation/Theory.md`.

### Step 20: Test failure modes

Deliberately test these:
- A question whose answer is not in any document (should say "I don't know")
- A question that is in the documents but phrased very differently (tests semantic retrieval)
- A very broad question (tests whether Claude stays grounded in sources)

---

## Extension Challenges

1. **Sentence-based chunking**: Split on sentences (`.`, `!`, `?`) rather than fixed character counts. Does retrieval quality improve?

2. **Metadata filtering**: If you ask "What did paper X say about Y?", pre-filter to chunks from paper X before running similarity search. ChromaDB supports this with `where={"source_file": "paper_x.pdf"}`.

3. **Multi-query retrieval**: For complex questions, generate 3 rephrased versions of the query, retrieve for each, then deduplicate and merge the result sets.

4. **Re-ranking with Claude**: After getting top-10 chunks, ask Claude to score each chunk's relevance to the question on a 1–5 scale. Use those scores instead of embedding similarity.

---

## Checklist Before Moving On

- [ ] Both PDF and .txt ingestion work
- [ ] Chunks have complete metadata (file, page, index, char offsets)
- [ ] ChromaDB persists across restarts
- [ ] Re-running ingestion does not create duplicate chunks
- [ ] Retrieval returns relevant results for test questions
- [ ] Claude's answers include [SOURCE N] citations
- [ ] System says "I don't know" when answer is not in documents
- [ ] You have tested at least 5 questions manually

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | What you'll build |
| Step_by_Step.md | ← you are here |
| [Starter_Code.md](./Starter_Code.md) | Code with TODOs |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [01 — Semantic Search Engine](../01_Semantic_Search_Engine/Project_Guide.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 — Multi-Tool Research Agent](../03_Multi_Tool_Research_Agent/Project_Guide.md)
