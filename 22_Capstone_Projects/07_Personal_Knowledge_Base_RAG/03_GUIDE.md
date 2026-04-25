# Project 07 — Personal Knowledge Base RAG: Build Guide

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

Read `01_MISSION.md` and `02_ARCHITECTURE.md` before starting.

---

## Stage 1 — Environment Setup

### Step 1: Install dependencies

```bash
pip install anthropic chromadb pdfplumber tiktoken python-dotenv openai
```

- `chromadb`: local vector database with persistence
- `pdfplumber`: reliable PDF text extraction (better than PyPDF2 for most PDFs)
- `tiktoken`: count tokens accurately before sending to an LLM
- `openai`: for the embeddings API (`text-embedding-3-small`)

### Step 2: Environment variables

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### Step 3: Collect documents

Put 5–15 documents in the `documents/` folder. Mix PDFs and `.txt` files. Good sources:
- Papers you have already read (save as PDF)
- Notes you have taken on AI concepts (copy from this repo's Theory files as .txt)
- Any technical documentation you have

At least 3 documents should share a topic so retrieval is non-trivial — there are multiple relevant sources to rank.

**Theory connection:** Read `09_RAG_Systems/01_RAG_Fundamentals/Theory.md` and `09_RAG_Systems/02_Document_Ingestion/Theory.md` before Stage 2.

---

## Stage 2 — Document Ingestion

### Step 4: Implement PDF extraction

Use `pdfplumber` to extract text from PDFs page by page. Store the page number as metadata — you will need it for citations.

<details><summary>💡 Hint</summary>

Open the file with `pdfplumber.open(file_path)` as a context manager. Iterate over `pdf.pages` with `enumerate(start=1)`. For each page call `page.extract_text()` — it may return `None` for scanned pages. Only append pages with non-empty text after stripping.

</details>

<details><summary>✅ Answer</summary>

```python
import pdfplumber

def extract_pdf(file_path: str) -> list[dict]:
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append({"page": i, "text": text})
    return pages
```

</details>

Watch for: scanned PDFs return empty text. If `page.extract_text()` returns `None` or empty for most pages, the PDF is image-based and requires OCR — skip those files for now.

### Step 5: Implement plain-text ingestion

<details><summary>💡 Hint</summary>

Open the file with `encoding="utf-8", errors="replace"` to handle non-UTF-8 files without crashing. Return a list with one dict — page 1 is the whole file.

</details>

<details><summary>✅ Answer</summary>

```python
def extract_text_file(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return [{"page": 1, "text": f.read().strip()}]
```

</details>

### Step 6: Build a unified document loader

Write `load_all_documents(documents_dir)` that iterates over all files, dispatches to the correct extractor by extension, and returns a unified list with `source_file` added to every page dict.

**Theory connection:** Read `09_RAG_Systems/02_Document_Ingestion/Theory.md` — pay attention to the metadata section. The source filename and page number you attach here travel with the chunk all the way to the final citation.

---

## Stage 3 — Chunking

### Step 7: Implement fixed-size chunking with overlap

The most common chunking approach: split text into chunks of `chunk_size` characters, with each chunk overlapping the previous by `chunk_overlap` characters.

Why overlap? The end of one chunk and the start of the next might contain a sentence broken across the boundary. Overlap ensures that boundary sentences appear in at least one complete chunk.

<details><summary>💡 Hint</summary>

Use a sliding window: `start = 0`, loop while `start < len(text)`, set `end = min(start + chunk_size, len(text))`, then advance with `start += (chunk_size - overlap)`. Guard against infinite loops if `overlap >= chunk_size`.

</details>

<details><summary>✅ Answer</summary>

```python
def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[dict]:
    if overlap >= chunk_size:
        overlap = chunk_size // 4  # safety guard
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"text": chunk, "char_start": start, "char_end": end})
        start += (chunk_size - overlap)
    return chunks
```

</details>

### Step 8: Token-aware chunking (extension)

Character count is an approximation. LLMs charge by tokens, and context windows are measured in tokens, not characters. After your character-based version works, add a token-counting check using `tiktoken`:

```python
import tiktoken

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    enc = tiktoken.get_encoding(model)
    return len(enc.encode(text))
```

Use this to verify your chunks are actually within your target token count.

**Theory connection:** Read `09_RAG_Systems/03_Chunking_Strategies/Theory.md` — it covers fixed-size, sentence-based, and semantic chunking.

### Step 9: Assign metadata to each chunk

Each chunk needs metadata that travels with it into ChromaDB:

```python
{
    "source_file": "attention_mechanism.pdf",
    "page": 2,
    "chunk_index": 4,
    "char_start": 1600,
    "char_end": 2000,
}
```

<details><summary>💡 Hint</summary>

Write a `create_chunks_for_page(page_dict)` function. Call `chunk_text(page["text"])` to get raw chunks, then use `enumerate` to add `chunk_index` and merge the page metadata (source_file, page) into each chunk dict.

</details>

<details><summary>✅ Answer</summary>

```python
def create_chunks_for_page(page: dict) -> list[dict]:
    raw_chunks = chunk_text(page["text"])
    result = []
    for i, chunk in enumerate(raw_chunks):
        result.append({
            "text": chunk["text"],
            "source_file": page["source_file"],
            "page": page["page"],
            "chunk_index": i,
            "char_start": chunk["char_start"],
            "char_end": chunk["char_end"],
        })
    return result
```

</details>

---

## Stage 4 — Embedding and Indexing

### Step 10: Initialize ChromaDB

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)
```

The `PersistentClient` saves to disk automatically. Your index survives restarts.

### Step 11: Embed and add chunks to ChromaDB

<details><summary>💡 Hint</summary>

Call `openai_client.embeddings.create(model="text-embedding-3-small", input=texts)` and return `[item.embedding for item in response.data]`. Then call `collection.add(ids=..., documents=..., embeddings=..., metadatas=...)`. Build IDs as `f"{source_file}_p{page}_c{chunk_index}"`.

</details>

<details><summary>✅ Answer</summary>

```python
def embed_texts(texts: list[str]) -> list[list[float]]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]
```

Embed in batches of 50 and add to ChromaDB:
```python
for i in range(0, len(all_chunks), 50):
    batch = all_chunks[i:i+50]
    embeddings = embed_texts([c["text"] for c in batch])
    collection.add(
        ids=[f"{c['source_file']}_p{c['page']}_c{c['chunk_index']}" for c in batch],
        documents=[c["text"] for c in batch],
        embeddings=embeddings,
        metadatas=[{k: v for k, v in c.items() if k != "text"} for c in batch],
    )
