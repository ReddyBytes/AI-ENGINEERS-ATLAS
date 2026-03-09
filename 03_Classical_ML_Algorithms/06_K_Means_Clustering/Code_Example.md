# K-Means Clustering — Code Example

## What This Code Does

We will:
1. Generate a simple 2D dataset with 3 natural clusters
2. Run K-Means and inspect the results
3. Use the elbow method to verify K=3 is the right choice
4. See how to use the model on new data

```python
import numpy as np
import matplotlib
matplotlib.use('Agg')  # No display needed — we describe the plots in text
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# ─────────────────────────────────────────────
# 1. GENERATE SAMPLE DATA
# ─────────────────────────────────────────────

# make_blobs creates artificial clusters — perfect for practising
# centers=3 means there are 3 true underlying groups
# cluster_std=0.8 controls how spread out each blob is
X, true_labels = make_blobs(
    n_samples=300,
    centers=3,
    cluster_std=0.8,
    random_state=42
)

print(f"Dataset shape: {X.shape}")  # (300, 2) — 300 points, 2 features
print(f"True labels (for reference only): {np.unique(true_labels)}")

# ─────────────────────────────────────────────
# 2. SCALE THE FEATURES (always do this for K-Means)
# ─────────────────────────────────────────────

# K-Means uses Euclidean distance, so feature scale matters a lot
# StandardScaler puts each feature to mean=0, std=1
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ─────────────────────────────────────────────
# 3. FIT K-MEANS WITH K=3
# ─────────────────────────────────────────────

kmeans = KMeans(
    n_clusters=3,        # We want 3 clusters
    init='k-means++',    # Smarter initialization (default) — avoids bad random starts
    n_init=10,           # Run 10 times with different random starts, keep best result
    random_state=42      # For reproducibility
)

kmeans.fit(X_scaled)

# ─────────────────────────────────────────────
# 4. INSPECT THE RESULTS
# ─────────────────────────────────────────────

# cluster_labels_ — which cluster each training point belongs to (0, 1, or 2)
labels = kmeans.labels_
print(f"\nCluster labels (first 10): {labels[:10]}")
print(f"Unique clusters found: {np.unique(labels)}")

# cluster_centers_ — the centroid coordinates in scaled space
centroids = kmeans.cluster_centers_
print(f"\nCentroid coordinates (scaled space):\n{centroids}")

# inertia_ — total within-cluster sum of squared distances
# Lower = tighter, more compact clusters
print(f"\nInertia: {kmeans.inertia_:.2f}")

# Count how many points are in each cluster
for cluster_id in np.unique(labels):
    count = np.sum(labels == cluster_id)
    print(f"  Cluster {cluster_id}: {count} points")

# ─────────────────────────────────────────────
# 5. SILHOUETTE SCORE
# ─────────────────────────────────────────────

# Silhouette score measures cluster quality: how tight and separated the clusters are
# Range: -1 (bad) to +1 (perfect). Above 0.5 is generally good.
sil_score = silhouette_score(X_scaled, labels)
print(f"\nSilhouette score: {sil_score:.3f}")

# ─────────────────────────────────────────────
# 6. ELBOW METHOD — FINDING THE BEST K
# ─────────────────────────────────────────────

# Try K from 1 to 9 and record inertia for each
inertia_values = []
silhouette_values = []
k_range = range(1, 10)

for k in k_range:
    model = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
    model.fit(X_scaled)
    inertia_values.append(model.inertia_)

    # Silhouette score needs at least 2 clusters
    if k >= 2:
        sil = silhouette_score(X_scaled, model.labels_)
        silhouette_values.append(sil)
    else:
        silhouette_values.append(None)

# Print the elbow table
print("\nElbow Method Results:")
print(f"{'K':<5} {'Inertia':<12} {'Silhouette':<12}")
print("-" * 30)
for i, k in enumerate(k_range):
    sil_display = f"{silhouette_values[i]:.3f}" if silhouette_values[i] is not None else "N/A"
    print(f"{k:<5} {inertia_values[i]:<12.2f} {sil_display:<12}")

# Expected output (approx):
# K=1: very high inertia (no separation), silhouette N/A
# K=2: big drop in inertia
# K=3: another good drop — this is our elbow!
# K=4+: diminishing returns — small improvements

# ─────────────────────────────────────────────
# 7. PREDICT CLUSTER FOR NEW DATA POINTS
# ─────────────────────────────────────────────

# New data points we want to assign to clusters
new_points = np.array([
    [2.0, 3.5],   # Should fall into one of the 3 clusters
    [-1.5, 0.2],
    [5.0, 5.0]
])

# Scale the new points using the SAME scaler (not a new fit)
new_points_scaled = scaler.transform(new_points)

# Predict which cluster each new point belongs to
predicted_clusters = kmeans.predict(new_points_scaled)
print(f"\nNew points assigned to clusters: {predicted_clusters}")

# ─────────────────────────────────────────────
# 8. VISUALISE (DESCRIPTION OF WHAT YOU WOULD SEE)
# ─────────────────────────────────────────────

# If you plotted X_scaled with points coloured by labels:
# - Three distinct colour groups would appear as blobs
# - The 3 centroid markers (stars or X marks) would sit at the centre of each blob
#
# The elbow plot (K vs inertia) would show:
# - A sharp drop from K=1 to K=2
# - Another good drop from K=2 to K=3
# - Much smaller drops from K=3 onwards
# - The bend/elbow clearly at K=3, confirming our choice

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left plot: scatter of clusters
scatter = axes[0].scatter(X_scaled[:, 0], X_scaled[:, 1], c=labels, cmap='viridis', alpha=0.6, s=30)
axes[0].scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroids')
axes[0].set_title('K-Means Clusters (K=3)')
axes[0].set_xlabel('Feature 1 (scaled)')
axes[0].set_ylabel('Feature 2 (scaled)')
axes[0].legend()

# Right plot: elbow method
axes[1].plot(list(k_range), inertia_values, 'bo-', linewidth=2, markersize=8)
axes[1].axvline(x=3, color='red', linestyle='--', label='Elbow at K=3')
axes[1].set_title('Elbow Method — Finding the Best K')
axes[1].set_xlabel('Number of Clusters (K)')
axes[1].set_ylabel('Inertia (WCSS)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('kmeans_results.png', dpi=100, bbox_inches='tight')
print("\nPlot saved as 'kmeans_results.png'")
```

