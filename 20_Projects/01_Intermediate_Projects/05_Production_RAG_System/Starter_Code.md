# Project 5 — Production RAG System: Starter Code

## How to Use This File

Five files to implement. Start with `cache.py`, then `guardrails.py`, `cost_tracker.py`, `evaluator.py`, and finally `production_rag.py` which ties them together. Each file is independently testable.

---

## Setup

```bash
pip install anthropic openai chromadb tiktoken python-dotenv numpy
```

This project reuses the ChromaDB index from Project 2. Copy your `chroma_db/` directory or run `python rag_pipeline.py --ingest` again.

---

## `cache.py`

```python
"""
Semantic Cache
==============
Query caching using cosine similarity against stored embeddings.
Backed by SQLite for persistence across restarts.
"""

import json
import sqlite3
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = "production_rag.db"
DEFAULT_THRESHOLD = 0.92   # similarity score to consider a cache hit
EMBEDDING_MODEL = "text-embedding-3-small"

openai_client = OpenAI()

# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------

def init_db(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create tables if they do not exist. Return the connection."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_cache (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text  TEXT NOT NULL,
            embedding   TEXT NOT NULL,
            answer_text TEXT NOT NULL,
            sources     TEXT NOT NULL,
            hit_count   INTEGER DEFAULT 0,
            created_at  REAL DEFAULT (strftime('%s', 'now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_stats (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text    TEXT NOT NULL,
            cache_hit     INTEGER NOT NULL,
            embed_tokens  INTEGER DEFAULT 0,
            input_tokens  INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cost_usd      REAL DEFAULT 0.0,
            latency_ms    INTEGER DEFAULT 0,
            blocked       INTEGER DEFAULT 0,
            created_at    REAL DEFAULT (strftime('%s', 'now'))
        )
    """)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Cache operations
# ---------------------------------------------------------------------------

class SemanticCache:
    """
    Semantic cache backed by SQLite.

    On lookup, embeds the query and compares against all stored embeddings
    using cosine similarity. Returns cached answer if similarity >= threshold.
    """

    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        threshold: float = DEFAULT_THRESHOLD,
    ):
        self.db_path = db_path
        self.threshold = threshold
        self.conn = init_db(db_path)

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def embed(self, text: str) -> list[float]:
        """Embed a single text string."""
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding

    def lookup(self, query: str) -> dict | None:
        """
        Check if a semantically similar query exists in the cache.

        Returns a dict with keys "answer" and "sources" if hit, else None.
        """
        # Load all cached entries
        rows = self.conn.execute(
            "SELECT id, embedding, answer_text, sources FROM query_cache"
        ).fetchall()

        if not rows:
            return None

        # TODO: Embed the query using self.embed(query).
        #
        # TODO: For each row, deserialize the embedding: json.loads(row[1]).
        #       Build a numpy matrix of all cached embeddings.
        #       Compute cosine similarity between query embedding and matrix.
        #       Use the same vectorized cosine formula as Project 1.
        #
        # TODO: Find the index of the maximum similarity.
        #       If max_similarity >= self.threshold:
        #           Increment hit_count in the database for that row's id.
        #           Return {"answer": row[2], "sources": json.loads(row[3]),
        #                   "similarity": max_similarity}
        #       Else: return None.
        pass

    def store(
        self,
        query: str,
        embedding: list[float],
        answer: str,
        sources: list[str],
    ) -> None:
        """
        Store a query-answer pair in the cache.

        Args:
            query: The original query text.
            embedding: Pre-computed embedding (so we do not call API twice).
            answer: The generated answer to cache.
            sources: List of source strings for citation display.
        """
        # TODO: Insert into query_cache table.
        #       Serialize embedding as json.dumps(embedding).
        #       Serialize sources as json.dumps(sources).
        #       Call self.conn.commit().
        pass

    def clear(self) -> int:
        """Delete all cache entries. Returns the number of rows deleted."""
        cursor = self.conn.execute("DELETE FROM query_cache")
        self.conn.commit()
        return cursor.rowcount

    def stats(self) -> dict:
        """Return cache statistics."""
        row = self.conn.execute(
            "SELECT COUNT(*), SUM(hit_count) FROM query_cache"
        ).fetchone()
        total_entries = row[0] or 0
        total_hits = row[1] or 0
        return {
            "total_entries": total_entries,
            "total_hits": total_hits,
            "threshold": self.threshold,
        }
```

