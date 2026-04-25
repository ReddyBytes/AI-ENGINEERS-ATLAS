"""
Advanced RAG Pipeline — Project 11 SOLUTION
=============================================
HyDE + Hybrid Search (BM25 + Vector) + Cross-Encoder Reranking + RAGAS Evaluation

Usage:
    python solution.py

Setup:
    pip install anthropic chromadb rank_bm25 sentence-transformers ragas datasets pandas

Set ANTHROPIC_API_KEY in your environment.
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

        # Build BM25 index: lowercase + whitespace tokenization
        self._tokenized_corpus = [c.text.lower().split() for c in chunks]  # ← tokenize each chunk
        self.bm25 = BM25Okapi(self._tokenized_corpus)                       # ← build inverted index

        print(f"[Store] Indexed {len(chunks)} chunks into ChromaDB and BM25.")

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

        query_tokens = query_text.lower().split()                    # ← same tokenization as index
        scores = self.bm25.get_scores(query_tokens)                  # ← BM25 score array (one per chunk)
        top_indices = np.argsort(scores)[::-1][:n_results]           # ← descending sort, take top N

        return [
            RetrievedChunk(
                chunk=self.chunks[i],
                score=float(scores[i]),
                retrieval_method="bm25",
            )
            for i in top_indices
            if scores[i] > 0  # ← skip chunks with zero overlap
        ]


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
        Generate a document-like paragraph that would answer the question.
        Uses authoritative, reference-document language to match the vocabulary
        of real documents in the index — this is what makes HyDE work.
        """
        prompt = (
            f'Given the question: "{question}"\n'
            "Write a factual, detailed paragraph that would answer this question. "
            "Be specific and use authoritative, reference-document language. "
            "Write as if you are an expert producing a technical reference. "
            "Keep it under 200 words. Do not use caveats or conversational language."
        )
        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=250,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


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
        Reciprocal Rank Fusion merges two ranked lists.
        Formula: score(doc) = sum of 1/(k + rank) over all lists (1-based rank).
        Docs appearing in both lists get their scores summed — the natural dedup.
        """
        scores: dict[str, float] = {}           # ← accumulated RRF scores per chunk_id
        chunk_map: dict[str, RetrievedChunk] = {}  # ← chunk_id -> RetrievedChunk for reconstruction

        # Process BM25 results (1-based rank)
        for rank, rc in enumerate(bm25_results, start=1):
            cid = rc.chunk.chunk_id
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)  # ← RRF contribution
            chunk_map[cid] = rc

        # Process vector results (1-based rank)
        for rank, rc in enumerate(vector_results, start=1):
            cid = rc.chunk.chunk_id
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)  # ← adds to existing score if in both lists
            if cid not in chunk_map:
                chunk_map[cid] = rc  # ← preserve chunk object from first list if already seen

        # Sort by RRF score descending
        sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

        # Rebuild as RetrievedChunk list with RRF score
        result = []
        for cid in sorted_ids:
            rc = chunk_map[cid]
            result.append(RetrievedChunk(
                chunk=rc.chunk,
                score=scores[cid],         # ← replace original score with RRF score
                retrieval_method="rrf",
            ))
        return result

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
        Cross-encoder scores (query, passage) pairs jointly — full attention between
        query and document tokens makes this more accurate than bi-encoder cosine similarity.
        Scores are raw logits (roughly -10 to +10); higher = more relevant.
        """
        if not candidates:
            return []

        print(f"[Rerank] Scoring {len(candidates)} candidates with cross-encoder...")

        pairs = [(query, rc.chunk.text) for rc in candidates]  # ← (query, doc) pairs for cross-encoder
        scores = self.model.predict(pairs)                       # ← returns numpy array of logit scores

        # Sort by cross-encoder score descending
        scored = list(zip(scores, candidates))
        scored.sort(key=lambda x: x[0], reverse=True)

        # Take top_n and update scores to cross-encoder logits
        result = []
        for score, rc in scored[:top_n]:
            result.append(RetrievedChunk(
                chunk=rc.chunk,
                score=float(score),        # ← cross-encoder logit replaces RRF score
                retrieval_method="reranked",
            ))

        print(f"[Rerank] Selected top {len(result)} from {len(candidates)} candidates")
        return result


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
        Build a grounded answer using ONLY the retrieved context.
        Each chunk is labeled with its chunk_id so the model can cite it inline.
        Regex extracts cited IDs from brackets in the response.
        """
        # Format each chunk with its source ID so model can cite it
        context_parts = []
        for rc in context_chunks:
            context_parts.append(f"[Source: {rc.chunk.chunk_id}]\n{rc.chunk.text}")
        context_str = "\n\n".join(context_parts)

        system_prompt = (
            "Answer ONLY from the provided context. "
            "Cite source IDs inline as [chunk_id] (e.g. [chunk_0002]). "
            "If the answer is not in the context, say 'The provided context does not contain this information.' "
            "Keep your answer under 200 words."
        )

        response = self.client.messages.create(
            model=LLM_MODEL,
            max_tokens=512,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {question}"}
            ],
        )
        answer = response.content[0].text

        # Extract all [bracket_content] citations from the answer
        cited_ids = re.findall(r'\[([^\]]+)\]', answer)  # ← matches [anything_in_brackets]

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

        # Stage 1: HyDE — generate a hypothetical document to use as the vector query
        print("\n[HyDE] Generating hypothetical answer...")
        hypothetical = self.hyde.generate(question)
        print(f"[HyDE] {len(hypothetical.split())} words generated")

        # Stage 2: Hybrid Retrieval — BM25 on original query + vector on HyDE query → RRF merge
        candidates = self.retriever.retrieve(question, hyde_query=hypothetical)

        # Stage 3: Reranking — cross-encoder scores (query, passage) pairs jointly
        reranked = self.reranker.rerank(question, candidates)
        print(f"[Rerank] Top {len(reranked)} chunks selected")

        # Stage 4: Answer Generation — grounded, citation-bearing answer
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
    Evaluate the pipeline using RAGAS metrics:
      - faithfulness: is the answer grounded in the retrieved context?
      - answer_relevancy: does the answer address the question?
      - context_recall: does the retrieved context cover the ground truth?
    """
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_recall
        from datasets import Dataset

        ragas_data = []
        for item in golden_dataset:
            print(f"[RAGAS] Running query: {item['question'][:50]}...")
            rag_result = pipeline.query(item["question"])

            ragas_data.append({
                "question": item["question"],
                "answer": rag_result.final_answer,
                "contexts": [rc.chunk.text for rc in rag_result.reranked_chunks] or [""],  # ← RAGAS needs non-empty list
                "ground_truth": item["ground_truth"],
            })

        # Convert to HuggingFace Dataset — RAGAS requires this format
        ds = Dataset.from_list(ragas_data)

        print("[RAGAS] Running evaluation (calls LLM internally)...")
        result = evaluate(ds, metrics=[faithfulness, answer_relevancy, context_recall])

        scores = {
            "faithfulness": float(result["faithfulness"]),
            "answer_relevancy": float(result["answer_relevancy"]),
            "context_recall": float(result["context_recall"]),
        }
        return scores

    except ImportError:
        print("[RAGAS] Not installed. Run: pip install ragas datasets")
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
    """Load a built-in sample corpus covering AI/ML topics for testing."""
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

        "HyDE (Hypothetical Document Embeddings) generates a hypothetical answer to a question "
        "and uses that answer as the vector search query. This bridges the vocabulary gap between "
        "a short user question and the longer documents it should retrieve.",

        "Reciprocal Rank Fusion (RRF) merges multiple ranked lists by summing reciprocal ranks. "
        "A document at rank 1 in any list contributes 1/(k+1) to its score. Documents appearing "
        "in multiple lists accumulate higher scores and naturally rise to the top.",

        "Fine-tuning adapts a pretrained model to a specific task using a small labeled dataset. "
        "LoRA (Low-Rank Adaptation) is a parameter-efficient technique that trains only two small "
        "adapter matrices per layer, reducing trainable parameters by over 99%.",

        "Prompt engineering involves designing input prompts to elicit desired behavior from "
        "language models without changing model weights. Techniques include few-shot examples, "
        "chain-of-thought reasoning, and structured output formatting.",

        "Embedding models convert text into dense numerical vectors where similar texts map to "
        "nearby points in vector space. Models like all-MiniLM-L6-v2 produce 384-dimensional "
        "vectors and balance speed with semantic accuracy.",

        "Context window size determines how much text a language model can process in one call. "
        "Modern models support 100k to 1M tokens, enabling retrieval over entire codebases or "
        "long documents without chunking.",
    ]
    return [
        Chunk(doc_id=f"doc_{i:04d}", chunk_id=f"chunk_{i:04d}", text=t, source="sample")
        for i, t in enumerate(sample_texts)
    ]


