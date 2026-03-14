# RAG Evaluation — Metrics Guide

A deep dive into each RAGAS metric: what it measures, how it's computed, examples, and how to improve it.

---

## Metric 1: Faithfulness

### What it measures
Whether every factual claim in the generated answer is supported by the retrieved context. Faithfulness = 1.0 means the answer contains only information from the retrieved documents. Faithfulness = 0.0 means the answer ignores the context entirely.

### Why it's the most important RAG metric
Faithfulness is the primary safety metric for RAG. High faithfulness means your system is grounded in your documents. Low faithfulness means the model is hallucinating facts — sometimes subtly. In high-stakes domains (legal, medical, financial), low faithfulness is a critical failure.

### How RAGAS computes it

```
Step 1: Extract claims
  Answer: "Returns are accepted within 30 days. Items must have a receipt.
           Return fees may apply."
  Claims: ["Returns accepted within 30 days",
           "Items must have receipt",
           "Return fees may apply"]

Step 2: Verify each claim against context
  Context: "Returns accepted within 30 days of purchase with original receipt."

  Claim 1: "Returns accepted within 30 days" → SUPPORTED ✓
  Claim 2: "Items must have receipt" → SUPPORTED ✓
  Claim 3: "Return fees may apply" → NOT IN CONTEXT ✗

Step 3: Score
  Faithfulness = 2/3 = 0.67
```

### Score interpretation
| Score | Meaning | Typical cause |
|-------|---------|--------------|
| > 0.90 | Excellent | Model reliably uses context |
| 0.75–0.90 | Good | Occasional minor additions |
| 0.50–0.75 | Concerning | Model regularly adds knowledge |
| < 0.50 | Failing | Model primarily using own knowledge |

### How to improve faithfulness
1. **System prompt grounding**: "Answer ONLY using the provided context. Never use your own knowledge. If the answer is not in the context, say so explicitly."
2. **Context quality**: Better retrieval → better context → less temptation to fill gaps with knowledge
3. **Model choice**: Some models are better at staying grounded than others; test multiple
4. **Temperature**: Lower temperature → less creative → more faithful
5. **Example-based prompting**: Include a few-shot example showing faithful vs unfaithful answers

---

## Metric 2: Answer Relevance

### What it measures
Whether the generated answer actually addresses the question that was asked. A model can generate a faithful, accurate response that answers a different question than was asked.

### Example failure
- **Question**: "How do I cancel my subscription?"
- **Answer**: "You can pause your subscription at any time from your account settings. Premium members have additional options for managing their subscription status."
- **Problem**: Answer is about pausing, not canceling. Faithful to context? Maybe. Relevant? No.

### How RAGAS computes it

```
Step 1: Given the answer, generate k reverse questions
  Answer: "You can pause your subscription at any time..."
  Generated Q1: "How do I pause my subscription?"
  Generated Q2: "What subscription management options are available?"
  Generated Q3: "How do I temporarily stop my subscription?"

Step 2: Compute similarity between each generated question and original question
  Original: "How do I cancel my subscription?"
  Similarity to Q1 (pause): 0.61 (pause ≠ cancel)
  Similarity to Q2 (options): 0.42
  Similarity to Q3 (temporary stop): 0.58

Step 3: Average = (0.61 + 0.42 + 0.58) / 3 = 0.54
  Low score → answer not addressing original question
```

### Score interpretation
| Score | Meaning |
|-------|---------|
| > 0.85 | Answer directly addresses question |
| 0.65–0.85 | Mostly relevant, some tangents |
| < 0.65 | Answer is off-topic or misunderstands question |

### How to improve answer relevance
1. **Better retrieval**: Retrieve documents more specifically about the question
2. **Clearer prompting**: "Answer specifically this question: {question}. Do not answer related questions."
3. **Query reformulation**: Add a step to reformulate unclear questions before retrieval
4. **Post-generation verification**: Have the model check "Did I answer the question that was asked?"

---

## Metric 3: Context Precision

### What it measures
Among all the documents retrieved, what proportion were actually useful for answering the question? High context precision = efficient, targeted retrieval. Low context precision = noisy, irrelevant documents polluting the context.

