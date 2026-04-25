"""
Production RAG System — Project 10
====================================
Extends the Project 2 RAG pipeline with:
  - Semantic caching (SQLite + cosine similarity)
  - Input/output safety guardrails
  - Per-query cost tracking
  - RAGAS-style faithfulness and answer relevancy evaluation

Usage:
    python starter.py
    > /stats
    > /eval
    > /cache clear
    > quit

Setup:
    pip install anthropic openai chromadb tiktoken python-dotenv numpy
    Copy chroma_db/ from Project 2 (or run the ingest step).
    Set ANTHROPIC_API_KEY and OPENAI_API_KEY in environment or .env file.
"""

import json
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Uncomment chromadb import once you have Project 2's chroma_db/ directory
# ---------------------------------------------------------------------------
# import chromadb

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration — adjust thresholds and models here
# ---------------------------------------------------------------------------

DB_PATH = "production_rag.db"
CACHE_THRESHOLD = 0.92          # cosine similarity threshold for cache hit  # ← tune this
TOP_K = 5                        # number of chunks to retrieve from ChromaDB
GENERATION_MODEL = "claude-opus-4-6"
EMBEDDING_MODEL = "text-embedding-3-small"
CHROMA_DIR = "./chroma_db"       # from Project 2
COLLECTION_NAME = "knowledge_base"

# ---------------------------------------------------------------------------
# Pricing — USD per 1M tokens (verify current rates at anthropic.com/pricing)
# ---------------------------------------------------------------------------

PRICING = {
    "claude-opus-4-6-input":        15.00,
    "claude-opus-4-6-output":       75.00,
    "claude-haiku-20240307-input":   0.25,
    "claude-haiku-20240307-output":  1.25,
    "text-embedding-3-small":        0.02,
}

# ---------------------------------------------------------------------------
# Clients — initialized at module level and reused across functions
# ---------------------------------------------------------------------------

anthropic_client = Anthropic()
openai_client = OpenAI()


# ===========================================================================
# DATABASE LAYER
# ===========================================================================

