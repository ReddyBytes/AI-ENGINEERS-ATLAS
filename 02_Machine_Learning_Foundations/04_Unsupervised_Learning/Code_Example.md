# Unsupervised Learning — Code Example

## K-Means Clustering: Finding Groups Without Labels

We will create a small dataset of customer spending data and let K-Means find the natural groupings — without us telling it what those groups are.

```python
# ============================================================
# UNSUPERVISED LEARNING — K-MEANS CLUSTERING
# Goal: Discover natural customer groups from spending behavior
# No labels used — the algorithm finds patterns on its own
# ============================================================

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ============================================================
# STEP 1: CREATE THE DATA
# 30 customers, each described by 2 features:
#   - annual_spend: how much they spend per year ($)
#   - visit_frequency: how many times they visit per month
# We are NOT providing any labels — no "type A customer" etc.
# ============================================================

np.random.seed(42)

# Simulate 3 natural groups (we won't tell the model this)
# Group 1: Low spenders, rare visitors (budget shoppers)
group1 = np.random.normal(loc=[200, 2], scale=[50, 1], size=(10, 2))

# Group 2: Medium spenders, moderate visitors (regular customers)
group2 = np.random.normal(loc=[600, 8], scale=[80, 2], size=(10, 2))

# Group 3: High spenders, frequent visitors (VIP customers)
group3 = np.random.normal(loc=[1200, 20], scale=[100, 3], size=(10, 2))

# Stack all customers into one dataset (no labels attached)
X = np.vstack([group1, group2, group3])

print(f"Dataset shape: {X.shape}")  # (30, 2) = 30 customers, 2 features

# ============================================================
# STEP 2: SCALE THE FEATURES
# K-Means uses distance — if annual_spend is in the hundreds
# and visit_frequency is in single digits, spend dominates.
# StandardScaler makes both features equally important.
# ============================================================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("Features scaled — both now have mean=0, std=1")

# ============================================================
# STEP 3: RUN K-MEANS WITH K=3
# We tell the algorithm to find 3 clusters.
# It starts with random centroids and iterates until stable.
# ============================================================

kmeans = KMeans(
    n_clusters=3,    # we want 3 groups
    n_init=10,       # run 10 times with different random starts, keep best
    random_state=42
)

# fit() is where clustering happens — the model finds the groups
kmeans.fit(X_scaled)

# Each customer is now assigned a cluster label: 0, 1, or 2
cluster_labels = kmeans.labels_
print(f"\nCluster assignments: {cluster_labels}")
# Note: label numbers are arbitrary — 0, 1, 2 are just IDs not rankings

# ============================================================
# STEP 4: EXAMINE THE RESULTS
# Look at the cluster centroids (the "average" of each group)
# and how many customers ended up in each cluster
# ============================================================

# Get centroids back in original scale for interpretability
centroids_scaled = kmeans.cluster_centers_
centroids_original = scaler.inverse_transform(centroids_scaled)

print("\nCluster Centroids (original scale):")
print(f"{'Cluster':<10} {'Avg Annual Spend ($)':<25} {'Avg Monthly Visits'}")
print("-" * 55)
for i, centroid in enumerate(centroids_original):
    count = np.sum(cluster_labels == i)
    print(f"Cluster {i}  ${centroid[0]:<23.0f} {centroid[1]:.1f} visits  ({count} customers)")

# ============================================================
# STEP 5: PREDICT CLUSTER FOR A NEW CUSTOMER
# Once trained, the model can assign new customers to clusters
# ============================================================

new_customer = np.array([[800, 12]])   # medium-high spender, frequent visitor
new_customer_scaled = scaler.transform(new_customer)
predicted_cluster = kmeans.predict(new_customer_scaled)

print(f"\nNew customer (spend=$800, visits=12) → Cluster {predicted_cluster[0]}")

# ============================================================
# STEP 6: CHECK THE ELBOW METHOD (HOW GOOD IS K=3?)
# Try different values of K and see where inertia stops dropping
# ============================================================

inertias = []
k_values = range(1, 8)

for k in k_values:
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

print("\nElbow Method — Inertia by K:")
print(f"{'K':<5} {'Inertia'}")
for k, inertia in zip(k_values, inertias):
    bar = "=" * int(inertia / 5)
    print(f"K={k}  {inertia:.1f}  {bar}")
# You should see a big drop from K=1 to K=3, then it flattens — the elbow
```

---

## What This Shows

- **No labels anywhere.** The algorithm receives only raw features (spend, visits) and discovers that customers naturally fall into groups.

- **StandardScaler is critical.** Without scaling, annual spend in the hundreds would dominate visit frequency in single digits, and the clustering would just be "sort by spend."

- **Cluster labels (0, 1, 2) are arbitrary IDs.** The algorithm does not know or care that cluster 0 happens to be budget shoppers. A human analyst interprets the centroids after the fact.

- **The elbow method** shows that K=3 is a good choice because adding more clusters beyond 3 gives diminishing returns — the inertia does not drop much.

- **predict() on new data** shows that the model generalizes — you can assign new, unseen customers to the clusters it discovered.

The pattern here (fit on data, examine clusters, assign new examples) is the same workflow for all clustering problems regardless of dataset size.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [03 Supervised Learning](../03_Supervised_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Model Evaluation](../05_Model_Evaluation/Theory.md)
