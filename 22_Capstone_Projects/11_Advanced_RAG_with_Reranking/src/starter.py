"""
Advanced RAG Pipeline — Project 11
======================================
HyDE + Hybrid Search (BM25 + Vector) + Cross-Encoder Reranking + RAGAS Evaluation

Usage:
    python starter.py

Setup:
    pip install anthropic chromadb rank_bm25 sentence-transformers ragas datasets pandas

Set ANTHROPIC_API_KEY in your environment or .env file.
Prepare corpus/sample_docs.txt with 30+ paragraphs before running.
"""

import os
import re
import json
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import anthropic
import chromadb
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EMBED_MODEL = "all-MiniLM-L6-v2"                           # local embedding model  # ←
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"      # local cross-encoder   # ←
LLM_MODEL = "claude-sonnet-4-6"
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "advanced_rag_docs"
BM25_TOP_K = 10
VECTOR_TOP_K = 10
RERANK_TOP_N = 5
RRF_K = 60          # standard RRF constant — higher k reduces the weight of rank differences  # ←


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """A single document chunk with metadata."""
    doc_id: str
    chunk_id: str
    text: str
    source: str = ""


@dataclass
class RetrievedChunk:
    """A chunk with its retrieval score."""
    chunk: Chunk
    score: float
    retrieval_method: str = ""


@dataclass
class RAGResult:
    """Full output of one RAG query."""
    question: str
    hypothetical_answer: str
    retrieved_chunks: list[RetrievedChunk]
    reranked_chunks: list[RetrievedChunk]
    final_answer: str
    cited_sources: list[str]


# ---------------------------------------------------------------------------
# Document Store — ChromaDB + BM25
# ---------------------------------------------------------------------------

class DocumentStore:
    """
    Dual-index document store: ChromaDB for semantic search, BM25 for keyword search.
    """

    def __init__(self, persist_dir: str = CHROMA_PERSIST_DIR):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBED_MODEL
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embed_fn,
        )
        self.chunks: list[Chunk] = []
        self.bm25: Optional[BM25Okapi] = None
        self._tokenized_corpus: list[list[str]] = []

    def add_documents(self, chunks: list[Chunk]) -> None:
        """Index a list of chunks into both ChromaDB and BM25."""
        self.chunks = chunks

        # Index into ChromaDB
        self.collection.add(
            documents=[c.text for c in chunks],
            ids=[c.chunk_id for c in chunks],
            metadatas=[{"doc_id": c.doc_id, "source": c.source} for c in chunks],
        )

        # TODO: Build BM25 index.
        #   1. Tokenize each chunk: text.lower().split()
        #   2. Store as self._tokenized_corpus
        #   3. self.bm25 = BM25Okapi(self._tokenized_corpus)
        self._tokenized_corpus = []  # ← replace with real tokenization
        self.bm25 = None             # ← replace with BM25Okapi(self._tokenized_corpus)

        print(f"[Store] Indexed {len(chunks)} chunks.")

    def vector_search(self, query_text: str, n_results: int = VECTOR_TOP_K) -> list[RetrievedChunk]:
        """Semantic search using ChromaDB."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        retrieved = []
        for doc_id, text, meta, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunk = Chunk(
                doc_id=meta["doc_id"],
                chunk_id=doc_id,
                text=text,
                source=meta["source"],
            )
            score = 1.0 / (1.0 + distance)  # ← convert L2 distance to similarity score
            retrieved.append(RetrievedChunk(chunk=chunk, score=score, retrieval_method="vector"))
        return retrieved

    def bm25_search(self, query_text: str, n_results: int = BM25_TOP_K) -> list[RetrievedChunk]:
        """Keyword search using BM25."""
        if self.bm25 is None:
            print("[BM25] Index not built — skipping BM25 retrieval.")
            return []

        # TODO: Implement BM25 search.
        #   1. query_tokens = query_text.lower().split()
        #   2. scores = self.bm25.get_scores(query_tokens)
        #   3. top_indices = np.argsort(scores)[::-1][:n_results]
        #   4. Return list of RetrievedChunk with retrieval_method="bm25"
        #      Filter out indices where scores[i] == 0.
        return []  # ← replace with real implementation


# ---------------------------------------------------------------------------
# HyDE — Hypothetical Document Embedding
# ---------------------------------------------------------------------------

class HyDEGenerator:
    """
    Generate a hypothetical answer to use as the vector search query.
    A short user question has sparse vocabulary. A hypothetical answer
    uses the vocabulary that would appear in a relevant document.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate(self, question: str) -> str:
        """
        TODO: Generate a document-like paragraph that would answer the question.

        Prompt structure:
          - "Given the question: {question}"
          - Instruct Claude to write a factual, authoritative paragraph
          - Keep it under 200 words
          - No conversational language — it should read like a reference document

        Return: response.content[0].text
        Fallback: return question if not implemented.
        """
        return question  # ← replace with real Claude call


