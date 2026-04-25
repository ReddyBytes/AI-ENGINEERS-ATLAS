# Project 11 — Advanced RAG with Reranking: Build Guide

## Build Phases

| Phase | What you build | Time estimate |
|---|---|---|
| 0 | Environment setup | 15 min |
| 1 | Document corpus + dual index (ChromaDB + BM25) | 60 min |
| 2 | HyDE generator | 30 min |
| 3 | Hybrid search with RRF fusion | 45 min |
| 4 | Cross-encoder reranker | 30 min |
| 5 | Answer generation | 30 min |
| 6 | RAGAS evaluation | 60 min |

Total: approximately 4–5 hours

---

## Phase 0 — Environment Setup

### Step 1: Install dependencies

```bash
pip install anthropic chromadb rank_bm25 sentence-transformers \
    ragas langchain langchain-community datasets pandas
```

### Step 2: Set your API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Step 3: Create your file structure

```
advanced_rag/
├── corpus/          # Your documents go here
│   └── sample_docs.txt
├── src/
│   └── starter.py   # Main pipeline (from src/starter.py)
└── golden_dataset.py  # 20 Q&A pairs for evaluation
```

Theory checkpoint: Read `09_RAG_Systems/Full_Pipeline_Overview.md` before continuing.

---

## Phase 1 — Document Corpus and Dual Index

### Step 4: Prepare your documents

Create `corpus/sample_docs.txt` with at least 30 paragraphs of text on a topic of your choice. Each paragraph = one chunk. For a ready-made corpus, use a Wikipedia subset:

```python
from datasets import load_dataset
ds = load_dataset("wikipedia", "20220301.en", split="train", streaming=True)
# Take first 200 articles, chunk to 300 tokens
```

### Step 5: Implement `DocumentStore.add_documents()`

Index into both ChromaDB and BM25 simultaneously.

<details><summary>💡 Hint</summary>

For ChromaDB, the embedding function is already configured with `SentenceTransformerEmbeddingFunction`. Just call `self.collection.add(documents=..., ids=..., metadatas=...)`.

For BM25, tokenize each chunk and build the index:
```python
self._tokenized_corpus = [text.lower().split() for text in [c.text for c in chunks]]
self.bm25 = BM25Okapi(self._tokenized_corpus)
```

Store `self.chunks = chunks` so you can cross-reference ChromaDB IDs back to `Chunk` objects.

</details>

<details><summary>✅ Answer</summary>

```python
def add_documents(self, chunks: list[Chunk]) -> None:
    self.chunks = chunks
    self.collection.add(
        documents=[c.text for c in chunks],
        ids=[c.chunk_id for c in chunks],
        metadatas=[{"doc_id": c.doc_id, "source": c.source} for c in chunks],
    )
    self._tokenized_corpus = [c.text.lower().split() for c in chunks]
    self.bm25 = BM25Okapi(self._tokenized_corpus)
    print(f"[Store] Indexed {len(chunks)} chunks into ChromaDB and BM25.")
```

</details>

### Step 6: Implement `DocumentStore.bm25_search()`

<details><summary>💡 Hint</summary>

```python
query_tokens = query_text.lower().split()
scores = self.bm25.get_scores(query_tokens)          # float array, one per chunk
top_indices = np.argsort(scores)[::-1][:n_results]   # descending sort, take top N
```

Then build `RetrievedChunk` objects for each index, using `self.chunks[idx]` to get the chunk.

</details>

<details><summary>✅ Answer</summary>

```python
def bm25_search(self, query_text: str, n_results: int = BM25_TOP_K) -> list[RetrievedChunk]:
    if self.bm25 is None:
        return []
    query_tokens = query_text.lower().split()
    scores = self.bm25.get_scores(query_tokens)
    top_indices = np.argsort(scores)[::-1][:n_results]
    return [
        RetrievedChunk(chunk=self.chunks[i], score=float(scores[i]), retrieval_method="bm25")
        for i in top_indices if scores[i] > 0
    ]
```

</details>

Theory checkpoint: Read `09_RAG_Systems/07_Advanced_RAG_Techniques/Theory.md` — the hybrid search section.

---

## Phase 2 — HyDE Generator

### Step 7: Implement `HyDEGenerator.generate()`

Generate a document-like paragraph that would answer the question. This becomes the vector search query instead of the original short question.

<details><summary>💡 Hint</summary>

Prompt structure:
```
Given the question: "{question}"
Write a factual, detailed paragraph that would answer this question.
Be specific and use authoritative, reference-document language.
Keep it under 200 words.
```

The key instruction: make it sound like a passage from a reference document, not a conversational reply.

</details>

<details><summary>✅ Answer</summary>

```python
def generate(self, question: str) -> str:
    prompt = (
        f"Given the question: \"{question}\"\n"
        "Write a factual, detailed paragraph that would answer this question. "
        "Be specific, use authoritative language as if writing from a reference document. "
        "Keep it under 200 words. Do not include caveats or uncertainty — write as if you know the answer."
    )
    response = self.client.messages.create(
        model=LLM_MODEL,
        max_tokens=250,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
```

</details>

### Step 8: Compare retrieval quality with and without HyDE