### Why it matters
- Irrelevant context wastes tokens (cost)
- Irrelevant context can confuse the generator
- Irrelevant context can lead to off-topic answers (hurts answer relevance)
- Too many irrelevant documents may push relevant ones out (if top-k is fixed)

### Computation

```
Retrieved documents for question "What is the return policy?":
  Doc 1: "Returns accepted within 30 days with receipt" → RELEVANT ✓
  Doc 2: "Shipping takes 3-5 business days" → NOT RELEVANT ✗
  Doc 3: "We accept Visa, Mastercard, PayPal" → NOT RELEVANT ✗

Context Precision = 1/3 = 0.33 (only 1 of 3 retrieved docs is relevant)
```

### Score interpretation
| Score | Meaning | Action |
|-------|---------|--------|
| > 0.80 | Retriever is highly precise | Maintain |
| 0.60–0.80 | Acceptable precision | Fine-tune threshold |
| 0.40–0.60 | Too much noise | Improve embeddings or filtering |
| < 0.40 | Retrieval is mostly noise | Major retrieval overhaul needed |

### How to improve context precision
1. **Raise similarity threshold**: Only retrieve documents above a minimum similarity score
2. **Better embeddings**: Domain-specific embedding models retrieve more relevant documents
3. **Reranking**: Add a cross-encoder reranker to re-score retrieved documents before passing to generator
4. **Smaller top-k**: Retrieve fewer documents (3 instead of 10) if precision is more important than recall
5. **Query expansion or HyDE**: Improve query representation before searching

---

## Metric 4: Context Recall

### What it measures
Of all the information needed to answer the question correctly, what proportion was actually retrieved? High recall = the retriever found all the important documents. Low recall = important information was missed.

### Why recall requires ground truth
Recall is measured against what *should have been retrieved*, which requires knowing what the complete correct answer is. This is why context recall requires a ground truth answer in the test set.

### Computation

```
Ground truth answer: "Returns accepted within 30 days. Require original receipt.
                     Item must be in original condition. No returns on damaged items."

Ground truth statements:
  S1: "Returns accepted within 30 days"
  S2: "Require original receipt"
  S3: "Item must be in original condition"
  S4: "No returns on damaged items"

Retrieved context covers:
  S1: "Returns accepted within 30 days with receipt" → COVERED ✓
  S2: "original receipt" appears in context → COVERED ✓
  S3: "original condition" appears in context → COVERED ✓
  S4: "damaged" items → NOT in retrieved context ✗

Context Recall = 3/4 = 0.75
```

### Score interpretation
| Score | Meaning | Action |
|-------|---------|--------|
| > 0.90 | Excellent — retriever finds almost everything | Maintain |
| 0.75–0.90 | Good — minor gaps | Add more coverage |
| 0.60–0.75 | Some important info missed | Increase top-k or improve embedding |
| < 0.60 | Significant info missing regularly | Major retrieval improvement needed |

### How to improve context recall
1. **Increase top-k**: Retrieve more documents (may hurt precision)
2. **Better chunking**: If relevant info is split across chunk boundaries, merge chunks or use sliding window
3. **Multi-query retrieval**: Generate multiple query variants, retrieve for each, merge results
4. **HyDE (Hypothetical Document Embeddings)**: Generate a hypothetical answer, use its embedding as query — often retrieves more relevant docs
5. **Improve embedding model**: Better domain-specific embeddings find more semantically related content

---

## Interpreting Combined Metric Patterns

| Pattern | Diagnosis | Fix priority |
|---------|-----------|-------------|
| Low faithfulness, high context precision | Generator hallucinating despite good context | Fix system prompt |
| High faithfulness, low answer relevance | Model answers a different question faithfully | Improve query understanding |
| Low context precision, high context recall | Retriever finds everything but also lots of noise | Add reranking step |
| High context precision, low context recall | Retriever finds relevant docs but misses some | Increase top-k |
| All metrics low | Fundamental system problem | Audit full pipeline |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | RAGAS evaluation code |
| 📄 **Metrics_Guide.md** | ← you are here |

⬅️ **Prev:** [03 — LLM as Judge](../03_LLM_as_Judge/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Agent Evaluation](../05_Agent_Evaluation/Theory.md)
