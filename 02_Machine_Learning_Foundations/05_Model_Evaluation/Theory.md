# Model Evaluation

## The Story

You took a practice exam and got 80% correct. Then your teacher says: "90% of the questions were on the easy topic. The hard topic — the one that actually matters — you got almost all wrong." Your 80% score was misleading.

👉 This is why we need **Model Evaluation** — to measure what actually matters, not just the headline number.

---

## Why Accuracy Alone Lies

A model detecting a rare disease (1% prevalence) that predicts "No disease" for everyone gets **99% accuracy** — but is completely useless. When one class is much rarer, accuracy is misleading. You need metrics that focus on specific error types.

---

## The Confusion Matrix — The Foundation

Every prediction a model makes falls into one of four categories:

```
                     PREDICTED
                  Positive  Negative
ACTUAL Positive |    TP    |   FN   |
       Negative |    FP    |   TN   |
```

- **TP (True Positive):** Model said "yes" and it was right
- **TN (True Negative):** Model said "no" and it was right
- **FP (False Positive):** Model said "yes" but it was wrong (false alarm)
- **FN (False Negative):** Model said "no" but it was wrong (missed a real case)

```mermaid
flowchart TD
    A[Model Makes a Prediction] --> B{Prediction vs Reality}
    B --> C[Predicted Positive]
    B --> D[Predicted Negative]
    C --> E[Actually Positive\nTrue Positive TP]
    C --> F[Actually Negative\nFalse Positive FP]
    D --> G[Actually Positive\nFalse Negative FN]
    D --> H[Actually Negative\nTrue Negative TN]
    E --> I[Metrics: Precision / Recall / F1 / Accuracy]
    F --> I
    G --> I
    H --> I
```

---

## The Four Main Metrics

### Accuracy
**What it is:** Out of all predictions, how many were correct?

```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

**Good when:** Classes are balanced. Bad when: one class is rare.

---

### Precision
**What it is:** Of everything the model said was positive, how many actually were?

```
Precision = TP / (TP + FP)
```

**Think:** "When the model fires the alarm, how often is it a real fire?"

High precision = fewer false alarms.

---

### Recall (Sensitivity)
**What it is:** Of all the real positives, how many did the model catch?

```
Recall = TP / (TP + FN)
```

**Think:** "Of all the real fires, how many did the alarm detect?"

High recall = fewer missed cases.

---

### F1 Score
**What it is:** The balance between precision and recall — the harmonic mean.

```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

Only high when BOTH precision AND recall are high — one high number cannot cancel the other.

---

## The Precision-Recall Tradeoff

Precision and recall fight each other. Improving one usually hurts the other.

| Situation | Should Prioritize | Why |
|---|---|---|
| Spam filter | Precision | You don't want good emails deleted (false positives are painful) |
| Cancer screening | Recall | You don't want to miss real cancer (false negatives are dangerous) |
| Credit fraud | Recall | Missing fraud is more costly than a few false alerts |
| Legal document review | Precision | A false positive flags an innocent person |

```mermaid
flowchart LR
    T[Lower decision threshold\npredict Positive more often] --> RP[Recall goes UP\ncatch more real positives]
    T --> PP[Precision goes DOWN\nmore false alarms]
    T2[Raise decision threshold\npredict Positive less often] --> RP2[Recall goes DOWN\nmiss more real positives]
    T2 --> PP2[Precision goes UP\nfewer false alarms]
    RP --> F1[F1 Score balances both]
    PP2 --> F1
```

---

## When to Use Which Metric

| Metric | Use When |
|---|---|
| **Accuracy** | Balanced classes, roughly equal cost of errors |
| **Precision** | False alarms are costly (spam, content moderation) |
| **Recall** | Missing real cases is costly (disease, fraud, safety) |
| **F1** | You need balance — neither precision nor recall alone tells the story |
| **ROC-AUC** | Comparing models regardless of threshold; ranked outputs |

---

✅ **What you just learned:** Accuracy is misleading on imbalanced data — precision, recall, F1, and the confusion matrix give you a real picture of model performance.

🔨 **Build this now:** Write a confusion matrix by hand. Make up 10 predictions: 5 "positive" and 5 "negative." Then make up the reality. Count your TP, TN, FP, FN, then calculate precision and recall manually. It takes 5 minutes and makes these concepts click instantly.

➡️ **Next step:** What happens when a model is too good on training data? → `06_Overfitting_and_Regularization/Theory.md`

---

## 🛠️ Practice Project

Apply what you just learned → **[B2: ML Model Comparison](../../22_Capstone_Projects/02_ML_Model_Comparison/03_GUIDE.md)**
> This project uses: accuracy, precision, recall, F1, confusion matrix, train/test split, cross-validation


---

## 📝 Practice Questions

- 📝 [Q7 · model-evaluation](../../ai_practice_questions_100.md#q7--critical--model-evaluation)


---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Metrics_Deep_Dive.md](./Metrics_Deep_Dive.md) | Deep dive into evaluation metrics |

⬅️ **Prev:** [04 Unsupervised Learning](../04_Unsupervised_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Overfitting and Regularization](../06_Overfitting_and_Regularization/Theory.md)
