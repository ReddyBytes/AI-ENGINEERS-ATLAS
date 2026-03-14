# RAG Evaluation — Code Example

## RAGAS Evaluation on a RAG Pipeline

```python
"""
rag_evaluation.py — Evaluate a RAG system using RAGAS metrics
pip install ragas anthropic langchain-anthropic chromadb sentence-transformers
"""
import os
import json
from datasets import Dataset


# ──────────────────────────────────────────────
# 1. Simple RAG system to evaluate
# ──────────────────────────────────────────────

import anthropic
from sentence_transformers import SentenceTransformer
import numpy as np

client = anthropic.Anthropic()
embedder = SentenceTransformer("all-MiniLM-L6-v2")


class SimpleRAG:
    """Minimal RAG system for demonstration."""

    def __init__(self, documents: list[str]):
        self.documents = documents
        self.embeddings = embedder.encode(documents)

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """Retrieve top-k most relevant documents."""
        query_emb = embedder.encode([query])
        scores = np.dot(self.embeddings, query_emb.T).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self.documents[i] for i in top_indices]

    def answer(self, question: str) -> dict:
        """Retrieve context and generate answer."""
        contexts = self.retrieve(question)
        context_text = "\n\n".join(contexts)

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=512,
            system="""You are a helpful assistant. Answer questions based ONLY on the provided context.
If the answer is not in the context, say "I cannot find this information in the provided documents."
Do not use your own knowledge beyond what is in the context.""",
            messages=[{
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion: {question}"
            }]
        )

        return {
            "question": question,
            "contexts": contexts,
            "answer": response.content[0].text
        }


# ──────────────────────────────────────────────
# 2. Build and run the RAG pipeline
# ──────────────────────────────────────────────

# Sample knowledge base
DOCUMENTS = [
    "Our return policy allows customers to return items within 30 days of purchase. All returns require the original receipt and the item must be in its original condition. Damaged or used items are not eligible for return.",
    "Shipping typically takes 3-5 business days for standard delivery. Express shipping (1-2 business days) is available for an additional $15. International shipping takes 7-14 business days.",
    "We accept Visa, Mastercard, American Express, and PayPal. All payments are processed securely. We do not store payment information on our servers.",
    "Customer support is available Monday through Friday, 9 AM to 5 PM EST. You can reach us via email at support@example.com or by phone at 1-800-555-0100.",
    "Our premium membership costs $99 per year and includes free express shipping on all orders, 10% off all purchases, and priority customer support.",
]

# Test questions with ground truth
TEST_CASES = [
    {
        "question": "What is the return window for purchases?",
        "ground_truth": "Customers can return items within 30 days of purchase with the original receipt."
    },
    {
        "question": "How long does standard shipping take?",
        "ground_truth": "Standard shipping takes 3-5 business days."
    },
    {
        "question": "What payment methods are accepted?",
        "ground_truth": "We accept Visa, Mastercard, American Express, and PayPal."
    },
    {
        "question": "When is customer support available?",
        "ground_truth": "Customer support is available Monday through Friday, 9 AM to 5 PM EST."
    },
    {
        "question": "How much does premium membership cost and what does it include?",
        "ground_truth": "Premium membership costs $99 per year and includes free express shipping, 10% off purchases, and priority support."
    }
]


def build_ragas_dataset(rag: SimpleRAG, test_cases: list[dict]) -> Dataset:
    """Run RAG pipeline on test cases and format for RAGAS."""
    data = {
        "question": [],
        "contexts": [],
        "answer": [],
        "ground_truth": []
    }

    print(f"Running RAG on {len(test_cases)} test cases...")
    for tc in test_cases:
        result = rag.answer(tc["question"])
        data["question"].append(tc["question"])
        data["contexts"].append(result["contexts"])
        data["answer"].append(result["answer"])
        data["ground_truth"].append(tc.get("ground_truth", ""))
        print(f"  Q: {tc['question'][:50]}...")
        print(f"  A: {result['answer'][:100]}...")

    return Dataset.from_dict(data)


# ──────────────────────────────────────────────
# 3. Run RAGAS evaluation
# ──────────────────────────────────────────────

def run_ragas_evaluation(dataset: Dataset) -> dict:
    """Run full RAGAS evaluation suite."""
    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        )

        results = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ]
        )
        return results

    except ImportError:
        print("RAGAS not installed. Running manual faithfulness check...")
        return run_manual_faithfulness(dataset)


def run_manual_faithfulness(dataset: Dataset) -> dict:
    """Manual faithfulness check without RAGAS dependency."""

    faithful_scores = []
    for i in range(len(dataset)):
        question = dataset[i]["question"]
        contexts = "\n".join(dataset[i]["contexts"])
        answer = dataset[i]["answer"]

        prompt = f"""Given this context:
{contexts}

And this answer:
{answer}

Is the answer fully supported by the context? Does it avoid adding information not in the context?
Return JSON: {{"faithful": true/false, "score": 0.0-1.0, "reason": "brief"}}"""

        r = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = r.content[0].text.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:-1])
        result = json.loads(raw)
        faithful_scores.append(result["score"])
        print(f"  Q{i+1}: faithfulness={result['score']:.2f} — {result['reason'][:80]}")

    avg_faithfulness = sum(faithful_scores) / len(faithful_scores)
    return {"faithfulness": avg_faithfulness}


def print_ragas_results(results):
    """Print RAGAS results in a readable format."""
    print("\n" + "="*50)
    print("RAGAS Evaluation Results")
    print("="*50)

    metrics = {
        "faithfulness": "Faithfulness (answer grounded in context)",
        "answer_relevancy": "Answer Relevance (addresses the question)",
        "context_precision": "Context Precision (retrieved docs relevant)",
        "context_recall": "Context Recall (all important docs found)"
    }

    targets = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.80,
        "context_precision": 0.70,
        "context_recall": 0.80
    }

    for key, label in metrics.items():
        if hasattr(results, key) or (isinstance(results, dict) and key in results):
            score = results[key] if isinstance(results, dict) else getattr(results, key)
            target = targets.get(key, 0.75)
            status = "PASS" if score >= target else "NEEDS WORK"
            print(f"\n  {label}")
            print(f"  Score: {score:.3f} | Target: {target} | {status}")


# ──────────────────────────────────────────────
# 4. Main
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("Initializing RAG system...")
    rag = SimpleRAG(DOCUMENTS)

    print("\nBuilding evaluation dataset...")
    dataset = build_ragas_dataset(rag, TEST_CASES)

    print("\nRunning RAGAS evaluation...")
    results = run_ragas_evaluation(dataset)
    print_ragas_results(results)

    # Save results
    results_dict = dict(results) if not isinstance(results, dict) else results
    with open("ragas_results.json", "w") as f:
        json.dump(results_dict, f, indent=2)
    print("\nResults saved to ragas_results.json")
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |
| [📄 Metrics_Guide.md](./Metrics_Guide.md) | Deep dive on each metric |

⬅️ **Prev:** [03 — LLM as Judge](../03_LLM_as_Judge/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Agent Evaluation](../05_Agent_Evaluation/Theory.md)