Run the same query both ways and print the top-3 chunks. You should see that HyDE retrieves more topically precise chunks for complex or conceptual questions. Short factual queries ("What year was X founded?") often don't benefit much.

---

## Phase 3 — Hybrid Search with RRF Fusion

### Step 9: Implement `_reciprocal_rank_fusion()`

RRF formula: `score(doc) = sum of 1 / (k + rank)` across all lists, where rank is 1-based position and k=60.

<details><summary>💡 Hint</summary>

Build two dicts: one for accumulated RRF scores, one mapping chunk_id to the `RetrievedChunk` object.

```python
scores: dict[str, float] = {}
chunk_map: dict[str, RetrievedChunk] = {}

for rank, rc in enumerate(bm25_results, start=1):
    cid = rc.chunk.chunk_id
    scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    chunk_map[cid] = rc

for rank, rc in enumerate(vector_results, start=1):
    cid = rc.chunk.chunk_id
    scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
    if cid not in chunk_map:
        chunk_map[cid] = rc
```

Then sort by score descending and return as `RetrievedChunk` list with updated scores.

</details>

### Step 10: Test hybrid vs. single-source retrieval

Run 5 queries. For each, compare BM25 only top-5, vector only top-5, and hybrid RRF top-5. Note which approach returns more relevant chunks for keyword-heavy vs. conceptual questions.

---

## Phase 4 — Cross-Encoder Reranker

### Step 11: Implement `Reranker.rerank()`

<details><summary>💡 Hint</summary>

```python
pairs = [(query, rc.chunk.text) for rc in candidates]
scores = self.model.predict(pairs)   # returns numpy array of logit scores
```

Note: cross-encoder scores are raw logits, not probabilities. Higher is better. Typical range is roughly -10 to +10. Sort descending, take top_n.

</details>

<details><summary>✅ Answer</summary>

```python
def rerank(self, query: str, candidates: list[RetrievedChunk], top_n: int = RERANK_TOP_N) -> list[RetrievedChunk]:
    if not candidates:
        return []
    pairs = [(query, rc.chunk.text) for rc in candidates]
    scores = self.model.predict(pairs)
    scored = [(float(s), rc) for s, rc in zip(scores, candidates)]
    scored.sort(key=lambda x: x[0], reverse=True)
    result = [rc for _, rc in scored[:top_n]]
    for rc, (score, _) in zip(result, scored[:top_n]):
        rc.score = score
    print(f"[Rerank] Selected top {len(result)} from {len(candidates)} candidates")
    return result
```

</details>

### Step 12: Measure reranker impact

Compare the top-5 before and after reranking. The reranker should surface the most directly relevant chunks even when they weren't in the top positions after hybrid merge.

---

## Phase 5 — Answer Generation

### Step 13: Implement `AnswerGenerator.generate()`

<details><summary>💡 Hint</summary>

Format each chunk as:
```
[Source: {chunk_id}]
{chunk_text}
```

System prompt: "Answer ONLY from the provided context. Cite source IDs inline as [chunk_id]. If the answer isn't in the context, say so. Keep the answer under 200 words."

After getting the response, extract cited source IDs with regex: `re.findall(r'\[([^\]]+)\]', answer)`.

</details>

---

## Phase 6 — RAGAS Evaluation

### Step 14: Create a golden dataset

In `golden_dataset.py`, define 20 Q&A pairs with ground-truth answers and the chunks that should be retrieved:

```python
golden_qa = [
    {
        "question": "...",
        "ground_truth": "...",
        "contexts": ["..."],  # chunks that should be retrieved
    },
]
```

### Step 15: Wire up RAGAS

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from datasets import Dataset

result = evaluate(
    Dataset.from_list(ragas_data),
    metrics=[faithfulness, answer_relevancy, context_recall]
)
```

### Step 16: Interpret scores and improve

| If this metric is low | Check this |
|---|---|
| Faithfulness < 0.8 | Answer generation prompt is too permissive — tighten grounding instruction |
| Answer Relevance < 0.8 | Reranker not surfacing right chunks — check RRF merge |
| Context Recall < 0.8 | Retrieval missing relevant docs — check chunk size and BM25 tokenization |

Theory checkpoint: Read `09_RAG_Systems/08_RAG_Evaluation/Theory.md` to understand what each metric actually measures.

---

## Testing Checklist

- [ ] ChromaDB collection persists between runs (no re-indexing required)
- [ ] BM25 and vector results correctly merged via RRF
- [ ] HyDE generates hypothetical answers under 200 words
- [ ] Cross-encoder reranker produces scores in range [-10, 10]
- [ ] Final answer cites document IDs
- [ ] RAGAS scores print after each query
- [ ] All three RAGAS metrics above 0.75 on golden dataset

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [01_MISSION.md](./01_MISSION.md) | Project context and motivation |
| [02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and component table |
| 03_GUIDE.md | you are here |
| [src/starter.py](./src/starter.py) | Runnable Python skeleton |
| [04_RECAP.md](./04_RECAP.md) | What you learned, extensions, job mapping |

⬅️ **Prev:** [10 — Production RAG System](../10_Production_RAG_System/01_MISSION.md)
➡️ **Next:** [12 — LangGraph Support Bot](../12_LangGraph_Support_Bot/01_MISSION.md)
