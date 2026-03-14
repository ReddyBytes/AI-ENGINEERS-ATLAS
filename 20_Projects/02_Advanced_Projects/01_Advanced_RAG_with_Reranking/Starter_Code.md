# Project 1: Starter Code

> Copy this into `advanced_rag.py`. All `# TODO:` blocks are yours to implement. The skeleton runs without errors — fill in each TODO to unlock the next stage.

```python
"""
Advanced RAG Pipeline with HyDE, Hybrid Search, Reranking, and RAGAS Evaluation
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

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EMBED_MODEL = "all-MiniLM-L6-v2"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
LLM_MODEL = "claude-sonnet-4-6"
CHROMA_PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "advanced_rag_docs"
BM25_TOP_K = 10
VECTOR_TOP_K = 10
RERANK_TOP_N = 5
RRF_K = 60  # Standard RRF constant


# ─────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# Document Store (ChromaDB + BM25)
# ─────────────────────────────────────────────

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

        # TODO: Build BM25 index
        # Steps:
        #   1. Tokenize each chunk's text (lowercase, split on whitespace/punctuation)
        #   2. Store tokenized corpus as self._tokenized_corpus
        #   3. Build BM25Okapi from tokenized corpus and assign to self.bm25
        # Hint: simple tokenize = text.lower().split()
        # Replace the line below with your implementation
        self._tokenized_corpus = []
        self.bm25 = None
        # END TODO

        print(f"[Store] Indexed {len(chunks)} chunks into ChromaDB and BM25.")

    def vector_search(self, query_text: str, n_results: int = VECTOR_TOP_K) -> list[RetrievedChunk]:
        """Semantic search using ChromaDB."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        retrieved = []
        for i, (doc_id, text, meta, distance) in enumerate(zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            chunk = Chunk(
                doc_id=meta["doc_id"],
                chunk_id=doc_id,
                text=text,
                source=meta["source"],
            )
            # ChromaDB returns L2 distance; convert to similarity score
            score = 1.0 / (1.0 + distance)
            retrieved.append(RetrievedChunk(chunk=chunk, score=score, retrieval_method="vector"))
        return retrieved

    def bm25_search(self, query_text: str, n_results: int = BM25_TOP_K) -> list[RetrievedChunk]:
        """Keyword search using BM25."""
        if self.bm25 is None:
            print("[BM25] Index not built — skipping BM25 retrieval.")
            return []

        # TODO: Implement BM25 search
        # Steps:
        #   1. Tokenize query_text the same way as corpus
        #   2. Call self.bm25.get_scores(tokenized_query) to get scores for all chunks
        #   3. Get top n_results indices (np.argsort descending)
        #   4. Return list of RetrievedChunk objects with retrieval_method="bm25"
        # Replace the return below with your implementation
        return []
        # END TODO


# ─────────────────────────────────────────────
# HyDE: Hypothetical Document Embedding
# ─────────────────────────────────────────────

class HyDEGenerator:
    """
    Generate a hypothetical answer to a question, then use that
    for retrieval instead of the raw question.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate(self, question: str) -> str:
        """
        TODO: Implement HyDE generation.
        Steps:
          1. Write a prompt that asks Claude to generate a factual, document-like
             paragraph that would answer the question.
          2. Instruct it to be specific, use authoritative language, keep it under 200 words.
          3. Call self.client.messages.create() with model=LLM_MODEL
          4. Return the response text.

        The returned text should read like a passage from a reference document,
        not like a chat answer.
        """
        # Replace this placeholder with your implementation
        return question  # Fallback: use raw question if not implemented


# ─────────────────────────────────────────────
# Hybrid Retriever with RRF Fusion
# ─────────────────────────────────────────────

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
        Formula: score(doc) = sum over lists of 1 / (k + rank)
        where rank is 1-based position in each list.

        Steps:
          1. Build a dict mapping chunk_id -> RRF score
          2. For BM25 results: for each position i (0-indexed), add 1/(k + i+1)
          3. For vector results: same
          4. Deduplicate: if a chunk appears in both lists, its scores are summed
          5. Sort by RRF score descending
          6. Return as list of RetrievedChunk, preserving the chunk object from
             whichever list it first appeared in

        Hint: build two dicts — one for scores, one mapping id->chunk — then merge.
        """
        # Replace this return with your implementation
        # For now, return a simple concatenation (no proper fusion)
        seen = {}
        combined = []
        for rc in bm25_results + vector_results:
            if rc.chunk.chunk_id not in seen:
                seen[rc.chunk.chunk_id] = True
                combined.append(rc)
        return combined
        # END TODO

    def retrieve(self, query: str, hyde_query: str) -> list[RetrievedChunk]:
        """
        Retrieve using both BM25 (on original query) and vector (on HyDE query),
        then merge with RRF.
        """
        print(f"[BM25]   Retrieving with original query...")
        bm25_results = self.store.bm25_search(query, n_results=BM25_TOP_K)
        print(f"[BM25]   Got {len(bm25_results)} results")

        print(f"[Vector] Retrieving with HyDE query...")
        vector_results = self.store.vector_search(hyde_query, n_results=VECTOR_TOP_K)
        print(f"[Vector] Got {len(vector_results)} results")

        merged = self._reciprocal_rank_fusion(bm25_results, vector_results)
        print(f"[Merged] {len(merged)} unique candidates after RRF")
        return merged


# ─────────────────────────────────────────────
# Cross-Encoder Reranker
# ─────────────────────────────────────────────

class Reranker:
    """
    Uses a cross-encoder model to rerank retrieved candidates.
    Slower but more accurate than bi-encoder similarity.
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
          1. Build a list of (query, chunk_text) pairs from candidates
          2. Call self.model.predict(pairs) — returns array of scores
          3. Attach each score to the corresponding RetrievedChunk
          4. Sort by score descending, return top_n

        Note: cross-encoder scores are NOT probabilities — they're raw logits.
        Higher is better. Typical range is roughly -10 to +10.
        """
        if not candidates:
            return []

        # Replace this placeholder with your implementation
        print(f"[Rerank] Selecting top {top_n} from {len(candidates)} candidates")
        return candidates[:top_n]
        # END TODO


# ─────────────────────────────────────────────
# Answer Generator
# ─────────────────────────────────────────────

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
          2. Build a system prompt that instructs Claude to:
               - Answer ONLY from the provided context
               - Cite source IDs inline (e.g., [doc_042])
               - If the answer isn't in the context, say so explicitly
               - Keep the answer concise (under 200 words)
          3. Call Claude with the formatted context + question
          4. Parse cited source IDs from the response (regex on [doc_*] pattern)
          5. Return (answer_text, cited_ids)
        """
        # Build context string
        context_parts = []
        for rc in context_chunks:
            context_parts.append(
                f"[Source: {rc.chunk.chunk_id}]\n{rc.chunk.text}"
            )
        context_str = "\n\n".join(context_parts)

        # TODO: Replace this placeholder call with your grounded answer prompt
        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=512,
            system="You are a helpful assistant. Answer questions based only on provided context.",
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n{context_str}\n\nQuestion: {question}"
                }
            ],
        )
        answer = response.content[0].text

        # TODO: Extract cited source IDs from answer text using regex
        # Pattern: find all occurrences of [Source_ID] in the answer
        cited_ids = []

        return answer, cited_ids
        # END TODO


# ─────────────────────────────────────────────
# Full Pipeline
# ─────────────────────────────────────────────

class AdvancedRAGPipeline:
    """
    Orchestrates: HyDE → Hybrid Retrieval → Reranking → Answer Generation
    """

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


# ─────────────────────────────────────────────
# RAGAS Evaluation
# ─────────────────────────────────────────────

def run_ragas_evaluation(pipeline: AdvancedRAGPipeline, golden_dataset: list[dict]) -> dict:
    """
    TODO: Implement RAGAS evaluation.

    Each item in golden_dataset has keys:
        - "question": str
        - "ground_truth": str  (ideal answer)
        - "contexts": list[str]  (relevant chunk texts that should be retrieved)

    Steps:
      1. For each golden item, run pipeline.query(item["question"])
      2. Build a ragas-compatible dataset:
           {
             "question": question,
             "answer": rag_result.final_answer,
             "contexts": [rc.chunk.text for rc in rag_result.reranked_chunks],
             "ground_truth": item["ground_truth"],
           }
      3. Convert to HuggingFace Dataset
      4. Call ragas.evaluate() with metrics:
           [faithfulness, answer_relevancy, context_recall]
      5. Return the scores dict

    Import hints:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_recall
        from datasets import Dataset

    Note: RAGAS uses an LLM internally. You'll need to configure it to use
    your preferred model. Check ragas docs for langchain_anthropic integration.
    """
    # TODO: Implement this function
    print("[RAGAS] Evaluation not yet implemented — complete the TODO above.")
    return {"faithfulness": 0.0, "answer_relevancy": 0.0, "context_recall": 0.0}


# ─────────────────────────────────────────────
# Corpus Loading Utilities
# ─────────────────────────────────────────────

def load_corpus_from_file(filepath: str) -> list[Chunk]:
    """Load and chunk a text file. Each paragraph becomes one chunk."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
    chunks = []
    for i, para in enumerate(paragraphs):
        chunks.append(Chunk(
            doc_id=f"doc_{i:04d}",
            chunk_id=f"chunk_{i:04d}",
            text=para,
            source=filepath,
        ))
    print(f"[Corpus] Loaded {len(chunks)} chunks from {filepath}")
    return chunks


def load_sample_corpus() -> list[Chunk]:
    """
    TODO: Load a real corpus for testing.
    Option A: Create corpus/sample_docs.txt with 30+ paragraphs and call
              load_corpus_from_file("corpus/sample_docs.txt")
    Option B: Use the datasets library to pull from Wikipedia or another source.
    Option C: Use the hardcoded sample below (too small for good RAGAS results).
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


# ─────────────────────────────────────────────
# Golden Dataset for RAGAS
# ─────────────────────────────────────────────

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
    # TODO: Add 18 more golden Q&A pairs based on your corpus
]


# ─────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────

def main():
    # Build pipeline
    pipeline = AdvancedRAGPipeline()

    # Load and index corpus
    corpus = load_sample_corpus()
    pipeline.index(corpus)

    # Test queries
    test_questions = [
        "What is retrieval-augmented generation?",
        "How do cross-encoders differ from bi-encoders?",
        "Why do language models hallucinate?",
    ]

    results = []
    for q in test_questions:
        result = pipeline.query(q)
        results.append(result)

    # RAGAS Evaluation
    print("\n" + "="*60)
    print("Running RAGAS Evaluation...")
    print("="*60)
    scores = run_ragas_evaluation(pipeline, GOLDEN_DATASET)
    print("\nRAGAS Scores:")
    for metric, score in scores.items():
        print(f"  {metric:25s}: {score:.3f}")


if __name__ == "__main__":
    main()
```
