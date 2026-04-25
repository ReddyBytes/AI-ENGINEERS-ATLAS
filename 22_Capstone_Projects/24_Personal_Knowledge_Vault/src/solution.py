"""
Project 24 — Personal Knowledge Vault
Complete reference solution.

Run:
  python solution.py watch            # monitor ~/vault/ for new files
  python solution.py ask "question"  # query the vault

Setup:
  pip install anthropic watchdog chromadb pdfplumber sentence-transformers click python-dotenv
  echo "ANTHROPIC_API_KEY=your-key" > .env
  mkdir -p ~/vault
"""

import os
import re
import time
import hashlib
from pathlib import Path
from datetime import datetime

import click
import chromadb
import pdfplumber
import anthropic
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VAULT_DIR = Path.home() / "vault"
CHROMA_PATH = ".chroma"
COLLECTION_NAME = "vault"
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
TOP_K = 5
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CLAUDE_MODEL = "claude-sonnet-4-6"
SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}

# Lazy-loaded singletons
_embedding_model: SentenceTransformer | None = None
_chroma_collection = None


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_pdf(filepath: str) -> str:
    """Extract text from all pages of a PDF using pdfplumber."""
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
    return "\n\n".join(pages)


def parse_markdown(filepath: str) -> str:
    """
    Read a markdown file and strip formatting syntax, returning plain text.
    Preserves paragraph breaks.
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    # Remove code fences
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", "", text)
    # Remove headings markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.+?)_{1,3}", r"\1", text)
    # Remove links: [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove images
    text = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_text(filepath: str) -> str:
    """Read a plain text file and normalize whitespace."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    # Normalize line endings, collapse excessive blank lines
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_document(filepath: str) -> str | None:
    """Dispatch to the correct parser. Returns None for unsupported types."""
    suffix = Path(filepath).suffix.lower()
    try:
        if suffix == ".pdf":
            return parse_pdf(filepath)
        elif suffix == ".md":
            return parse_markdown(filepath)
        elif suffix == ".txt":
            return parse_text(filepath)
    except Exception as e:
        click.echo(f"  [parse error] {Path(filepath).name}: {e}")
    return None


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Recursive text splitter.
    Tries to split on paragraph breaks, then sentence breaks, then characters.
    Returns a list of overlapping text windows.
    """
    if not text or not text.strip():
        return []

    # If the whole text fits in one chunk, return it directly
    if len(text) <= chunk_size:
        return [text.strip()]

    chunks = []

    def split_at(text: str, separator: str) -> list[str]:
        parts = text.split(separator)
        return [p.strip() for p in parts if p.strip()]

    # Try splitting on paragraph boundaries first
    paragraphs = split_at(text, "\n\n")
    if len(paragraphs) <= 1:
        # Fall back to sentence-level splitting
        paragraphs = split_at(text, ". ")

    # Accumulate paragraphs into chunk_size windows
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            # Start the new chunk with overlap from the previous chunk
            overlap_text = current[-overlap:] if len(current) > overlap else current
            current = (overlap_text + "\n\n" + para).strip()

    if current:
        chunks.append(current)

    # If any single paragraph is larger than chunk_size, force-split it
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > chunk_size:
            # Hard character split with overlap
            start = 0
            while start < len(chunk):
                end = start + chunk_size
                final_chunks.append(chunk[start:end].strip())
                start += chunk_size - overlap
        else:
            final_chunks.append(chunk)

    return [c for c in final_chunks if c]


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Embed a list of text chunks using sentence-transformers."""
    model = get_embedding_model()
    embeddings = model.encode(chunks, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    model = get_embedding_model()
    vec = model.encode([query], normalize_embeddings=True)
    return vec[0].tolist()


# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------

def get_collection():
    global _chroma_collection
    if _chroma_collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _chroma_collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _chroma_collection


def make_chunk_id(filename: str, chunk_index: int) -> str:
    raw = f"{filename}::{chunk_index}"
    return hashlib.sha256(raw.encode()).hexdigest()


def upsert_document(filename: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    collection = get_collection()
    date_added = datetime.now().isoformat()
    ids = [make_chunk_id(filename, i) for i in range(len(chunks))]
    metadatas = [
        {"filename": filename, "date_added": date_added, "chunk_index": i}
        for i in range(len(chunks))
    ]
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )


def delete_document(filename: str) -> None:
    collection = get_collection()
    try:
        collection.delete(where={"filename": filename})
    except Exception:
        # Collection may be empty — chromadb raises on empty where-delete
        pass


# ---------------------------------------------------------------------------
# Ingestion Pipeline
# ---------------------------------------------------------------------------

def ingest(filepath: str) -> None:
    """Full ingestion pipeline: parse → chunk → embed → store."""
    path = Path(filepath)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return

    filename = path.name
    click.echo(f"Ingesting: {filename} ...", nl=False)

    text = parse_document(filepath)
    if not text or not text.strip():
        click.echo(f"  [skipped — no text extracted]")
        return

    chunks = chunk_text(text)
    if not chunks:
        click.echo(f"  [skipped — no chunks produced]")
        return

    embeddings = embed_chunks(chunks)

    # Remove existing chunks for this file before re-inserting
    delete_document(filename)
    upsert_document(filename, chunks, embeddings)

    collection = get_collection()
    click.echo(f" done ({len(chunks)} chunks, vault total: {collection.count()})")


# ---------------------------------------------------------------------------
# File Watcher
# ---------------------------------------------------------------------------

class VaultEventHandler(FileSystemEventHandler):
    def _handle(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            ingest(str(path))

    def on_created(self, event):
        self._handle(event)

    def on_modified(self, event):
        self._handle(event)


# ---------------------------------------------------------------------------
# Query Agent
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a research assistant with access to the user's personal document vault.
Answer the user's question using ONLY the provided context passages.
For each claim you make, cite the source in the format [filename, chunk N].
If the context does not contain sufficient information to answer the question, say so explicitly.
Be concise and precise."""


def query_vault(question: str) -> None:
    """Retrieve relevant chunks and generate a cited answer with Claude."""
    collection = get_collection()
    total = collection.count()

    if total == 0:
        click.echo("Vault is empty. Add documents first with: python solution.py watch")
        return

    click.echo(f"\nSearching vault ({total} chunks)...\n")

    # Embed the question and query ChromaDB
    query_vec = embed_query(question)
    results = collection.query(
        query_embeddings=[query_vec],
        n_results=min(TOP_K, total),
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        click.echo("No relevant documents found.")
        return

    # Build numbered context block
    context_parts = []
    for i, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        context_parts.append(
            f"[{i}] Source: {meta['filename']}, chunk {meta['chunk_index']}, "
            f"added {meta['date_added'][:10]}\n{doc}"
        )
    context_block = "\n\n---\n\n".join(context_parts)

    # Call Claude
    client = anthropic.Anthropic()
    user_message = f"Context passages:\n\n{context_block}\n\n---\n\nQuestion: {question}"

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    answer = response.content[0].text

    # Print answer
    click.echo("Answer:")
    click.echo("-" * 60)
    click.echo(answer)
    click.echo("-" * 60)

    # Print sources table
    click.echo("\nSources:")
    for i, meta in enumerate(metadatas, start=1):
        click.echo(
            f"  [{i}] {meta['filename']} — chunk {meta['chunk_index']} "
            f"(added {meta['date_added'][:10]})"
        )
    click.echo()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """Personal Knowledge Vault — RAG over your local documents."""
    pass


@cli.command()
@click.option("--folder", default=str(VAULT_DIR), help="Folder to watch")
def watch(folder: str):
    """Watch a folder and auto-ingest new or modified documents."""
    folder_path = Path(folder).expanduser()
    folder_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"Watching: {folder_path}")
    click.echo(f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
    click.echo("Press Ctrl-C to stop.\n")

    # Ingest anything already in the folder
    existing = [f for f in folder_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    if existing:
        click.echo(f"Found {len(existing)} existing file(s) — ingesting...\n")
        for f in existing:
            ingest(str(f))
        click.echo()

    handler = VaultEventHandler()
    observer = Observer()
    observer.schedule(handler, str(folder_path), recursive=False)
    observer.start()
    click.echo("Watching for new files...\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nStopping watcher.")
        observer.stop()
    observer.join()


@cli.command()
@click.argument("question")
@click.option("--top-k", default=TOP_K, help="Number of chunks to retrieve")
def ask(question: str, top_k: int):
    """Ask a question over the entire knowledge vault."""
    global TOP_K
    TOP_K = top_k
    query_vault(question)


@cli.command(name="list")
def list_docs():
    """List all indexed documents with chunk counts."""
    collection = get_collection()
    total = collection.count()
    if total == 0:
        click.echo("Vault is empty.")
        return

    # Get all metadatas (up to 10,000)
    results = collection.get(include=["metadatas"], limit=10000)
    metadatas = results["metadatas"]

    # Aggregate by filename
    from collections import defaultdict
    doc_info: dict[str, dict] = defaultdict(lambda: {"chunks": 0, "date_added": ""})
    for m in metadatas:
        fn = m["filename"]
        doc_info[fn]["chunks"] += 1
        if not doc_info[fn]["date_added"] or m["date_added"] > doc_info[fn]["date_added"]:
            doc_info[fn]["date_added"] = m["date_added"]

    click.echo(f"\nVault: {len(doc_info)} documents, {total} chunks\n")
    click.echo(f"{'Filename':<40} {'Chunks':>6}  {'Date Added'}")
    click.echo("-" * 65)
    for fn, info in sorted(doc_info.items()):
        click.echo(f"{fn:<40} {info['chunks']:>6}  {info['date_added'][:10]}")
    click.echo()


if __name__ == "__main__":
    cli()
