# Build a RAG App — Step by Step

Complete walkthrough. Each step builds on the last. At the end of step 5, you have a working PDF Q&A system.

---

## Step 0: Setup

```bash
# Create project folder
mkdir rag_app && cd rag_app

# Install dependencies
pip install anthropic chromadb sentence-transformers pypdf

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"
```

Get a sample PDF to test with. Any PDF works — policy documents, manuals, articles.

---

## Step 1: Load and Chunk the PDF

Create `rag_app.py` with the indexing code:

```python
# rag_app.py
import hashlib
import sys
import anthropic
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "claude-opus-4-6"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3
MIN_SIMILARITY = 0.5
INDEX_PATH = "./rag_index"
COLLECTION_NAME = "rag_documents"

# ─────────────────────────────────────────────
# STEP 1A: Load PDF
# ─────────────────────────────────────────────

def load_pdf(path: str) -> list[dict]:
    """Extract text from each page of the PDF."""
    reader = PdfReader(path)
    documents = []
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text and text.strip():
            documents.append({
                "text": text.strip(),
                "metadata": {
                    "source": path,
                    "page": page_num,
                    "total_pages": len(reader.pages)
                }
            })
    print(f"  Loaded {len(documents)} pages from {path}")
    return documents


# ─────────────────────────────────────────────
# STEP 1B: Split into chunks
# ─────────────────────────────────────────────

def chunk_documents(documents: list[dict],
                    chunk_size: int = CHUNK_SIZE,
                    overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Split page text into overlapping chunks."""
    chunks = []
    for doc in documents:
        text = doc["text"]
        start = 0
        chunk_index = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if len(chunk_text) > 50:  # skip very short chunks
                chunks.append({
                    "text": chunk_text,
                    "metadata": {**doc["metadata"], "chunk_index": chunk_index}
                })
                chunk_index += 1
            if end >= len(text):
                break
            start = end - overlap
    print(f"  Created {len(chunks)} chunks")
    return chunks
```

**Test this step:**
```python
# At the end of rag_app.py, temporarily add:
docs = load_pdf("your_document.pdf")
chunks = chunk_documents(docs)
print(f"First chunk:\n{chunks[0]['text'][:200]}")
print(f"Metadata: {chunks[0]['metadata']}")
```

You should see the first 200 characters of your PDF and its page number. If you see garbled text, your PDF may be scanned (needs OCR) — see Troubleshooting.

---

## Step 2: Embed and Index

Add the indexing functions:

```python
# ─────────────────────────────────────────────
# STEP 2: Build ChromaDB index
# ─────────────────────────────────────────────

def get_collection():
    """Connect to (or create) the ChromaDB collection."""
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    client = chromadb.PersistentClient(path=INDEX_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn
    )


def index_chunks(chunks: list[dict], collection) -> int:
    """Embed and store chunks in ChromaDB. Returns count of new/updated chunks."""
    ids = []
    texts = []
    metadatas = []

    for chunk in chunks:
        # Deterministic ID: same content always maps to same ID
        chunk_id = hashlib.md5(
            f"{chunk['metadata']['source']}:p{chunk['metadata']['page']}:{chunk['text'][:50]}".encode()
        ).hexdigest()[:16]

        ids.append(chunk_id)
        texts.append(chunk["text"])
        metadatas.append({k: str(v) for k, v in chunk["metadata"].items()})  # ChromaDB needs strings

    collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
    return len(ids)


def run_indexing(pdf_path: str):
    """Full indexing pipeline."""
    print(f"\nIndexing {pdf_path}...")
    documents = load_pdf(pdf_path)
    chunks = chunk_documents(documents)

    collection = get_collection()
    n = index_chunks(chunks, collection)

    print(f"  Stored {n} chunks in ChromaDB")
    print(f"  Total in index: {collection.count()}")
    print("  Indexing complete.")
```

**Test this step:**
```bash
python -c "
import rag_app
rag_app.run_indexing('your_document.pdf')
"
```

The first run downloads the embedding model (~90MB) — this takes a minute. Subsequent runs are fast. You should see a `./rag_index/` directory created.

---

## Step 3: Retrieval

Add the retrieval function:

```python
# ─────────────────────────────────────────────
# STEP 3: Retrieve relevant chunks
# ─────────────────────────────────────────────

def retrieve(question: str, collection, top_k: int = TOP_K, min_sim: float = MIN_SIMILARITY) -> list[dict]:
    """Find the most relevant chunks for a question."""
    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )

    chunks = []
    for text, metadata, distance, chunk_id in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        results["ids"][0]
    ):
        similarity = 1 - distance
        if similarity >= min_sim:
            chunks.append({
                "id": chunk_id,
                "text": text,
                "metadata": metadata,
                "similarity": round(similarity, 4)
            })

    return chunks
```