---

## `guardrails.py`

```python
"""
Safety Guardrails
=================
Input and output safety checks for the production RAG system.
"""

import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Input guardrails
# ---------------------------------------------------------------------------

# Patterns that indicate prompt injection or jailbreak attempts
INPUT_BLOCKED_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(your\s+)?system\s+prompt",
    r"disregard\s+(any|all|your)\s+(previous|prior|original)\s+",
    r"output\s+your\s+(system\s+)?(prompt|instructions)",
    r"reveal\s+your\s+(system\s+)?(prompt|instructions|context)",
    r"print\s+your\s+(system\s+)?prompt",
    r"what\s+are\s+your\s+instructions",
    r"act\s+as\s+(if\s+you\s+are\s+)?(?:an?\s+)?(?:evil|uncensored|unfiltered|unrestricted)",
    r"pretend\s+(that\s+)?you\s+(are|have\s+no)",
    r"you\s+are\s+now\s+(?:called|named|acting\s+as)\s+\w+",
    r"your\s+new\s+(primary\s+)?instructions?\s+are",
    r"jailbreak",
    r"prompt\s+injection",
    r"bypass\s+(your\s+)?(safety|filter|restriction|guardrail)",
    r"do\s+anything\s+now",    # DAN prompt
]

MAX_QUERY_LENGTH = 1000
MIN_QUERY_LENGTH = 3


@dataclass
class GuardrailResult:
    is_safe: bool
    reason: str = ""
    category: str = ""    # "injection", "length", "pii", "hallucination", ""


def check_input(query: str) -> GuardrailResult:
    """
    Run all input guardrail checks on a query.

    Returns GuardrailResult with is_safe=True if the query passes all checks.
    """
    # TODO: Check 1 — length
    #   If len(query.strip()) < MIN_QUERY_LENGTH:
    #       return GuardrailResult(is_safe=False, reason="Query too short", category="length")
    #   If len(query) > MAX_QUERY_LENGTH:
    #       return GuardrailResult(is_safe=False, reason="Query too long", category="length")

    # TODO: Check 2 — injection patterns
    #   query_lower = query.lower()
    #   For each pattern in INPUT_BLOCKED_PATTERNS:
    #       If re.search(pattern, query_lower):
    #           return GuardrailResult(is_safe=False,
    #                                  reason=f"Prompt injection pattern detected",
    #                                  category="injection")

    # TODO: Check 3 — excessive repetition (simple heuristic for junk inputs)
    #   words = query.split()
    #   if len(words) > 10:
    #       most_common_word = max(set(words), key=words.count)
    #       if words.count(most_common_word) / len(words) > 0.5:
    #           return GuardrailResult(is_safe=False,
    #                                  reason="Excessive repetition detected",
    #                                  category="spam")

    # If all checks pass:
    return GuardrailResult(is_safe=True)


# ---------------------------------------------------------------------------
# Output guardrails
# ---------------------------------------------------------------------------

PII_PATTERNS = {
    "email":        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "us_phone":     r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ssn":          r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card":  r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ip_address":   r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
}

# Soft warning markers (log but do not block)
HALLUCINATION_SOFT_MARKERS = [
    "I think",
    "I believe",
    "I'm not certain",
    "I'm not sure",
    "it might be",
    "possibly",
    "I'm guessing",
    "not totally sure",
]


def check_output(response_text: str) -> GuardrailResult:
    """
    Scan a generated response for PII or other prohibited content.

    Hard blocks: PII patterns → return is_safe=False
    Soft warnings: hallucination markers → is_safe=True but log reason

    Returns GuardrailResult.
    """
    # TODO: Check for PII patterns.
    #   For each name, pattern in PII_PATTERNS.items():
    #       If re.search(pattern, response_text):
    #           return GuardrailResult(is_safe=False,
    #                                  reason=f"PII detected: {name}",
    #                                  category="pii")

    # TODO: Check for soft hallucination markers (log only — is_safe=True).
    #   For each marker in HALLUCINATION_SOFT_MARKERS:
    #       If marker.lower() in response_text.lower():
    #           return GuardrailResult(is_safe=True,
    #                                  reason=f"Soft warning: '{marker}' detected",
    #                                  category="hallucination_warning")

    return GuardrailResult(is_safe=True)
```

