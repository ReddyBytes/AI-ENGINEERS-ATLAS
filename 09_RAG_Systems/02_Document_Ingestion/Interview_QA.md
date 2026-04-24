# Document Ingestion — Interview Q&A

## Beginner

**Q1: What is document ingestion in a RAG pipeline and why is it the first step?**

<details>
<summary>💡 Show Answer</summary>

Document ingestion is the process of loading raw source files (PDFs, web pages, databases, Word documents) and converting them into a standard format that the rest of the RAG pipeline can process. The standard output is a list of Document objects, each with `page_content` (the extracted text) and `metadata` (source info like filename, page number, date).

It's the first step because RAG can only retrieve what has been indexed, and indexing requires clean text. Without ingestion, you can't chunk, embed, or store anything. The quality of ingestion determines the quality of everything downstream — if text extraction is poor (garbled PDFs, missing tables), retrieval will be poor no matter how good your embedding model or vector database is.

</details>

---

<br>

**Q2: What are the most common document types in RAG systems and what challenges does each present?**

<details>
<summary>💡 Show Answer</summary>

PDFs: most common. Regular PDFs extract cleanly with libraries like PyPDF or pdfplumber. Scanned PDFs (images of text) return empty strings without OCR preprocessing. Multi-column PDFs often have reading order issues. Tables lose structure.

Word documents (DOCX): extract well with python-docx. Complex formatting (text boxes, SmartArt) can be lost. Track changes and comments need special handling.

Web pages: HTML requires stripping navigation, ads, and boilerplate while keeping the article content. BeautifulSoup or dedicated scrapers handle this. Dynamic JavaScript pages need Selenium or Playwright.

CSV/Excel: each row becomes a document. Need to decide whether to keep headers in each row's text or store column names in metadata.

Plain text/Markdown: easiest. No extraction issues — just read the file.

</details>

---

<br>

**Q3: What is metadata and why is it important to store alongside document text?**

<details>
<summary>💡 Show Answer</summary>

Metadata is structured information about a document that isn't part of the main text: source file path, page number, section title, creation date, author, document type, department, etc.

It's important because: (1) Source citation — when the RAG system answers a question, users need to know where the information came from. "See Company Policy Manual, page 3, Benefits section." (2) Metadata filtering — you can scope searches to specific sources. "Only search Q4 2024 reports." (3) Debugging — when retrieval returns the wrong results, metadata tells you exactly which chunk was returned and where it came from. (4) Access control — metadata like `department` or `security_level` lets you enforce what data different users can access.

Always store at minimum: source filename/URL, page number (for PDFs), and date. Add domain-specific fields based on your use case.

</details>

---

## Intermediate

**Q4: How do you handle scanned PDFs in a RAG pipeline?**

<details>
<summary>💡 Show Answer</summary>

Scanned PDFs are images of text — standard text extraction libraries return empty strings or garbled output. You need Optical Character Recognition (OCR).

Process: (1) Detect if a PDF is scanned — check if the extracted text is very short or empty despite the PDF having content. (2) If scanned, convert pages to images using `pdf2image`. (3) Run OCR on each image using `pytesseract` (free, local) or a cloud service like AWS Textract, Google Document AI, or Azure Form Recognizer (paid, higher accuracy). (4) Post-process: OCR output often has line-break artifacts, spacing issues, and character recognition errors. Clean with regex and spell correction.

For production: cloud OCR services dramatically outperform local Tesseract, especially on complex layouts, handwriting, and non-English text. Budget accordingly for your document volume.

</details>

---

<br>

**Q5: What document metadata strategy would you use for a legal document RAG system?**

<details>
<summary>💡 Show Answer</summary>

Legal documents have unique characteristics: numbered sections, cross-references ("see Section 4.2"), specific clause types, parties involved, dates.

Metadata strategy:
```python
metadata = {
    "source": "contract_acme_2024.pdf",
    "document_type": "contract",
    "parties": ["Acme Corp", "TechVendor LLC"],
    "effective_date": "2024-03-01",
    "expiry_date": "2025-03-01",
    "section": "4.2 Indemnification",
    "page": 12,
    "clause_type": "indemnification"
}
```

Use `clause_type` for filtering ("find all indemnification clauses"). Use `parties` for filtering ("find all contracts with Acme Corp"). Use `effective_date` range filtering for "what were our terms in Q1 2024?"

Preserve section numbering in metadata and in the chunk text itself — users will reference specific sections, and citations need to point to them.

</details>

---

<br>