**Test this step:**
```python
collection = get_collection()
chunks = retrieve("your question here", collection)
for c in chunks:
    print(f"[{c['similarity']:.3f}] p.{c['metadata']['page']}: {c['text'][:80]}")
```

You should see 1–3 chunks with similarity scores. If you see 0 results, lower `MIN_SIMILARITY` or check that you indexed the right document.

---

## Step 4: Context Assembly and Answer Generation

Add the prompt assembly and generation functions:

```python
# ─────────────────────────────────────────────
# STEP 4: Assemble prompt and generate answer
# ─────────────────────────────────────────────

def assemble_prompt(question: str, chunks: list[dict]) -> str:
    """Build a RAG prompt from question + retrieved chunks."""
    if not chunks:
        context = "No relevant information found in the document."
    else:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            page = chunk["metadata"].get("page", "?")
            source = chunk["metadata"].get("source", "document")
            context_parts.append(
                f"[Context {i} | {source}, p.{page}]\n{chunk['text']}"
            )
        context = "\n\n".join(context_parts)

    return f"""You are a helpful assistant. Answer based ONLY on the provided context.
If the answer isn't in the context, say "I don't have that information in this document."
Include [Context X] citations when referencing specific information.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def generate_answer(prompt: str) -> str:
    """Call Claude to generate the answer."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=512,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def run_query(question: str):
    """Full query pipeline: retrieve → assemble → generate → display."""
    collection = get_collection()
    chunks = retrieve(question, collection)

    prompt = assemble_prompt(question, chunks)
    answer = generate_answer(prompt)

    print(f"\nQ: {question}")
    print(f"\nA: {answer}")

    if chunks:
        print(f"\nSources ({len(chunks)}):")
        for c in chunks:
            page = c['metadata'].get('page', '?')
            source = c['metadata'].get('source', 'document')
            print(f"  [{c['similarity']:.3f}] {source}, p.{page} — {c['text'][:60]}...")
    else:
        print("\n(No relevant chunks found)")
```

---

## Step 5: Wire It All Together

Add the main entry point:

```python
# ─────────────────────────────────────────────
# STEP 5: Main entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python rag_app.py --index <pdf_file>    # Index a PDF")
        print("  python rag_app.py --query <question>    # Ask a question")
        sys.exit(1)

    mode = sys.argv[1]
    arg = " ".join(sys.argv[2:])  # join in case question has spaces

    if mode == "--index":
        run_indexing(arg)
    elif mode == "--query":
        run_query(arg)
    else:
        print(f"Unknown mode: {mode}. Use --index or --query")
        sys.exit(1)
```

---

## Step 6: Run It

```bash
# Index a PDF
python rag_app.py --index your_document.pdf

# Query it
python rag_app.py --query "What is the main topic of this document?"
python rag_app.py --query "What are the key requirements?"
python rag_app.py --query "What is the deadline mentioned?"

# Test out-of-scope question
python rag_app.py --query "What is the capital of France?"
# Should respond: "I don't have that information in this document."
```

---

## Step 7: Add Multiple Documents

To index multiple PDFs into one knowledge base, just index them one at a time:

```bash
python rag_app.py --index document1.pdf
python rag_app.py --index document2.pdf
python rag_app.py --index document3.pdf

# Now query across all three
python rag_app.py --query "Compare the policies in document1 and document2"
```

The `upsert` operation means re-indexing the same file is safe — it updates existing chunks rather than creating duplicates.

---

## Step 8: Evaluate Quality

Create a test set and run evaluation:

```bash
# Create test_questions.json
cat > test_questions.json << 'EOF'
[
  {"question": "What is the main policy?", "expected_chunk_contains": "policy text here"},
  {"question": "What are the deadlines?", "expected_chunk_contains": "date text here"}
]
EOF

# Add a quick evaluation to rag_app.py
python rag_app.py --evaluate test_questions.json
```

See `09_RAG_Systems/08_RAG_Evaluation/` for full evaluation code.

---

## Complete File (copy-paste ready)

All 5 steps in one file: see `Architecture_Blueprint.md` for component details and `Troubleshooting.md` if things go wrong.

The complete file is approximately 150 lines. Each function is independently testable. That's the right size for a working RAG system.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | Architecture blueprint |
| [📄 Project_Guide.md](./Project_Guide.md) | Project guide |
| 📄 **Step_by_Step.md** | ← you are here |
| [📄 Troubleshooting.md](./Troubleshooting.md) | Troubleshooting guide |

⬅️ **Prev:** [08 RAG Evaluation](../08_RAG_Evaluation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Agent Fundamentals](../../10_AI_Agents/01_Agent_Fundamentals/Theory.md)
