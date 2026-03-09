# Chunking Strategies — Comparison

Choose the right chunking strategy for your document type and use case.

---

## Strategy Comparison Table

| Strategy | Pros | Cons | Best For | Recommended Chunk Size |
|----------|------|------|---------|----------------------|
| **Fixed-size (character)** | Very simple, fast | Splits mid-sentence, mid-word | Quick prototypes only | 500 chars |
| **Recursive text splitter** | Respects paragraph/sentence boundaries, configurable, fast | May still split concepts across chunks | General-purpose knowledge bases | 400–600 chars, 10% overlap |
| **Sentence-based** | Semantically clean, no mid-sentence cuts | Variable chunk size, harder to control token count | Articles, news, reports | 3–5 sentences per chunk |
| **Token-based** | Precise token control (important for context limits) | Splits mid-word boundary | When token budget is tight | 128–256 tokens |
| **Markdown/header-based** | Respects document structure, sections stay intact | Only works for structured docs | Documentation, wikis, reports with headers | Section-by-section |
| **Semantic chunking** | Topic-aware splits, highly relevant chunks | Slow, requires embedding model upfront, variable size | Research papers, encyclopedia articles | Variable (topic-based) |
| **Parent-child** | Precise retrieval + full context | Complex implementation, 2x storage | Production RAG, technical docs | Child: 200 chars, Parent: 1000 chars |

---

## When to Use Which

### Use Fixed-Size When:
- You're prototyping and want to start fast
- Your documents are short and fairly uniform
- Simplicity matters more than quality

### Use Recursive Text Splitter When:
- General-purpose knowledge base
- Mixed document types
- You want a reliable default that works well
- Starting a new RAG project (start here, optimize later)

### Use Sentence-Based When:
- Documents are well-written with clear sentence structure
- You're chunking news articles, blog posts, or reports
- You want clean splits without mid-sentence cuts

### Use Token-Based When:
- You're using a model with a tight context limit (e.g., 256 tokens)
- You need precise control over chunk size for cost calculations
- You're pre-computing budget requirements

### Use Header-Based When:
- Documents have clear section structure (`.md`, technical docs, HTML)
- Users will ask questions about specific sections
- You want section titles preserved as context in chunks

### Use Semantic Chunking When:
- Documents have distinct topic changes (research papers, encyclopedias)
- You have the compute budget to embed during chunking
- Retrieval quality is critical and worth extra complexity

### Use Parent-Child When:
- You need both precise retrieval AND rich context
- Your documents have natural hierarchical structure
- You're building a production system and need the best quality

---

## Sample Chunk Output Comparison

Same text, different strategies — with this input:
```
Machine learning is a method of data analysis that automates analytical model building.
It is based on the idea that systems can learn from data. They can identify patterns and make decisions.
Neural networks are a specific type of ML model. They are inspired by the human brain.
```

**Fixed-size (100 chars):**
```
Chunk 1: "Machine learning is a method of data analysis that automates analytical model b"
Chunk 2: "uilding.\nIt is based on the idea that systems can learn from data. They can iden"
```
Issue: splits mid-word "building"

**Recursive text splitter (100 chars):**
```
Chunk 1: "Machine learning is a method of data analysis that automates analytical model building."
Chunk 2: "It is based on the idea that systems can learn from data. They can identify patterns..."
```
Clean sentence-level splits.

**Sentence-based:**
```
Chunk 1: "Machine learning is a method of data analysis that automates analytical model building. It is based on the idea that systems can learn from data."
Chunk 2: "They can identify patterns and make decisions. Neural networks are a specific type of ML model. They are inspired by the human brain."
```
Grouped by N sentences.

---

## The Production Decision

For most production RAG systems, the progression is:

1. **Start:** `RecursiveCharacterTextSplitter`, 500 chars, 50 overlap
2. **Measure:** build a test set, check recall@5
3. **If recall is low on short factual questions:** reduce chunk size to 250–300 chars
4. **If answers lack context:** try parent-child chunking
5. **If document structure is clear:** switch to header-based + recursive
6. **If still struggling:** try semantic chunking for that document type

Don't over-optimize before measuring. Start simple and improve based on data.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Comparison.md** | ← you are here |

⬅️ **Prev:** [02 Document Ingestion](../02_Document_Ingestion/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Embedding and Indexing](../04_Embedding_and_Indexing/Theory.md)