**Q6: How do you handle a knowledge base that updates frequently — new documents added daily?**

<details>
<summary>💡 Show Answer</summary>

Design for incremental updates, not full re-indexing:

(1) Track document fingerprints — store a hash of each document's content. When loading, compare the hash to what's already indexed. Only re-embed documents that have changed.

(2) Immutable IDs — assign stable IDs to each document chunk based on source + position. Use upsert in the vector DB so updating a document replaces its existing vectors.

(3) Deletion handling — when a document is removed or superseded, delete its vectors from the vector DB. Set a `valid_until` metadata field and filter expired documents from retrieval.

(4) Versioning — instead of replacing chunks, version them. Store `version: 2` alongside `version: 1`. Default retrieval shows only latest versions.

(5) Processing queue — don't load documents synchronously on upload. Use a job queue (Celery, AWS SQS) to process in the background. The user's document is available for search within minutes of upload.

</details>

---

## Advanced

**Q7: How would you build a robust document ingestion pipeline that handles diverse file types at scale?**

<details>
<summary>💡 Show Answer</summary>

Architecture: input queue → file type detection → format-specific loader → text cleaner → metadata enricher → output queue → chunker.

Key design decisions:

**Type detection**: use file extension AND mime type check. A renamed .pdf that's actually a .docx needs to be handled correctly.

**Fault isolation**: process each document independently. One malformed PDF shouldn't fail the entire batch. Use a dead-letter queue for failed documents.

**Parallel processing**: document loading is I/O-bound (reading files) and compute-bound (OCR). Use a worker pool with multiple processes. For cloud-hosted files, async I/O to overlap network and processing.

**Idempotency**: if a document is submitted twice (upload duplication), the pipeline should detect the duplicate and skip or update. Hash-based deduplication at ingestion time.

**Monitoring**: track metrics per document type: average extraction time, failure rate, OCR confidence score. High failure rates for a specific file type signal a loader that needs improvement.

</details>

---

<br>

**Q8: What are the challenges of extracting structured data (tables, forms) for RAG?**

<details>
<summary>💡 Show Answer</summary>

Standard text extraction destroys table structure. A 5-column, 20-row table becomes 100 lines of unsorted text. Queries about specific cells in the table will fail because the embedding won't represent the tabular relationship.

Approaches:

(1) **Keep as markdown**: use `pdfplumber` or `camelot` to detect and extract tables, then convert to markdown format. Markdown tables preserve structure and are readable by LLMs.

(2) **Convert to natural language**: describe the table content as sentences. "The Q1 2024 revenue was $1.2M, up 15% from Q4 2023." Better for lookup queries, loses the aggregate structure.

(3) **Separate table index**: store tables in a structured database alongside the vector index. When a query seems table-like, route to the structured query path instead of semantic search.

(4) **Multi-modal models**: use vision models (GPT-4o Vision, Claude) to process PDFs as images and directly understand table structure. Expensive but most accurate.

For financial reports, contracts with schedules, or anything table-heavy: invest in proper table extraction. It's a common production failure mode.

</details>

---

<br>

**Q9: How does document ingestion change when dealing with real-time or streaming data sources (e.g., Slack, email)?**

<details>
<summary>💡 Show Answer</summary>

Batch ingestion loads files that already exist. Streaming ingestion handles data that arrives continuously.

Key differences:

**No clear document boundaries**: a Slack conversation isn't a document — it's a continuous stream. Define what constitutes a "document": a day's messages in a channel? A thread? A conversation window of N minutes?

**Volume and velocity**: a busy Slack channel generates thousands of messages per hour. Don't embed every message in real-time — too expensive. Batch processing with a short delay (5–15 minutes) is usually fine.

**Deduplication**: the same message might arrive multiple times (retries, reconnects). Add deduplication based on message ID.

**Expiry**: older messages become less relevant. Auto-delete or archive embeddings older than N days/months based on your use case.

**Webhooks vs. polling**: webhooks push data to you when events happen (real-time). Polling checks for new data on a schedule (simpler, higher latency). For low-latency RAG on real-time data, use webhooks.

Implementation: use an event-driven architecture (Kafka, AWS Kinesis, or a simple Redis queue). Messages arrive → transform to Document → add to embedding queue → embed in batches → upsert to vector DB.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Supported_Formats.md](./Supported_Formats.md) | Supported document formats |

⬅️ **Prev:** [01 RAG Fundamentals](../01_RAG_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Chunking Strategies](../03_Chunking_Strategies/Theory.md)
