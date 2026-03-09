# PCA — Cheatsheet

**One-liner:** PCA finds the directions of maximum variance in high-dimensional data and projects the data onto the top N directions, creating a compact lower-dimensional representation.

---

## Key Terms

| Term | What It Means |
|---|---|
| Dimensionality | The number of features in a dataset — each feature is one dimension |
| Curse of Dimensionality | As dimensions grow, data becomes sparse and models degrade |
| Principal Component | A new direction in feature space that captures the most remaining variance |
| PC1, PC2, ... | Components ordered by variance explained — PC1 is always most important |
| Explained Variance Ratio | Fraction of total variance each component captures (sums to 1.0 across all components) |
| Projection | Mapping data onto the principal component axes |
| Eigenvector | The mathematical direction of a principal component |
| Eigenvalue | The amount of variance explained by its corresponding eigenvector — larger = more important |
| Covariance Matrix | Describes how features vary together — PCA is computed from this |
| n_components | How many principal components to keep — controls the output dimensionality |

---

## When to Use vs When Not to Use

| Use PCA When | Avoid PCA When |
|---|---|
| Features are highly correlated | Features are already independent or uncorrelated |
| Dataset has many features (100+) | You have very few features |
| You want 2D/3D visualisation | You need feature interpretability |
| Training is slow due to high dimensionality | You are using tree-based models (they handle correlated features well) |
| Pre-processing before KNN or K-Means | You specifically need to select original features (use SelectKBest instead) |

---

## Key sklearn Parameters

| Parameter | Default | What It Controls |
|---|---|---|
| `n_components` | None (keeps all) | Number of components to keep |
| `svd_solver` | `'auto'` | Algorithm for decomposition |
| `whiten` | False | Normalize variance of components — useful before some classifiers |
| `random_state` | None | Seed for reproducibility (when using randomized solver) |

---

## Useful Attributes After Fitting

| Attribute | What It Contains |
|---|---|
| `pca.explained_variance_ratio_` | Array of variance fraction per component |
| `pca.components_` | The actual principal component directions (eigenvectors) |
| `pca.n_components_` | Number of components selected |
| `pca.explained_variance_` | Raw variance (not fraction) per component |
| `np.cumsum(pca.explained_variance_ratio_)` | Cumulative variance — useful for choosing n_components |

---

## Golden Rules

1. **Always scale features before PCA.** PCA is variance-based. Features on larger scales will dominate. Use `StandardScaler` first.
2. **PCA creates new features — not a subset of old ones.** The new features are linear combinations with no direct meaning.
3. **Use cumulative explained variance to choose n_components.** A common threshold is 95% — keep enough components to explain 95% of total variance.
4. **Fit PCA on training data only, then transform both train and test.** Never fit on test data — this would leak information.
5. **PCA does not use labels.** It is unsupervised — it compresses based on structure in X, not Y.
6. **PCA is linear.** For non-linear dimensionality reduction, consider t-SNE (visualisation) or UMAP (general use).
7. **For very large datasets**, use `IncrementalPCA` or `TruncatedSVD` (which works on sparse matrices).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, curse of dimensionality, when to use PCA |
| **Cheatsheet.md** | ← you are here |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| [Math_Intuition.md](./Math_Intuition.md) | Eigenvectors, variance geometry, covariance matrix |
| [Code_Example.md](./Code_Example.md) | Full working Python example with Iris dataset |

⬅️ **Prev:** [06 K-Means Clustering](../06_K_Means_Clustering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Naive Bayes](../08_Naive_Bayes/Theory.md)