---

## `cost_tracker.py`

```python
"""
Cost Tracker
============
Token counting, cost calculation, and statistics logging to SQLite.
"""

import sqlite3
import time

# ---------------------------------------------------------------------------
# Pricing (USD per 1M tokens) — verify current rates at anthropic.com/pricing
# ---------------------------------------------------------------------------

PRICING = {
    "claude-opus-4-6-input":       15.00,
    "claude-opus-4-6-output":      75.00,
    "claude-haiku-20240307-input":  0.25,
    "claude-haiku-20240307-output": 1.25,
    "text-embedding-3-small":       0.02,
}


def calculate_cost(
    embed_tokens: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    generation_model: str = "claude-opus-4-6",
) -> float:
    """
    Calculate the estimated USD cost of a single query.

    Args:
        embed_tokens: Tokens used for embedding (query + any doc re-embeds).
        input_tokens: Claude input tokens (system + context + question).
        output_tokens: Claude output tokens (generated answer).
        generation_model: Which Claude model was used for generation.

    Returns:
        Estimated cost in USD.
    """
    # TODO: Compute cost for each token type.
    #   embed_cost  = (embed_tokens / 1_000_000) * PRICING["text-embedding-3-small"]
    #   input_cost  = (input_tokens / 1_000_000) * PRICING[f"{generation_model}-input"]
    #   output_cost = (output_tokens / 1_000_000) * PRICING[f"{generation_model}-output"]
    #   Return sum.
    #
    # Guard against KeyError: if model key not in PRICING, use 0.0 for that component
    # and print a warning.
    pass


def log_query(
    conn: sqlite3.Connection,
    query_text: str,
    cache_hit: bool,
    embed_tokens: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
    latency_ms: int = 0,
    blocked: bool = False,
) -> None:
    """Insert a query record into the query_stats table."""
    # TODO: Execute INSERT INTO query_stats with all provided fields.
    #       Call conn.commit().
    pass


def get_stats(conn: sqlite3.Connection) -> dict:
    """
    Query the database for cost and usage statistics.

    Returns a dict with:
        total_queries, cache_hits, cache_hit_rate,
        total_cost_usd, avg_cost_usd, blocked_queries,
        estimated_monthly_cost_usd
    """
    # TODO: Run these queries:
    #   Total queries: SELECT COUNT(*) FROM query_stats WHERE blocked=0
    #   Cache hits: SELECT COUNT(*) FROM query_stats WHERE cache_hit=1
    #   Total cost: SELECT SUM(cost_usd) FROM query_stats
    #   Blocked: SELECT COUNT(*) FROM query_stats WHERE blocked=1
    #
    # Compute:
    #   cache_hit_rate = cache_hits / total_queries (handle division by zero)
    #   avg_cost = total_cost / (total_queries - cache_hits) — cost per non-cached query
    #
    # Estimate monthly cost:
    #   Use the avg daily query count (total_queries / days_since_first_query)
    #   and multiply by 30.
    #   For simplicity: estimated_monthly = total_cost * (30 / max(days_active, 1))
    pass


def format_stats(stats: dict) -> str:
    """Format stats dict as a printable string."""
    if stats is None or stats.get("total_queries", 0) == 0:
        return "No queries recorded yet."

    return (
        f"\n=== Cost and Usage Summary ===\n"
        f"Total queries:         {stats['total_queries']}\n"
        f"Blocked queries:       {stats['blocked_queries']}\n"
        f"Cache hits:            {stats['cache_hits']} "
        f"({stats['cache_hit_rate']:.1%})\n"
        f"Total cost (USD):      ${stats['total_cost_usd']:.4f}\n"
        f"Avg cost per query:    ${stats['avg_cost_usd']:.4f}\n"
        f"Est. monthly cost:     ${stats['estimated_monthly_cost_usd']:.2f}\n"
    )
```