# ---------------------------------------------------------------------------
# Hybrid Retriever with RRF Fusion
# ---------------------------------------------------------------------------

class HybridRetriever:
    """
    Combines BM25 keyword retrieval and semantic vector retrieval
    using Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, store: DocumentStore):
        self.store = store

    def _reciprocal_rank_fusion(
        self,
        bm25_results: list[RetrievedChunk],
        vector_results: list[RetrievedChunk],
        k: int = RRF_K,
    ) -> list[RetrievedChunk]:
        """
        TODO: Implement Reciprocal Rank Fusion.
        Formula: score(doc) = sum of 1/(k + rank) over all lists (1-based rank).

        Steps:
          1. Build scores: dict[chunk_id -> float] and chunk_map: dict[chunk_id -> RetrievedChunk]
          2. For BM25 results: for rank i (1-based), scores[id] += 1/(k + i)
          3. For vector results: same
          4. Sort by accumulated score descending
          5. Return as list[RetrievedChunk] with score set to the RRF score

        Chunks appearing in both lists get their scores summed — this is the deduplication.
        """
        # Placeholder: simple concatenation without proper fusion
        seen: dict[str, bool] = {}
        combined: list[RetrievedChunk] = []
        for rc in bm25_results + vector_results:
            if rc.chunk.chunk_id not in seen:
                seen[rc.chunk.chunk_id] = True
                combined.append(rc)
        return combined  # ← replace with real RRF implementation

    def retrieve(self, query: str, hyde_query: str) -> list[RetrievedChunk]:
        """Retrieve using BM25 (original query) and vector (HyDE query), then merge."""
        print(f"[BM25]   Retrieving with original query...")
        bm25_results = self.store.bm25_search(query, n_results=BM25_TOP_K)
        print(f"[BM25]   Got {len(bm25_results)} results")

        print(f"[Vector] Retrieving with HyDE query...")
        vector_results = self.store.vector_search(hyde_query, n_results=VECTOR_TOP_K)
        print(f"[Vector] Got {len(vector_results)} results")

        merged = self._reciprocal_rank_fusion(bm25_results, vector_results)
        print(f"[Merged] {len(merged)} unique candidates after RRF")
        return merged


# ---------------------------------------------------------------------------
# Cross-Encoder Reranker
# ---------------------------------------------------------------------------

class Reranker:
    """
    Cross-encoder reranker — slower but more accurate than bi-encoder similarity.
    Takes (query, passage) pairs and scores their relevance jointly.
    """

    def __init__(self, model_name: str = RERANK_MODEL):
        print(f"[Reranker] Loading {model_name}...")
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_n: int = RERANK_TOP_N,
    ) -> list[RetrievedChunk]:
        """
        TODO: Implement cross-encoder reranking.

        Steps:
          1. pairs = [(query, rc.chunk.text) for rc in candidates]
          2. scores = self.model.predict(pairs)  — returns array of logit scores
          3. Sort candidates by score descending
          4. Return top_n with score updated to logit score

        Note: scores are raw logits, NOT probabilities. Higher = more relevant.
        Typical range is roughly -10 to +10.
        """
        if not candidates:
            return []
        print(f"[Rerank] Selecting top {top_n} from {len(candidates)} candidates")
        return candidates[:top_n]  # ← replace with real cross-encoder scoring


# ---------------------------------------------------------------------------
# Answer Generator
# ---------------------------------------------------------------------------

class AnswerGenerator:
    """Generate a grounded answer from retrieved chunks."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate(
        self,
        question: str,
        context_chunks: list[RetrievedChunk],
    ) -> tuple[str, list[str]]:
        """
        TODO: Build a grounded answer generation prompt.

        Steps:
          1. Format each chunk as:
               [Source: {chunk_id}]
               {chunk_text}
          2. System prompt: "Answer ONLY from the provided context.
             Cite source IDs inline as [chunk_id]. If the answer isn't
             in the context, say so. Keep the answer under 200 words."
          3. Call Claude with formatted context + question
          4. Extract cited source IDs from response: re.findall(r'\[([^\]]+)\]', answer)
          5. Return (answer_text, cited_ids)
        """
        context_parts = []
        for rc in context_chunks:
            context_parts.append(f"[Source: {rc.chunk.chunk_id}]\n{rc.chunk.text}")
        context_str = "\n\n".join(context_parts)

        # TODO: Replace this with a properly grounded prompt
        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=512,
            system="You are a helpful assistant. Answer questions based only on provided context.",
            messages=[
                {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {question}"}
            ],
        )
        answer = response.content[0].text

        # TODO: Extract cited source IDs using regex
        cited_ids: list[str] = []  # ← replace with real extraction

        return answer, cited_ids


