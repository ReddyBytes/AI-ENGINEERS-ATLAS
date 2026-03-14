# Project 1: Step-by-Step Build Guide

## Overview

You will build the pipeline in six phases, each adding one component. At each phase you have a working (but incomplete) system you can test.

---

## Phase 0 — Environment Setup

### Step 1: Create your project directory and virtual environment

```bash
mkdir advanced_rag && cd advanced_rag
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### Step 2: Install dependencies

```bash
pip install anthropic chromadb rank_bm25 sentence-transformers \
    ragas langchain langchain-community datasets pandas
```

### Step 3: Set your API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Step 4: Create your file structure

```
advanced_rag/
├── corpus/          # Your documents go here
│   └── sample_docs.txt
├── advanced_rag.py  # Main pipeline (from Starter_Code.md)
├── evaluate.py      # RAGAS evaluation runner
└── golden_dataset.py  # 20 Q&A pairs for evaluation
```

**Theory checkpoint:** Read `09_RAG_Systems/Full_Pipeline_Overview.md` before continuing.

---

## Phase 1 — Build the Document Corpus and Basic Vector Store

### Step 5: Prepare your documents

Create `corpus/sample_docs.txt` with at least 30 paragraphs of text on a topic of your choice (e.g., AI safety, climate science, software architecture). Each paragraph = one chunk.

For a ready-made corpus, use the AI safety papers subset:
```python
from datasets import load_dataset
ds = load_dataset("wikipedia", "20220301.en", split="train", streaming=True)
# Take first 200 articles, chunk to 300 tokens
```

### Step 6: Chunk and index documents into ChromaDB

In `advanced_rag.py`, implement the `DocumentStore` class:
- Split documents into ~300-token chunks (by sentence boundary, not hard split)
- Embed each chunk using `sentence-transformers` (`all-MiniLM-L6-v2`)
- Store in a persistent ChromaDB collection

Test: `store.query("your test query", n_results=5)` should return five relevant chunks.

### Step 7: Build the BM25 index alongside

The `rank_bm25` library needs tokenized documents as input. When you index into ChromaDB, simultaneously build a `BM25Okapi` index over the same tokenized chunks.

Store the mapping `bm25_index → chromadb_id` so you can cross-reference results.

Test: `bm25_retrieve("your test query", k=10)` returns chunk IDs.

**Theory checkpoint:** Read `09_RAG_Systems/07_Advanced_RAG_Techniques/Hybrid_Search.md`.

---

## Phase 2 — Implement HyDE

### Step 8: Write the HyDE generator

Call Claude with a prompt like:

```
Given the question: "{question}"
Write a factual, detailed paragraph that would answer this question.
Be specific and use the kind of language that would appear in an authoritative document.
```

This generates a hypothetical answer. You then embed this answer (not the original question) for vector retrieval.

### Step 9: Compare retrieval quality with and without HyDE

Run the same query both ways. Print the top-3 chunks returned by each. You should see that HyDE retrieves more topically precise chunks for complex questions.

Log the difference to understand where HyDE helps and where it doesn't (short factual questions often don't benefit much).

**Theory checkpoint:** Re-read the HyDE section in `09_RAG_Systems/07_Advanced_RAG_Techniques/Theory.md`.

---

## Phase 3 — Implement Hybrid Search and Merge

### Step 10: Implement Reciprocal Rank Fusion (RRF)

BM25 returns a ranked list. Vector search returns another ranked list. Merge them with RRF:

```
score(doc) = Σ 1 / (k + rank_in_list)
```

Where `k = 60` is the standard constant. This avoids the problem of incomparable raw scores between BM25 and cosine similarity.

### Step 11: Deduplicate merged results

After merging, deduplicate by chunk ID. You should end up with 15–25 unique candidates depending on overlap.

### Step 12: Test hybrid vs. single-source retrieval

Run 5 queries. For each, compare:
- BM25 only top-5
- Vector only top-5
- Hybrid RRF top-5

Note which approach returns more relevant chunks for keyword-heavy questions vs. conceptual questions.

**Theory checkpoint:** Read `09_RAG_Systems/07_Advanced_RAG_Techniques/Hybrid_Search.md` again with code in hand.

---

## Phase 4 — Add the Cross-Encoder Reranker

### Step 13: Load the cross-encoder model

```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
```

This model takes `(query, passage)` pairs and returns a relevance score. It's slower than bi-encoder embedding but significantly more accurate.

### Step 14: Rerank the top-20 hybrid candidates

For each of your ~20 merged candidates, create the pair `(original_question, chunk_text)` and call `reranker.predict(pairs)`. Sort by score descending. Keep top 5.

### Step 15: Measure reranker impact

Compare the top-5 before and after reranking. For well-crafted test queries, you should see the reranker surface the most directly relevant chunks even when they weren't in the top positions after hybrid merge.

**Theory checkpoint:** Read `09_RAG_Systems/07_Advanced_RAG_Techniques/Reranking.md`.

---

## Phase 5 — Generate the Final Answer

### Step 16: Build the answer generation step

Concatenate the top-5 reranked chunks as context. Call Claude claude-sonnet-4-6 with a grounded answer prompt:

```
Answer the question using ONLY the provided context.
If the context doesn't contain the answer, say so.
Cite the source document IDs in your answer.