---

## `evaluator.py`

```python
"""
RAGAS-style Evaluation
======================
Faithfulness and answer relevancy metrics for the RAG pipeline.
"""

import json
import numpy as np
from anthropic import Anthropic
from openai import OpenAI

anthropic_client = Anthropic()
openai_client = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"
EVAL_MODEL = "claude-haiku-20240307"   # cheap model for evaluation tasks


# ---------------------------------------------------------------------------
# Faithfulness
# ---------------------------------------------------------------------------

DECOMPOSE_PROMPT = """Break the following answer into a numbered list of simple, atomic factual claims.
Each claim should be one sentence containing exactly one fact.
If the answer makes no factual claims, output: ["No factual claims."]
Output as a JSON array of strings only, no other text.

Answer: {answer}"""

CHECK_CLAIM_PROMPT = """Given the context below and a single factual claim, determine if the claim is
directly supported by the context. Reply with only "SUPPORTED" or "NOT SUPPORTED".

Context:
{context}

Claim: {claim}"""


def decompose_answer(answer: str) -> list[str]:
    """Use an LLM to break an answer into atomic claims."""
    # TODO: Call anthropic_client.messages.create() with DECOMPOSE_PROMPT.
    #       Parse the response as JSON.
    #       Return the list of claim strings.
    #       Wrap in try/except json.JSONDecodeError — return [answer] as fallback.
    pass


def check_claim_supported(claim: str, context: str) -> bool:
    """Ask an LLM whether a claim is supported by the context."""
    # TODO: Call anthropic_client.messages.create() with CHECK_CLAIM_PROMPT.
    #       Return True if response starts with "SUPPORTED", else False.
    pass


def compute_faithfulness(answer: str, context: str) -> float:
    """
    Compute faithfulness score: fraction of answer claims supported by context.

    Score range: [0.0, 1.0]
    1.0 = all claims are supported by retrieved documents
    0.0 = no claims are supported (likely hallucination)
    """
    # TODO:
    #   1. Call decompose_answer(answer) to get list of claims.
    #   2. If empty or only "No factual claims.", return 1.0 (vacuously faithful).
    #   3. For each claim, call check_claim_supported(claim, context).
    #   4. Return (number of supported claims) / (total claims).
    pass


# ---------------------------------------------------------------------------
# Answer Relevancy
# ---------------------------------------------------------------------------

GENERATE_QUESTIONS_PROMPT = """Given the following answer, generate 3 different questions that this
answer would be a good response to. Focus on the main topic and key information.
Output as a JSON array of 3 question strings only, no other text.

Answer: {answer}"""


def generate_hypothetical_questions(answer: str) -> list[str]:
    """Generate questions that the answer would address."""
    # TODO: Call anthropic_client.messages.create() with GENERATE_QUESTIONS_PROMPT.
    #       Parse as JSON. Return list of question strings.
    #       Fallback: return [answer] if parsing fails.
    pass


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts. Returns numpy array shape (N, 1536)."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return np.array([item.embedding for item in response.data])


def compute_answer_relevancy(question: str, answer: str) -> float:
    """
    Compute answer relevancy: how well does the answer address the question?

    Algorithm:
    1. Generate N hypothetical questions from the answer
    2. Embed original question and hypothetical questions
    3. Score = average cosine similarity between original and hypotheticals

    Score range: [0.0, 1.0]
    1.0 = answer perfectly addresses the question
    ~0.5 = answer is tangentially related
    ~0.0 = answer is completely off-topic
    """
    # TODO:
    #   1. Call generate_hypothetical_questions(answer) to get hypothetical questions.
    #   2. Embed all questions: [question] + hypothetical_questions.
    #   3. query_vec = embeddings[0], hyp_vecs = embeddings[1:]
    #   4. Compute cosine similarity between query_vec and each hyp_vec.
    #   5. Return the mean similarity.
    pass


# ---------------------------------------------------------------------------
# Full evaluation run
# ---------------------------------------------------------------------------

def run_evaluation(
    test_file: str,
    rag_fn,   # callable: (question: str) -> (answer: str, context: str)
    verbose: bool = True,
) -> dict:
    """
    Run evaluation on a test set.

    Args:
        test_file: Path to JSONL file with {"question": ..., "expected_answer": ...} lines.
        rag_fn: Function that takes a question and returns (answer, context_text).
        verbose: Print per-question scores.

    Returns:
        {"faithfulness": float, "answer_relevancy": float, "per_question": list[dict]}
    """
    with open(test_file) as f:
        test_cases = [json.loads(line) for line in f if line.strip()]

    faithfulness_scores = []
    relevancy_scores = []
    per_question = []

    for i, case in enumerate(test_cases, start=1):
        question = case["question"]
        if verbose:
            print(f"  [{i}/{len(test_cases)}] {question[:60]}...")

        # TODO: Call rag_fn(question) to get (answer, context).
        #       Compute faithfulness = compute_faithfulness(answer, context).
        #       Compute relevancy = compute_answer_relevancy(question, answer).
        #       Append to faithfulness_scores, relevancy_scores.
        #       Append per-question dict to per_question list.
        #
        # Wrap in try/except — log error and use score 0.0 for that question.

        pass

    avg_faithfulness = sum(faithfulness_scores) / max(len(faithfulness_scores), 1)
    avg_relevancy = sum(relevancy_scores) / max(len(relevancy_scores), 1)

    return {
        "faithfulness": avg_faithfulness,
        "answer_relevancy": avg_relevancy,
        "per_question": per_question,
        "num_evaluated": len(faithfulness_scores),
    }
```

