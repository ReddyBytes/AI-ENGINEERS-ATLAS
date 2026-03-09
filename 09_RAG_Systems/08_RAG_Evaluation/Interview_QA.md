# RAG Evaluation — Interview Q&A

## Beginner

**Q1: Why do you need to evaluate a RAG system separately from the LLM itself?**

Because a RAG system has two failure modes, and fixing the wrong one wastes time.

Failure mode 1: bad retrieval. The right document chunk isn't returned, so the LLM doesn't have the information it needs. No matter how good the LLM is, it can't answer correctly from missing information.

Failure mode 2: bad generation. The right chunks were retrieved, but the LLM ignored them or added invented information not in the context.

If you only measure the final answer quality (end-to-end score), you can't tell which stage is failing. You might spend weeks improving your prompt engineering when the real problem is that your chunking strategy is too coarse and the right chunks are never retrieved.

Evaluate both stages with separate metrics. Fix retrieval issues (hit rate, context recall) independently from generation issues (faithfulness, answer relevancy). The diagnostic clarity saves enormous time.

---

**Q2: What is faithfulness in RAG evaluation and why is it the most important metric?**

Faithfulness measures whether every claim in the generated answer can be traced back to the retrieved context. A faithfulness score of 1.0 means the LLM only used information from the provided chunks — nothing was made up. A score of 0.7 means roughly 30% of the claims in answers are not supported by the context.

It's the most critical metric because low faithfulness is the definition of hallucination. For any application where users make decisions based on RAG answers — customer support, policy lookups, medical information, legal research — hallucinated facts are dangerous. The system sounds confident but is providing false information.

High faithfulness doesn't guarantee the answer is correct (the context itself might be wrong), but it guarantees the system is reliable — it only asserts what the documents actually say.

---

**Q3: What is the difference between context precision and context recall?**

Both measure retrieval quality but from opposite directions:

**Context precision**: of the chunks you retrieved, what fraction were actually useful? If you retrieved 5 chunks and only 2 contained relevant information, precision = 2/5 = 0.4. Low precision means you're passing too many irrelevant chunks to the LLM, adding noise.

**Context recall**: of all the information needed to answer correctly, what fraction did you retrieve? If the answer requires 3 facts and your retrieved chunks contained 2 of them, recall = 2/3 = 0.67. Low recall means you're missing information — the LLM simply can't answer completely.

The trade-off:
- High K (retrieve many chunks) → higher recall, lower precision
- Low K → higher precision, lower recall

You want both to be high. When you can't have both, which matters more depends on your use case: information-completeness tasks need high recall; precision-critical tasks (where noise causes hallucination) need high precision.

---

## Intermediate

**Q4: How do you build a test set for RAG evaluation and what makes a good test set?**

A test set is a collection of (question, expected_answer, optional: expected_chunk_id) triples. For each question, you run the full RAG pipeline and score the result.

A good test set has:

**1. Representative coverage** — questions across all major topics in your knowledge base. If your knowledge base has 5 topic areas, have test questions from all 5.

**2. Diversity of difficulty** — easy questions (direct term match), medium (paraphrase required), hard (multi-hop: answer spans multiple chunks), and out-of-scope (no relevant chunk exists).

**3. At least 20–50 questions** — fewer than 20 and random variance dominates your scores. A single outlier question changes your average by 5%.

**4. Ground truth at the right level** — for retrieval evaluation, you need the expected chunk ID. For generation evaluation, you need the expected answer text.

How to build:
```python
test_set = [
    {
        "question": "How many days do I have to return a product?",
        "expected_answer": "You have 30 days from the purchase date.",
        "expected_chunk_id": "returns_policy_chunk_1"
    },
    {
        "question": "What is the company's vacation policy?",
        "expected_answer": None,  # out-of-scope
        "expected_chunk_id": None
    }
]
```

For out-of-scope questions: the expected answer is "I don't have information on that" — the system should recognize no relevant chunk exists.

---

**Q5: What is LLM-as-judge evaluation and what are its limitations?**

LLM-as-judge means using an LLM (e.g., Claude, GPT-4) to evaluate the quality of another LLM's output. For RAG evaluation, you write a prompt that asks the judge LLM to score faithfulness, answer relevancy, or other metrics.

```python
def evaluate_faithfulness(question, context, answer, judge_client):
    prompt = f"""You are evaluating an AI assistant's answer for factual faithfulness.

Question: {question}
Retrieved context: {context}
Answer given: {answer}

Rate faithfulness from 0 to 1:
- 1.0: Every claim in the answer is directly supported by the context
- 0.5: Some claims are supported, but some are not in the context
- 0.0: Most claims cannot be verified from the context

Return JSON: {{"score": 0.0-1.0, "unsupported_claims": ["claim1", "claim2"]}}"""

    response = judge_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)
```

Limitations:
- **Judge bias**: the judge LLM has its own biases and may systematically score certain answer styles higher
- **Self-referential evaluation**: using the same LLM to judge its own outputs amplifies its biases
- **Consistency**: the same judge may give different scores on the same example on different runs (especially at temperature > 0)
- **Cost**: evaluating 1,000 test cases with a full LLM is expensive

Mitigations: use temperature=0 for the judge, use a different model than the one being evaluated, validate judge scores against a sample of human annotations.

