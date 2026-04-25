# Project 24 — Build Guide

**Format:** Minimal Hints — steps tell you what to do, not how. Figure out the how.

---

## Step 1 — Environment Setup

Install dependencies and verify they all import cleanly:

```
pip install anthropic watchdog chromadb pdfplumber sentence-transformers click python-dotenv
```

Create a `.env` file at the project root with `ANTHROPIC_API_KEY=your-key`. Create `~/vault/` as the watch folder. Create a small test corpus: one `.txt`, one `.md`, and one small `.pdf` (any PDF from the web works).

Hint: run `python -c "import chromadb, pdfplumber, sentence_transformers, watchdog, click"` — if no ImportError, you are ready.

---

## Step 2 — CLI Skeleton with Click

Build `vault.py` with two commands: `watch` and `ask`. Use Click's `@click.group()` decorator. The `ask` command should accept a positional string argument (the question). The `watch` command takes an optional `--folder` argument defaulting to `~/vault/`.

At this point neither command should do anything yet — just print a placeholder message. Verify the routing works:

```
python vault.py watch          # prints "watching ~/vault/"
python vault.py ask "hello"   # prints "question: hello"
```

---

## Step 3 — PDF Parser

Write a `parse_pdf(filepath)` function. Use `pdfplumber.open()`, iterate over pages, extract text per page, join with `"\n"`. Handle empty pages gracefully (some PDFs have blank pages that return `None`). Return a single string of the full document text.

Test it: point it at any PDF and `print(text[:500])` to see the first 500 characters.

---

## Step 4 — Markdown and Text Parsers

Write `parse_markdown(filepath)` and `parse_text(filepath)`. For markdown: read the file, use a simple regex or the `re` module to strip markdown syntax characters (`#`, `*`, `_`, `[`, `]`, `(`, `)`). For text: just `open().read()` with whitespace normalization.

Write a dispatcher `parse_document(filepath)` that checks the extension and calls the right parser. Return `None` for unsupported extensions.

---

## Step 5 — Recursive Text Chunker

Write `chunk_text(text, chunk_size=2000, overlap=200)`. Do not use LangChain for this — implement it yourself. The naive version: slide a window of `chunk_size` characters across the text, stepping by `chunk_size - overlap`. Return a list of strings.

The better version: try to split on paragraph boundaries first (`\n\n`), then sentence boundaries (`. `), then character boundaries. This is what "recursive" means in recursive text splitter.

Test: chunk a 5,000-character document and verify you get the expected number of chunks with overlap at the boundaries.

---

## Step 6 — Embedding Model

Load `SentenceTransformer("all-MiniLM-L6-v2")`. Write `embed_chunks(chunks)` that calls `model.encode(chunks, show_progress_bar=False)` and returns a list of numpy arrays. The model auto-downloads on first use (~23MB).

Verify the shape: `embed_chunks(["hello world"])` should return an array of shape `(1, 384)`.

---

## Step 7 — ChromaDB Collection

Initialize a `chromadb.PersistentClient(path=".chroma")` and get-or-create a collection named `"vault"`. Write two functions:

- `upsert_document(filename, chunks, embeddings)` — generates a deterministic ID per chunk using `sha256(filename + str(chunk_index))`, upserts all chunks with their embeddings and metadata
- `delete_document(filename)` — deletes all chunks for a given filename (use `collection.delete(where={"filename": filename})`)

Test: ingest one document, then `collection.count()` should return the number of chunks.

---

## Step 8 — Ingestion Pipeline

Wire Steps 3–7 into a single `ingest(filepath)` function:

1. Parse the document
2. If `parse_document()` returns `None`, skip
3. Chunk the text
4. Embed the chunks
5. Delete any existing chunks for this filename (handles re-ingestion)
6. Upsert the new chunks
7. Print `"Ingested: {filename} ({n} chunks)"`

Test: call `ingest("test.pdf")` and verify ChromaDB count increases.

---

## Step 9 — File Watcher

Use watchdog's `FileSystemEventHandler`. Override `on_created` and `on_modified`. In each handler, call `ingest(event.src_path)` if the extension is in `{".pdf", ".md", ".txt"}`.

Wire the watcher into the `watch` CLI command: create an `Observer`, schedule the handler on the vault folder with `recursive=False`, start the observer, and block with `while True: time.sleep(1)` until the user hits Ctrl-C.

Test: start `python vault.py watch`, drop a file into `~/vault/`, and watch it ingest in real time.

---

## Step 10 — Query Agent

Implement the `ask` command end-to-end:

1. Embed the user's question (single string → 384-dim vector)
2. Query ChromaDB: `collection.query(query_embeddings=[vector], n_results=5)`
3. Extract the `documents` and `metadatas` from the result
4. Build a context block: numbered list of retrieved chunks with source citations
5. Call Claude `claude-sonnet-4-6` with a system prompt that says "Answer strictly from the provided context. Cite the source filename and chunk number for each claim."
6. Print Claude's answer
7. Print the sources table (filename, chunk_index, date_added)

Test: ask a question whose answer is in one of your test documents. Verify Claude cites the right file.

---

## Stretch Goals

- Add a `vault.py list` command that prints all indexed documents with chunk counts
- Add a `vault.py remove <filename>` command that deletes a document from the vault
- Replace sentence-transformers with the Anthropic Embeddings API
- Add a `--top-k` flag to the `ask` command
- Store a per-document summary generated by Claude at ingest time

---

## 📂 Navigation

| File | |
|------|---|
| [01_MISSION.md](./01_MISSION.md) | Project brief |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design |
| **03_GUIDE.md** | You are here |
| [src/starter.py](./src/starter.py) | Starter scaffold |
| [src/solution.py](./src/solution.py) | Complete reference solution |
| [04_RECAP.md](./04_RECAP.md) | What you learned |
