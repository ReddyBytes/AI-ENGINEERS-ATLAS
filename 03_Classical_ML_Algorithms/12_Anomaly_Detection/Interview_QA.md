# Anomaly Detection — Interview Q&A

---

## Beginner

**Q1: What is anomaly detection and how does it differ from standard classification?**

<details>
<summary>💡 Show Answer</summary>

Anomaly detection identifies data points that deviate significantly from the expected pattern. It differs from standard classification in three key ways: (1) **label availability** — standard classification requires labeled positive examples for every class, but anomaly detection often operates with no anomaly labels at all, only examples of normal behavior; (2) **class balance** — standard classifiers work best when classes are roughly balanced, but anomaly detection deals with extreme imbalance (0.01% fraud rate); and (3) **generalization** — a standard classifier learns to recognize specific patterns of fraud it has seen before, while a good anomaly detector flags anything that deviates from normal, including novel attack types it has never seen.

</details>

---

<br>

**Q2: What is Isolation Forest and why does it work well for anomaly detection?**

<details>
<summary>💡 Show Answer</summary>

Isolation Forest isolates data points by building random trees: at each node, randomly select a feature and a random split threshold, and keep splitting until each point is in its own leaf. The key insight is that anomalies are rare and different — they sit far from the cluster of normal data. This means anomalies get isolated in very few splits (short path length), while normal points require many splits to isolate (long path length). An anomaly score is computed as the inverse of the average path length across many trees. Isolation Forest works well because it doesn't require computing distances or densities (which fail in high dimensions) and scales linearly with data size. It requires no labeled anomalies — only the assumption that anomalies are few and different.

</details>

---

<br>

**Q3: Why is accuracy a bad metric for anomaly detection in highly imbalanced datasets?**

<details>
<summary>💡 Show Answer</summary>

With 1% fraud rate, a model that always predicts "normal" achieves 99% accuracy but detects zero fraud — zero utility. Accuracy treats every prediction equally, so the 99,000 correct "normal" predictions overwhelm the 1,000 missed frauds. The correct metrics are precision (of everything we flagged as anomalous, how many were actually anomalous — measures false alarm rate), recall (of all actual anomalies, how many did we catch — measures miss rate), F1 (harmonic mean of precision and recall), and PR-AUC (area under the precision-recall curve, which summarizes model performance across all decision thresholds). PR-AUC is the most reliable single metric for imbalanced anomaly detection.

</details>

---

## Intermediate

**Q4: What is SMOTE and what is the most important rule about when to apply it?**

<details>
<summary>💡 Show Answer</summary>

SMOTE (Synthetic Minority Over-sampling Technique) creates synthetic positive examples by interpolating between existing minority-class samples in feature space. For each minority sample, it selects k nearest neighbors and generates new points along the line segments connecting them. This balances the class distribution without just duplicating existing examples. The critical rule: **only apply SMOTE to the training fold, never to the test set**. Applying SMOTE to test data creates unrealistic synthetic anomalies that inflate evaluation metrics — your test set should reflect the real distribution you'll encounter in production. In sklearn/imbalanced-learn, use SMOTE inside a `Pipeline` object so it is applied only during `fit`, not during `predict`.

</details>

---

<br>

**Q5: What is the difference between ROC-AUC and PR-AUC, and which should you use for fraud detection?**

<details>
<summary>💡 Show Answer</summary>

ROC-AUC measures the probability that the model ranks a random positive higher than a random negative. It can be misleadingly high for imbalanced datasets: if 99% of data is normal, the model can achieve high ROC-AUC simply by ranking normals correctly — the many true negatives dominate the curve. PR-AUC (area under the precision-recall curve) focuses entirely on the minority class: it measures how well the model separates true positives from false positives across all thresholds, without being diluted by the large negative class. For fraud detection (or any highly imbalanced problem), prefer PR-AUC. A model with ROC-AUC of 0.95 can have PR-AUC of 0.30 if it fails to rank most fraud cases highly.

