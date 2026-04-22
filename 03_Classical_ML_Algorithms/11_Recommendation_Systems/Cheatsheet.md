# Recommendation Systems — Cheatsheet

## Algorithm Decision Guide

| Situation | Use |
|---|---|
| New item, no interactions yet | Content-Based Filtering |
| New user, no history | Popularity baseline + onboarding |
| Large user-item interaction history | Matrix Factorization (ALS/SVD) |
| Need explainability ("because you watched X") | Item-Based CF |
| Large-scale production with deep features | Two-Tower Neural Network |
| Small dataset, quick prototype | Surprise library with SVD |

---

## Content-Based Filtering

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

tfidf = TfidfVectorizer(stop_words="english")
item_matrix = tfidf.fit_transform(items["description"])   # (n_items, n_terms)

def get_recommendations(item_idx, top_k=5):
    scores = cosine_similarity(item_matrix[item_idx], item_matrix).flatten()
    similar = scores.argsort()[::-1][1:top_k+1]   # exclude self
    return items.iloc[similar]["title"].tolist()
```

---

## Item-Based Collaborative Filtering

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ratings: (n_users, n_items) — 0 means not rated
item_sim = cosine_similarity(ratings.T)    # (n_items, n_items)

def predict_ratings(user_idx, ratings, item_sim):
    user_ratings = ratings[user_idx]                       # shape: (n_items,)
    scores = item_sim.T @ user_ratings                     # weighted by similarity
    # Zero out already-rated items
    scores[user_ratings > 0] = 0
    return scores.argsort()[::-1]                          # ranked indices
```

---

## Matrix Factorization with Surprise

```python
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from surprise import accuracy

reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(df[["userId", "itemId", "rating"]], reader)
trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

model = SVD(n_factors=50, n_epochs=20, lr_all=0.005, reg_all=0.02, random_state=42)
model.fit(trainset)

predictions = model.test(testset)
print(f"RMSE: {accuracy.rmse(predictions):.4f}")
print(f"MAE:  {accuracy.mae(predictions):.4f}")

# Predict single user-item pair
pred = model.predict(uid="user_1", iid="item_42")
print(f"Predicted rating: {pred.est:.2f}")

# Get top-N for a user
def top_n_for_user(model, user_id, all_item_ids, rated_items, n=10):
    candidates = [i for i in all_item_ids if i not in rated_items]
    predictions = [model.predict(user_id, iid) for iid in candidates]
    predictions.sort(key=lambda x: x.est, reverse=True)
    return [p.iid for p in predictions[:n]]
```

---

## Implicit Feedback with ALS

```python
import implicit
import scipy.sparse as sp

# Build sparse user-item matrix from implicit signals
user_ids = df["userId"].astype("category").cat.codes
item_ids = df["itemId"].astype("category").cat.codes
confidence = df["play_count"].values    # confidence: higher = stronger signal

matrix = sp.csr_matrix((confidence, (user_ids, item_ids)))

model = implicit.als.AlternatingLeastSquares(
    factors=50,
    iterations=20,
    regularization=0.1,
    alpha=40,    # confidence scaling: Cui = 1 + α * rui
)
model.fit(matrix)

# Recommend for user 0
ids, scores = model.recommend(0, matrix[0], N=10, filter_already_liked_items=True)
```

---

## Evaluation Metrics

```python
import numpy as np

def precision_at_k(recommended, relevant, k):
    top_k = recommended[:k]
    hits = len(set(top_k) & set(relevant))
    return hits / k

def recall_at_k(recommended, relevant, k):
    top_k = recommended[:k]
    hits = len(set(top_k) & set(relevant))
    return hits / len(relevant) if relevant else 0

def ndcg_at_k(recommended, relevant, k):
    dcg = sum(
        1 / np.log2(rank + 2)
        for rank, item in enumerate(recommended[:k])
        if item in set(relevant)
    )
    ideal_dcg = sum(1 / np.log2(rank + 2) for rank in range(min(k, len(relevant))))
    return dcg / ideal_dcg if ideal_dcg > 0 else 0
```

| Metric | Formula | When to Use |
|---|---|---|
| **RMSE** | `√mean((pred−true)²)` | Explicit ratings, regression evaluation |
| **Precision@K** | `hits in top-K / K` | When you care about false positives |
| **Recall@K** | `hits in top-K / all relevant` | When you care about missing relevant items |
| **NDCG@K** | DCG / ideal DCG | When rank position matters (top slot is most valuable) |
| **MAP** | Mean of AP across users | Overall ranking quality across the user base |

---

## Approach Comparison

| | Content-Based | User-CF | Item-CF | Matrix Factorization |
|---|---|---|---|---|
| Cold start — new user | ✅ Works | ❌ No data | ❌ No data | ❌ No data |
| Cold start — new item | ❌ New item needed | ❌ No interactions | ❌ No interactions | ❌ No interactions |
| Serendipity | Low (more of same) | High | Medium | High |
| Explainability | High | Medium | High | Low |
| Scalability | High | Low | High | High |
| Data needed | Item features | User ratings | User ratings | User ratings |

---

## Cold Start Strategies

| Scenario | Strategy |
|---|---|
| New user | Onboarding questionnaire → short content-based bootstrap |
| New user | Show trending / most popular as default |
| New item | Content-based only until N interactions reached |
| New item | Editorial boosting (manually surfaced) |
| Both | Hybrid model: weight CF vs CB by data availability |

---

## Two-Tower Neural Model (Production)

```python
import torch
import torch.nn as nn

class UserTower(nn.Module):
    def __init__(self, n_users, embedding_dim=64):
        super().__init__()
        self.embed = nn.Embedding(n_users, embedding_dim)
        self.fc = nn.Sequential(nn.Linear(embedding_dim, 128), nn.ReLU(),
                                nn.Linear(128, 64))
    def forward(self, user_ids):
        return self.fc(self.embed(user_ids))       # ← (batch, 64)

class ItemTower(nn.Module):
    def __init__(self, n_items, embedding_dim=64):
        super().__init__()
        self.embed = nn.Embedding(n_items, embedding_dim)
        self.fc = nn.Sequential(nn.Linear(embedding_dim, 128), nn.ReLU(),
                                nn.Linear(128, 64))
    def forward(self, item_ids):
        return self.fc(self.embed(item_ids))       # ← (batch, 64)

# At serving: pre-compute all item embeddings → store in vector DB
# Query: embed user → ANN search for top-k nearest item embeddings
```

---

## Golden Rules

1. Always evaluate with ranking metrics (NDCG, Precision@K) — RMSE alone is not enough
2. Plan for cold start from day one — collaborative filtering breaks without interaction history
3. Implicit feedback (views, clicks) is almost always more abundant than explicit ratings
4. Item-based CF scales better than user-based CF — precompute item similarities offline
5. The two-tower model is the production standard — use it when you outgrow Surprise/ALS