Context:
{chunk_1}
[Source: doc_id_1]
...

Question: {question}
```

### Step 17: Add source citation extraction

Parse Claude's response to extract cited document IDs. Return them alongside the answer text.

---

## Phase 6 — RAGAS Evaluation

### Step 18: Create a golden dataset

In `golden_dataset.py`, define 20 question/answer pairs that you know the correct answers to from your corpus:

```python
golden_qa = [
    {
        "question": "...",
        "ground_truth": "...",   # The ideal answer
        "contexts": ["..."],     # The chunks that should be retrieved
    },
    ...
]
```

### Step 19: Wire up RAGAS

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from datasets import Dataset

result = evaluate(
    Dataset.from_list(ragas_data),
    metrics=[faithfulness, answer_relevancy, context_recall]
)
```

RAGAS uses an LLM internally to evaluate faithfulness. Set it to use Claude via LangChain integration.

### Step 20: Interpret and improve

Run RAGAS on your 20 golden questions. If:
- **Faithfulness < 0.8:** Your answer generation prompt is too permissive — tighten the grounding instruction
- **Answer Relevance < 0.8:** Your reranker isn't surfacing the right chunks — check your RRF merge
- **Context Recall < 0.8:** Your retrieval is missing relevant documents — check chunk size and BM25 tokenization

**Theory checkpoint:** Read `09_RAG_Systems/08_RAG_Evaluation/Metrics_Guide.md` to understand what each metric actually measures.

---

## Phase 7 — Extensions (Choose One)

### Step 21a: Add query rewriting

Before HyDE, add a query rewriting step that expands ambiguous questions into multiple sub-queries. Retrieve for each sub-query and merge.

### Step 21b: Semantic cache

After generating an answer, store `(question_embedding, answer)` in a cache. On new queries, check cosine similarity to cached embeddings — if above 0.95, return cached answer directly.

### Step 21c: Evaluation dashboard

Use `pandas` + `matplotlib` to plot RAGAS metric trends across your 20 golden questions, identifying which question types perform worst.

---

## Testing Checklist

- [ ] ChromaDB collection persists between runs (no re-indexing)
- [ ] BM25 and vector results correctly merged via RRF
- [ ] HyDE generates hypothetical answers under 200 tokens
- [ ] Cross-encoder reranker produces scores in range [-10, 10]
- [ ] Final answer cites document IDs
- [ ] RAGAS scores print after each query
- [ ] All three RAGAS metrics above 0.75 on golden dataset