# ---------------------------------------------------------------------------
# Full Pipeline
# ---------------------------------------------------------------------------

class AdvancedRAGPipeline:
    """Orchestrates: HyDE -> Hybrid Retrieval -> Reranking -> Answer Generation."""

    def __init__(self):
        self.store = DocumentStore()
        self.hyde = HyDEGenerator()
        self.retriever = HybridRetriever(self.store)
        self.reranker = Reranker()
        self.generator = AnswerGenerator()

    def index(self, chunks: list[Chunk]) -> None:
        """Index documents. Call once before querying."""
        self.store.add_documents(chunks)

    def query(self, question: str) -> RAGResult:
        """Run the full pipeline for a single question."""
        print(f"\n{'='*60}")
        print(f"Query: {question}")
        print('='*60)

        # Stage 1: HyDE
        print("\n[HyDE] Generating hypothetical answer...")
        hypothetical = self.hyde.generate(question)
        print(f"[HyDE] {len(hypothetical.split())} words generated")

        # Stage 2: Hybrid Retrieval
        candidates = self.retriever.retrieve(question, hyde_query=hypothetical)

        # Stage 3: Reranking
        reranked = self.reranker.rerank(question, candidates)
        print(f"[Rerank] Top {len(reranked)} chunks selected")

        # Stage 4: Answer Generation
        answer, cited_sources = self.generator.generate(question, reranked)
        print(f"\nAnswer:\n{answer}")
        print(f"\nSources: {cited_sources}")

        return RAGResult(
            question=question,
            hypothetical_answer=hypothetical,
            retrieved_chunks=candidates,
            reranked_chunks=reranked,
            final_answer=answer,
            cited_sources=cited_sources,
        )


# ---------------------------------------------------------------------------
# RAGAS Evaluation
# ---------------------------------------------------------------------------

def run_ragas_evaluation(pipeline: AdvancedRAGPipeline, golden_dataset: list[dict]) -> dict:
    """
    TODO: Implement RAGAS evaluation.

    Each item in golden_dataset has keys:
        "question": str
        "ground_truth": str   (ideal answer)
        "contexts": list[str] (relevant chunk texts that should be retrieved)

    Steps:
      1. For each item, run pipeline.query(item["question"])
      2. Build a ragas-compatible dict:
           {
             "question": question,
             "answer": rag_result.final_answer,
             "contexts": [rc.chunk.text for rc in rag_result.reranked_chunks],
             "ground_truth": item["ground_truth"],
           }
      3. Convert to HuggingFace Dataset
      4. Call ragas.evaluate() with:
           from ragas import evaluate
           from ragas.metrics import faithfulness, answer_relevancy, context_recall
           from datasets import Dataset
      5. Return the scores dict

    Note: RAGAS uses an LLM internally. Configure it to use your preferred model.
    """
    print("[RAGAS] Evaluation not yet implemented — complete the TODO above.")
    return {"faithfulness": 0.0, "answer_relevancy": 0.0, "context_recall": 0.0}