</details>

---

<br>

**Q6: How would you handle a 99:1 class imbalance with XGBoost?**

<details>
<summary>💡 Show Answer</summary>

Three complementary strategies: (1) **`scale_pos_weight`**: set to `sum(negatives) / sum(positives)` = 99. This tells XGBoost to treat each positive sample as if it were 99 negative samples — the loss function penalizes missing fraud proportionally more than missing normal transactions. (2) **Evaluation metric**: use `eval_metric="aucpr"` instead of the default accuracy or AUC — PR-AUC correctly captures performance on the minority class. (3) **Threshold tuning**: after training, don't use the default 0.5 probability threshold. Compute the precision-recall curve on validation data and find the threshold that maximizes F1 (or the business-specific tradeoff between false positives and false negatives). `scale_pos_weight` is typically sufficient and simpler than SMOTE for XGBoost; both can be combined for very extreme imbalance.

</details>

---

## Advanced

**Q7: How do autoencoders work for anomaly detection, and when do you use them over Isolation Forest?**

<details>
<summary>💡 Show Answer</summary>

An autoencoder is trained on normal data only to compress inputs to a low-dimensional bottleneck representation and then reconstruct the original input. After training, normal data reconstructs well (low reconstruction error). Anomalous data does not fit the learned compression — the autoencoder struggles to reconstruct it, yielding high reconstruction error. Anomaly score = `||x - decoder(encoder(x))||²`. Use autoencoders over Isolation Forest when: (1) the data is high-dimensional (images, sequences, sensor arrays) where Isolation Forest degrades due to the curse of dimensionality; (2) you need to detect anomalies in the feature space that emerge from complex non-linear interactions; (3) you want to build a model of normalcy rather than just an isolation score. Isolation Forest remains faster to train and simpler to tune for moderate-dimensional tabular data.

</details>

---

<br>

**Q8: What are the three types of anomalies and give a real-world example of each?**

<details>
<summary>💡 Show Answer</summary>

**Point anomaly**: a single observation that is statistically inconsistent with the overall distribution. Example: a user who normally spends $50/day suddenly makes a $5,000 transaction. **Contextual anomaly**: an observation that would be normal in a different context but is anomalous in its specific context. Example: 35°C temperature in Alaska in January — perfectly normal in August, but anomalous for winter. The value itself is not extreme globally; its context makes it anomalous. **Collective anomaly**: no single observation is individually unusual, but a group of observations together forms an anomalous pattern. Example: network packets that are individually unremarkable in size and timing, but collectively form a distributed denial-of-service attack pattern. Point anomalies are the easiest to detect; collective anomalies require sequence or graph-based methods.

</details>

---

<br>

**Q9: How would you build an anomaly detection system for credit card fraud in production?**

<details>
<summary>💡 Show Answer</summary>

A production fraud detection system typically uses multiple layers: (1) **Feature engineering**: create features like time since last transaction, distance from home location, velocity (number of transactions in last hour), amount z-score relative to user's history; (2) **Real-time scoring**: an XGBoost or gradient boosted model with `scale_pos_weight` returns a fraud probability per transaction in < 100ms; (3) **Threshold strategy**: high-confidence fraud (probability > 0.95) is auto-declined; medium-confidence (0.5–0.95) is queued for analyst review or triggers step-up authentication; low confidence passes; (4) **Feedback loop**: analysts label queued transactions → these become new training data → model is retrained weekly; (5) **Concept drift monitoring**: track feature distributions and model score distributions in production — alert when they shift significantly, indicating a new fraud pattern or concept drift. Evaluation uses precision-recall on the held-out test period, not random split.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [Recommendation Systems](../11_Recommendation_Systems/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [Neural Networks — Perceptron](../../04_Neural_Networks_and_Deep_Learning/01_Perceptron/Theory.md)
