# Metrics Guide — Evaluation Pipelines

A comprehensive reference for every major evaluation metric in AI systems. Includes how each metric works, what it measures, and when to use it.

---

## Master Metrics Reference Table

| Metric | Task Type | Range | How Computed | Strengths | Weaknesses |
|---|---|---|---|---|---|
| **Accuracy** | Classification | 0-1 | correct / total | Simple, interpretable | Misleading on imbalanced classes |
| **F1 Score** | Classification, NER | 0-1 | 2×(P×R)/(P+R) | Balances precision & recall | Less intuitive than accuracy |
| **Precision** | Classification | 0-1 | TP / (TP + FP) | Important when false positives are costly | Ignores false negatives |
| **Recall** | Classification | 0-1 | TP / (TP + FN) | Important when false negatives are costly | Ignores false positives |
| **AUC-ROC** | Binary classification | 0-1 | Area under ROC curve | Threshold-independent | Less interpretable |
| **BLEU** | Translation | 0-1 | n-gram precision with brevity penalty | Standard for translation | Poor correlation with human judgment at sentence level |
| **ROUGE-1** | Summarization | 0-1 | Unigram recall overlap | Simple, fast | Only measures word overlap |
| **ROUGE-L** | Summarization | 0-1 | Longest common subsequence | Captures structure better than ROUGE-1 | Still lexical only |
| **BERTScore** | Any text | -1 to 1 | Cosine sim of BERT embeddings | Semantic similarity | Computationally expensive |
| **LLM Judge Score** | Any task | 1-5 (configurable) | LLM rates on rubric | Flexible, correlates with human judgment | Cost, LLM bias |
| **Pass@k** | Code generation | 0-1 | P(any of k solutions pass tests) | Captures generative diversity | Requires runnable tests |
| **Faithfulness** | RAG | 0-1 | % statements supported by context | Detects hallucination | Requires LLM to compute |
| **Answer Relevance** | RAG, Q&A | 0-1 | Semantic sim(question, answer) | Task-specific | Doesn't measure factual accuracy |
| **Context Precision** | RAG | 0-1 | Relevant retrieved chunks / total retrieved | Measures retrieval precision | Requires relevance labels |
| **Context Recall** | RAG | 0-1 | Needed info covered by context | Measures retrieval completeness | Requires ground truth |
| **MRR** | Retrieval | 0-1 | Mean Reciprocal Rank | Good for ranked retrieval | Only considers rank of first hit |
| **NDCG@k** | Retrieval, ranking | 0-1 | Normalized Discounted Cumulative Gain | Handles multiple relevant items | More complex to compute |
| **Latency (P99)** | Any | ms | 99th percentile response time | Captures worst-case experience | Not a quality metric |
| **Refusal rate** | Safety, guardrails | 0-1 | Refusals / total requests | Safety signal | Doesn't tell you why |

---

## Classification Metrics Deep Dive

### Confusion Matrix

```
                Predicted: Positive    Predicted: Negative
Actual: Positive     TP (True Pos)         FN (False Neg)
Actual: Negative     FP (False Pos)        TN (True Neg)

Accuracy  = (TP + TN) / (TP + TN + FP + FN)
Precision = TP / (TP + FP)       ← "Of predicted positives, how many were right?"
Recall    = TP / (TP + FN)       ← "Of actual positives, how many did we catch?"
F1        = 2 × (Precision × Recall) / (Precision + Recall)
```

### When to prioritize Precision vs Recall

| Scenario | Prioritize | Reason |
|---|---|---|
| Spam filter | Precision | False positive (ham → spam) is worse than false negative |
| Cancer screening | Recall | False negative (cancer missed) is worse than false positive |
| Fraud detection | Recall | Missing fraud is costly; some false alerts are acceptable |
| Search ranking | Precision | Showing irrelevant results degrades experience |

---

## NLP Metrics Deep Dive

### BLEU Score

**What it measures**: Fraction of n-grams in the generated text that appear in the reference text. Includes a brevity penalty for too-short outputs.

```python
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction

reference = "the cat sat on the mat".split()
candidate = "the cat is sitting on the mat".split()

score = sentence_bleu(
    [reference],
    candidate,
    smoothing_function=SmoothingFunction().method1
)
print(f"BLEU: {score:.3f}")  # → ~0.45
```

**Limitations**:
- Doesn't capture meaning — a synonym scores 0
- Measures precision, not recall (ignores reference words not in candidate)
- High variance at sentence level; more reliable at corpus level

**When to use**: MT evaluation, only when you have high-quality human reference translations. For open-ended generation, use LLM judge instead.

---

### ROUGE Scores

**ROUGE-1**: Overlap of individual words (unigrams)
**ROUGE-2**: Overlap of word pairs (bigrams)
**ROUGE-L**: Longest Common Subsequence — rewards similar ordering

```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

reference = "The cat sat on the mat near the window."
generated = "A cat was sitting on the mat close to the window."

scores = scorer.score(reference, generated)
print(f"ROUGE-1: {scores['rouge1'].fmeasure:.3f}")  # → ~0.65
print(f"ROUGE-2: {scores['rouge2'].fmeasure:.3f}")  # → ~0.43
print(f"ROUGE-L: {scores['rougeL'].fmeasure:.3f}")  # → ~0.62
```

**When to use**: Summarization, where capturing key phrases matters. Always report all three (ROUGE-1, ROUGE-2, ROUGE-L) for comparability.

---

### BERTScore

Uses contextual BERT embeddings instead of exact word overlap. Better for paraphrases.

