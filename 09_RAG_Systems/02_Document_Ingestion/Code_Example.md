# Document Ingestion — Code Example

LangChain document loaders — load a PDF, a CSV, and a web page. Shows the output structure.

```python
# pip install langchain pypdf requests beautifulsoup4 lxml
from langchain.document_loaders import PyPDFLoader, CSVLoader, WebBaseLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
import json

# ─────────────────────────────────────────────
# EXAMPLE 1: Load a PDF
# Each page becomes a separate Document
# ─────────────────────────────────────────────

print("=" * 60)
print("EXAMPLE 1: PDF Loading")
print("=" * 60)

# Download a sample PDF for testing
import urllib.request
sample_pdf_url = "https://www.w3.org/WAI/WCAG21/wcag21-diff.pdf"
# In practice, use your own PDF file

loader = PyPDFLoader("your_document.pdf")  # replace with actual path
docs = loader.load()

print(f"Total pages loaded: {len(docs)}")
print(f"\nFirst document:")
print(f"  page_content (first 300 chars): {docs[0].page_content[:300]}")
print(f"  metadata: {docs[0].metadata}")
# Output: {'source': 'your_document.pdf', 'page': 0}

# Access specific pages
for doc in docs[:3]:
    print(f"\nPage {doc.metadata['page'] + 1}: {len(doc.page_content)} chars")
    print(f"  Preview: {doc.page_content[:100].strip()}")


# ─────────────────────────────────────────────
# EXAMPLE 2: Load a CSV
# Each row becomes a Document
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("EXAMPLE 2: CSV Loading")
print("=" * 60)

# Create a sample CSV file for demonstration
import csv
import io

sample_csv_content = """product_name,description,price,category
Wireless Headphones,Noise-cancelling bluetooth headphones with 30-hour battery,129.99,electronics
Running Shoes,Lightweight mesh shoes with cushioned sole for long-distance running,89.99,footwear
Coffee Maker,12-cup programmable drip coffee maker with auto-shutoff,49.99,appliances
"""

# Write sample CSV
with open("products.csv", "w") as f:
    f.write(sample_csv_content)

csv_loader = CSVLoader("products.csv")
csv_docs = csv_loader.load()

print(f"Total rows loaded: {len(csv_docs)}")
print(f"\nFirst CSV document:")
print(f"  page_content: {csv_docs[0].page_content}")
print(f"  metadata: {csv_docs[0].metadata}")
# Each row's page_content = "column1: value1\ncolumn2: value2\n..."


# ─────────────────────────────────────────────
# EXAMPLE 3: Load a web page
# Extracts main text content from HTML
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("EXAMPLE 3: Web Page Loading")
print("=" * 60)

web_loader = WebBaseLoader(
    web_paths=["https://en.wikipedia.org/wiki/Retrieval-augmented_generation"],
    # You can customize the parser to extract specific elements
)

web_docs = web_loader.load()

print(f"Documents loaded: {len(web_docs)}")
print(f"\nWeb document metadata: {web_docs[0].metadata}")
print(f"Content length: {len(web_docs[0].page_content)} chars")
print(f"\nFirst 500 chars:\n{web_docs[0].page_content[:500]}")


# ─────────────────────────────────────────────
# EXAMPLE 4: Custom document creation
# When you want to build Documents manually from your own data
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("EXAMPLE 4: Manual Document Creation")
print("=" * 60)

from langchain.schema import Document

# Build documents from any data source
records = [
    {"id": "policy_001", "text": "All refunds must be requested within 30 days of purchase.", "section": "Refund Policy"},
    {"id": "policy_002", "text": "Employees are entitled to 15 days of annual leave per year.", "section": "HR Policy"},
    {"id": "policy_003", "text": "Remote work is permitted up to 3 days per week with manager approval.", "section": "Work Policy"},
]

custom_docs = [
    Document(
        page_content=record["text"],
        metadata={
            "id": record["id"],
            "section": record["section"],
            "source": "company_policies",
            "date": "2024-01-01"
        }
    )
    for record in records
]

print(f"Created {len(custom_docs)} custom documents")
for doc in custom_docs:
    print(f"\n  ID: {doc.metadata['id']}")
    print(f"  Section: {doc.metadata['section']}")
    print(f"  Content: {doc.page_content}")


# ─────────────────────────────────────────────
# EXAMPLE 5: Clean and enrich document metadata
# Always post-process loaded documents
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("EXAMPLE 5: Document Post-Processing")
print("=" * 60)

import re
from datetime import datetime

def clean_document(doc: Document, extra_metadata: dict = None) -> Document:
    """Clean text and enrich metadata."""
    # Clean text
    text = doc.page_content
    text = re.sub(r'\s+', ' ', text)          # collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)    # max 2 consecutive newlines
    text = text.strip()

    # Enrich metadata
    new_metadata = {
        **doc.metadata,
        "ingested_at": datetime.now().isoformat(),
        "char_count": len(text),
        "word_count": len(text.split()),
    }
    if extra_metadata:
        new_metadata.update(extra_metadata)

    return Document(page_content=text, metadata=new_metadata)


# Apply to all loaded documents
cleaned_docs = [
    clean_document(doc, extra_metadata={"source_type": "policy", "version": "2024"})
    for doc in custom_docs
]

print(f"Cleaned {len(cleaned_docs)} documents")
print(f"\nEnriched metadata example:")
print(json.dumps(cleaned_docs[0].metadata, indent=2))


# ─────────────────────────────────────────────
# EXAMPLE 6: Check for empty content (scanned PDF problem)
# ─────────────────────────────────────────────

def validate_documents(docs: list, min_chars: int = 50) -> tuple:
    """Separate valid and empty documents."""
    valid = [d for d in docs if len(d.page_content.strip()) >= min_chars]
    empty = [d for d in docs if len(d.page_content.strip()) < min_chars]
    return valid, empty


valid_docs, empty_docs = validate_documents(custom_docs)
print(f"\nDocument validation:")
print(f"  Valid: {len(valid_docs)}")
print(f"  Empty/too short: {len(empty_docs)}")
if empty_docs:
    print(f"  Empty docs (may be scanned PDFs):")
    for doc in empty_docs:
        print(f"    - {doc.metadata.get('source', 'unknown')}, page {doc.metadata.get('page', '?')}")
```

**Install and run:**
```bash
pip install langchain langchain-community pypdf requests beautifulsoup4 lxml
python document_ingestion.py
```

**Key output structure:**
```
Document(
    page_content="The refund policy states...",
    metadata={
        "source": "policy.pdf",
        "page": 3,
        "ingested_at": "2024-03-01T10:30:00",
        "char_count": 245,
        "word_count": 42
    }
)
```

Every document has two things: the text and where it came from. The metadata travels with the document through every subsequent stage (chunking, embedding, retrieval, citation).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Supported_Formats.md](./Supported_Formats.md) | Supported document formats |

⬅️ **Prev:** [01 RAG Fundamentals](../01_RAG_Fundamentals/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Chunking Strategies](../03_Chunking_Strategies/Theory.md)
