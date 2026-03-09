# Supported Document Formats

A reference guide for loading different document types in RAG pipelines.

---

## Format Reference Table

| Format | LangChain Loader | pip install | Gotchas |
|--------|-----------------|-------------|---------|
| **PDF (text)** | `PyPDFLoader` | `pypdf` | Scanned PDFs return empty content |
| **PDF (advanced)** | `PDFPlumberLoader` | `pdfplumber` | Better table extraction, slower |
| **PDF (OCR)** | `UnstructuredPDFLoader` | `unstructured[pdf]` | Handles scanned PDFs, needs tesseract |
| **Word (.docx)** | `Docx2txtLoader` | `docx2txt` | Loses text boxes, footnotes |
| **Word (rich)** | `UnstructuredWordDocumentLoader` | `unstructured` | Preserves more structure |
| **CSV** | `CSVLoader` | (included) | Each row = 1 Document |
| **Excel (.xlsx)** | `UnstructuredExcelLoader` | `unstructured openpyxl` | Multiple sheets need separate handling |
| **Plain text** | `TextLoader` | (included) | Simplest case, no issues |
| **Markdown** | `UnstructuredMarkdownLoader` | `unstructured` | Headers preserved in structure |
| **HTML** | `UnstructuredHTMLLoader` | `unstructured` | Strips tags, keeps text |
| **Web page** | `WebBaseLoader` | `beautifulsoup4` | Dynamic JS pages need Playwright |
| **JSON** | `JSONLoader` | `jq` | Needs jq path to specify which field |
| **YAML** | `TextLoader` | (included) | Treat as text |
| **PowerPoint** | `UnstructuredPowerPointLoader` | `unstructured python-pptx` | Slide text only, no speaker notes by default |
| **Email (.eml)** | `UnstructuredEmailLoader` | `unstructured` | Handles attachments separately |
| **YouTube** | `YoutubeLoader` | `youtube-transcript-api` | Needs video ID, not all videos have transcripts |
| **Notion** | `NotionDirectoryLoader` | (included) | Needs exported Notion pages |
| **Confluence** | `ConfluenceLoader` | `atlassian-python-api` | Needs API token |
| **Slack** | `SlackDirectoryLoader` | (included) | Needs exported Slack workspace |
| **GitHub** | `GitLoader` | `gitpython` | Indexes code files |
| **SQL Database** | `SQLDatabaseLoader` | `sqlalchemy` | Each row = 1 Document |
| **MongoDB** | `MongodbLoader` | `pymongo` | Each document = 1 Document |

---

## Gotchas by Format

### PDFs

**Scanned PDFs (image-based)**
- Problem: text extraction returns empty strings
- Detection: `if len(doc.page_content.strip()) < 50: # likely scanned`
- Fix: use `UnstructuredPDFLoader` with OCR mode, or preprocess with `pdf2image` + `pytesseract`

**Multi-column PDFs**
- Problem: text reads across columns horizontally instead of top-to-bottom in each column
- Fix: use `pdfplumber` which has better layout analysis

**Tables in PDFs**
- Problem: tables become jumbled text without column structure
- Fix: use `pdfplumber` which can extract tables as structured data

**Password-protected PDFs**
- Problem: extraction fails with encryption error
- Fix: decrypt first with `pikepdf` before loading

---

### Web Pages

**Dynamic JavaScript (React, Vue, Angular)**
- Problem: `WebBaseLoader` gets the HTML shell, not the rendered content
- Fix: use `SeleniumURLLoader` or `PlaywrightURLLoader` to render JS first

**Paywalled content**
- Problem: loader gets the paywall page, not the article
- Fix: no automated solution — requires authentication credentials

**Rate limiting**
- Problem: scraping too fast triggers rate limits or IP bans
- Fix: add delays between requests, use rotating proxies, respect `robots.txt`

---

### CSV / Excel

**Large spreadsheets**
- Problem: each row becomes a Document with all column headers repeated — huge context overhead
- Fix: select only relevant columns, or combine multiple rows into one Document

**Excel with multiple sheets**
- Problem: `UnstructuredExcelLoader` may only load the active sheet
- Fix: specify sheet name or use `openpyxl` directly to iterate sheets

**CSV with embedded newlines**
- Problem: rows with newlines in field values split incorrectly
- Fix: ensure CSV is properly quoted; use `pandas` to read then convert to Documents

---

### Word Documents

**Complex formatting**
- Problem: text boxes, SmartArt, embedded objects not extracted
- Fix: accept limitation or convert to PDF first then load

**Track changes**
- Problem: deleted and added text both appear
- Fix: accept final version of document before ingestion

---

## Recommended Loader by Use Case

| Use Case | Recommended Loader |
|----------|--------------------|
| Simple internal PDFs | `PyPDFLoader` |
| PDFs with tables/forms | `PDFPlumberLoader` |
| Scanned documents | `UnstructuredPDFLoader` (with OCR) |
| Company documentation (web) | `WebBaseLoader` |
| Public documentation sites | `SitemapLoader` |
| Internal knowledge base | `NotionDirectoryLoader` or `ConfluenceLoader` |
| Support tickets/CRM | Direct DB loader or `CSVLoader` |
| Code documentation | `GitLoader` + `TextLoader` |
| FAQ / structured data | `CSVLoader` or manual `Document` creation |

---

## Metadata Best Practices

Always add these fields:

```python
metadata = {
    "source": "full file path or URL",
    "source_type": "pdf | web | csv | ...",
    "page": 1,                    # for PDFs
    "date_ingested": "2024-03-01",
    "last_modified": "2024-02-15", # if available
}
```

Domain-specific additions:
- Legal: `document_type`, `effective_date`, `parties`
- HR: `policy_version`, `department`, `classification`
- Technical: `product`, `version`, `language`
- News: `author`, `published_date`, `category`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Supported_Formats.md** | ← you are here |

⬅️ **Prev:** [01 RAG Fundamentals](../01_RAG_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Chunking Strategies](../03_Chunking_Strategies/Theory.md)
