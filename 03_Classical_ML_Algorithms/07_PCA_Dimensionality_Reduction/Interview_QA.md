# PCA — Interview Q&A

## Beginner Level

**Q1. What problem does PCA solve?**

PCA solves the curse of dimensionality. When datasets have many features, models can become slow, overfit, and hard to visualise. PCA compresses the data into fewer dimensions by finding the directions that capture the most variation. You keep most of the information while throwing away redundant or low-variance dimensions.

**Q2. What are principal components?**

Principal components are new directions in feature space, computed by PCA. The first principal component (PC1) points in the direction where the data varies the most. The second (PC2) points in the direction of second-most variation, and it must be perpendicular (orthogonal) to PC1. Each subsequent component captures less and less variance. They are linear combinations of the original features — not selections of original features.

**Q3. What does explained variance ratio tell you?**

It tells you what fraction of the total information each component captures. For example, `explained_variance_ratio_ = [0.72, 0.23, 0.04, 0.01]` means PC1 captures 72% of the data's variance, PC2 captures 23%, and so on. Together PC1 and PC2 capture 95% of all information. This is how you decide how many components to keep — most people keep enough to reach 90–95% cumulative variance.

---

## Intermediate Level

**Q4. Why must you scale features before applying PCA?**

PCA finds directions of maximum variance. If one feature ranges from 0 to 10,000 (e.g. annual salary) and another ranges from 0 to 1 (e.g. a ratio), the large-scale feature will artificially dominate the variance calculation. PCA will think that feature is the most important just because of its scale, not because it actually carries more information. Scaling (using `StandardScaler`) puts all features on equal footing before PCA computes variance.

**Q5. What is the difference between PCA and feature selection?**

Feature selection picks a subset of the original features and discards the rest. The selected features are still interpretable — you can point to them and say "this is sepal length." PCA creates entirely new features (principal components) that are linear combinations of all original features. After PCA, you cannot directly say what PC1 means in terms of the original features. PCA typically retains more information than simple feature selection, but at the cost of interpretability.

**Q6. How do you choose the number of components to keep?**

The standard approach is the cumulative explained variance method:
1. Fit PCA with all components
2. Compute `np.cumsum(pca.explained_variance_ratio_)`
3. Find the smallest N where the cumulative sum reaches your threshold (commonly 95%)
4. Refit PCA with `n_components=N`

You can also use a scree plot — plot each component's explained variance and look for the "elbow" where the curve flattens. Components after the elbow add little information.

---

## Advanced Level

**Q7. How is PCA mathematically computed? Explain without heavy notation.**

PCA starts by computing the covariance matrix of the centred (mean-subtracted) feature matrix. The covariance matrix captures how every pair of features varies together. Then PCA finds the eigenvectors and eigenvalues of this covariance matrix. Each eigenvector is a principal component direction. Each eigenvalue tells you how much variance that direction captures. You sort them by eigenvalue (largest first) and keep the top N eigenvectors. In practice, this is computed via Singular Value Decomposition (SVD) of the data matrix directly, which is more numerically stable than computing the covariance matrix explicitly.

**Q8. When should you use t-SNE or UMAP instead of PCA?**

PCA is linear — it can only find linear structure. If the data has non-linear structure (like a spiral or a manifold), PCA will miss it. t-SNE and UMAP are non-linear methods:
- **t-SNE** — excellent for 2D/3D visualisation. Preserves local structure (nearby points stay nearby). Very slow on large datasets. Not suitable as preprocessing for ML — the transformation is not reusable (you cannot transform new points).
- **UMAP** — faster than t-SNE, can be used as ML preprocessing, better at preserving global structure too.
- Use PCA for preprocessing (speed up training, remove correlation). Use t-SNE/UMAP for visualisation only.

**Q9. If you apply PCA before training a classifier, can you get the original features back?**

Approximately yes, using the inverse transform. `pca.inverse_transform(X_compressed)` projects the data back into the original feature space. However, if you kept fewer than all components, the reconstruction is lossy — you lost the information in the discarded components. The reconstructed data is a denoised approximation of the original. The reconstruction error equals the variance explained by the discarded components — exactly the information you threw away. This property makes PCA useful for anomaly detection: reconstruct the data and flag points with high reconstruction error as anomalies.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, curse of dimensionality, when to use PCA |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| **Interview_QA.md** | ← you are here |
| [Math_Intuition.md](./Math_Intuition.md) | Eigenvectors, variance geometry, covariance matrix |
| [Code_Example.md](./Code_Example.md) | Full working Python example with Iris dataset |

⬅️ **Prev:** [06 K-Means Clustering](../06_K_Means_Clustering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Naive Bayes](../08_Naive_Bayes/Theory.md)
