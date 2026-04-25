"""
Personal Knowledge Base RAG
============================
A full retrieval-augmented generation pipeline over local documents.

Usage:
    python starter.py --ingest    # index documents in ./documents/
    python starter.py             # run Q&A interface

Requirements:
    pip install anthropic openai chromadb pdfplumber tiktoken python-dotenv
"""

import argparse
import os
import time
from pathlib import Path

import chromadb
import pdfplumber
import tiktoken
from anthropic import Anthropic
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOCUMENTS_DIR = Path("documents")
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "knowledge_base"
EMBEDDING_MODEL = "text-embedding-3-small"
GENERATION_MODEL = "claude-opus-4-6"
CHUNK_SIZE = 400          # characters per chunk  ← adjust to experiment
CHUNK_OVERLAP = 60        # overlap between consecutive chunks  ← adjust to experiment
TOP_K = 5                 # chunks to retrieve per query
MAX_CONTEXT_TOKENS = 8000 # max tokens to send as context to Claude

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anthropic_client = Anthropic()                          # ← uses ANTHROPIC_API_KEY
openai_client = OpenAI()                               # ← uses OPENAI_API_KEY for embeddings
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
tokenizer = tiktoken.get_encoding("cl100k_base")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def count_tokens(text: str) -> int:
    """Return the number of tokens in text using tiktoken."""
    return len(tokenizer.encode(text))


# ---------------------------------------------------------------------------
# Stage 1: Document Ingestion
# ---------------------------------------------------------------------------

def extract_pdf(file_path: Path) -> list[dict]:
    """
    Extract text from a PDF file, one dict per page.

    Returns:
        List of {"page": int, "text": str} dicts.
        Pages with no extractable text are excluded.
    """
    pages = []
    # TODO: Open file_path with pdfplumber.open().
    #       Iterate over pdf.pages with enumerate(start=1).
    #       For each page, call page.extract_text() — it may return None.
    #       If text is non-empty after stripping, append {"page": i, "text": text}.
    return pages


def extract_text_file(file_path: Path) -> list[dict]:
    """
    Read a plain-text file.

    Returns:
        List with a single {"page": 1, "text": content} dict.
    """
    # TODO: Open file_path with encoding="utf-8", errors="replace".
    #       Read and strip content. Return a list with one dict.
    pass


def load_all_documents(documents_dir: Path) -> list[dict]:
    """
    Load all supported documents from documents_dir.

    Returns:
        List of dicts:
        {
            "source_file": "filename.pdf",
            "page": 2,
            "text": "extracted text content..."
        }
    """
    if not documents_dir.exists():
        raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

    all_pages = []
    supported_extensions = {".pdf", ".txt", ".md"}

    for file_path in sorted(documents_dir.iterdir()):
        if file_path.suffix.lower() not in supported_extensions:
            continue

        print(f"  Loading: {file_path.name}")

        # TODO: Dispatch to extract_pdf() or extract_text_file() based on suffix.
        #       For each returned page dict, add "source_file": file_path.name.
        #       Append to all_pages.
        #       Skip files that return no pages (print a warning).

    print(f"Loaded {len(all_pages)} pages from {documents_dir}.")
    return all_pages


# ---------------------------------------------------------------------------
# Stage 2: Chunking
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Split text into overlapping fixed-size character chunks.

    Args:
        text: Input text.
        chunk_size: Target chunk size in characters.
        overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        List of {"text": str, "char_start": int, "char_end": int} dicts.
    """
    chunks = []

    # TODO: Implement sliding window chunking.
    #
    # Algorithm:
    #   start = 0
    #   while start < len(text):
    #       end = min(start + chunk_size, len(text))
    #       chunk_str = text[start:end].strip()
    #       if chunk_str:  # skip empty chunks
    #           append {"text": chunk_str, "char_start": start, "char_end": end}
    #       start += (chunk_size - overlap)  # advance with overlap
    #
    # Edge case: if overlap >= chunk_size, you get an infinite loop. Add a guard.

    return chunks


def create_chunks_for_page(
    page: dict,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """
    Chunk a single page and attach full metadata to each chunk.

    Args:
        page: {"source_file": str, "page": int, "text": str}

    Returns:
        List of chunk dicts with all metadata needed for ChromaDB:
        {
            "text": str,
            "source_file": str,
            "page": int,
            "chunk_index": int,    # position within this page
            "char_start": int,
            "char_end": int,
        }
    """
    raw_chunks = chunk_text(page["text"], chunk_size, overlap)
    result = []

    # TODO: Enumerate raw_chunks.
    #       For each, create a new dict merging the chunk fields with page metadata.
    #       Add "chunk_index": i (0-based index within this page).

    return result


# ---------------------------------------------------------------------------
# Stage 3: Embedding and Indexing
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts using the OpenAI embeddings API.

    Returns:
        List of float vectors (1536-d for text-embedding-3-small), one per input text.
    """
    # TODO: Call openai_client.embeddings.create(model=EMBEDDING_MODEL, input=texts).
    #       Return [item.embedding for item in response.data].
    pass


