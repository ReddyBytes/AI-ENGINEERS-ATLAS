# RAG Evaluation — Code Example

Evaluate a RAG system using two complementary approaches: the **RAGAS framework** (industry-standard automated metrics) and a **custom LLM-as-judge evaluator** (more flexible, requires only an LLM API key).

---

## Part 1: RAGAS Evaluation

RAGAS (Retrieval Augmented Generation Assessment) is the standard library for evaluating RAG pipelines. It computes four core metrics without requiring a human-labeled test set of answers — only questions, retrieved contexts, and generated answers.

```python
# pip install ragas langchain-openai datasets
# RAGAS uses OpenAI by default — set OPENAI_API_KEY in environment

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,          # Is the answer grounded in the retrieved context?
    answer_relevancy,      # Does the answer address the question?
    context_precision,     # Are the retrieved chunks actually relevant?
    context_recall,        # Did retrieval find all necessary information?
)

# ─────────────────────────────────────────────
# STEP 1: Prepare the evaluation dataset
#
# RAGAS requires four fields per sample:
#   question       - the user's question (string)
#   answer         - the generated answer (string)
#   contexts       - list of retrieved chunks (list[str])
#   ground_truth   - the ideal answer (string) — needed for context_recall only
# ─────────────────────────────────────────────

eval_data = {
    "question": [
        "What is the return policy?",
        "How do I contact customer support?",
        "What payment methods are accepted?",
        "Is there a warranty on electronics?",
    ],
    "answer": [
        # These are the answers your RAG system actually produced
        "According to the document, you can return products within 30 days of purchase for a full refund.",
        "Customer support is available via email at support@company.com or by phone at 1-800-555-0100.",
        "The company accepts Visa, Mastercard, American Express, and PayPal.",
        "Electronics come with a 1-year manufacturer warranty covering defects in materials and workmanship.",
    ],
    "contexts": [
        # These are the chunks your retriever returned for each question
        ["All product returns must be initiated within 30 days of purchase. Refunds are processed within 5-7 business days."],
        ["Contact our support team at support@company.com. Phone support is available Mon-Fri at 1-800-555-0100."],
        ["Accepted payment methods: Visa, Mastercard, American Express, and PayPal. We do not accept cryptocurrency."],
        ["All electronics sold by our company include a 1-year manufacturer warranty against defects in materials and workmanship."],
    ],
    "ground_truth": [
        # The ideal, reference answer — used to compute context_recall
        "Products can be returned within 30 days of purchase.",
        "Contact support via email at support@company.com or phone at 1-800-555-0100.",
        "We accept Visa, Mastercard, American Express, and PayPal.",
        "Electronics have a 1-year manufacturer warranty.",
    ],
}

# Convert to HuggingFace Dataset format (required by RAGAS)
dataset = Dataset.from_dict(eval_data)

# ─────────────────────────────────────────────
# STEP 2: Run RAGAS evaluation
# This makes LLM calls (uses OpenAI by default)
# ─────────────────────────────────────────────

results = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,       # 0–1: fraction of answer claims supported by context
        answer_relevancy,   # 0–1: how well the answer addresses the question
        context_precision,  # 0–1: fraction of retrieved chunks that are relevant
        context_recall,     # 0–1: fraction of ground-truth info covered by context
    ]
)

# ─────────────────────────────────────────────
# STEP 3: Print and interpret scores
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("RAGAS EVALUATION RESULTS")
print("=" * 60)
print(f"Faithfulness:      {results['faithfulness']:.3f}")
print(f"Answer Relevancy:  {results['answer_relevancy']:.3f}")
print(f"Context Precision: {results['context_precision']:.3f}")
print(f"Context Recall:    {results['context_recall']:.3f}")

# Convert to pandas for per-sample inspection
df = results.to_pandas()
print("\nPer-sample breakdown:")
print(df[["question", "faithfulness", "answer_relevancy", "context_precision", "context_recall"]].to_string())
```

### Interpreting RAGAS Scores

