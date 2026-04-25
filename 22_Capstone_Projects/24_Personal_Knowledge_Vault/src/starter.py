"""
Project 24 — Personal Knowledge Vault
Starter scaffold — fill in every TODO to complete the project.

Run:
  python vault.py watch            # monitor ~/vault/ for new files
  python vault.py ask "question"  # query the vault

Setup:
  pip install anthropic watchdog chromadb pdfplumber sentence-transformers click python-dotenv
  echo "ANTHROPIC_API_KEY=your-key" > .env
  mkdir -p ~/vault
"""

import os
import time
import hashlib
from pathlib import Path
from datetime import datetime

import click
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VAULT_DIR = Path.home() / "vault"
CHROMA_PATH = ".chroma"
COLLECTION_NAME = "vault"
CHUNK_SIZE = 2000      # characters (approx 500 tokens)
CHUNK_OVERLAP = 200    # characters (approx 50 tokens)
TOP_K = 5
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CLAUDE_MODEL = "claude-sonnet-4-6"
SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}


# ---------------------------------------------------------------------------
# Step 3 — PDF Parser
# ---------------------------------------------------------------------------

def parse_pdf(filepath: str) -> str:
    """Extract text from a PDF using pdfplumber."""
    # TODO: open the PDF with pdfplumber, iterate pages,
    # extract text per page (handle None returns), join with "\n"
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 4 — Markdown and Text Parsers
# ---------------------------------------------------------------------------

def parse_markdown(filepath: str) -> str:
    """Strip markdown syntax and return plain text."""
    # TODO: read the file, use re.sub to strip **, __, #, [], ()
    raise NotImplementedError


def parse_text(filepath: str) -> str:
    """Read plain text file and normalize whitespace."""
    # TODO: open, read, strip, normalize
    raise NotImplementedError


def parse_document(filepath: str) -> str | None:
    """Dispatch to the right parser based on file extension."""
    # TODO: check suffix, call the right parser, return None for unknown types
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 5 — Text Chunker
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping windows.
    Try paragraph boundaries first, then fall back to character sliding window.
    """
    # TODO: implement recursive chunking
    # Simplest acceptable version: sliding window of chunk_size chars, step = chunk_size - overlap
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 6 — Embedding Model
# ---------------------------------------------------------------------------

def get_embedding_model():
    """Load and return the SentenceTransformer model (cached after first call)."""
    # TODO: load SentenceTransformer(EMBEDDING_MODEL)
    raise NotImplementedError


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Embed a list of text chunks. Returns list of float vectors."""
    # TODO: use model.encode(), convert to list of lists
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 7 — ChromaDB
# ---------------------------------------------------------------------------

def get_collection():
    """Return the ChromaDB collection, creating it if it does not exist."""
    # TODO: chromadb.PersistentClient(path=CHROMA_PATH)
    # get_or_create_collection(COLLECTION_NAME)
    raise NotImplementedError


def upsert_document(filename: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    """
    Upsert all chunks for a document into ChromaDB.
    ID = sha256(filename + str(chunk_index))
    Metadata: filename, date_added, chunk_index
    """
    # TODO: build ids, metadatas, call collection.upsert()
    raise NotImplementedError


def delete_document(filename: str) -> None:
    """Delete all chunks for a given filename from ChromaDB."""
    # TODO: collection.delete(where={"filename": filename})
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 8 — Ingestion Pipeline
# ---------------------------------------------------------------------------

def ingest(filepath: str) -> None:
    """Parse, chunk, embed, and store a document."""
    filepath = str(filepath)
    filename = Path(filepath).name

    # TODO:
    # 1. parse_document()
    # 2. chunk_text()
    # 3. embed_chunks()
    # 4. delete_document() (handle re-ingestion)
    # 5. upsert_document()
    # 6. print success message
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Step 9 — File Watcher
# ---------------------------------------------------------------------------

def build_event_handler():
    """Return a watchdog FileSystemEventHandler that calls ingest()."""
    from watchdog.events import FileSystemEventHandler

    class VaultHandler(FileSystemEventHandler):
        def on_created(self, event):
            # TODO: check not directory, check extension, call ingest()
            pass

        def on_modified(self, event):
            # TODO: same as on_created
            pass

    return VaultHandler()


# ---------------------------------------------------------------------------
# Step 10 — Query Agent
# ---------------------------------------------------------------------------

def query_vault(question: str) -> None:
    """Embed question, retrieve top-k chunks, call Claude, print answer."""
    import anthropic

    # TODO:
    # 1. embed the question
    # 2. collection.query(query_embeddings=[...], n_results=TOP_K)
    # 3. extract documents and metadatas
    # 4. build context string with numbered citations
    # 5. call claude-sonnet-4-6 with RAG system prompt
    # 6. print answer
    # 7. print sources table
    raise NotImplementedError


# ---------------------------------------------------------------------------
# CLI Commands
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """Personal Knowledge Vault — RAG over your local documents."""
    pass


@cli.command()
@click.option("--folder", default=str(VAULT_DIR), help="Folder to watch")
def watch(folder: str):
    """Watch a folder and auto-ingest new/modified documents."""
    from watchdog.observers import Observer

    folder_path = Path(folder).expanduser()
    folder_path.mkdir(parents=True, exist_ok=True)

    click.echo(f"Watching: {folder_path}")
    click.echo("Drop PDF, Markdown, or text files to ingest them.")
    click.echo("Press Ctrl-C to stop.\n")

    # Ingest any existing files first
    for f in folder_path.iterdir():
        if f.suffix in SUPPORTED_EXTENSIONS:
            ingest(str(f))

    handler = build_event_handler()
    observer = Observer()
    observer.schedule(handler, str(folder_path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@cli.command()
@click.argument("question")
def ask(question: str):
    """Ask a question over the entire vault."""
    query_vault(question)


if __name__ == "__main__":
    cli()
