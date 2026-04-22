# Anomaly Detection — Cheatsheet

## Algorithm Selection Guide

| Situation | Use |
|---|---|
| No labels, tabular data | Isolation Forest |
| No labels, density-based outliers | Local Outlier Factor (LOF) |
| No labels, high-dimensional / image | Autoencoder reconstruction error |
| Labels available, severe imbalance | XGBoost + `scale_pos_weight` |
| Labels available, want oversampling | SMOTE + Random Forest |
| Time series anomalies | ARIMA residuals or LSTM reconstruction |
| One-class classification | One-Class SVM |

---

## Isolation Forest

```python
from sklearn.ensemble import IsolationForest

clf = IsolationForest(
    n_estimators=100,        # more trees = more stable scores
    contamination=0.01,      # expected fraction of anomalies
    max_samples="auto",      # samples used per tree (auto = min(256, n_samples))
    random_state=42,
)
clf.fit(X_train)

# Predict: -1 = anomaly, 1 = normal
y_pred = clf.predict(X_test)

# Continuous anomaly score (lower = more anomalous)
scores = clf.decision_function(X_test)

# Flag the most anomalous 1%
threshold = np.percentile(scores, 1)
anomalies = X_test[scores < threshold]
```

---

## Local Outlier Factor (LOF)

```python
from sklearn.neighbors import LocalOutlierFactor

# Transductive (predict on training data):
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.01)
y_pred = lof.fit_predict(X)    # -1 = anomaly, 1 = normal

# Novelty detection (predict on new data):
lof = LocalOutlierFactor(n_neighbors=20, novelty=True)
lof.fit(X_train)
y_pred = lof.predict(X_test)
scores = lof.decision_function(X_test)    # lower = more anomalous
```

---

## SMOTE — Handling Class Imbalance

```python
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier

# Standalone SMOTE
sm = SMOTE(sampling_strategy=0.1, random_state=42)   # minority → 10% of majority
X_res, y_res = sm.fit_resample(X_train, y_train)

# SMOTE inside a pipeline (correct — avoids leakage)
pipeline = ImbPipeline([
    ("smote", SMOTE(random_state=42)),
    ("clf", RandomForestClassifier(n_estimators=100, class_weight="balanced")),
])
pipeline.fit(X_train, y_train)
```

**SMOTE variants:**

| Variant | When to Use |
|---|---|
| `SMOTE` | Default — interpolates between minority neighbors |
| `ADASYN` | Adaptive — generates more in harder regions |
| `BorderlineSMOTE` | Only oversample near decision boundary |
| `SMOTEENN` | SMOTE + undersampling of noisy majority samples |

---

## XGBoost for Imbalanced Classification

```python
from xgboost import XGBClassifier
import numpy as np

neg = (y_train == 0).sum()
pos = (y_train == 1).sum()
scale_pos_weight = neg / pos    # e.g., 99 for 1% fraud rate

clf = XGBClassifier(
    n_estimators=500,
    max_depth=5,
    learning_rate=0.05,
    scale_pos_weight=scale_pos_weight,   # ← key for imbalance
    eval_metric="aucpr",                 # PR-AUC better than ROC-AUC here
    early_stopping_rounds=50,
    random_state=42,
)
clf.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

y_prob = clf.predict_proba(X_test)[:, 1]
```

---

## Threshold Tuning

```python
from sklearn.metrics import f1_score, precision_recall_curve
import numpy as np

# Find the threshold that maximizes F1
precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
f1_scores = 2 * precision * recall / (precision + recall + 1e-8)
best_threshold = thresholds[np.argmax(f1_scores)]

y_pred_tuned = (y_prob >= best_threshold).astype(int)
print(f"Best threshold: {best_threshold:.3f}")
print(f"F1 at best threshold: {f1_scores.max():.4f}")
```

---

## Evaluation Metrics (Imbalanced Data)

```python
from sklearn.metrics import (
    classification_report,
    average_precision_score,
    roc_auc_score,
    confusion_matrix,
)

print(classification_report(y_true, y_pred))   # precision, recall, f1 per class

print(f"PR-AUC:  {average_precision_score(y_true, y_prob):.4f}")
print(f"ROC-AUC: {roc_auc_score(y_true, y_prob):.4f}")

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
print(f"Precision: {tp / (tp + fp):.4f}")  # of flagged anomalies, how many were real
print(f"Recall:    {tp / (tp + fn):.4f}")  # of all real anomalies, how many caught
```

| Metric | Formula | Use When |
|---|---|---|
| **Precision** | `TP / (TP + FP)` | Cost of false alarms is high (blocking legitimate users) |
| **Recall** | `TP / (TP + FN)` | Cost of missing anomaly is high (fraud escapes) |
| **F1** | `2 × P × R / (P + R)` | Balanced view of both |
| **PR-AUC** | Area under P-R curve | Best overall for imbalanced — use instead of ROC-AUC |
| **ROC-AUC** | Area under ROC curve | Misleadingly high when negatives dominate |

---

## Autoencoder for Anomaly Detection

```python
import torch
import torch.nn as nn

class Autoencoder(nn.Module):
    def __init__(self, input_dim, bottleneck=16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 64), nn.ReLU(),
            nn.Linear(64, bottleneck),
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck, 64), nn.ReLU(),
            nn.Linear(64, input_dim),
        )

    def forward(self, x):
        return self.decoder(self.encoder(x))

# Train on NORMAL data only
model = Autoencoder(input_dim=X_train.shape[1])
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

for epoch in range(50):
    out = model(torch.tensor(X_normal, dtype=torch.float32))
    loss = criterion(out, torch.tensor(X_normal, dtype=torch.float32))
    optimizer.zero_grad(); loss.backward(); optimizer.step()

# At inference: high reconstruction error = anomaly
with torch.no_grad():
    X_t = torch.tensor(X_test, dtype=torch.float32)
    reconstruction = model(X_t)
    errors = ((X_t - reconstruction) ** 2).mean(dim=1).numpy()

threshold = np.percentile(errors, 99)   # top 1% are anomalies
anomalies = X_test[errors > threshold]
```

---

## Anomaly Type Reference

| Type | Example | Best Method |
|---|---|---|
| **Point anomaly** | Single fraud transaction | Isolation Forest, XGBoost |
| **Contextual anomaly** | Hot temperature in winter | Time series models |
| **Collective anomaly** | DDoS packet pattern | Sequence models, clustering |

---

## Golden Rules

1. Never use accuracy for imbalanced data — use PR-AUC, F1, or precision/recall separately
2. Never apply SMOTE to the test set — only to the training fold inside a pipeline
3. Tune the decision threshold on validation data — the default 0.5 threshold is almost always wrong
4. Set `contamination` to your realistic anomaly rate — not the default 0.1
5. Prefer PR-AUC over ROC-AUC for imbalanced problems — ROC-AUC is inflated by the large true negative base
