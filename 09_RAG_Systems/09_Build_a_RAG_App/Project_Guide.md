# Build a RAG App — Project Guide

**Project:** PDF Q&A system. Upload one or more PDF documents, ask questions in plain English, get answers with source citations.

This is a complete, runnable project that ties together every concept from this section: document ingestion, chunking, embedding, indexing, retrieval, context assembly, and evaluation.

---

## What You're Building

A command-line RAG application that:
1. Ingests a PDF document and indexes it in ChromaDB
2. Takes natural language questions from the user
3. Retrieves the most relevant chunks from the indexed document
4. Generates a cited answer using Claude
5. Shows which pages/sections the answer came from

```
$ python rag_app.py --index my_document.pdf
Indexed 42 chunks from my_document.pdf

$ python rag_app.py --query "What is the return policy?"
Q: What is the return policy?
A: According to the document [Context 1, p.3], all product returns must be
   initiated within 30 days of purchase. Digital products cannot be returned
   once accessed [Context 2, p.3].

Sources:
  [0.87] my_document.pdf, p.3 — "All product returns must be initiated within 30 days..."
  [0.75] my_document.pdf, p.3 — "Refunds are processed within 5-7 business days..."
```

---

## Prerequisites

| Requirement | Details |
|---|---|
| Python | 3.10 or later |
| Anthropic API key | `export ANTHROPIC_API_KEY="your-key"` |
| Disk space | ~200MB for models |
| PDF document | Any PDF you want to query |

---

## Dependencies

```bash
pip install anthropic chromadb sentence-transformers pypdf
```

| Package | Used for |
|---|---|
| `anthropic` | LLM calls (Claude) |
| `chromadb` | Vector database |
| `sentence-transformers` | Embedding model (local, free) |
| `pypdf` | PDF text extraction |

---

## Project Structure

```
rag_app/
├── rag_app.py          ← main script (index + query modes)
├── indexer.py          ← PDF loading, chunking, embedding, storing
├── retriever.py        ← query embedding, search, filtering
├── generator.py        ← context assembly, LLM call, citation
├── evaluator.py        ← test set, hit rate, faithfulness scoring
├── rag_index/          ← ChromaDB persistent storage (created at runtime)
└── test_questions.json ← your evaluation test set
```

For this project guide: all code is in a single `rag_app.py` file. See `Step_by_Step.md` for the split-file production version.

---

## Configuration Constants

```python
# rag_app.py — Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # fast, good quality, free
LLM_MODEL = "claude-opus-4-6"          # generation model
CHUNK_SIZE = 500                        # characters per chunk
CHUNK_OVERLAP = 50                      # character overlap between chunks
TOP_K = 3                               # chunks to retrieve per query
MIN_SIMILARITY = 0.5                    # minimum similarity threshold
INDEX_PATH = "./rag_index"              # ChromaDB storage path
COLLECTION_NAME = "rag_documents"       # ChromaDB collection name
```

These defaults work well for most PDF documents. See `Troubleshooting.md` if you need to tune them.

---

## Phases

The project has three phases:

**Phase 1: Indexing** (run once per document)
- Load PDF → extract text → split into chunks → embed → store in ChromaDB

**Phase 2: Querying** (run for each question)
- Embed question → retrieve top-K chunks → assemble prompt → generate answer → display with citations

**Phase 3: Evaluation** (optional, run to measure quality)
- Create test set → run retrieval evaluation (hit rate, MRR) → run generation evaluation (faithfulness)

Each phase is independent. You index once, then query as many times as you want. Evaluation is a separate step you run to measure and improve quality.

---

## Learning Goals

After completing this project you will be able to:

1. Extract and clean text from a PDF document
2. Split text into overlapping chunks with metadata
3. Embed chunks using a local sentence-transformer model
4. Store and retrieve vectors from ChromaDB with metadata
5. Assemble a RAG prompt with grounding instructions and source labels
6. Parse cited answers from Claude
7. Measure hit rate and faithfulness on a test set

---

## Extensions (After the Basics Work)

| Extension | Difficulty | Impact |
|---|---|---|
| Add BM25 hybrid search | Medium | Better exact-term matching |
| Add a cross-encoder reranker | Medium | Better answer quality |
| Support multiple PDFs in one index | Easy | More useful knowledge base |
| Add a web interface (Gradio/Streamlit) | Medium | Much better UX |
| Add streaming responses | Easy | Faster perceived response |
| Production: use Pinecone instead of ChromaDB | Medium | Scalable cloud index |

Start with the basics. Add extensions once the core system works and you've run evaluation.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Architecture_Blueprint.md](./Architecture_Blueprint.md) | Architecture blueprint |
| 📄 **Project_Guide.md** | ← you are here |
| [📄 Step_by_Step.md](./Step_by_Step.md) | Step-by-step instructions |
| [📄 Troubleshooting.md](./Troubleshooting.md) | Troubleshooting guide |

⬅️ **Prev:** [08 RAG Evaluation](../08_RAG_Evaluation/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Agent Fundamentals](../../10_AI_Agents/01_Agent_Fundamentals/Theory.md)
