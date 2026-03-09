# K-Means Clustering — Cheatsheet

**One-liner:** K-Means is an unsupervised algorithm that partitions data into K clusters by iteratively assigning points to the nearest centroid and updating centroids to the mean of their assigned points.

---

## Key Terms

| Term | What It Means |
|---|---|
| Unsupervised Learning | Learning from data with no labels — finding structure on its own |
| Cluster | A group of data points that are similar to each other |
| Centroid | The centre point of a cluster — the mean of all points assigned to it |
| K | The number of clusters you want — you must choose this before running |
| Inertia (WCSS) | Within-Cluster Sum of Squares — total distance from each point to its centroid. Lower = tighter clusters |
| Elbow Method | Plot K vs inertia; pick K at the "elbow" where improvement slows sharply |
| Convergence | When assignments stop changing between iterations — the algorithm is done |
| n_init | Number of times K-Means runs with different random starts — best result kept |
| k-means++ | Smarter centroid initialization that spreads initial centroids out — the sklearn default |

---

## When to Use vs When Not to Use

| Use K-Means When | Avoid K-Means When |
|---|---|
| You have no labels and want to find groups | You need clusters with complex shapes (use DBSCAN instead) |
| You have a rough idea of how many clusters exist | You have no idea how many clusters and cannot explore |
| Clusters are roughly spherical and similar-sized | Clusters have very different sizes or densities |
| Dataset is large and you need speed | Data has many outliers that will skew centroids |
| Exploratory analysis / data segmentation | You need a guarantee of finding the global optimum |

---

## Algorithm Steps (Quick Reference)

```
1. Choose K
2. Initialize K centroids (randomly or k-means++)
3. ASSIGN: each point → nearest centroid (by Euclidean distance)
4. UPDATE: each centroid → mean of its assigned points
5. Repeat 3–4 until assignments stop changing
```

---

## Key sklearn Parameters

| Parameter | Default | What It Controls |
|---|---|---|
| `n_clusters` | 8 | Number of clusters K |
| `init` | `'k-means++'` | Centroid initialization method |
| `n_init` | 10 | Number of random restarts — best result kept |
| `max_iter` | 300 | Maximum iterations per run |
| `random_state` | None | Seed for reproducibility |

---

## Golden Rules

1. **Always scale your features** — K-Means uses Euclidean distance, so features on different scales will dominate the calculation. Use `StandardScaler`.
2. **Use k-means++ initialization** — it is the default in sklearn and almost always better than pure random initialization.
3. **Run multiple times** — set `n_init=10` or higher to avoid getting stuck in a bad local minimum.
4. **Use the elbow method to find K** — plot inertia vs K and look for the bend.
5. **K-Means is non-deterministic** — set `random_state` for reproducible results.
6. **Inertia always decreases as K increases** — do not just pick the largest K. Use the elbow or silhouette score.
7. **Check silhouette score** — values close to 1 mean well-separated clusters; values near 0 or negative mean overlapping clusters.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, how K-Means works, elbow method |
| **Cheatsheet.md** | ← you are here |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| [Code_Example.md](./Code_Example.md) | Full working Python example with elbow method |

⬅️ **Prev:** [05 SVM](../05_SVM/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 PCA](../07_PCA_Dimensionality_Reduction/Theory.md)
