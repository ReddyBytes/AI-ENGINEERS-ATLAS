# Model Evaluation — Cheatsheet

**One-liner:** Evaluation metrics tell you not just if your model is right, but where and how it's wrong.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Confusion matrix** | A 2x2 table showing TP, TN, FP, FN for a binary classifier |
| **True Positive (TP)** | Model predicted positive and was correct |
| **True Negative (TN)** | Model predicted negative and was correct |
| **False Positive (FP)** | Model predicted positive but was wrong (false alarm) |
| **False Negative (FN)** | Model predicted negative but was wrong (missed real case) |
| **Accuracy** | (TP+TN) / all predictions |
| **Precision** | TP / (TP + FP) — how often positive predictions are right |
| **Recall** | TP / (TP + FN) — how many real positives were caught |
| **F1 Score** | 2 × (P × R) / (P + R) — harmonic mean of precision and recall |
| **ROC-AUC** | Area under the ROC curve — model's ranking ability across all thresholds |
| **Imbalanced data** | One class is much rarer than the other — accuracy lies here |

---

## Quick Metric Reference

| Metric | Formula | When It Lies | Best For |
|---|---|---|---|
| Accuracy | (TP+TN)/total | Imbalanced classes | Balanced datasets |
| Precision | TP/(TP+FP) | When FN cost is ignored | Spam, content moderation |
| Recall | TP/(TP+FN) | When FP cost is ignored | Disease, fraud, safety |
| F1 | 2PR/(P+R) | Rarely — balances both | Most classification tasks |
| ROC-AUC | Area under curve | Doesn't reflect threshold choice | Comparing models |

---

## When to Use / Not Use

| Use This | When |
|---|---|
| Accuracy | Classes are balanced (50/50 ish) |
| Precision | False alarms are expensive (email filtering, legal) |
| Recall | Missing cases is dangerous (medical, fraud, safety) |
| F1 | You need to balance both precision and recall |
| ROC-AUC | Comparing models; threshold-independent evaluation |

---

## Golden Rules

1. **Never trust accuracy alone on imbalanced data.** A 99% accurate model that never predicts the rare class is useless.
2. **Precision and recall trade off.** Improving one usually hurts the other.
3. **F1 is only high if BOTH precision AND recall are high.** One can't save the other.
4. **Always look at the confusion matrix.** The four cells tell you more than any single number.
5. **Pick your metric before training.** Decide what kind of error is more costly — that determines which metric you optimize.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Metrics_Deep_Dive.md](./Metrics_Deep_Dive.md) | Deep dive into evaluation metrics |

⬅️ **Prev:** [04 Unsupervised Learning](../04_Unsupervised_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Overfitting and Regularization](../06_Overfitting_and_Regularization/Theory.md)
