# Build a RAG App — Troubleshooting

Common problems, causes, and fixes. Each problem is organized by the stage where it appears.

---

## Indexing Problems

### Problem: PDF loads but extracts garbled text

**Symptom**: `load_pdf()` returns text that looks like: `"Ã¼Ã³Ã©..."` or random symbols.

**Cause**: The PDF is a scanned image, not a text PDF. `pypdf` can only extract text from text-based PDFs.

**Fix**: Use OCR-based extraction.
```bash
pip install pytesseract pillow pdf2image
# Also install Tesseract: brew install tesseract (Mac) or apt install tesseract-ocr (Linux)
```

```python
from pdf2image import convert_from_path
import pytesseract

def load_scanned_pdf(path: str) -> list[dict]:
    images = convert_from_path(path, dpi=300)
    documents = []
    for page_num, image in enumerate(images, 1):
        text = pytesseract.image_to_string(image)
        if text.strip():
            documents.append({
                "text": text.strip(),
                "metadata": {"source": path, "page": page_num, "total_pages": len(images)}
            })
    return documents
```

---

### Problem: `load_pdf()` returns empty list

**Symptom**: "Loaded 0 pages from document.pdf"

**Causes and fixes:**

1. **File path is wrong**: check that the file exists with `os.path.exists(path)`
2. **PDF is password-protected**: use `PdfReader(path, password="your_password")`
3. **PDF only contains images with no text layer**: see the OCR fix above

---

### Problem: ChromaDB raises `InvalidCollectionException`

**Symptom**: `chromadb.errors.InvalidCollectionException: Collection not found`

**Cause**: You're calling `get_collection()` on a collection that doesn't exist yet.

**Fix**: Use `get_or_create_collection()` instead of `get_collection()`:
```python
# Wrong:
collection = client.get_collection(name="rag_documents", ...)

# Right:
collection = client.get_or_create_collection(name="rag_documents", ...)
```

---

### Problem: "Embedding model download is slow"

**Symptom**: First run takes 2–5 minutes.

**Cause**: `sentence-transformers` downloads the embedding model (~90MB) on first use.

**This is normal**. Subsequent runs use the cached model. If you want to pre-download:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")  # download now
print("Model downloaded and cached")
```

---

## Retrieval Problems

### Problem: `retrieve()` returns 0 results

**Symptom**: `chunks = retrieve("my question", collection)` returns an empty list.

**Cause options:**
1. **Minimum similarity threshold is too high**
2. **Wrong collection name**: you indexed into one collection, querying another
3. **Index is empty**: the indexing step failed silently

**Diagnosis:**
```python
# Check how many documents are in the index
collection = get_collection()
print(f"Index contains: {collection.count()} chunks")

# Try without a minimum similarity threshold
chunks = retrieve("your question", collection, min_sim=0.0)
print(f"Top result similarity: {chunks[0]['similarity'] if chunks else 'empty'}")
```

**Fix if threshold too high**: lower `MIN_SIMILARITY` from 0.5 to 0.3 for initial testing.

---

### Problem: Retrieved chunks are from the wrong topic

**Symptom**: asking about "return policy" returns chunks about "shipping policy".

**Cause**: The query embedding is landing near the wrong chunks in vector space. The question phrasing doesn't match the document vocabulary well.

**Fixes:**
1. Try rephrasing the question: "What is the product return and refund policy?"
2. Add more query variation by increasing `TOP_K` from 3 to 5
3. Check the document: does it actually contain the answer? Run `retrieve` with `min_sim=0.0` and inspect all results

---

### Problem: Similarity scores are all low (< 0.4)

**Symptom**: Best similarity score is 0.35 even for a question you know is in the document.

**Cause options:**
1. **Chunks are too large**: a 1000-token chunk dilutes the signal of any single sentence
2. **Embedding model mismatch**: you indexed with one model and are querying with another
3. **Document preprocessing issues**: special characters, headers/footers adding noise

**Fix for chunk size**: re-index with smaller chunks:
```python
chunks = chunk_documents(documents, chunk_size=300, overlap=30)
```

**Fix for model mismatch**: delete the index and re-index from scratch:
```bash
rm -rf ./rag_index
python rag_app.py --index your_document.pdf
```

---

## Generation Problems

### Problem: Answers contain information not in the document

**Symptom**: The answer mentions facts that aren't in any retrieved chunk (hallucination).

**Cause**: The LLM is using its training knowledge instead of staying grounded to the context.

**Fixes:**
1. Strengthen the grounding instruction:
```python
system = """You are a precise document assistant. You MUST answer ONLY using the
information in the provided CONTEXT. If the exact information is not in the CONTEXT,
you MUST say "This information is not available in the provided document."
NEVER use your general knowledge. NEVER guess. NEVER infer beyond what is explicitly stated."""
```

2. Set `temperature=0` (if not already set)
3. Use `anthropic_client.messages.create(system=system, ...)` to move grounding instruction to system message

---

### Problem: Answer says "I don't have that information" for questions that ARE in the document

**Symptom**: The document clearly contains the answer, but the system says it doesn't have it.

**Cause**: Retrieval is failing — the relevant chunk isn't being returned.

**Diagnosis:**
```python
# Check what's actually being retrieved
chunks = retrieve("your question", collection, min_sim=0.0, top_k=10)
for c in chunks:
    print(f"[{c['similarity']:.3f}] p.{c['metadata']['page']}: {c['text'][:100]}")