def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create both tables if they do not exist. Returns the connection."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_cache (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text  TEXT NOT NULL,
            embedding   TEXT NOT NULL,        -- JSON array of floats
            answer_text TEXT NOT NULL,
            sources     TEXT NOT NULL,        -- JSON array of source strings
            hit_count   INTEGER DEFAULT 0,
            created_at  REAL DEFAULT (strftime('%s', 'now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_stats (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text    TEXT NOT NULL,
            cache_hit     INTEGER NOT NULL,   -- 0 or 1
            embed_tokens  INTEGER DEFAULT 0,
            input_tokens  INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cost_usd      REAL DEFAULT 0.0,
            latency_ms    INTEGER DEFAULT 0,
            blocked       INTEGER DEFAULT 0,  -- 0 or 1
            created_at    REAL DEFAULT (strftime('%s', 'now'))
        )
    """)
    conn.commit()
    return conn


# ===========================================================================
# SEMANTIC CACHE
# ===========================================================================

class SemanticCache:
    """
    Semantic cache backed by SQLite.

    On lookup, embeds the query and compares against all stored embeddings
    using cosine similarity. Returns cached answer if similarity >= threshold.
    """

    def __init__(self, db_path: str = DB_PATH, threshold: float = CACHE_THRESHOLD):
        self.db_path = db_path
        self.threshold = threshold
        self.conn = init_db(db_path)

    def _embed(self, text: str) -> tuple[list[float], int]:
        """Embed a single text string. Returns (vector, token_count)."""
        response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
        return response.data[0].embedding, response.usage.total_tokens

    def lookup(self, query: str) -> dict | None:
        """
        Check if a semantically similar query exists in the cache.

        Returns dict with keys "answer", "sources", "similarity" if hit, else None.
        """
        rows = self.conn.execute(
            "SELECT id, embedding, answer_text, sources FROM query_cache"
        ).fetchall()

        if not rows:
            return None

        # TODO: Embed the query using self._embed(query)[0].
        #
        # TODO: Build a numpy matrix from all cached embeddings:
        #       cached_matrix = np.array([json.loads(row[1]) for row in rows])
        #
        # TODO: Compute cosine similarity between query_vec and cached_matrix.
        #       Vectorized formula:
        #         norms = np.linalg.norm(cached_matrix, axis=1) * np.linalg.norm(query_vec)
        #         similarities = cached_matrix @ query_vec / np.maximum(norms, 1e-10)
        #
        # TODO: Find best_idx = np.argmax(similarities), max_sim = similarities[best_idx].
        #       If max_sim >= self.threshold:
        #           Increment hit_count in the database for rows[best_idx][0].
        #           Return {"answer": rows[best_idx][2],
        #                   "sources": json.loads(rows[best_idx][3]),
        #                   "similarity": float(max_sim)}
        #       Else: return None.
        pass  # ← replace with your implementation

    def store(self, query: str, embedding: list[float], answer: str, sources: list[str]) -> None:
        """Store a query-answer pair in the cache."""
        # TODO: INSERT INTO query_cache.
        #       Serialize embedding as json.dumps(embedding).
        #       Serialize sources as json.dumps(sources).
        #       Call self.conn.commit().
        pass  # ← replace with your implementation

    def clear(self) -> int:
        """Delete all cache entries. Returns the number of rows deleted."""
        cursor = self.conn.execute("DELETE FROM query_cache")
        self.conn.commit()
        return cursor.rowcount

    def stats(self) -> dict:
        row = self.conn.execute(
            "SELECT COUNT(*), SUM(hit_count) FROM query_cache"
        ).fetchone()
        return {
            "total_entries": row[0] or 0,
            "total_hits": row[1] or 0,
            "threshold": self.threshold,
        }


# ===========================================================================
# GUARDRAILS
# ===========================================================================

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
    r"your\s+new\s+(primary\s+)?instructions?\s+are",
    r"jailbreak",
    r"bypass\s+(your\s+)?(safety|filter|restriction|guardrail)",
    r"do\s+anything\s+now",
]

MAX_QUERY_LENGTH = 1000
MIN_QUERY_LENGTH = 3

PII_PATTERNS = {
    "email":        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "us_phone":     r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ssn":          r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card":  r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
}

HALLUCINATION_SOFT_MARKERS = [
    "I think", "I believe", "I'm not certain", "I'm not sure",
    "it might be", "possibly", "I'm guessing", "not totally sure",
]


@dataclass
class GuardrailResult:
    is_safe: bool
    reason: str = ""
    category: str = ""  # "injection", "length", "pii", "hallucination_warning", ""


def check_input(query: str) -> GuardrailResult:
    """
    Run all input guardrail checks on a query.
    Returns GuardrailResult with is_safe=True if the query passes all checks.
    """
    # TODO: Check 1 — length (use MIN_QUERY_LENGTH and MAX_QUERY_LENGTH)
    #
    # TODO: Check 2 — injection patterns (iterate INPUT_BLOCKED_PATTERNS,
    #       use re.search on query.lower())
    #
    # TODO: Check 3 — excessive repetition
    #       words = query.split()
    #       if len(words) > 10 and most_common_word_frequency > 0.5:
    #           block with category="spam"

    return GuardrailResult(is_safe=True)  # ← replace with real implementation


def check_output(response_text: str) -> GuardrailResult:
    """
    Scan a generated response for PII or hallucination markers.

    Hard blocks (PII): return is_safe=False
    Soft warnings (hallucination markers): is_safe=True with reason set
    """
    # TODO: Check PII_PATTERNS (hard block on any match)
    #
    # TODO: Check HALLUCINATION_SOFT_MARKERS (soft warning — is_safe=True)

    return GuardrailResult(is_safe=True)  # ← replace with real implementation


# ===========================================================================
# COST TRACKING
# ===========================================================================

def calculate_cost(
    embed_tokens: int = 0,
    input_tokens: int = 0,
    output_tokens: int = 0,
    generation_model: str = GENERATION_MODEL,
) -> float:
    """Return estimated USD cost for one query's API calls."""
    # TODO: Compute three cost components using PRICING dict.
    #       Guard against KeyError with .get(..., 0.0).
    #       Return the sum.
    return 0.0  # ← replace with real implementation


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
    """Insert one record into query_stats."""
    # TODO: Execute INSERT INTO query_stats with all provided fields.
    #       Call conn.commit().
    pass  # ← replace with real implementation


def get_stats(conn: sqlite3.Connection) -> dict:
    """Query the database for cost and usage statistics."""
    # TODO: Run these queries:
    #   total_queries: SELECT COUNT(*) FROM query_stats WHERE blocked=0
    #   cache_hits:    SELECT COUNT(*) FROM query_stats WHERE cache_hit=1
    #   total_cost:    SELECT SUM(cost_usd) FROM query_stats
    #   blocked:       SELECT COUNT(*) FROM query_stats WHERE blocked=1
    #
    # Compute cache_hit_rate and avg_cost (handle division by zero).
    # Estimate monthly cost: total_cost * (30 / max(days_active, 1))
    return {}  # ← replace with real implementation


def format_stats(stats: dict) -> str:
    if not stats or stats.get("total_queries", 0) == 0:
        return "No queries recorded yet."
    return (
        f"\n=== Cost and Usage Summary ===\n"
        f"Total queries:         {stats['total_queries']}\n"
        f"Blocked queries:       {stats['blocked_queries']}\n"
        f"Cache hits:            {stats['cache_hits']} ({stats['cache_hit_rate']:.1%})\n"
        f"Total cost (USD):      ${stats['total_cost_usd']:.4f}\n"
        f"Avg cost per query:    ${stats['avg_cost_usd']:.4f}\n"
        f"Est. monthly cost:     ${stats['estimated_monthly_cost_usd']:.2f}\n"
    )


# ===========================================================================
# RAGAS EVALUATION
# ===========================================================================

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

GENERATE_QUESTIONS_PROMPT = """Given the following answer, generate 3 different questions that this
answer would be a good response to. Focus on the main topic and key information.
Output as a JSON array of 3 question strings only, no other text.

Answer: {answer}"""


def decompose_answer(answer: str) -> list[str]:
    """Use Claude to break an answer into atomic claims."""
    # TODO: Call anthropic_client.messages.create() with DECOMPOSE_PROMPT.
    #       Parse response as JSON. Return list of claim strings.
    #       Wrap in try/except json.JSONDecodeError — return [answer] as fallback.
    return [answer]  # ← replace with real implementation


def check_claim_supported(claim: str, context: str) -> bool:
    """Ask Claude whether a claim is supported by the context."""
    # TODO: Call anthropic_client.messages.create() with CHECK_CLAIM_PROMPT.
    #       Return True if response starts with "SUPPORTED", else False.
    return True  # ← replace with real implementation


def compute_faithfulness(answer: str, context: str) -> float:
    """
    Fraction of answer claims that are supported by the retrieved context.
    Score range: [0.0, 1.0]
    """
    # TODO:
    #   1. claims = decompose_answer(answer)
    #   2. If empty or only "No factual claims.", return 1.0.
    #   3. For each claim, call check_claim_supported(claim, context).
    #   4. Return supported / total.
    return 1.0  # ← replace with real implementation


def generate_hypothetical_questions(answer: str) -> list[str]:
    """Generate 3 questions that the answer would address."""
    # TODO: Call anthropic_client.messages.create() with GENERATE_QUESTIONS_PROMPT.
    #       Parse as JSON. Fallback: return [answer].
    return []  # ← replace with real implementation


def _embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of texts. Returns numpy array shape (N, 1536)."""
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.array([item.embedding for item in response.data])


def compute_answer_relevancy(question: str, answer: str) -> float:
    """
    How well does the answer address the question?
    Algorithm: generate hypothetical questions from the answer, embed them
    and the original question, return average cosine similarity.
    Score range: [0.0, 1.0]
    """
    # TODO:
    #   1. hyp_questions = generate_hypothetical_questions(answer)
    #   2. If empty, return 0.5 as a neutral fallback.
    #   3. embeddings = _embed_texts([question] + hyp_questions)
    #   4. query_vec = embeddings[0], hyp_vecs = embeddings[1:]
    #   5. Compute cosine similarity between query_vec and each hyp_vec.
    #   6. Return mean similarity.
    return 0.5  # ← replace with real implementation


def run_evaluation(test_file: str, rag_fn, verbose: bool = True) -> dict:
    """
    Run RAGAS evaluation on a JSONL test set.

    Args:
        test_file: Path to JSONL file with {"question": ..., "expected_answer": ...} lines.
        rag_fn: Callable (question: str) -> (answer: str, context: str)
        verbose: Print per-question scores.
    """
    with open(test_file) as f:
        test_cases = [json.loads(line) for line in f if line.strip()]

    faithfulness_scores, relevancy_scores, per_question = [], [], []

    for i, case in enumerate(test_cases, start=1):
        question = case["question"]
        if verbose:
            print(f"  [{i}/{len(test_cases)}] {question[:60]}...")

        # TODO: Call rag_fn(question) to get (answer, context).
        #       Compute faithfulness = compute_faithfulness(answer, context).
        #       Compute relevancy = compute_answer_relevancy(question, answer).
        #       Append scores. Wrap in try/except — log error, use 0.0 fallback.
        pass  # ← replace with real implementation

    avg_faith = sum(faithfulness_scores) / max(len(faithfulness_scores), 1)
    avg_rel = sum(relevancy_scores) / max(len(relevancy_scores), 1)
    return {
        "faithfulness": avg_faith,
        "answer_relevancy": avg_rel,
        "per_question": per_question,
        "num_evaluated": len(faithfulness_scores),
    }


# ===========================================================================
# CORE RAG FUNCTIONS (from Project 2)
# ===========================================================================

def embed_query(query: str) -> tuple[list[float], int]:
    """Embed a query. Returns (vector, token_count)."""
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    return response.data[0].embedding, response.usage.total_tokens


def generate_answer(question: str, context: str) -> tuple[str, int, int]:
    """
    Call Claude to generate an answer grounded in context.
    Returns (answer_text, input_tokens, output_tokens).
    """
    system = (
        "You are a helpful assistant answering questions from a personal knowledge base. "
        "Answer ONLY using the provided sources. Cite sources as [SOURCE N]. "
        "If the answer is not in the sources, say: "
        "'I don't have information about that in the knowledge base.'"
    )
    user_msg = f"Sources:\n{context}\n\nQuestion: {question}\n\nAnswer (with citations):"

    # TODO: Call anthropic_client.messages.create() with GENERATION_MODEL.
    #       Return (response.content[0].text, response.usage.input_tokens, response.usage.output_tokens)
    return "TODO: implement generate_answer()", 0, 0  # ← replace with real implementation


# ===========================================================================
# PRODUCTION QUERY PIPELINE
# ===========================================================================

def handle_query(query: str, cache: SemanticCache) -> None:
    """
    Full production pipeline:
    input guardrails -> cache lookup -> RAG -> output guardrails
    -> cache store -> log stats -> display
    """
    start_time = time.time()
    db_conn = cache.conn

    # Step 1: Input guardrails
    guard_result = check_input(query)
    if not guard_result.is_safe:
        print(f"\n[GUARDRAIL] Input rejected: {guard_result.reason}")
        log_query(db_conn, query, cache_hit=False, blocked=True)
        return

    # Step 2: Embed query
    query_embedding, embed_tokens = embed_query(query)

    # Step 3: Cache lookup
    # Note: calling cache.lookup() here embeds again internally.
    # To avoid double-embedding, extend SemanticCache with a
    # lookup_by_embedding() method and pass query_embedding directly.
    cache_result = cache.lookup(query)  # ← acceptable duplication for this project

    if cache_result:
        similarity = cache_result.get("similarity", 1.0)
        print(f"\n[CACHE HIT] Similarity: {similarity:.3f} (threshold: {CACHE_THRESHOLD})")
        print(f"[COST] Cache hit — $0.00\n")
        print(f"Answer:\n{cache_result['answer']}")
        print("\nSources (cached):")
        for s in cache_result["sources"]:
            print(f"  {s}")
        log_query(db_conn, query, cache_hit=True, cost_usd=0.0)
        return

    # Step 4: Full RAG pipeline
    # NOTE: ChromaDB retrieval is commented out below.
    # Uncomment and implement retrieve_chunks() once you have chroma_db/ from Project 2.
    print("[CACHE MISS] Retrieving...")
    # chunks = retrieve_chunks(query_embedding)       # ← uncomment for real retrieval
    # context = assemble_context(chunks)              # ← uncomment for real retrieval
    # sources = get_sources_list(chunks)              # ← uncomment for real retrieval
    context = "TODO: retrieve real chunks from ChromaDB"  # ← placeholder
    sources = []                                          # ← placeholder

    print("[GENERATING] Calling Claude...")
    answer, input_tokens, output_tokens = generate_answer(query, context)

    # Step 5: Output guardrails
    out_guard = check_output(answer)
    if not out_guard.is_safe:
        print(f"\n[GUARDRAIL] Output blocked: {out_guard.reason}")
        log_query(db_conn, query, cache_hit=False, blocked=True)
        return
    if out_guard.reason:
        print(f"[WARNING] {out_guard.reason}")

    # Step 6: Cost calculation
    cost = calculate_cost(embed_tokens, input_tokens, output_tokens, GENERATION_MODEL)
    latency_ms = int((time.time() - start_time) * 1000)
    print(f"[COST] ${cost:.6f} "
          f"(embed: {embed_tokens}tok, input: {input_tokens}tok, output: {output_tokens}tok)"
          f" | {latency_ms}ms")

    # Step 7: Store in cache
    cache.store(query, query_embedding, answer, sources)
    print("[CACHED] Stored in semantic cache.")

    # Step 8: Log stats
    log_query(db_conn, query, cache_hit=False,
              embed_tokens=embed_tokens, input_tokens=input_tokens,
              output_tokens=output_tokens, cost_usd=cost, latency_ms=latency_ms)

    # Step 9: Display
    print(f"\nAnswer:\n{answer}")
    if sources:
        print("\nSources:")
        for s in sources:
            print(f"  {s}")
    print()


def handle_command(command: str, cache: SemanticCache) -> None:
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
            print('Create it with {"question": ..., "expected_answer": ...} lines.')
            return
        print(f"Running evaluation on {test_file}...")

        def rag_fn(question):
            embedding, _ = embed_query(question)
            # TODO: retrieve real chunks here once ChromaDB is wired up
            context = "placeholder context"
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
            s = cache.stats()
            print(f"Cache entries: {s['total_entries']}, Total hits: {s['total_hits']}, Threshold: {s['threshold']}")
        else:
            print("Usage: /cache clear | /cache stats")
    else:
        print(f"Unknown command: {command}")
        print("Commands: /stats, /eval, /cache clear, /cache stats")


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    print("=" * 60)
    print("  Production RAG System — Project 10")
    print("  Semantic cache | Guardrails | Cost tracking | RAGAS eval")
    print("=" * 60)
    print("Commands: /stats, /eval, /cache clear, /cache stats, quit\n")

    cache = SemanticCache(db_path=DB_PATH, threshold=CACHE_THRESHOLD)

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
            handle_command(user_input, cache)
        else:
            handle_query(user_input, cache)


if __name__ == "__main__":
    main()
