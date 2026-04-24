# Model Evaluation — Interview Q&A

## Beginner Level

**Q1: What is a confusion matrix and what does each cell represent?**

<details>
<summary>💡 Show Answer</summary>

A: A confusion matrix is a 2x2 table that breaks down a classifier's predictions. The four cells are: True Positive (model predicted positive, was correct), True Negative (model predicted negative, was correct), False Positive (model predicted positive, was wrong — a false alarm), and False Negative (model predicted negative, was wrong — a missed case). Every evaluation metric for classification is derived from these four numbers.

</details>

<br>

**Q2: Why is accuracy a bad metric for imbalanced datasets? Give an example.**

<details>
<summary>💡 Show Answer</summary>

A: Consider a disease affecting 1% of people. A model that always predicts "no disease" has 99% accuracy — but it catches zero actual cases. Accuracy rewards predicting the majority class. On imbalanced datasets it looks good while being completely useless for the rare class. You need metrics that specifically measure performance on the minority class, like recall (how many real positives were caught) or F1-score.

</details>

<br>

**Q3: What is the difference between precision and recall?**

<details>
<summary>💡 Show Answer</summary>

A: Precision asks "when the model predicted positive, how often was it right?" It measures false alarm rate. Recall asks "of all the actual positives, how many did the model find?" It measures miss rate. A spam filter with high precision rarely marks good emails as spam. A spam filter with high recall catches almost all spam. They pull in opposite directions — improving one tends to hurt the other.

</details>

---

## Intermediate Level

**Q4: When should you optimize for precision vs recall? Give concrete examples.**

<details>
<summary>💡 Show Answer</summary>

A: Optimize for precision when false alarms are costly: a spam filter that incorrectly deletes important emails is very frustrating; a content moderation system that wrongly bans innocent users causes real harm. Optimize for recall when missing real cases is costly: a cancer screening test that misses actual tumors is dangerous; a fraud detection system that misses real fraud allows financial losses. In security/safety contexts, recall almost always matters more. In user-facing filtering contexts, precision often matters more.

</details>

<br>

**Q5: What is the F1 score and why use it instead of just looking at precision and recall separately?**

<details>
<summary>💡 Show Answer</summary>

A: F1 is the harmonic mean of precision and recall: 2PR/(P+R). It gives you a single number that represents both. The key property of the harmonic mean is that it is only high when BOTH values are high — a high precision with near-zero recall gives a near-zero F1, and vice versa. This makes it impossible for one good metric to hide a bad one. F1 is particularly useful when you need to compare models and want a balanced single-number summary.

</details>

<br>

**Q6: What is ROC-AUC and when is it useful?**

<details>
<summary>💡 Show Answer</summary>

A: ROC (Receiver Operating Characteristic) curve plots True Positive Rate (recall) against False Positive Rate at every possible classification threshold. AUC is the area under that curve — it ranges from 0.5 (no better than random) to 1.0 (perfect). AUC is threshold-independent: it tells you how well the model ranks positives above negatives regardless of where you set the decision boundary. It is useful for comparing models and for problems where the threshold will be tuned later. It is less useful when you need to evaluate at a specific operating threshold.

</details>

---

## Advanced Level

**Q7: How do you evaluate a multi-class classifier (not just binary)?**

<details>
<summary>💡 Show Answer</summary>

A: You extend the confusion matrix to NxN for N classes. For metrics, you can aggregate in three ways: macro average (calculate the metric per class, then take the unweighted average — treats all classes equally regardless of size), weighted average (average weighted by class frequency — appropriate when class distribution matters), and micro average (aggregate all TP/FP/FN across all classes before calculating — dominated by the largest class). For imbalanced multi-class problems, macro F1 is usually the most informative — it penalizes poor performance on rare classes.

</details>

<br>

**Q8: What is calibration and how does it differ from accuracy?**

<details>
<summary>💡 Show Answer</summary>

A: A model is calibrated if its probability outputs match real-world frequencies. If a calibrated model says "70% probability of rain" for 100 different days, it should rain on roughly 70 of them. Accuracy measures whether predictions are correct. Calibration measures whether predicted probabilities are trustworthy. A model can have high accuracy but be poorly calibrated — for example, it might be right most of the time but say 95% confidence for predictions that are actually only correct 60% of the time. Calibration matters when downstream decisions depend on the probability (like risk scoring or ranking). Techniques for improving calibration include Platt scaling and isotonic regression.

</details>

<br>

**Q9: How do you evaluate a model when you have a very small test set and results are noisy?**

<details>
<summary>💡 Show Answer</summary>

A: With a small test set, a single train/test split gives unreliable estimates — the result depends heavily on which examples ended up in the test set. Solutions: k-fold cross-validation (split data into k folds, train on k-1, test on 1, rotate k times, average the results — gives a more stable estimate), stratified k-fold (ensures each fold has the same class proportions as the full dataset), leave-one-out cross-validation (extreme case of k-fold where k = n, expensive but nearly unbiased), and bootstrapping (sample training data with replacement many times, evaluate on out-of-bag examples, average results). For final model comparison, report mean and standard deviation across folds — not just the mean.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Metrics_Deep_Dive.md](./Metrics_Deep_Dive.md) | Deep dive into evaluation metrics |

⬅️ **Prev:** [04 Unsupervised Learning](../04_Unsupervised_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Overfitting and Regularization](../06_Overfitting_and_Regularization/Theory.md)
