# K-Means Clustering — Interview Q&A

## Beginner Level

**Q1. What is K-Means clustering and how is it different from classification?**

<details>
<summary>💡 Show Answer</summary>

K-Means is an unsupervised learning algorithm that groups data points into K clusters based on similarity. Classification is supervised — it learns from labelled examples to predict a known category. K-Means has no labels. It discovers natural groupings in the data from scratch. You feed it data points, and it figures out the groups on its own.

</details>

<br>

**Q2. Walk me through how K-Means works step by step.**

<details>
<summary>💡 Show Answer</summary>

1. You choose K (the number of clusters you want).
2. The algorithm places K centroids — initially at random positions.
3. Every data point is assigned to whichever centroid is closest (using Euclidean distance).
4. Each centroid moves to the average (mean) position of all points assigned to it.
5. Steps 3 and 4 repeat until the assignments stop changing — the algorithm has converged.

</details>

<br>

**Q3. What is inertia in K-Means?**

<details>
<summary>💡 Show Answer</summary>

Inertia (also called Within-Cluster Sum of Squares, WCSS) is the total sum of squared distances from each data point to its assigned centroid. It measures how tight the clusters are. Lower inertia means points are closer to their centroids — better, more compact clusters. Inertia always decreases as you increase K, which is why you use the elbow method to find the right K rather than just maximizing K.

</details>

---

## Intermediate Level

**Q4. What is the elbow method and how do you use it?**

<details>
<summary>💡 Show Answer</summary>

The elbow method is a visual technique for choosing K. You run K-Means with K = 1, 2, 3, ..., 10 (or more) and record the inertia for each. Then you plot K on the x-axis and inertia on the y-axis. As K increases, inertia decreases. At first the drop is steep — each new cluster is genuinely helping. At some point the improvement slows dramatically and the curve bends like an elbow. That elbow point is the recommended K. Beyond it, extra clusters are splitting tight groups rather than finding genuinely separate ones.

</details>

<br>

**Q5. Why is K-Means sensitive to initialization, and how does k-means++ solve this?**

<details>
<summary>💡 Show Answer</summary>

K-Means can converge to a local optimum rather than the global one. If the initial centroids happen to start in bad positions (e.g. two centroids in the same actual cluster), the algorithm may settle into a suboptimal solution. k-means++ fixes this with a smarter initialization: instead of placing centroids at random, it places the first one randomly, then chooses each subsequent centroid with probability proportional to its squared distance from the nearest already-chosen centroid. This spreads the initial centroids out, making it much more likely to start near the true cluster centres.

</details>

<br>

**Q6. What are the key limitations of K-Means?**

<details>
<summary>💡 Show Answer</summary>

- **You must choose K** — the algorithm cannot figure out the right number of clusters on its own.
- **Assumes spherical clusters** — fails on elongated, ring-shaped, or irregular clusters.
- **Sensitive to outliers** — one extreme point can pull a centroid far away.
- **Equal cluster size assumption** — struggles when true clusters are very different in size or density.
- **Non-deterministic** — different random starts can give different results (mitigated by `n_init`).
- **Only finds linear boundaries** — cannot discover complex cluster shapes.

</details>

---

## Advanced Level

**Q7. How would you handle K-Means when clusters are not spherical?**

<details>
<summary>💡 Show Answer</summary>

K-Means assumes clusters are convex and roughly spherical because it uses Euclidean distance to a single centroid. For non-spherical shapes, use alternative algorithms:
- **DBSCAN** (Density-Based Spatial Clustering) — finds clusters of arbitrary shape based on density, handles noise/outliers natively
- **Gaussian Mixture Models (GMM)** — soft clustering, allows clusters to be elliptical, uses probabilistic assignment
- **Spectral Clustering** — uses graph structure to find non-convex clusters

The right choice depends on cluster shape, data size, and whether you need hard or soft assignments.

</details>

<br>

**Q8. What is the silhouette score and how is it better than just using inertia?**

<details>
<summary>💡 Show Answer</summary>

The silhouette score measures both how tight a cluster is internally and how separated it is from other clusters. For each point, it computes:
- `a` = average distance to all other points in the same cluster (cohesion)
- `b` = average distance to all points in the nearest other cluster (separation)
- Silhouette = `(b - a) / max(a, b)`

Values range from -1 to 1. Values near 1 mean the point is well-matched to its cluster. Values near 0 mean it is on the boundary. Negative values mean it might be in the wrong cluster. Inertia is always biased toward more clusters. Silhouette score is more honest — it actually decreases if you add unnecessary clusters.

</details>

<br>

**Q9. How does K-Means relate to the Expectation-Maximization (EM) algorithm?**

<details>
<summary>💡 Show Answer</summary>

K-Means is actually a special case of the EM algorithm. In EM, you have latent (hidden) variables and you alternate between:
- **E step (Expectation)**: compute expected values of latent variables given current parameters — in K-Means, this is the assignment step (assign each point to a cluster)
- **M step (Maximization)**: update parameters to maximize likelihood given the current assignments — in K-Means, this is the centroid update step (move centroids to the mean)

K-Means uses hard (binary) assignments in the E step. Gaussian Mixture Models use soft (probabilistic) assignments, making them a more general form of EM. Understanding this connection explains why K-Means converges (each step monotonically decreases inertia) but may find local rather than global optima.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, how K-Means works, elbow method |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| **Interview_QA.md** | ← you are here |
| [Code_Example.md](./Code_Example.md) | Full working Python example with elbow method |

⬅️ **Prev:** [05 SVM](../05_SVM/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 PCA](../07_PCA_Dimensionality_Reduction/Theory.md)
