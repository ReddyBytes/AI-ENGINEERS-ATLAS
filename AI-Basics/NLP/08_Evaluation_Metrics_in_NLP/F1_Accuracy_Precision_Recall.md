# F1, Accuracy, Precision, and Recall in NLP

Imagine you are building a **spam detection system** for emails. Your system flags emails as spam or not spam. After testing, you find that sometimes it **misses spam emails** or **labels normal emails as spam**. To evaluate how well your system performs, you need **metrics like F1-score, Accuracy, Precision, and Recall**. These metrics help quantify **how good your model is at making correct predictions**.

# What are F1, Accuracy, Precision, and Recall?

These are **common evaluation metrics** used to measure the performance of NLP models, particularly for classification tasks. They help assess **correctness, completeness, and reliability** of predictions.

 

### Key Metrics Explained

1. **Accuracy:**  
   - Fraction of **correct predictions** out of total predictions.  
   - Formula:  
     \[
     \text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
     \]  
   - Example: Out of 100 emails, if 90 are correctly classified (spam or not spam), accuracy = 90%.  
   - **Limitation:** Can be misleading in imbalanced datasets (e.g., 95% non-spam, 5% spam).

2. **Precision:**  
   - Fraction of **correct positive predictions** out of all positive predictions.  
   - Formula:  
     \[
     \text{Precision} = \frac{TP}{TP + FP}
     \]  
   - Example: Model flags 50 emails as spam, 45 are actually spam. Precision = 45/50 = 0.9  
   - Focuses on **quality of positive predictions**.

3. **Recall (Sensitivity):**  
   - Fraction of **correct positive predictions** out of all actual positives.  
   - Formula:  
     \[
     \text{Recall} = \frac{TP}{TP + FN}
     \]  
   - Example: There are 60 spam emails, model correctly detects 45. Recall = 45/60 = 0.75  
   - Focuses on **completeness of positive predictions**.

4. **F1-Score:**  
   - Harmonic mean of Precision and Recall.  
   - Formula:  
     \[
     F1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
     \]  
   - Balances **precision and recall**, especially when one is more important than the other.  
   - Example: Precision = 0.9, Recall = 0.75 → F1 = 0.82  

 

### Why These Metrics Are Needed

- Accuracy alone may be **misleading** for imbalanced datasets.  
- Precision and recall help understand **trade-offs between false positives and false negatives**.  
- F1-score provides a **single metric balancing precision and recall**.  
- Without proper evaluation:
  - Models may seem accurate but **fail in real-world applications**.  
  - For spam detection, misclassified emails can lead to **lost important emails or spam inbox clutter**.

 

### Applications in NLP

- **Text Classification:** Spam detection, sentiment analysis, topic labeling.  
- **Named Entity Recognition (NER):** Evaluate correctly identified entities.  
- **Question Answering Systems:** Measure correct answers vs. missed answers.  
- **Information Retrieval:** Precision and recall in search engine results.  
- **Machine Translation / Summarization:** BLEU and ROUGE are extensions of precision/recall concepts.

 

## Interview Q&A

**Q1. What is accuracy, and when can it be misleading?**  
A: Accuracy measures the proportion of correct predictions. It can be misleading in **imbalanced datasets**, where one class dominates.

**Q2. What is the difference between precision and recall?**  
A:  
- Precision = correctness of positive predictions.  
- Recall = completeness of detecting actual positives.

**Q3. What is F1-score and why is it important?**  
A: F1-score is the **harmonic mean of precision and recall**, useful when there is a trade-off between them.

**Q4. How do you evaluate a model for imbalanced classes?**  
A: Use **precision, recall, F1-score, or area under the precision-recall curve**, not just accuracy.

**Q5. Give a real-world example where recall is more important than precision.**  
A: Medical diagnosis: Missing a disease (false negative) is worse than falsely flagging a healthy patient.

 

## Key Takeaways

- **Accuracy:** Overall correctness, may fail on imbalanced datasets.  
- **Precision:** Correctness of positive predictions.  
- **Recall:** Completeness of detecting actual positives.  
- **F1-Score:** Balances precision and recall.  
- Metrics are **essential for evaluating NLP tasks** like classification, NER, QA, and retrieval.  
- Choosing the right metric depends on **task requirements and dataset characteristics**.
