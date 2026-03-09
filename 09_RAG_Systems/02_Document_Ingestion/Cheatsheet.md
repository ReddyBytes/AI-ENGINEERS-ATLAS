# Document Ingestion — Cheatsheet

**One-liner:** Document ingestion loads raw source material from any format into standardized Document objects (text + metadata) — the first mandatory step in every RAG pipeline.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Document** | The standard unit in LangChain: `{page_content: str, metadata: dict}` |
| **Document loader** | A class that loads a specific format and returns `List[Document]` |
| **page_content** | The raw extracted text of the document/chunk |
| **metadata** | Dict of contextual info: source, page, date, author, etc. |
| **OCR** | Optical Character Recognition — extracting text from images/scanned PDFs |
| **Text extraction** | Converting binary formats (PDF, DOCX) to plain text |
| **Boilerplate** | Repeated content like headers, footers, legal disclaimers — usually noise |

---

## Common LangChain Loaders

| Format | Loader | Install |
|--------|--------|---------|
| PDF | `PyPDFLoader` | `pip install pypdf` |
| PDF (advanced) | `PDFPlumberLoader` | `pip install pdfplumber` |
| Word | `Docx2txtLoader` | `pip install docx2txt` |
| CSV | `CSVLoader` | (included) |
| JSON | `JSONLoader` | (included) |
| Web page | `WebBaseLoader` | `pip install requests beautifulsoup4` |
| YouTube transcript | `YoutubeLoader` | `pip install youtube-transcript-api` |
| Notion | `NotionDirectoryLoader` | (included) |
| GitHub | `GitLoader` | (included) |

---

## Quick Code Pattern

```python
from langchain.document_loaders import PyPDFLoader

docs = PyPDFLoader("file.pdf").load()

for doc in docs:
    print(doc.metadata["page"])      # page number
    print(doc.page_content[:200])    # first 200 chars
```

---

## When to Use / Not Use

| Use document ingestion when... | Don't when... |
|-------------------------------|--------------|
| Building a RAG pipeline | Data is already in string format |
| Need to load multiple file types | Working with only in-memory text |
| Need structured metadata | Single small document |

---

## Golden Rules

1. **Always check page_content isn't empty** — scanned PDFs return empty strings without OCR.
2. **Preserve page numbers** — they're critical for citations ("see page 5 of handbook").
3. **Store source path in metadata** — you'll need it to tell users where the answer came from.
4. **Clean text before chunking** — remove excess whitespace, decode encoding issues.
5. **For large corpora: batch load** — load in parallel rather than sequentially.
6. **Test with your hardest documents first** — tables, multi-column PDFs, and scanned docs are the problem cases.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Supported_Formats.md](./Supported_Formats.md) | Supported document formats |

⬅️ **Prev:** [01 RAG Fundamentals](../01_RAG_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Chunking Strategies](../03_Chunking_Strategies/Theory.md)