---

**Q6: How would you set up a continuous evaluation pipeline for a production RAG system?**

Production evaluation has two components: offline evaluation and online monitoring.

**Offline evaluation** (runs before deployment):
```
1. Run test set against candidate version
2. Compare scores to baseline version
3. Block deployment if any metric drops > 5%
4. Add new test cases when users report bugs
```

**Online monitoring** (runs in production):
```
1. Sample 5% of live queries (or all if feasible)
2. Run faithfulness check on each sampled answer
3. Log results to monitoring dashboard
4. Alert if faithfulness drops below threshold over a rolling window
```

```python
import random

def maybe_evaluate(question, context, answer, sample_rate=0.05):
    """Run evaluation on a sample of production queries."""
    if random.random() < sample_rate:
        score = evaluate_faithfulness(question, context, answer)
        log_to_monitoring({"question": question, "faithfulness": score, "timestamp": now()})
```

The key insight: offline test sets only cover questions you anticipated. Online sampling catches failure modes you didn't think to test for. Both are necessary for a production system.

---

## Advanced

**Q7: How does the RAGAS framework compute answer relevancy, and why does it work without a ground truth answer?**

Answer relevancy doesn't compare the generated answer to a ground truth. Instead, it asks: "If someone had received this answer, what question would they have asked?"

The algorithm:
1. Take the generated answer
2. Prompt an LLM to generate N questions that this answer would logically be a response to
3. Embed all N generated questions + the original question
4. Answer relevancy score = average cosine similarity between the original question and each generated question

If the generated answer actually answers the question, the reverse-engineered questions will be similar to the original. If the answer went off-topic, the reverse-engineered questions will be different.

```python
def answer_relevancy(original_question, generated_answer, n_variations=5):
    # Generate hypothetical questions
    prompt = f"""Generate {n_variations} different questions that this answer could be a response to.
Answer: {generated_answer}
Return one question per line."""
    hyp_questions = llm_generate(prompt).split("\n")[:n_variations]

    # Embed everything
    embeddings = embed([original_question] + hyp_questions)
    original_emb = embeddings[0]
    hyp_embs = embeddings[1:]

    # Average cosine similarity
    similarities = [cosine_similarity(original_emb, h) for h in hyp_embs]
    return sum(similarities) / len(similarities)
```

This is elegant because it doesn't require ground truth answers, making it scalable to large production datasets.

---

**Q8: How do you evaluate a RAG system's ability to correctly handle out-of-scope questions?**

Out-of-scope handling is a distinct evaluation category: the correct behavior is to decline to answer, not to answer incorrectly.

Create a specific out-of-scope test set:
```python
out_of_scope_cases = [
    "What is the company's environmental sustainability policy?",  # not in knowledge base
    "What is the CEO's home address?",                             # not in knowledge base
    "What will interest rates be next year?",                      # not answerable
]
```

Measure:
1. **False positive rate**: what fraction of out-of-scope questions get a (potentially hallucinated) confident answer?
2. **Correct refusal rate**: what fraction correctly say "I don't have information about that"?

```python
def evaluate_out_of_scope(question, answer, context):
    # Check if the similarity threshold correctly caused an empty context
    judge_prompt = f"""Does this answer appropriately decline to answer the question,
or does it make up information?

Question: {question}
Context provided: {context}
Answer: {answer}

Score: 1 = correctly declined, 0 = incorrectly provided made-up information"""
    return llm_judge(judge_prompt)
```

Key design: your retrieval pipeline should return no context when similarity is low, and your prompt should instruct the LLM to decline when context is empty. Evaluation of out-of-scope cases validates that this mechanism works.

---

**Q9: What is G-Eval and how does it improve on standard LLM-as-judge evaluation?**

Standard LLM-as-judge asks for a single score. G-Eval (from the paper "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment") improves this by:

1. **Using evaluation criteria with explicit steps**: instead of asking "rate faithfulness 0-1", G-Eval provides a chain-of-thought checklist the judge should work through
2. **Asking for token probabilities** instead of a single number, using the probability distribution over score tokens to compute a weighted average score — more fine-grained than an integer rating
3. **Multiple criteria, multiple prompts** — separate judge calls for each metric rather than one call for all metrics

Example G-Eval prompt for faithfulness:
```
You will evaluate factual faithfulness. Follow these steps:

Step 1: Identify all factual claims made in the answer.
Step 2: For each claim, check if it can be directly verified from the context.
Step 3: Count the number of verified claims and total claims.
Step 4: Calculate the faithfulness score as verified_claims / total_claims.

After completing the steps, provide your final score as a number between 0 and 1.

Context: {context}
Answer: {answer}
```

The chain-of-thought steps make the judge's reasoning explicit and consistent, which has been shown to better correlate with human judgments than single-prompt scoring. The trade-off: each evaluation takes longer and uses more tokens.

For production use: G-Eval is worth implementing when your judge LLM's scores correlate poorly with human judgments on your domain. Validate on 50–100 human-labeled examples before relying on it.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Metrics_Guide.md](./Metrics_Guide.md) | RAG evaluation metrics guide |

⬅️ **Prev:** [07 Advanced RAG Techniques](../07_Advanced_RAG_Techniques/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 Build a RAG App](../09_Build_a_RAG_App/Project_Guide.md)
