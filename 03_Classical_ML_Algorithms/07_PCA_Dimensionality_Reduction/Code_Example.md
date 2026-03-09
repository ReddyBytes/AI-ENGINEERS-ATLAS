# PCA — Code Example

## What This Code Does

We will:
1. Load the Iris dataset (4 features)
2. Reduce it from 4D to 2D using PCA
3. Check how much variance is preserved
4. Describe what the scatter plot would show
5. Show how to use PCA as a preprocessing step in a pipeline

```python
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ─────────────────────────────────────────────
# 1. LOAD THE IRIS DATASET
# ─────────────────────────────────────────────

iris = load_iris()
X = iris.data          # Shape: (150, 4) — 150 flowers, 4 measurements
y = iris.target        # 3 classes: 0=setosa, 1=versicolor, 2=virginica
feature_names = iris.feature_names
class_names = iris.target_names

print(f"Original dataset shape: {X.shape}")
print(f"Features: {feature_names}")
print(f"Classes: {class_names}")

# ─────────────────────────────────────────────
# 2. SCALE THE FEATURES FIRST (ALWAYS required before PCA)
# ─────────────────────────────────────────────

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# All features now have mean=0, std=1
# Without this, features like petal_length (range 1-7) would dominate
# over sepal_width (range 2-4.5)

print(f"\nMean of scaled features: {X_scaled.mean(axis=0).round(2)}")  # Should be ~[0,0,0,0]
print(f"Std of scaled features:  {X_scaled.std(axis=0).round(2)}")     # Should be ~[1,1,1,1]

# ─────────────────────────────────────────────
# 3. FIT PCA — FIRST WITH ALL COMPONENTS TO SEE VARIANCE
# ─────────────────────────────────────────────

# Fit with all 4 components to understand variance structure
pca_full = PCA(n_components=4)
pca_full.fit(X_scaled)

print("\n=== Variance Explained by Each Component ===")
for i, ratio in enumerate(pca_full.explained_variance_ratio_):
    cumulative = np.cumsum(pca_full.explained_variance_ratio_)[i]
    print(f"  PC{i+1}: {ratio:.4f} ({ratio*100:.1f}%) | Cumulative: {cumulative*100:.1f}%")

# Expected output:
# PC1: 0.7296 (72.96%)  | Cumulative: 73.0%
# PC2: 0.2285 (22.85%)  | Cumulative: 95.8%
# PC3: 0.0367 ( 3.67%)  | Cumulative: 99.5%
# PC4: 0.0052 ( 0.52%)  | Cumulative: 100.0%
#
# Insight: PC1 and PC2 alone capture 95.8% of all information!
# We can safely drop PC3 and PC4 with minimal loss.

# ─────────────────────────────────────────────
# 4. APPLY PCA — REDUCE 4D TO 2D
# ─────────────────────────────────────────────

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

print(f"\nOriginal shape: {X_scaled.shape}")   # (150, 4)
print(f"After PCA shape: {X_pca.shape}")       # (150, 2)
print(f"Variance retained: {pca.explained_variance_ratio_.sum()*100:.1f}%")  # ~95.8%

# The two new features are linear combinations of the original 4
# Let's see the component loadings — how each original feature contributes
print("\n=== Component Loadings (how much each feature contributes) ===")
print(f"{'Feature':<25} {'PC1':>8} {'PC2':>8}")
print("-" * 45)
for name, pc1, pc2 in zip(feature_names, pca.components_[0], pca.components_[1]):
    print(f"  {name:<23} {pc1:>8.3f} {pc2:>8.3f}")

# Interpretation:
# PC1 is dominated by petal measurements (most variation between species)
# PC2 captures the sepal dimensions that are orthogonal to petal variation

# ─────────────────────────────────────────────
# 5. VISUALISE — SCATTER PLOT DESCRIPTION AND CODE
# ─────────────────────────────────────────────

colours = ['#e74c3c', '#2ecc71', '#3498db']  # Red, green, blue

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Original 4D data, showing just first 2 original features
for i, (colour, label) in enumerate(zip(colours, class_names)):
    mask = y == i
    axes[0].scatter(X_scaled[mask, 0], X_scaled[mask, 1],
                    c=colour, label=label, alpha=0.7, s=50)
axes[0].set_xlabel('Sepal Length (scaled)')
axes[0].set_ylabel('Sepal Width (scaled)')
axes[0].set_title('Original Features (2 of 4 shown)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Right: PCA-reduced 2D data (captures 95.8% of all 4 features' information)
for i, (colour, label) in enumerate(zip(colours, class_names)):
    mask = y == i
    axes[1].scatter(X_pca[mask, 0], X_pca[mask, 1],
                    c=colour, label=label, alpha=0.7, s=50)
axes[1].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)')
axes[1].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)')
axes[1].set_title('After PCA: 4D → 2D (95.8% variance kept)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('pca_iris.png', dpi=100, bbox_inches='tight')
print("\nPlot saved as 'pca_iris.png'")

# ─────────────────────────────────────────────
# WHAT THE SCATTER PLOT WOULD SHOW
# ─────────────────────────────────────────────

# Left plot (original features — sepal length vs sepal width):
# - The three species would be partially mixed together
# - Setosa would be slightly separate but overlapping with the others
# - Versicolor and Virginica would be hard to distinguish
#
# Right plot (PCA — PC1 vs PC2):
# - Setosa (red) would be clearly separated in the far left/bottom region
# - Versicolor (green) and Virginica (blue) would separate along the PC1 axis
# - Much cleaner separation visible than in the original feature plot
# - This is because PC1 captures the petal measurements which strongly
#   distinguish species, better than sepal alone

# ─────────────────────────────────────────────
# 6. USE PCA IN A PIPELINE — THE RIGHT WAY
# ─────────────────────────────────────────────

# IMPORTANT: PCA must be fit ONLY on training data, then applied to test data
# Using a Pipeline ensures this happens correctly automatically

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Pipeline: Scale → PCA → Classifier
# This ensures no data leakage — fit only on training data
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=2)),
    ('classifier', LogisticRegression(random_state=42, max_iter=200))
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)

accuracy_with_pca = accuracy_score(y_test, y_pred)
print(f"\n=== Pipeline Results ===")
print(f"Accuracy with PCA (4D → 2D): {accuracy_with_pca:.3f}")

# Compare: logistic regression on all 4 features (no PCA)
from sklearn.pipeline import Pipeline as P2
pipeline_no_pca = P2([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression(random_state=42, max_iter=200))
])
pipeline_no_pca.fit(X_train, y_train)
accuracy_no_pca = accuracy_score(y_test, pipeline_no_pca.predict(X_test))
print(f"Accuracy without PCA (all 4D): {accuracy_no_pca:.3f}")
print(f"\nConclusion: PCA kept {pca.explained_variance_ratio_.sum()*100:.1f}% of variance")
print(f"and lost only {(accuracy_no_pca - accuracy_with_pca)*100:.1f}% accuracy")
print(f"while halving the number of features (4 → 2)")

# ─────────────────────────────────────────────
# 7. INVERSE TRANSFORM — RECONSTRUCT ORIGINAL DATA
# ─────────────────────────────────────────────

# You can approximately recover the original data from the PCA representation
# This will not be perfect — the information in PC3 and PC4 is lost
X_reconstructed = pca.inverse_transform(X_pca)
X_reconstructed = scaler.inverse_transform(X_reconstructed)

reconstruction_error = np.mean((X - X_reconstructed) ** 2)
print(f"\nMean squared reconstruction error: {reconstruction_error:.4f}")
print("(Non-zero because we discarded PC3 and PC4)")
```