def get_or_create_collection() -> chromadb.Collection:
    """Get or create the ChromaDB collection with cosine distance."""
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # ← cosine similarity for text embeddings
    )


def is_file_indexed(collection: chromadb.Collection, source_file: str) -> bool:
    """Check if any chunks from source_file are already in the collection."""
    results = collection.get(where={"source_file": source_file}, limit=1)
    return len(results["ids"]) > 0


def index_documents(documents_dir: Path = DOCUMENTS_DIR) -> None:
    """
    Full ingestion pipeline: load → chunk → embed → store in ChromaDB.
    Skips files that are already indexed.
    """
    collection = get_or_create_collection()
    pages = load_all_documents(documents_dir)

    # Group pages by source file
    files: dict[str, list[dict]] = {}
    for page in pages:
        files.setdefault(page["source_file"], []).append(page)

    total_chunks = 0

    for source_file, file_pages in files.items():
        if is_file_indexed(collection, source_file):
            print(f"  Skipping {source_file} — already indexed.")
            continue

        print(f"  Indexing {source_file}...")

        all_chunks = []
        for page in file_pages:
            all_chunks.extend(create_chunks_for_page(page))

        if not all_chunks:
            print(f"    No chunks extracted from {source_file}. Skipping.")
            continue

        # TODO: Embed all chunks in batches of 50 (to avoid API payload limits).
        #
        # Algorithm:
        #   batch_size = 50
        #   embeddings = []
        #   for i in range(0, len(all_chunks), batch_size):
        #       batch_texts = [c["text"] for c in all_chunks[i:i+batch_size]]
        #       embeddings.extend(embed_texts(batch_texts))
        #       time.sleep(0.1)  # rate limit buffer

        embeddings = []  # ← replace with your batching loop above

        # TODO: Add chunks to ChromaDB collection.
        #
        # collection.add() requires:
        #   ids:        unique string per chunk
        #               use f"{source_file}_p{c['page']}_c{c['chunk_index']}"
        #   documents:  [c["text"] for c in all_chunks]
        #   embeddings: the embeddings list
        #   metadatas:  [{k: v for k, v in c.items() if k != "text"} for c in all_chunks]

        total_chunks += len(all_chunks)
        print(f"    Added {len(all_chunks)} chunks.")

    print(f"\nIndexing complete. Total chunks in index: {total_chunks}")


# ---------------------------------------------------------------------------
# Stage 4: Retrieval
# ---------------------------------------------------------------------------

def retrieve(
    query: str,
    collection: chromadb.Collection,
    top_k: int = TOP_K,
) -> list[dict]:
    """
    Embed query and retrieve top_k most relevant chunks from ChromaDB.

    Returns:
        List of result dicts with text, score (0–1), and metadata.
    """
    # TODO:
    #   1. Embed the query: embed_texts([query])[0]
    #   2. Call collection.query(
    #           query_embeddings=[query_embedding],
    #           n_results=top_k,
    #           include=["documents", "metadatas", "distances"]
    #      )
    #   3. results["documents"][0] → list of chunk texts
    #      results["metadatas"][0] → list of metadata dicts
    #      results["distances"][0] → list of cosine distances [0, 2]
    #   4. Convert distance to similarity: score = 1 - (distance / 2)
    #   5. Build and return result dicts merging text, score, and metadata.
    pass