# ---------------------------------------------------------------------------
# Corpus Loading Utilities
# ---------------------------------------------------------------------------

def load_corpus_from_file(filepath: str) -> list[Chunk]:
    """Load and chunk a text file. Each paragraph becomes one chunk."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
    chunks = [
        Chunk(doc_id=f"doc_{i:04d}", chunk_id=f"chunk_{i:04d}", text=para, source=filepath)
        for i, para in enumerate(paragraphs)
    ]
    print(f"[Corpus] Loaded {len(chunks)} chunks from {filepath}")
    return chunks


def load_sample_corpus() -> list[Chunk]:
    """
    TODO: Load a real corpus for testing.
    Option A: Create corpus/sample_docs.txt and call load_corpus_from_file().
    Option B: Use the datasets library (Wikipedia subset).
    Option C: Use the hardcoded sample below for quick testing (too small for good RAGAS results).
    """
    sample_texts = [
        "Large language models are trained on vast corpora of text using self-supervised objectives. "
        "The transformer architecture, introduced in 2017, enables parallel processing of sequences "
        "and has become the dominant paradigm for language modeling.",

        "Retrieval-augmented generation (RAG) combines a retrieval component with a language model. "
        "The retriever finds relevant documents from an external knowledge base, and the generator "
        "conditions its output on both the query and retrieved documents.",

        "Hallucination in language models refers to the generation of factually incorrect content "
        "that sounds plausible. This occurs when the model fills gaps in its training data with "
        "confidently stated but incorrect information.",

        "Vector databases store high-dimensional embeddings and support approximate nearest neighbor "
        "search. Systems like ChromaDB, Pinecone, and Weaviate are optimized for similarity search "
        "at scale with billions of vectors.",

        "The BM25 algorithm is a bag-of-words retrieval function that ranks documents based on "
        "term frequency and inverse document frequency. It remains competitive with neural retrieval "
        "methods for keyword-heavy queries.",

        "Cross-encoders process query-document pairs jointly, allowing full attention between "
        "the query and document tokens. This gives more accurate relevance scores than bi-encoders "
        "but requires running inference on every candidate.",
    ]
    return [
        Chunk(doc_id=f"doc_{i:04d}", chunk_id=f"chunk_{i:04d}", text=t, source="sample")
        for i, t in enumerate(sample_texts)
    ]


# ---------------------------------------------------------------------------
# Golden Dataset — add 18 more Q&A pairs based on your corpus
# ---------------------------------------------------------------------------

GOLDEN_DATASET = [
    {
        "question": "What is retrieval-augmented generation?",
        "ground_truth": "RAG combines a retrieval component with a language model to condition generation on retrieved external documents.",
        "contexts": ["Retrieval-augmented generation (RAG) combines a retrieval component with a language model."],
    },
    {
        "question": "Why do language models hallucinate?",
        "ground_truth": "Hallucination occurs when models fill gaps in their training data with confidently stated but incorrect information.",
        "contexts": ["Hallucination in language models refers to the generation of factually incorrect content that sounds plausible."],
    },
    # TODO: Add 18 more golden Q&A pairs based on your corpus  # ←
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    pipeline = AdvancedRAGPipeline()

    corpus = load_sample_corpus()
    # TODO: Replace with load_corpus_from_file("corpus/sample_docs.txt") once you have a real corpus
    pipeline.index(corpus)

    test_questions = [
        "What is retrieval-augmented generation?",
        "How do cross-encoders differ from bi-encoders?",
        "Why do language models hallucinate?",
    ]

    results = []
    for q in test_questions:
        result = pipeline.query(q)
        results.append(result)

    print("\n" + "="*60)
    print("Running RAGAS Evaluation...")
    print("="*60)
    scores = run_ragas_evaluation(pipeline, GOLDEN_DATASET)
    print("\nRAGAS Scores:")
    for metric, score in scores.items():
        print(f"  {metric:25s}: {score:.3f}")


if __name__ == "__main__":
    main()
