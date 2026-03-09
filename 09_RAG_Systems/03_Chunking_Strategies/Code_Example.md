# Chunking Strategies — Code Example

LangChain `RecursiveCharacterTextSplitter` with different settings. Shows how chunks look at different sizes.

```python
# pip install langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Sample document to chunk
sample_text = """
Retrieval-Augmented Generation (RAG) is a technique that enhances large language models
by retrieving relevant information from external sources before generating a response.

RAG systems work by first converting documents into vector embeddings and storing them
in a vector database. When a user asks a question, the system retrieves the most relevant
document chunks using semantic similarity search.

The retrieved chunks are then combined with the user's question into a prompt that is
sent to the language model. This allows the model to generate accurate, factual responses
grounded in real documents rather than relying solely on its training data.

Key benefits of RAG include:
- Access to up-to-date information beyond the model's training cutoff
- Ability to cite sources for generated answers
- Reduced hallucination by grounding responses in retrieved context
- Cost-effective alternative to fine-tuning for knowledge-intensive tasks

The main components of a RAG pipeline are document ingestion, chunking, embedding,
vector storage, retrieval, and generation. Each component affects the overall quality
of the system, but chunking strategy and retrieval quality have the largest impact.
"""


# ─────────────────────────────────────────────
# EXAMPLE 1: Small chunks — precise for factual lookups
# ─────────────────────────────────────────────

print("=" * 60)
print("EXAMPLE 1: Small chunks (200 chars, 20 overlap)")
print("=" * 60)

small_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
    separators=["\n\n", "\n", ". ", " ", ""],
)

small_chunks = small_splitter.split_text(sample_text)
print(f"Produced {len(small_chunks)} chunks\n")

for i, chunk in enumerate(small_chunks[:4]):
    print(f"Chunk {i+1} ({len(chunk)} chars):")
    print(f"  '{chunk.strip()}'")
    print()


# ─────────────────────────────────────────────
# EXAMPLE 2: Medium chunks — good balance (recommended default)
# ─────────────────────────────────────────────

print("=" * 60)
print("EXAMPLE 2: Medium chunks (500 chars, 50 overlap)")
print("=" * 60)

medium_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

medium_chunks = medium_splitter.split_text(sample_text)
print(f"Produced {len(medium_chunks)} chunks\n")

for i, chunk in enumerate(medium_chunks[:3]):
    print(f"Chunk {i+1} ({len(chunk)} chars):")
    print(f"  '{chunk.strip()[:150]}...'")
    print()


# ─────────────────────────────────────────────
# EXAMPLE 3: Split Documents (preserves metadata)
# Always use split_documents(), not split_text(), in RAG pipelines
# ─────────────────────────────────────────────

print("=" * 60)
print("EXAMPLE 3: split_documents() — metadata preserved")
print("=" * 60)

docs = [
    Document(
        page_content=sample_text,
        metadata={
            "source": "rag_overview.pdf",
            "page": 1,
            "author": "AI Team",
            "date": "2024-01-15"
        }
    )
]

splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
split_docs = splitter.split_documents(docs)

print(f"Input: 1 document → Output: {len(split_docs)} chunks")
print(f"\nFirst chunk:")
print(f"  page_content: '{split_docs[0].page_content[:150].strip()}...'")
print(f"  metadata: {split_docs[0].metadata}")
# Notice metadata is inherited from the original document


# ─────────────────────────────────────────────
# EXAMPLE 4: Compare chunk overlap effect
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("EXAMPLE 4: Effect of chunk overlap")
print("=" * 60)

no_overlap = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
with_overlap = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=60)

no_overlap_chunks = no_overlap.split_text(sample_text)
with_overlap_chunks = with_overlap.split_text(sample_text)

print(f"Without overlap: {len(no_overlap_chunks)} chunks")
print(f"With overlap:    {len(with_overlap_chunks)} chunks (more because some content duplicated)")

# Show the boundary between chunks 1 and 2 for both
print(f"\nNo overlap - End of chunk 1:   '...{no_overlap_chunks[0][-60:]}'")
print(f"No overlap - Start of chunk 2: '{with_overlap_chunks[1][:60]}...'")
print()
print(f"With overlap - End of chunk 1:   '...{with_overlap_chunks[0][-60:]}'")
print(f"With overlap - Start of chunk 2: '{with_overlap_chunks[1][:60]}...'")
# Notice the overlap: the end of chunk 1 reappears at the start of chunk 2


# ─────────────────────────────────────────────
# EXAMPLE 5: Custom separators for code/markdown
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("EXAMPLE 5: Custom separators for markdown/code")
print("=" * 60)

markdown_text = """
## Introduction

This is the introduction section with several sentences. It explains the basics clearly.

## Methods

The methods section describes the approach in detail. We used Python for implementation.
Results were verified with unit tests and integration testing.

```python
def hello_world():
    print("Hello, World!")
    return True
```

## Results

The results show significant improvement over baseline approaches.
"""

# For markdown: split on headers first, then paragraphs, then sentences
markdown_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=30,
    separators=["## ", "\n\n", "\n", ". ", " ", ""],
)

md_chunks = markdown_splitter.split_text(markdown_text)
print(f"Produced {len(md_chunks)} chunks from markdown")
for i, chunk in enumerate(md_chunks):
    print(f"\nChunk {i+1}: '{chunk.strip()}'")


# ─────────────────────────────────────────────
# EXAMPLE 6: Token-based splitting (more precise)
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("EXAMPLE 6: Token counting vs character counting")
print("=" * 60)

# Character count is approximate — tokens are ~0.75 words
# 500 chars ≈ 100-150 tokens depending on word length

sample = "The quick brown fox jumps over the lazy dog. " * 10

char_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
char_chunks = char_splitter.split_text(sample)

print(f"Character splitter (chunk_size=200): {len(char_chunks)} chunks")
print(f"Average chars per chunk: {sum(len(c) for c in char_chunks) / len(char_chunks):.0f}")

# To use token-based splitting:
# from langchain.text_splitter import TokenTextSplitter
# token_splitter = TokenTextSplitter(chunk_size=100, chunk_overlap=10)
# token_chunks = token_splitter.split_text(sample)
# print(f"Token splitter (chunk_size=100 tokens): {len(token_chunks)} chunks")
```

**Install and run:**
```bash
pip install langchain
python chunking_example.py
```

**Key takeaways:**
- `split_text()` → list of strings. `split_documents()` → list of Documents with metadata.
- Always use `split_documents()` in RAG pipelines — metadata (source, page) must travel with the chunk.
- `chunk_size` is in characters, not tokens. ~500 chars ≈ 100–125 tokens.
- Overlap creates redundancy but prevents missing boundary information.
- Custom `separators` list lets you respect your document's specific structure.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Comparison.md](./Comparison.md) | Chunking strategies comparison |

⬅️ **Prev:** [02 Document Ingestion](../02_Document_Ingestion/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Embedding and Indexing](../04_Embedding_and_Indexing/Theory.md)