---

## `production_rag.py`

```python
"""
Production RAG System
=====================
Extends the Project 2 RAG pipeline with:
  - Semantic caching
  - Input/output guardrails
  - Cost tracking
  - RAGAS evaluation

Usage:
    python production_rag.py
    > /stats
    > /eval
    > /cache clear
    > quit
"""

import time
from pathlib import Path

import chromadb
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

from cache import SemanticCache
from guardrails import check_input, check_output
from cost_tracker import calculate_cost, log_query, get_stats, format_stats
from evaluator import run_evaluation

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHROMA_DIR = "./chroma_db"              # from Project 2
COLLECTION_NAME = "knowledge_base"       # from Project 2
DB_PATH = "production_rag.db"
CACHE_THRESHOLD = 0.92
TOP_K = 5
GENERATION_MODEL = "claude-opus-4-6"
EMBEDDING_MODEL = "text-embedding-3-small"

# ---------------------------------------------------------------------------
# Clients and shared resources
# ---------------------------------------------------------------------------

anthropic_client = Anthropic()
openai_client = OpenAI()
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
cache = SemanticCache(db_path=DB_PATH, threshold=CACHE_THRESHOLD)


# ---------------------------------------------------------------------------
# Core RAG functions (adapted from Project 2)
# ---------------------------------------------------------------------------

def embed_query(query: str) -> tuple[list[float], int]:
    """Embed a query. Returns (vector, token_count)."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    return response.data[0].embedding, response.usage.total_tokens


def retrieve_chunks(query_embedding: list[float], top_k: int = TOP_K) -> list[dict]:
    """Retrieve top_k chunks from ChromaDB."""
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "score": 1 - (dist / 2),
            **meta,
        })
    return chunks


def assemble_context(chunks: list[dict]) -> str:
    """Format retrieved chunks as a numbered source block."""
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        header = (
            f"[SOURCE {i}] File: {chunk.get('source_file', 'unknown')} | "
            f"Page: {chunk.get('page', '?')} | "
            f"Chunk: {chunk.get('chunk_index', '?')}"
        )
        parts.append(f"{header}\n{chunk['text']}")
    return "\n\n".join(parts)


def generate_answer(question: str, context: str) -> tuple[str, int, int]:
    """
    Call Claude to generate an answer.
    Returns (answer_text, input_tokens, output_tokens).
    """
    system = """You are a helpful assistant answering questions from a personal knowledge base.
Answer ONLY using the provided sources. Cite sources as [SOURCE N].
If the answer is not in the sources, say: "I don't have information about that in the knowledge base.\""""

    user_msg = f"Sources:\n{context}\n\nQuestion: {question}\n\nAnswer (with citations):"

    # TODO: Call anthropic_client.messages.create() with MODEL, system, user_msg.
    #       Return (response.content[0].text, response.usage.input_tokens, response.usage.output_tokens).
    pass


def get_sources_list(chunks: list[dict]) -> list[str]:
    """Build a list of human-readable source strings for display and caching."""
    sources = []
    for i, chunk in enumerate(chunks, start=1):
        sources.append(
            f"[{i}] {chunk.get('source_file', 'unknown')} — "
            f"Page {chunk.get('page', '?')}, "
            f"Chunk {chunk.get('chunk_index', '?')}"
        )
    return sources


# ---------------------------------------------------------------------------
# Full production query pipeline
# ---------------------------------------------------------------------------

def handle_query(query: str) -> None:
    """
    Process a user query through the full production pipeline:
    guardrails → cache → RAG → guardrails → cache store → log stats → display.
    """
    start_time = time.time()
    db_conn = cache.conn   # reuse the cache's SQLite connection

    # Step 1: Input guardrails
    guard_result = check_input(query)
    if not guard_result.is_safe:
        print(f"\n[GUARDRAIL] Input rejected: {guard_result.reason}")
        # TODO: Log the blocked query to query_stats with blocked=True.
        return

    # Step 2: Embed query (needed for both cache lookup and retrieval)
    query_embedding, embed_tokens = embed_query(query)

    # Step 3: Cache lookup
    # TODO: Call cache.lookup(query) — but the SemanticCache.lookup() also embeds.
    #       To avoid double-embedding, we already have the embedding.
    #       For this integration: call a cache method that accepts a pre-computed embedding.
    #       Add a `lookup_by_embedding(embedding)` method to SemanticCache if needed,
    #       or call the existing `lookup(query)` and accept the duplicate API call.
    #       (For this project, the duplicate call is acceptable.)
    cache_result = cache.lookup(query)

    if cache_result:
        similarity = cache_result.get("similarity", 1.0)
        print(f"\n[CACHE HIT] Similarity: {similarity:.3f} (threshold: {CACHE_THRESHOLD})")
        print(f"[COST] Cache hit — $0.00\n")
        print(f"Answer:\n{cache_result['answer']}")
        print("\nSources (cached):")
        for s in cache_result["sources"]:
            print(f"  {s}")

        # TODO: Log cache hit to query_stats with cache_hit=True, cost=0.
        return

    # Step 4: Full RAG pipeline
    print("[CACHE MISS] Retrieving...")
    chunks = retrieve_chunks(query_embedding)
    context = assemble_context(chunks)

    print("[GENERATING] Calling Claude...")
    answer, input_tokens, output_tokens = generate_answer(query, context)

    # Step 5: Output guardrails
    out_guard = check_output(answer)
    if not out_guard.is_safe:
        print(f"\n[GUARDRAIL] Output blocked: {out_guard.reason}")
        # TODO: Log as blocked, do not cache.
        return
    if out_guard.reason:  # soft warning
        print(f"[WARNING] {out_guard.reason}")

    # Step 6: Cost calculation
    cost = calculate_cost(embed_tokens, input_tokens, output_tokens, GENERATION_MODEL)
    latency_ms = int((time.time() - start_time) * 1000)
    print(f"[COST] ${cost:.6f} "
          f"(embed: {embed_tokens} tok, "
          f"input: {input_tokens} tok, "
          f"output: {output_tokens} tok) | {latency_ms}ms")

    # Step 7: Store in cache
    sources = get_sources_list(chunks)
    cache.store(query, query_embedding, answer, sources)
    print("[CACHED] Stored in semantic cache.")

    # Step 8: Log stats
    # TODO: Call log_query() with all the tracked values.

    # Step 9: Display
    print(f"\nAnswer:\n{answer}")
    print("\nSources:")
    for s in sources:
        print(f"  {s}")
    print()


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def handle_command(command: str) -> None:
    """Handle /commands."""
    parts = command.strip().lower().split()
    cmd = parts[0]

    if cmd == "/stats":
        stats = get_stats(cache.conn)
        print(format_stats(stats))

    elif cmd == "/eval":
        test_file = "test_questions.jsonl"
        if not Path(test_file).exists():
            print(f"Test file not found: {test_file}")
            print("Create it with {\"question\": ..., \"expected_answer\": ...} lines.")
            return

        print(f"Running RAGAS evaluation on {test_file}...")

        def rag_fn(question):
            """Adapter: returns (answer, context) for the evaluator."""
            embedding, _ = embed_query(question)
            chunks = retrieve_chunks(embedding)
            context = assemble_context(chunks)
            answer, _, _ = generate_answer(question, context)
            return answer, context

        results = run_evaluation(test_file, rag_fn, verbose=True)
        print(f"\n=== Evaluation Results ===")
        print(f"Questions evaluated: {results['num_evaluated']}")
        print(f"Faithfulness:        {results['faithfulness']:.3f}  (target: > 0.80)")
        print(f"Answer relevancy:    {results['answer_relevancy']:.3f}  (target: > 0.75)")

    elif cmd == "/cache":
        sub = parts[1] if len(parts) > 1 else ""
        if sub == "clear":
            n = cache.clear()
            print(f"Cleared {n} cache entries.")
        elif sub == "stats":
            stats = cache.stats()
            print(f"Cache entries: {stats['total_entries']}")
            print(f"Total hits:    {stats['total_hits']}")
            print(f"Threshold:     {stats['threshold']}")
        else:
            print("Usage: /cache clear | /cache stats")
    else:
        print(f"Unknown command: {command}")
        print("Commands: /stats, /eval, /cache clear, /cache stats")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Production RAG System")
    print("  Semantic cache | Guardrails | Cost tracking | RAGAS eval")
    print("=" * 60)
    print("Commands: /stats, /eval, /cache clear, /cache stats, quit\n")

    # Check that ChromaDB has content
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
        if collection.count() == 0:
            print("WARNING: Knowledge base is empty.")
            print("Copy your chroma_db/ from Project 2, or run the ingest step.")
    except Exception:
        print("WARNING: Could not connect to ChromaDB.")
        print("Make sure chroma_db/ exists with indexed documents.")

    while True:
        try:
            user_input = input("Query > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break
        if user_input.startswith("/"):
            handle_command(user_input)
        else:
            handle_query(user_input)


if __name__ == "__main__":
    main()
```

---

## Common Mistakes

**Cache lookup embeds twice**: The current design embeds the query for cache lookup and again (implicitly) inside the SemanticCache. To optimize, pass the pre-computed embedding to the cache. The starter code notes this as a known duplication for simplicity.

**RAGAS eval uses production cache**: The `rag_fn` passed to `run_evaluation` should bypass the cache so every test question gets a fresh retrieval and generation. Otherwise, cached answers skew your scores.

**Faithfulness score of 1.0 for short answers**: If `decompose_answer` returns an empty list for a very short answer, the fallback `return 1.0` fires. Consider returning `0.5` for unevaluable answers instead.

**Cost calculations becoming stale**: API prices change. Always verify against the current Anthropic pricing page before citing cost figures.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Project_Guide.md](./Project_Guide.md) | What you'll build |
| [Step_by_Step.md](./Step_by_Step.md) | Build instructions |
| Starter_Code.md | ← you are here |
| [Architecture_Blueprint.md](./Architecture_Blueprint.md) | System diagram |

⬅️ **Prev:** [04 — Custom LoRA Fine-Tuning](../04_Custom_LoRA_Fine_Tuning/Project_Guide.md) &nbsp;&nbsp;&nbsp; No next project (end of Intermediate series)
