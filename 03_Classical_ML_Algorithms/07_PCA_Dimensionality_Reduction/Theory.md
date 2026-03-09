# PCA — Principal Component Analysis

Imagine you sculpted something in 3D — a detailed face. You want to show it to someone far away, but you cannot ship the whole sculpture. So you take two photographs from the best angles. One from the front — captures the shape of the nose, eyes, cheeks. One from the side — captures the depth of the forehead and chin. Two flat photos. You have gone from 3D to 2D, but you have kept the most important structure. Someone looking at both photos understands the face without ever seeing the sculpture.

👉 This is why we need **PCA** — to compress high-dimensional data into fewer dimensions while keeping as much of the important structure (variance) as possible.

---

## What Is Dimensionality?

Every feature in your dataset is a dimension. A dataset with 4 features lives in 4-dimensional space. A dataset with 500 features lives in 500-dimensional space.

Why does high dimensionality cause problems?

---

## The Curse of Dimensionality

As dimensions increase, data becomes increasingly sparse. Here is the intuition:

Imagine you have 100 data points in a 1D line of length 1. Points are fairly close together. Now stretch that into a 2D square — same 100 points, but now spread across an area. Stretch to 3D — even more sparse. By the time you reach 100 dimensions, your 100 data points are incredibly spread out. Every point is far from every other point.

This creates real problems:
- Distance-based algorithms (K-Means, KNN) stop working well
- Models overfit because they need exponentially more data as dimensions grow
- Training is slow
- Visualisation becomes impossible

---

## PCA: Finding the Best Angles

PCA solves the dimensionality problem by finding the "best camera angles" — directions that capture the most variation in your data.

These best directions are called **principal components**.

```mermaid
flowchart LR
    A[High-Dimensional Data] --> B[Compute Variance in Each Direction]
    B --> C[Find Principal Components\nDirections of Max Variance]
    C --> D[Select Top N Components]
    D --> E[Project Data onto Those Directions]
    E --> F[Lower-Dimensional Representation]
```

Principal Component 1 (PC1) is the direction where the data varies the most — the most information.

Principal Component 2 (PC2) is the direction of second-most variation, and it must be perpendicular to PC1.

PC3 is perpendicular to both PC1 and PC2, and so on.

---

## Variance Explained

Not all principal components are equally useful. The first few usually capture most of the information. PCA tells you exactly how much of the total variance each component explains.

For example, on the famous Iris dataset (4 features: sepal length, sepal width, petal length, petal width):
- PC1 might explain 72% of the variance
- PC2 might explain 23% of the variance
- Together: 95% of all information in just 2 dimensions

You can visualise the Iris dataset in 2D and still understand most of its structure.

This is measured by the **explained variance ratio** — a number between 0 and 1 for each component.

---

## What Does PCA Actually Do to the Data?

PCA does not select existing features. It creates **new features** (the principal components) that are combinations of the original features.

Think of it like this: instead of measuring height and arm-length separately, PCA might find that "general body size" (a combination of both) captures most of the variation. The new feature "body size" is not a column in your original dataset — PCA computed it.

This means after PCA:
- The new features have no direct interpretable names
- But they capture the most important structure
- And there are fewer of them

---

## When to Use PCA

| Use PCA When | Avoid PCA When |
|---|---|
| Too many features, model is slow | You need interpretable features |
| Features are highly correlated | You have very few features already |
| You want to visualise high-dimensional data | Your features are already independent |
| Preprocessing before KNN or K-Means | You are using tree-based models (they handle high-dim well) |

---

## Important: PCA Is Unsupervised

PCA does not know about your labels. It only looks at the structure of X (the features), not y (the target). This means it may compress features that are important for prediction along with features that are not. It is a general-purpose compression tool, not a feature selection tool.

---

✅ **What you just learned:** PCA reduces the number of features by finding the directions of maximum variance (principal components) and projecting data onto the top few, preserving most of the information.

🔨 **Build this now:** Load the Iris dataset with `sklearn.datasets.load_iris()`. Create a `PCA(n_components=2)` object. Fit and transform the 4-feature data to 2 components. Print `pca.explained_variance_ratio_` to see how much information is kept.

➡️ **Next step:** Naive Bayes → `03_Classical_ML_Algorithms/08_Naive_Bayes/Theory.md`

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| **Theory.md** | ← you are here |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| [Math_Intuition.md](./Math_Intuition.md) | Eigenvectors, variance geometry, covariance matrix |
| [Code_Example.md](./Code_Example.md) | Full working Python example with Iris dataset |

⬅️ **Prev:** [06 K-Means Clustering](../06_K_Means_Clustering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Naive Bayes](../08_Naive_Bayes/Theory.md)