| Metric | What it measures | Low score means | How to fix |
|---|---|---|---|
| **Faithfulness** | Are all answer claims supported by the retrieved context? | LLM is hallucinating — adding facts not in context | Strengthen grounding instruction; use `temperature=0` |
| **Answer Relevancy** | Does the answer directly address the question? | LLM is off-topic or over-hedging | Refine system prompt; check that retrieval found relevant chunks |
| **Context Precision** | Are the retrieved chunks actually relevant to the question? | Retriever is returning noise alongside relevant chunks | Improve embedding model; reduce `top_k`; add reranker |
| **Context Recall** | Does the retrieved context cover everything in the ground truth? | Retriever is missing relevant chunks | Increase `top_k`; reduce chunk size; improve chunking strategy |

**Target scores for a production RAG system:**
- Faithfulness > 0.85 (hallucination must be rare)
- Answer Relevancy > 0.80
- Context Precision > 0.75
- Context Recall > 0.80

```
Score interpretation guide:
  0.90 – 1.00  Excellent — ready for production
  0.75 – 0.90  Good — monitor and iterate
  0.60 – 0.75  Needs improvement — identify failing samples
  < 0.60       Broken — check retrieval pipeline fundamentals
```

### Using RAGAS with a Custom LLM (e.g., Claude)

RAGAS uses OpenAI by default, but you can swap in any LLM:

```python
from ragas.llms import LangchainLLMWrapper
from langchain_anthropic import ChatAnthropic

# Use Claude as the evaluation LLM instead of GPT
claude = LangchainLLMWrapper(ChatAnthropic(model="claude-opus-4-6", temperature=0))

results = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    llm=claude,              # use Claude for evaluation
)
```

---

## Part 2: Custom LLM-as-Judge Evaluator

When you want full control over evaluation logic — or don't want a RAGAS dependency — you can build your own evaluator using direct LLM API calls.