# ---------------------------------------------------------------------------
# Golden Dataset — 20 Q&A pairs covering the sample corpus
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
    {
        "question": "How does BM25 rank documents?",
        "ground_truth": "BM25 ranks documents using term frequency and inverse document frequency.",
        "contexts": ["The BM25 algorithm is a bag-of-words retrieval function that ranks documents based on term frequency and inverse document frequency."],
    },
    {
        "question": "What is the difference between cross-encoders and bi-encoders?",
        "ground_truth": "Cross-encoders process query and document jointly with full attention, giving more accurate scores. Bi-encoders encode them separately.",
        "contexts": ["Cross-encoders process query-document pairs jointly, allowing full attention between the query and document tokens."],
    },
    {
        "question": "What is HyDE and why does it help retrieval?",
        "ground_truth": "HyDE generates a hypothetical answer and uses it as the search query, bridging the vocabulary gap between short questions and long documents.",
        "contexts": ["HyDE (Hypothetical Document Embeddings) generates a hypothetical answer to a question and uses that answer as the vector search query."],
    },
    {
        "question": "How does Reciprocal Rank Fusion work?",
        "ground_truth": "RRF merges ranked lists by summing 1/(k+rank) scores. Documents appearing in multiple lists accumulate higher scores.",
        "contexts": ["Reciprocal Rank Fusion (RRF) merges multiple ranked lists by summing reciprocal ranks."],
    },
    {
        "question": "What is LoRA?",
        "ground_truth": "LoRA is a parameter-efficient fine-tuning technique that trains only two small adapter matrices per layer, reducing trainable parameters by over 99%.",
        "contexts": ["LoRA (Low-Rank Adaptation) is a parameter-efficient technique that trains only two small adapter matrices per layer."],
    },
    {
        "question": "What are vector databases used for?",
        "ground_truth": "Vector databases store high-dimensional embeddings and support approximate nearest neighbor search for similarity search at scale.",
        "contexts": ["Vector databases store high-dimensional embeddings and support approximate nearest neighbor search."],
    },
    {
        "question": "What architecture dominates modern language modeling?",
        "ground_truth": "The transformer architecture, introduced in 2017, enables parallel sequence processing and is the dominant paradigm for language modeling.",
        "contexts": ["The transformer architecture, introduced in 2017, enables parallel processing of sequences."],
    },
    {
        "question": "What is prompt engineering?",
        "ground_truth": "Prompt engineering involves designing input prompts to elicit desired behavior from language models without changing model weights.",
        "contexts": ["Prompt engineering involves designing input prompts to elicit desired behavior from language models without changing model weights."],
    },
    {
        "question": "What dimensionality do embedding models like all-MiniLM-L6-v2 produce?",
        "ground_truth": "all-MiniLM-L6-v2 produces 384-dimensional vectors.",
        "contexts": ["Models like all-MiniLM-L6-v2 produce 384-dimensional vectors and balance speed with semantic accuracy."],
    },
    {
        "question": "What context window sizes do modern LLMs support?",
        "ground_truth": "Modern models support 100k to 1M tokens, enabling retrieval over entire codebases without chunking.",
        "contexts": ["Modern models support 100k to 1M tokens, enabling retrieval over entire codebases or long documents without chunking."],
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    pipeline = AdvancedRAGPipeline()

    print("\n[Setup] Loading sample corpus...")
    corpus = load_sample_corpus()
    # To use a real corpus: corpus = load_corpus_from_file("corpus/sample_docs.txt")
    pipeline.index(corpus)

    test_questions = [
        "What is retrieval-augmented generation?",
        "How do cross-encoders differ from bi-encoders?",
        "Why do language models hallucinate?",
        "What is HyDE and how does it improve retrieval?",
    ]

    results = []
    for q in test_questions:
        result = pipeline.query(q)
        results.append(result)

    print("\n" + "="*60)
    print("Summary of results:")
    print("="*60)
    for r in results:
        print(f"\nQ: {r.question}")
        print(f"A: {r.final_answer[:150]}...")
        print(f"Sources cited: {r.cited_sources}")

    print("\n" + "="*60)
    print("Running RAGAS Evaluation on golden dataset...")
    print("="*60)
    scores = run_ragas_evaluation(pipeline, GOLDEN_DATASET[:3])  # subset to save API calls
    print("\nRAGAS Scores:")
    for metric, score in scores.items():
        status = "GOOD" if score >= 0.75 else "NEEDS WORK"
        print(f"  {metric:25s}: {score:.3f}  ({status})")


if __name__ == "__main__":
    main()