---

## Expected Output

```
Original dataset shape: (150, 4)
Features: ['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']
Classes: ['setosa' 'versicolor' 'virginica']

Mean of scaled features: [ 0.  0.  0. -0.]
Std of scaled features:  [1. 1. 1. 1.]

=== Variance Explained by Each Component ===
  PC1: 0.7296 (73.0%) | Cumulative: 73.0%
  PC2: 0.2285 (22.9%) | Cumulative: 95.8%
  PC3: 0.0367 ( 3.7%) | Cumulative: 99.5%
  PC4: 0.0052 ( 0.5%) | Cumulative: 100.0%

Original shape: (150, 4)
After PCA shape: (150, 2)
Variance retained: 95.8%

=== Component Loadings ===
Feature                      PC1      PC2
---------------------------------------------
  sepal length (cm)         0.521   -0.377
  sepal width (cm)         -0.269   -0.923
  petal length (cm)         0.580   -0.024
  petal width (cm)          0.565   -0.067

=== Pipeline Results ===
Accuracy with PCA (4D → 2D): 0.956
Accuracy without PCA (all 4D): 0.978
Conclusion: PCA kept 95.8% of variance and lost only 2.2% accuracy
while halving the number of features (4 → 2)

Mean squared reconstruction error: 0.0241
```

---

## Key Takeaways from the Code

- **Scaling is mandatory** before PCA — never skip it.
- **95.8% of variance** in 4 features captured by just 2 principal components in Iris.
- **The scatter plot shows** much cleaner class separation in PCA space vs original feature space.
- **Use a Pipeline** to ensure PCA is fit only on training data — prevents data leakage.
- **Inverse transform** lets you reconstruct original features from compressed representation, at the cost of the discarded variance.
- **Small accuracy loss** (2.2%) is acceptable for halving the feature count — in real 500-feature datasets, this trade-off is much more dramatic.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, curse of dimensionality, when to use PCA |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| [Math_Intuition.md](./Math_Intuition.md) | Eigenvectors, variance geometry, covariance matrix |
| **Code_Example.md** | ← you are here |

⬅️ **Prev:** [06 K-Means Clustering](../06_K_Means_Clustering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Naive Bayes](../08_Naive_Bayes/Theory.md)