```

If the correct chunk appears but with low similarity, the retrieval system is finding it but filtering it out. Lower `MIN_SIMILARITY`. If it doesn't appear at all, the chunk might not be indexed — check the index.

---

### Problem: Answers are very short and generic

**Symptom**: The answer is just "Yes, returns are allowed." without any detail.

**Cause**: The retrieved chunks don't contain enough detail, or `max_tokens` is too low.

**Fixes:**
1. Increase `max_tokens` from 256 to 512 or 1024
2. Add a length instruction to the prompt: "Provide a complete and detailed answer."
3. Check chunk size: if chunks are 100 characters each, there's not much for the LLM to work with — increase `CHUNK_SIZE`

---

### Problem: `anthropic.AuthenticationError`

**Symptom**: `anthropic.AuthenticationError: Error code: 401`

**Cause**: API key is not set or is invalid.

**Fix:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify it's set:
echo $ANTHROPIC_API_KEY

# Or set it in Python directly (not recommended for production):
client = anthropic.Anthropic(api_key="sk-ant-...")
```

---

## Performance Problems

### Problem: Indexing is slow for large documents

**Symptom**: Indexing a 100-page PDF takes more than 2 minutes.

**Cause**: Embedding is done one chunk at a time, or the embedding model is slow on CPU.

**Fix — batch embedding:**
```python
def index_chunks_batched(chunks: list[dict], collection, batch_size: int = 50):
    """Index in batches for better throughput."""
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        ids = [generate_id(c) for c in batch]
        texts = [c["text"] for c in batch]
        metadatas = [{k: str(v) for k, v in c["metadata"].items()} for c in batch]
        collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
        print(f"  Indexed {min(i + batch_size, len(chunks))}/{len(chunks)} chunks")
```

---

### Problem: Querying is slow (> 2 seconds per question)

**Symptom**: Each question takes 2–5 seconds to answer.

**Breakdown of typical latency:**
- Embedding the question: ~50ms
- ChromaDB ANN search: ~10ms
- Anthropic API call: 1–3 seconds (network + generation)

**The API call dominates**. Not much you can do without:
1. Using a faster model (reduce `max_tokens`, consider `claude-haiku-3-5` for speed)
2. Using streaming (`anthropic_client.messages.stream()`) so the first tokens appear quickly
3. Caching: if the same question is asked repeatedly, cache the answer

---

## Quick Diagnostic Checklist

When something is wrong, run through this list:

```
[ ] Is the index non-empty? collection.count() > 0
[ ] Is the ANTHROPIC_API_KEY set? echo $ANTHROPIC_API_KEY
[ ] Is the PDF text-based (not scanned)? Check first chunk text
[ ] Are similarity scores > 0.5 for in-scope questions? Test with min_sim=0.0
[ ] Is the embedding model the same for indexing and querying? Check EMBEDDING_MODEL constant
[ ] Is the collection name the same in indexer and retriever? Check COLLECTION_NAME
[ ] Are metadatas stored as strings? ChromaDB requires string metadata values
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | Architecture blueprint |
| [📄 Project_Guide.md](./Project_Guide.md) | Project guide |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Step-by-step instructions |
| 📄 **Troubleshooting.md** | ← you are here |

⬅️ **Prev:** [08 RAG Evaluation](../08_RAG_Evaluation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Agent Fundamentals](../../10_AI_Agents/01_Agent_Fundamentals/Theory.md)
