# RAG Evaluation — Interview Q&A

## Beginner Level

**Q1: What is RAGAS and what problem does it solve?**
**A:** RAGAS (Retrieval-Augmented Generation Assessment) is an evaluation framework for RAG systems. It solves the problem that standard quality metrics don't capture RAG-specific failure modes. A RAG system can fail in multiple ways: the retriever can find irrelevant documents, the generator can ignore the retrieved documents, or the answer can be off-topic. RAGAS measures each failure mode separately with dedicated metrics: faithfulness, answer relevance, context precision, and context recall.

**Q2: What does faithfulness measure in RAG evaluation?**
**A:** Faithfulness measures whether every claim in the generated answer is actually supported by the retrieved documents. A model can hallucinate facts that aren't in the retrieved context — generating confident, plausible-sounding answers that contradict or add to the source material. Faithfulness score = (claims supported by retrieved context) / (total claims in answer). Target: > 0.85. A faithfulness score of 0.5 means half the claims in the answer are unsupported hallucinations.

**Q3: What's the difference between context precision and context recall?**
**A:** These evaluate different aspects of retrieval: **Context precision** = of the documents retrieved, what proportion were actually relevant? (Are we retrieving useful documents, or a lot of noise?) **Context recall** = of all the important information needed to answer the question, what proportion was actually retrieved? (Did we find everything we needed?) A system can have high precision but low recall (retrieves few but all relevant documents), or high recall but low precision (retrieves everything including lots of irrelevant documents).

---

## Intermediate Level

**Q4: How does RAGAS compute faithfulness?**
**A:** RAGAS uses LLM-as-judge internally to compute faithfulness:
1. An LLM extracts all factual claims from the generated answer (e.g., "The price is $29", "Returns are accepted within 30 days")
2. For each claim, another LLM call asks: "Is this claim fully supported by the retrieved context? Answer yes or no with brief reasoning"
3. Faithfulness = supported_claims / total_claims
This means faithfulness computation itself costs 2–5 LLM API calls per evaluated sample. At scale, this cost should be budgeted. RAGAS evaluation of 1,000 samples might cost $5–50 in API fees depending on context lengths and models used.

**Q5: How do you build a test set for RAG evaluation?**
**A:** Components needed:
1. **Questions**: 100–500 representative questions your system should answer. Sources: sample from production logs, have domain experts write them, or use LLM-generated questions from documents.
2. **Ground truth answers**: What the correct answer is. Required for context recall. Have domain experts write these or extract from authoritative documentation.
3. **Ground truth relevant documents** (optional): For even more precise context recall, annotate which documents should be retrieved for each question.
Process: Run your RAG pipeline on each question to get the retrieved context and generated answer. These, combined with questions and ground truth, give you the full dataset for RAGAS evaluation.

**Q6: If your RAGAS faithfulness score is 0.6, where should you look to fix it?**
**A:** A faithfulness score of 0.6 means ~40% of claims aren't supported by retrieved context — the model is hallucinating. Diagnostic steps:
1. **Look at failing examples**: Are the unsupported claims made-up facts, or are they missing from the retrieved context?
2. **If hallucinated**: Fix the system prompt — add explicit instruction "Only answer based on the provided context. If the answer is not in the context, say so. Never use your own knowledge."
3. **If information not in context**: The retriever is missing relevant documents — look at context recall. May need to improve chunking, embeddings, or retrieval top-k.
4. **Check for "knowledge override"**: Some models strongly prefer to use their training knowledge. May need to increase context relevance (better retrieval) so the model has less reason to improvise.

---

## Advanced Level

**Q7: How would you implement a production RAG evaluation pipeline?**
**A:** Architecture:
1. **Test set**: 200 questions with ground truth answers, sampled from production queries + expert-written edge cases. Refresh quarterly.
2. **Automated eval on every deploy**: Run RAGAS on full test set before deploying any change. Block deploy if faithfulness drops >5% or answer relevance drops >3%.
3. **Continuous production sampling**: Sample 1% of live queries daily. Run RAGAS. Generate daily dashboard.
4. **Alert thresholds**: Faithfulness < 0.75 → immediate alert. Context precision < 0.60 → alert (retrieval degraded). Answer relevance < 0.75 → alert.
5. **Root cause dashboard**: Show which metric dropped to guide where to investigate (retriever vs generator)
6. **Weekly deep dive**: Human review of 20 failing examples per metric category to validate automated scores and catch systematic issues

**Q8: System design question: A RAG system's end-to-end quality dropped. How do you diagnose which component failed?**
**A:** Diagnostic framework using RAGAS:
1. **Run all four RAGAS metrics** on a representative sample of recent queries
2. **Interpret the pattern**:
   - Low faithfulness only → generator problem (hallucinating despite good context)
   - Low context precision only → retriever finding wrong documents
   - Low context recall only → retriever missing important documents
   - Low answer relevance only → prompt/instruction following problem
   - Low context precision + low context recall → retrieval fundamentally broken (embedding model degraded, index corrupted, or documents changed significantly)
   - Low faithfulness + low context recall → both failing: retriever misses docs, generator fills gaps with hallucination
3. **Check for non-AI causes**:
   - Did the document corpus change? (new documents added, old ones modified)
   - Did the embedding model change or get updated?
   - Did the query distribution change? (new types of questions users are asking)
4. **Targeted fixes**:
   - Retriever issues: re-embed, tune similarity threshold, adjust chunk size
   - Generator issues: revise system prompt, add grounding instructions

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | RAGAS evaluation code |
| [📄 Metrics_Guide.md](./Metrics_Guide.md) | Deep dive on each metric |

⬅️ **Prev:** [03 — LLM as Judge](../03_LLM_as_Judge/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 — Agent Evaluation](../05_Agent_Evaluation/Theory.md)