```

</details>

**Important:** ChromaDB IDs must be unique. If you re-run ingestion, you will get duplicate ID errors. Either clear the collection first or check if a chunk already exists before adding.

**Theory connection:** Read `09_RAG_Systems/04_Embedding_and_Indexing/Theory.md`.

### Step 12: Skip already-indexed files

```python
def is_file_indexed(collection, source_file: str) -> bool:
    results = collection.get(where={"source_file": source_file}, limit=1)
    return len(results["ids"]) > 0
```

If a file is already indexed, skip it. This makes re-running safe and fast.

---

## Stage 5 — Retrieval Pipeline

### Step 13: Query ChromaDB

<details><summary>💡 Hint</summary>

Embed the query string with `embed_texts([query])[0]`. Pass it to `collection.query(query_embeddings=[...], n_results=top_k, include=["documents", "metadatas", "distances"])`. The results dict has `documents[0]`, `metadatas[0]`, and `distances[0]` as lists.

</details>

<details><summary>✅ Answer</summary>

```python
def retrieve(query: str, collection, top_k: int = 5) -> list[dict]:
    query_embedding = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "text": text,
            "score": 1 - (dist / 2),  # cosine distance [0,2] → similarity [0,1]
            **meta,
        })
    return chunks
```

</details>

### Step 14: Convert distances to similarity scores

ChromaDB with cosine space returns distances in `[0, 2]` where 0 = identical. Convert to similarity score `[0, 1]` for display:

```python
similarity = 1 - (distance / 2)
```

**Theory connection:** Read `09_RAG_Systems/05_Retrieval_Pipeline/Theory.md`.

---

## Stage 6 — Context Assembly and Generation

### Step 15: Assemble the context window

<details><summary>💡 Hint</summary>

Enumerate your chunks starting at 1. For each, format a block: `[SOURCE N] File: {source_file} | Page: {page} | Chunk: {chunk_index}\n{text}`. Join all blocks with double newlines. Then trim: while `count_tokens(assembled) > MAX_CONTEXT_TOKENS`, pop the last block.

</details>

<details><summary>✅ Answer</summary>

```python
def assemble_context(chunks: list[dict], max_tokens: int = 8000) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        header = f"[SOURCE {i}] File: {chunk['source_file']} | Page: {chunk['page']} | Chunk: {chunk['chunk_index']}"
        parts.append(f"{header}\n{chunk['text']}")
    assembled = "\n\n".join(parts)
    while count_tokens(assembled) > max_tokens and parts:
        parts.pop()
        assembled = "\n\n".join(parts)
    return assembled
```

</details>

**Theory connection:** Read `09_RAG_Systems/06_Context_Assembly/Theory.md` — it covers prompt templates, source ordering, and staying within the context window.

### Step 16: Count tokens before sending

```python
total_tokens = count_tokens(system_prompt + context + question)
if total_tokens > 180_000:   # Claude's context window is 200K
    # trim chunks from the end until you fit
    pass
```

In practice, your 5 chunks will be much smaller than 180K. This matters at scale.

### Step 17: Generate with Claude

<details><summary>💡 Hint</summary>

Call `anthropic_client.messages.create(model=..., max_tokens=1024, system=..., messages=[{"role": "user", "content": user_message}])`. Build `user_message` as `f"Sources:\n{context}\n\nQuestion: {question}\n\nAnswer (with citations):"`. Return `response.content[0].text`.

</details>

<details><summary>✅ Answer</summary>

```python
def generate_answer(question: str, context: str) -> str:
    system = """You are a helpful assistant answering questions from a personal knowledge base.

Use ONLY the information in the provided sources to answer.
If the answer is not in the sources, say so clearly.
When you use information from a source, cite it as [SOURCE N]."""

    user_message = f"""Sources:
{context}

Question: {question}

Answer (with citations):"""

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text
```

</details>

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

Log these evaluations.

**Theory connection:** Read `09_RAG_Systems/08_RAG_Evaluation/Theory.md`.

### Step 20: Test failure modes

Deliberately test these:
- A question whose answer is not in any document (should say "I don't know")
- A question that is in the documents but phrased very differently (tests semantic retrieval)
- A very broad question (tests whether Claude stays grounded in sources)

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
| [01_MISSION.md](./01_MISSION.md) | Context and goals |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| 03_GUIDE.md | you are here |
| [src/starter.py](./src/starter.py) | Runnable starter code |
| [04_RECAP.md](./04_RECAP.md) | What you built + next steps |

⬅️ **Prev:** [06 — Semantic Search Engine](../06_Semantic_Search_Engine/01_MISSION.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 — Multi-Tool Research Agent](../08_Multi_Tool_Research_Agent/01_MISSION.md)