# ---------------------------------------------------------------------------
# Stage 5: Context Assembly and Generation
# ---------------------------------------------------------------------------

def assemble_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a numbered context block for the LLM.

    Example output:
        [SOURCE 1] File: doc.pdf | Page: 2 | Chunk: 4
        Text content here...

        [SOURCE 2] File: notes.txt | Page: 1 | Chunk: 0
        More text content...
    """
    # TODO: Iterate over chunks with enumerate(start=1).
    #       For each chunk, format a block with SOURCE header and text.
    #       Join with double newline.
    #
    # Trim if over token limit:
    #   assembled = "\n\n".join(parts)
    #   while count_tokens(assembled) > MAX_CONTEXT_TOKENS and parts:
    #       parts.pop()
    #       assembled = "\n\n".join(parts)
    pass


def generate_answer(question: str, context: str) -> str:
    """
    Send question + retrieved context to Claude and return the answer.

    Claude is instructed to cite sources as [SOURCE N] and admit when
    the answer is not in the provided context.
    """
    system_prompt = """You are a helpful assistant answering questions from a personal knowledge base.

Rules:
1. Answer ONLY using the information in the provided sources.
2. If the answer is not in the sources, say: "I don't have information about that in the knowledge base."
3. Cite your sources inline as [SOURCE N] where N matches the source number.
4. Be concise and accurate."""

    user_message = f"""Sources:
{context}

Question: {question}

Answer (with inline citations):"""

    # TODO: Call anthropic_client.messages.create() with:
    #         model=GENERATION_MODEL
    #         max_tokens=1024
    #         system=system_prompt
    #         messages=[{"role": "user", "content": user_message}]
    #       Return response.content[0].text.
    pass


def display_answer(answer: str, chunks: list[dict]) -> None:
    """Print the answer and the source list."""
    print(f"\nAnswer:\n{answer}")
    print("\nSources:")
    for i, chunk in enumerate(chunks, start=1):
        print(
            f"  [{i}] {chunk['source_file']} — "
            f"Page {chunk['page']}, Chunk {chunk['chunk_index']} "
            f"(chars {chunk['char_start']}–{chunk['char_end']})"
        )
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_qa_loop() -> None:
    """Interactive Q&A loop over the indexed knowledge base."""
    collection = get_or_create_collection()

    count = collection.count()
    if count == 0:
        print("Knowledge base is empty. Run with --ingest first.")
        print("  python starter.py --ingest")
        return

    print(f"Knowledge base ready: {count} chunks indexed.")
    print("Ask a question, or type 'quit' to exit.\n")

    while True:
        try:
            question = input("Question > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        print("Retrieving...")

        # TODO: Call retrieve(question, collection) to get chunks.
        #       Call assemble_context(chunks) to format them.
        #       Call generate_answer(question, context) to get the answer.
        #       Call display_answer(answer, chunks).
        #       Wrap in try/except — print error message, don't crash the loop.


def main():
    parser = argparse.ArgumentParser(description="Personal Knowledge Base RAG")
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Ingest documents from ./documents/ into ChromaDB",
    )
    args = parser.parse_args()

    if args.ingest:
        print("Ingesting documents...")
        index_documents()
    else:
        run_qa_loop()


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Quick functional tests (run after implementing all TODOs)
# ---------------------------------------------------------------------------
#
# def test_chunking():
#     sample = "A" * 1000
#     chunks = chunk_text(sample, chunk_size=200, overlap=50)
#     assert len(chunks) > 0
#     assert all(c["char_end"] - c["char_start"] <= 200 for c in chunks)
#     for i in range(len(chunks) - 1):
#         assert chunks[i]["char_end"] > chunks[i+1]["char_start"], "No overlap"
#     print("Chunking test passed.")
#
# def test_embeddings():
#     vecs = embed_texts(["hello world", "foo bar"])
#     assert len(vecs) == 2
#     assert len(vecs[0]) == 1536
#     print("Embedding test passed.")
#
# def test_score_conversion():
#     assert 1 - (0.0 / 2) == 1.0  # identical → score 1.0
#     assert 1 - (2.0 / 2) == 0.0  # opposite → score 0.0
#     print("Score conversion test passed.")