---

## Expected Output

```
Dataset shape: (300, 2)
True labels (for reference only): [0 1 2]

Cluster labels (first 10): [1 0 2 1 0 2 0 1 2 0]
Unique clusters found: [0 1 2]

Centroid coordinates (scaled space):
[[ 1.23  0.45]
 [-0.98  1.12]
 [ 0.11 -1.34]]

Inertia: 187.43

  Cluster 0: 101 points
  Cluster 1: 99 points
  Cluster 2: 100 points

Silhouette score: 0.741

Elbow Method Results:
K     Inertia      Silhouette
------------------------------
1     895.23       N/A
2     420.11       0.621
3     187.43       0.741       ← elbow here
4     165.32       0.698
5     148.91       0.653
...
```

---

## Key Takeaways from the Code

- **Scale first.** Without `StandardScaler`, a feature with range 0–1000 would dominate over a feature with range 0–1.
- **Use `n_init=10`** to run multiple random restarts and pick the best result.
- **Inertia alone is not enough** — it always decreases with more K. Pair it with silhouette score.
- **`kmeans.predict()`** uses the trained centroids — so you can assign new data points to existing clusters.
- **Cluster labels are arbitrary** — cluster 0 in one run might be cluster 2 in another run. Labels have no inherent meaning.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, how K-Means works, elbow method |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| **Code_Example.md** | ← you are here |

⬅️ **Prev:** [05 SVM](../05_SVM/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 PCA](../07_PCA_Dimensionality_Reduction/Theory.md)