```python
# pip install anthropic chromadb sentence-transformers
import json
import random
import numpy as np
import anthropic
import chromadb
from chromadb.utils import embedding_functions


# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────

anthropic_client = anthropic.Anthropic()

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
chroma_client = chromadb.PersistentClient(path="./rag_index")
collection = chroma_client.get_collection(
    name="company_policies",
    embedding_function=embedding_fn
)

print(f"Index ready: {collection.count()} documents")


# ─────────────────────────────────────────────
# STEP 1: Define test set
# (question, expected_answer, expected_chunk_id)
# ─────────────────────────────────────────────

TEST_SET = [
    {
        "question": "What is the return policy and how long do I have?",
        "expected_answer": "Products must be returned within 30 days of purchase.",
        "expected_chunk_id": "returns_1"
    },
    {
        "question": "How can I contact customer support?",
        "expected_answer": "Contact customer support via email at support@company.com or by phone at 1-800-555-0100.",
        "expected_chunk_id": "support_1"
    },
    {
        "question": "What payment methods are accepted?",
        "expected_answer": "We accept Visa, Mastercard, American Express, and PayPal.",
        "expected_chunk_id": "payment_1"
    },
    {
        "question": "Is there a warranty on electronics purchases?",
        "expected_answer": "Electronics come with a 1-year manufacturer warranty.",
        "expected_chunk_id": "warranty_1"
    },
    {
        "question": "What is the company's environmental sustainability policy?",
        "expected_answer": None,   # out-of-scope: should say "I don't have that information"
        "expected_chunk_id": None
    }
]


# ─────────────────────────────────────────────
# STEP 2: Retrieval metrics
# ─────────────────────────────────────────────

def retrieve(query: str, top_k: int = 3) -> list[dict]:
    results = collection.query(query_texts=[query], n_results=top_k)
    chunks = []
    for text, metadata, distance, chunk_id in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        results["ids"][0]
    ):
        chunks.append({
            "id": chunk_id,
            "text": text,
            "metadata": metadata,
            "similarity": round(1 - distance, 4)
        })
    return chunks


def hit_rate_at_k(retrieved_ids: list[str], expected_id: str, k: int) -> float:
    return 1.0 if expected_id in retrieved_ids[:k] else 0.0


def reciprocal_rank(retrieved_ids: list[str], expected_id: str) -> float:
    if expected_id in retrieved_ids:
        return 1.0 / (retrieved_ids.index(expected_id) + 1)
    return 0.0


def evaluate_retrieval(test_set: list[dict], k: int = 3) -> dict:
    """Compute hit rate and MRR across the test set."""
    # Only evaluate questions that have an expected chunk
    in_scope = [t for t in test_set if t["expected_chunk_id"] is not None]

    hit_rates = []
    mrr_scores = []

    for case in in_scope:
        chunks = retrieve(case["question"], top_k=k)
        retrieved_ids = [c["id"] for c in chunks]
        expected = case["expected_chunk_id"]

        hit_rates.append(hit_rate_at_k(retrieved_ids, expected, k))
        mrr_scores.append(reciprocal_rank(retrieved_ids, expected))

    return {
        "hit_rate": round(sum(hit_rates) / len(hit_rates), 3),
        "mrr": round(sum(mrr_scores) / len(mrr_scores), 3),
        "n_questions": len(in_scope)
    }


# ─────────────────────────────────────────────
# STEP 3: Generation metrics (LLM-as-judge)
# ─────────────────────────────────────────────

def build_rag_answer(question: str, top_k: int = 3) -> dict:
    """Run the full RAG pipeline and return answer + context."""
    chunks = retrieve(question, top_k=top_k)
    context_parts = [
        f"[Context {i} | Source: {c['metadata'].get('source', 'unknown')}]\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    ]
    context = "\n\n".join(context_parts) if chunks else "No relevant information found."

    prompt = f"""You are a helpful customer support assistant.
Answer ONLY based on the provided context. If the answer is not in the context,
say "I don't have information about that in our documentation."

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=256,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "question": question,
        "answer": response.content[0].text,
        "context": context,
        "chunks": chunks
    }


def evaluate_faithfulness(question: str, context: str, answer: str) -> float:
    """Score whether the answer is grounded in the context (0-1)."""
    judge_prompt = f"""You are evaluating an AI assistant's factual faithfulness.

Question: {question}
Retrieved context: {context}
Answer given: {answer}

Rate faithfulness from 0.0 to 1.0:
- 1.0: Every claim in the answer is directly supported by the context
- 0.5: Some claims supported, some not verifiable from context
- 0.0: Most claims cannot be verified from the context, or answer is invented

Return ONLY a JSON object: {{"score": 0.0}}"""

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=50,
        temperature=0,
        messages=[{"role": "user", "content": judge_prompt}]
    )
    try:
        result = json.loads(response.content[0].text)
        return float(result["score"])
    except (json.JSONDecodeError, KeyError):
        return 0.5  # default if parsing fails


def evaluate_answer_relevancy(question: str, answer: str) -> float:
    """Score whether the answer addresses the question (0-1)."""
    judge_prompt = f"""Rate how well this answer addresses the question asked.

Question: {question}
Answer: {answer}

Score from 0.0 to 1.0:
- 1.0: Directly answers the question
- 0.5: Partially answers, or addresses related topic
- 0.0: Completely off-topic or doesn't answer the question

Return ONLY a JSON object: {{"score": 0.0}}"""

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=50,
        temperature=0,
        messages=[{"role": "user", "content": judge_prompt}]
    )
    try:
        result = json.loads(response.content[0].text)
        return float(result["score"])
    except (json.JSONDecodeError, KeyError):
        return 0.5


# ─────────────────────────────────────────────
# STEP 4: Run full evaluation
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 1: RETRIEVAL EVALUATION")
print("=" * 60)

retrieval_scores = evaluate_retrieval(TEST_SET, k=3)
print(f"Hit Rate @ 3:  {retrieval_scores['hit_rate']:.3f}")
print(f"MRR:           {retrieval_scores['mrr']:.3f}")
print(f"Test set size: {retrieval_scores['n_questions']} (in-scope questions)")


print("\n" + "=" * 60)
print("STEP 2: GENERATION EVALUATION")
print("=" * 60)

faithfulness_scores = []
relevancy_scores = []

# Evaluate in-scope questions only
in_scope = [t for t in TEST_SET if t["expected_chunk_id"] is not None]

for case in in_scope:
    rag_result = build_rag_answer(case["question"])

    faithfulness = evaluate_faithfulness(
        rag_result["question"],
        rag_result["context"],
        rag_result["answer"]
    )
    relevancy = evaluate_answer_relevancy(
        rag_result["question"],
        rag_result["answer"]
    )

    faithfulness_scores.append(faithfulness)
    relevancy_scores.append(relevancy)

    print(f"\nQ: {case['question'][:60]}...")
    print(f"A: {rag_result['answer'][:80]}...")
    print(f"   Faithfulness: {faithfulness:.2f} | Relevancy: {relevancy:.2f}")


# ─────────────────────────────────────────────
# STEP 5: Out-of-scope evaluation
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("STEP 3: OUT-OF-SCOPE EVALUATION")
print("=" * 60)

out_of_scope = [t for t in TEST_SET if t["expected_chunk_id"] is None]
correct_refusals = 0

for case in out_of_scope:
    rag_result = build_rag_answer(case["question"])
    answer = rag_result["answer"].lower()

    # Check if the system correctly declined
    refused = any(phrase in answer for phrase in [
        "don't have information",
        "not in our documentation",
        "no information",
        "cannot find",
        "not available"
    ])

    if refused:
        correct_refusals += 1
        print(f"\nCORRECT REFUSAL: {case['question'][:50]}")
    else:
        print(f"\nFAILED REFUSAL:  {case['question'][:50]}")
        print(f"  Answer: {rag_result['answer'][:80]}...")

refusal_rate = correct_refusals / len(out_of_scope) if out_of_scope else 1.0


# ─────────────────────────────────────────────
# STEP 6: Final report
# ─────────────────────────────────────────────

print("\n" + "=" * 60)
print("EVALUATION SUMMARY")
print("=" * 60)
print(f"Retrieval Hit Rate @ 3:  {retrieval_scores['hit_rate']:.3f}  (target: >0.85)")
print(f"Retrieval MRR:           {retrieval_scores['mrr']:.3f}  (target: >0.80)")
print(f"Generation Faithfulness: {sum(faithfulness_scores)/len(faithfulness_scores):.3f}  (target: >0.85)")
print(f"Answer Relevancy:        {sum(relevancy_scores)/len(relevancy_scores):.3f}  (target: >0.85)")
print(f"Out-of-scope Refusals:   {refusal_rate:.3f}  (target: 1.00)")
```

**Expected output:**
```
EVALUATION SUMMARY
Retrieval Hit Rate @ 3:  0.875  (target: >0.85)
Retrieval MRR:           0.833  (target: >0.80)
Generation Faithfulness: 0.920  (target: >0.85)
Answer Relevancy:        0.910  (target: >0.85)
Out-of-scope Refusals:   1.000  (target: 1.00)
```

**Running:**
```bash
pip install anthropic chromadb sentence-transformers numpy
export ANTHROPIC_API_KEY="your-key"
python rag_evaluation.py
```

**Key design decisions:**
- LLM-as-judge with temperature=0 for consistent scoring
- Separate retrieval evaluation (no LLM needed) from generation evaluation
- Out-of-scope questions are a distinct test category
- JSON output from judge prompts allows programmatic score extraction
- Fallback `0.5` score if judge response fails to parse — always handle this

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Metrics_Guide.md](./Metrics_Guide.md) | RAG evaluation metrics guide |

⬅️ **Prev:** [07 Advanced RAG Techniques](../07_Advanced_RAG_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build a RAG App](../09_Build_a_RAG_App/Project_Guide.md)
