# Model Evaluation — Metrics Deep Dive

## Running Example: A Spam Filter

We will use a spam filter throughout this document. The filter looks at each incoming email and decides: spam or not spam?

- **Positive class** = spam (what we are trying to detect)
- **Negative class** = not spam (legitimate email)

Suppose our filter processes 1,000 emails:
- 100 are actually spam
- 900 are legitimate

Our filter's results: TP=80, FP=20, FN=20, TN=880

---

## Metric 1: Accuracy

**Formula:**
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
         = (80 + 880) / 1000
         = 96%
```

**Plain-English Meaning:**
Out of every 100 emails, the filter made the right call on 96 of them.

**When It Matters Most:**
When both classes are roughly equal in size and errors in both directions cost the same.

**Spam Filter Example:**
96% accuracy sounds great. But this hides something important — the filter missed 20 real spam emails (FN=20) and falsely flagged 20 legitimate emails as spam (FP=20). Depending on which error matters more to you, 96% may or may not be acceptable.

**Watch Out For:**
If you had 990 legitimate emails and 10 spam, a filter that marks everything as "not spam" would score 99% accuracy while catching zero spam. Accuracy is unreliable whenever one class is much rarer than the other.

---

## Metric 2: Precision

**Formula:**
```
Precision = TP / (TP + FP)
           = 80 / (80 + 20)
           = 80%
```

**Plain-English Meaning:**
When the filter calls something spam, it is right 80% of the time. 20% of its "spam" calls are false alarms.

**When It Matters Most:**
When false alarms are costly. In a spam filter, a false positive means a legitimate email lands in the spam folder — the user might miss an important message. High precision = fewer good emails incorrectly quarantined.

**Spam Filter Example:**
Precision of 80% means 1 in 5 emails the filter flags is actually legitimate. If you run this on someone's inbox, they will regularly miss real emails. That is a bad user experience. You would want to raise the decision threshold to increase precision, even if it means missing more actual spam (lower recall).

---

## Metric 3: Recall (Sensitivity)

**Formula:**
```
Recall = TP / (TP + FN)
       = 80 / (80 + 20)
       = 80%
```

**Plain-English Meaning:**
Of all the real spam emails, the filter caught 80% of them. 20% slipped through to the inbox.

**When It Matters Most:**
When missing a real case is costly. For spam, a missed spam email is annoying but not dangerous. For a medical test, a missed real disease case (FN) could be fatal. For fraud detection, a missed fraud case means real financial loss.

**Spam Filter Example:**
Recall of 80% means 20 out of 100 spam emails get through. For a spam filter this is acceptable — most people tolerate some spam in their inbox. For a medical screening test for cancer, 80% recall would be dangerously low — 1 in 5 real cancer cases goes undetected.

---

## Metric 4: F1 Score

**Formula:**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
   = 2 × (0.80 × 0.80) / (0.80 + 0.80)
   = 2 × 0.64 / 1.60
   = 80%
```

**Plain-English Meaning:**
A single balanced score that captures both precision and recall. It is only high when both are high.

**When It Matters Most:**
When you need one number that represents overall classifier quality on an imbalanced problem — especially when you are comparing multiple models.

**Spam Filter Example:**
Both precision and recall are 80% in our example, so F1 is also 80%. Now imagine a second filter: precision=95%, recall=50%. F1 = 2×(0.95×0.50)/(0.95+0.50) = 65%. Despite the impressive precision, the F1 reveals this filter misses too much spam to be truly useful. F1 prevents one good metric from hiding a bad one.

**The Harmonic Mean Matters:**
The harmonic mean punishes imbalance. Precision=100%, Recall=1% gives F1 = 2%. Arithmetic mean would give 50.5% — misleadingly high. F1 correctly shows this classifier is nearly useless.

---

## Metric 5: ROC-AUC

**Concept:**
Most classifiers output a probability (e.g., "72% chance this is spam") rather than a hard yes/no. You choose a threshold (e.g., "flag as spam if > 50%") to convert probabilities to decisions.

The ROC curve plots, at every possible threshold:
- Y-axis: True Positive Rate = Recall = TP / (TP + FN)
- X-axis: False Positive Rate = FP / (FP + TN)

**What AUC Means:**
AUC (Area Under the Curve) is a single number from 0.5 to 1.0.
- 1.0 = perfect model: can perfectly separate spam from non-spam at the right threshold
- 0.5 = random model: no better than flipping a coin
- 0.8+ = generally considered good

**Formula (informal):**
```
AUC = probability that the model ranks a random spam email
      higher than a random legitimate email
```

**When It Matters Most:**
When comparing models regardless of threshold — you want to know which model has better inherent discriminative ability, before deciding where to set the threshold.

**Spam Filter Example:**
Filter A: AUC = 0.95. Filter B: AUC = 0.75. Filter A is better at separating spam from non-spam across all possible thresholds. Once you deploy, you can tune the threshold for your specific precision/recall needs, but you want the highest AUC to start from.

**Watch Out For:**
AUC does not tell you how the model performs at any specific threshold. A model with AUC=0.90 might still have bad precision at your operating threshold. Always check the actual precision/recall at your chosen threshold in production.

---

## Summary Table

| Metric | Formula | Score in Example | Best For |
|---|---|---|---|
| Accuracy | (TP+TN)/total | 96% | Balanced classes |
| Precision | TP/(TP+FP) | 80% | False alarms are costly |
| Recall | TP/(TP+FN) | 80% | Missing cases is costly |
| F1 | 2PR/(P+R) | 80% | Balanced single-number summary |
| ROC-AUC | Area under ROC curve | ~0.93 (example) | Model comparison, threshold-agnostic |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Metrics_Deep_Dive.md** | ← you are here |

⬅️ **Prev:** [04 Unsupervised Learning](../04_Unsupervised_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Overfitting and Regularization](../06_Overfitting_and_Regularization/Theory.md)
