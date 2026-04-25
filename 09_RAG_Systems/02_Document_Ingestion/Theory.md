# Document Ingestion — Theory

Setting up a new library takes a week before a single book is on the shelf — first, you get all the books in the door. Document ingestion is that first step for RAG: before you can chunk, embed, or search your knowledge base, you need to load all source material and clean it up.

👉 This is why we need **Document Ingestion** — RAG can only search what you've loaded. Garbage in, garbage out.

---

## What Document Ingestion Does

Takes raw source material in any format and converts it to a standard structure:

```python
Document(
    page_content="The refund policy states that...",
    metadata={
        "source": "company_policy.pdf",
        "page": 3,
        "date": "2024-01-15"
    }
)
```

Every document becomes `page_content` (string) plus `metadata` (source, page, date, etc.).

```mermaid
flowchart LR
    A[Raw Source] --> B[Parser\nPDF / DOCX / CSV / HTML]
    B --> C[Raw Text]
    C --> D[Cleaner\nstrip boilerplate, fix encoding]
    D --> E[Document Object\npage_content + metadata]
    E --> F[(Next step:\nChunking)]
```

---

## The Main Source Types

```mermaid
flowchart TD
    A[Source Types] --> B[Local Files\nPDF, DOCX, CSV, TXT]
    A --> C[Web Pages\nHTML scraping]
    A --> D[Databases\nSQL, MongoDB]
    A --> E[APIs\nSlack, Notion, Confluence]
    B --> F[Document Objects]
    C --> F
    D --> F
    E --> F
```

---

## Key Challenges

**Scanned PDFs** — Standard PDF loaders return empty strings for scanned PDFs (images of text). Fix: use OCR (`pytesseract` or AWS Textract) before loading.

**Tables** — Tables in PDFs/Word lose their structure when extracted as plain text. Fix: use specialized loaders (`pdfplumber`, `camelot`) that preserve table structure, or convert to markdown.

**Long documents with irrelevant sections** — Headers, footers, boilerplate, and table of contents add noise. Fix: pre-process to strip common patterns. Store page numbers in metadata.

---

## LangChain Document Loaders

```python
from langchain.document_loaders import PyPDFLoader, CSVLoader, WebBaseLoader

pdf_docs = PyPDFLoader("report.pdf").load()
csv_docs = CSVLoader("data.csv").load()
web_docs = WebBaseLoader("https://example.com/docs").load()
```

Each returns a list of `Document` objects with `page_content` and `metadata`.

---

## Document Metadata

Metadata lets you:
- **Filter** searches ("only documents from Q4 2024")
- **Display** sources in answers ("Source: Policy Manual, page 3")
- **Debug** retrieval ("why did this chunk get returned?")

```python
metadata = {
    "source": "company_handbook.pdf",
    "page": 5,
    "section": "Benefits",
    "date_created": "2024-01-15",
    "author": "HR Department",
    "document_type": "policy"
}
```

---

✅ **What you just learned:** Document ingestion loads raw source material from any format (PDFs, web pages, databases) into standardized Document objects with text content and metadata — the first step of every RAG pipeline.

🔨 **Build this now:** Use PyPDFLoader to load any PDF. Print the first 3 documents' page_content (first 200 chars each) and metadata. Notice how each page becomes a separate document.

➡️ **Next step:** Chunking Strategies → `09_RAG_Systems/03_Chunking_Strategies/Theory.md`

---

## 🛠️ Practice Project

Apply what you just learned → **[I2: Personal Knowledge Base (RAG)](../../22_Capstone_Projects/07_Personal_Knowledge_Base_RAG/03_GUIDE.md)**
> This project uses: loading PDF and text files, extracting raw text, cleaning it before chunking

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Supported_Formats.md](./Supported_Formats.md) | Supported document formats |

⬅️ **Prev:** [01 RAG Fundamentals](../01_RAG_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Chunking Strategies](../03_Chunking_Strategies/Theory.md)