```python
from bert_score import score

references = ["The cat sat on the mat."]
candidates = ["A cat was resting on the rug."]

P, R, F1 = score(candidates, references, lang="en", verbose=True)
print(f"BERTScore F1: {F1.mean():.3f}")  # → ~0.92 (captures semantic similarity)
# vs ROUGE-1: ~0.25 (doesn't recognize rug ≈ mat)
```

**When to use**: When semantic similarity matters more than exact lexical overlap. More computationally expensive but better correlates with human judgment.

---

## LLM-as-Judge Implementation

### Absolute Scoring

```python
JUDGE_PROMPT = """Rate this AI response on a 1-5 scale for each criterion.

Question: {question}
Response: {response}
{reference_section}

Rate each (1-5, where 5 = excellent):
- accuracy: Is the information correct and factual?
- relevance: Does it directly address the question?
- clarity: Is it well-written and easy to understand?
- completeness: Does it cover all important aspects?

Return JSON only:
{{"accuracy": int, "relevance": int, "clarity": int, "completeness": int,
  "overall": int, "reasoning": "1-2 sentences"}}"""

def judge_response(question, response, reference=None):
    ref_section = f"Reference: {reference}" if reference else ""
    prompt = JUDGE_PROMPT.format(
        question=question, response=response, reference_section=ref_section
    )
    result = anthropic.Anthropic().messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(result.content[0].text)
```

### Pairwise Comparison (Lower Bias)

```python
PAIRWISE_PROMPT = """Compare these two responses to the same question.

Question: {question}

Response A: {response_a}
Response B: {response_b}

Which is better overall (accuracy + clarity + helpfulness)?
Return JSON: {{"winner": "A" or "B" or "tie", "reasoning": "brief explanation"}}"""
```

**Best practices for LLM judges:**
- Use a different model family than what you're evaluating
- Randomize which response appears first (A vs B)
- Run each comparison 3x if possible; take majority vote
- Avoid judging on criteria the judge model handles poorly (e.g., math accuracy)

---

## RAG-Specific Metrics (RAGAS)

### Faithfulness

Measures whether the generated answer is supported by the retrieved context.

```
Steps:
1. Extract all factual statements from the answer
2. For each statement, check if it is supported by any retrieved context chunk
3. Faithfulness = supported_statements / total_statements

Example:
Answer: "The capital of France is Paris. It has 2 million people."
Context: "Paris is the capital of France and has a metropolitan area of 12 million."

Statement 1: "Paris is capital of France" → Supported ✓
Statement 2: "Paris has 2 million people" → Contradicted ✗ (context says 12M)

Faithfulness = 1/2 = 0.5
```

### Context Precision

```
Definition: Of all retrieved chunks, what fraction contain information
            relevant to answering the question?

If you retrieve 5 chunks but only 2 are relevant: Precision = 2/5 = 0.40
```

### Answer Relevance

```
Method:
1. Generate 3-5 questions that the given answer could be a response to
2. Compute cosine similarity between the generated questions and the original question
3. Answer Relevance = mean similarity

High relevance → the answer naturally answers the question
Low relevance → the answer addresses something tangential
```

---

## Code Evaluation: Pass@k

Used for code generation evaluation (HumanEval, MBPP benchmarks).

```python
import numpy as np

def pass_at_k(n: int, c: int, k: int) -> float:
    """
    Calculate Pass@k metric.
    n: total number of generated samples
    c: number of correct samples
    k: number of samples we're "using" (reporting k=1, k=5, k=10)

    P(at least 1 of k samples is correct)
    = 1 - P(none of k samples are correct)
    = 1 - C(n-c, k) / C(n, k)
    """
    if n - c < k:
        return 1.0
    return 1.0 - np.prod([(n - c - i) / (n - i) for i in range(k)])

# Example: Generated 10 solutions, 3 pass all tests
# What's the probability that any 1 of them passes? Any 3? Any 5?
print(f"Pass@1:  {pass_at_k(n=10, c=3, k=1):.3f}")   # ~0.300
print(f"Pass@3:  {pass_at_k(n=10, c=3, k=3):.3f}")   # ~0.617
print(f"Pass@5:  {pass_at_k(n=10, c=3, k=5):.3f}")   # ~0.833
```

---

## Choosing the Right Metrics for Your Task

```
Task: Multiple-choice or binary classification
  → Accuracy + F1. If imbalanced classes, add Macro-F1.

Task: Named entity recognition or extraction
  → Entity-level F1 (exact match), partial F1 (overlap)

Task: Summarization
  → ROUGE-1, ROUGE-2, ROUGE-L + optionally BERTScore
  → LLM judge for nuanced quality (faithfulness to source, abstractiveness)

Task: Translation
  → BLEU at corpus level + chrF (character n-gram F-score, more robust)

Task: Open-ended Q&A / Chatbot
  → LLM judge (accuracy, helpfulness, clarity) — best correlation with human judgment
  → Faithfulness if grounded in documents

Task: RAG pipeline
  → RAGAS full suite: Faithfulness + Answer Relevance + Context Precision + Context Recall

Task: Code generation
  → Pass@1 and Pass@10 on unit tests (most reliable)
  → Syntax error rate (quick filter)

Task: Safety / guardrails
  → Attack success rate (fraction of harmful queries that got harmful responses)
  → Refusal rate on benign queries (over-refusal penalizes users)
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| 📄 **Metrics_Guide.md** | ← you are here |

⬅️ **Prev:** [05 Observability](../05_Observability/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Safety and Guardrails](../07_Safety_and_Guardrails/Theory.md)
