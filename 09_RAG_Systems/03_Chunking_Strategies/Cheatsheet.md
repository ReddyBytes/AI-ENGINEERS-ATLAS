# Chunking Strategies — Cheatsheet

**One-liner:** Chunking splits large documents into smaller, focused passages that can be embedded and retrieved precisely — the chunk size and split method are the biggest factors in RAG retrieval quality.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Chunk** | A small text passage (typically 256–512 tokens) ready for embedding |
| **Chunk size** | Maximum number of tokens/characters per chunk |
| **Chunk overlap** | Number of tokens shared between adjacent chunks to avoid boundary cuts |
| **Splitter** | The class/function that performs the chunking |
| **Recursive splitting** | Tries to split on paragraphs first, then sentences, then words |
| **Semantic chunking** | Uses embedding similarity to split at topic boundaries |
| **Parent-child chunking** | Small chunks for retrieval + larger parent returned for context |
| **Token vs character count** | Tokens are ~0.75 words; 1 token ≈ 4 characters in English |

---

## Strategy Comparison

| Strategy | Pros | Cons | Best For |
|----------|------|------|---------|
| Fixed-size (character) | Simple, fast | Splits mid-sentence | Quick prototypes |
| Recursive text splitter | Respects paragraph/sentence boundaries | Still can split concepts | General-purpose (default choice) |
| Sentence-based | Semantically clean splits | Variable chunk size | Articles, reports |
| Semantic chunking | Topic-aware splits | Slow, needs embedding model | Long documents with distinct sections |
| Parent-child | Best of both (precise + context) | Complex to implement | Production RAG systems |

---

## Chunk Size Recommendations

| Document Type | Chunk Size | Overlap |
|--------------|-----------|---------|
| General knowledge base | 512 tokens | 50 tokens |
| Technical documentation | 400 tokens | 40 tokens |
| Legal/compliance docs | 300 tokens | 50 tokens (high overlap for citations) |
| Conversational QA | 200 tokens | 20 tokens |
| Long-form articles | 600 tokens | 60 tokens |

---

## RecursiveCharacterTextSplitter Quick Reference

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # max characters per chunk (not tokens!)
    chunk_overlap=50,     # overlap between chunks
    separators=["\n\n", "\n", " ", ""],  # split priority
)

chunks = splitter.split_text(your_text)
docs = splitter.split_documents(your_document_list)
```

Note: `chunk_size` is in characters, not tokens. ~500 chars ≈ ~125 tokens (rough estimate).

---

## Golden Rules

1. **Start with RecursiveCharacterTextSplitter** — it's the best general-purpose option.
2. **Chunk size 400–600 characters is a good default** for most knowledge base use cases.
3. **Always add overlap** — 10–20% of chunk size prevents information loss at boundaries.
4. **Test your chunks manually** — print 5–10 chunks and ask: "Would this chunk answer a user question alone?"
5. **Smaller is usually better** — it's easier to retrieve 3 precise small chunks than 1 vague large chunk.
6. **Preserve metadata through chunking** — each chunk should inherit the source document's metadata.
7. **Evaluate chunk quality** — retrieval recall is the proxy metric. Build test cases and measure.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Comparison.md](./Comparison.md) | Chunking strategies comparison |

⬅️ **Prev:** [02 Document Ingestion](../02_Document_Ingestion/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Embedding and Indexing](../04_Embedding_and_Indexing/Theory.md)
