# PCA — Math Intuition

No matrix algebra required. Just the ideas, explained with everyday analogies.

---

## Eigenvectors in Plain English

You have probably heard "eigenvector" and immediately glazed over. Here is the plain English version.

Imagine a rubber sheet stretched flat on a table. You grab the sheet and pull in different directions. Most directions distort the sheet — things stretch unevenly. But there are certain special directions: when you pull in those directions, the sheet just stretches uniformly without rotating or twisting. Everything along that direction scales by the same amount. Those special directions are the **eigenvectors**.

For a matrix (like a covariance matrix), eigenvectors are the directions the transformation "naturally" acts along — where the matrix just scales things without changing direction.

**Eigenvalues** are the amounts of that scaling. A large eigenvalue means the matrix stretches a lot in that direction. A small eigenvalue means it barely moves things in that direction.

In PCA:
- The covariance matrix of your data describes how features vary together
- The eigenvectors of that covariance matrix are the principal component directions
- The eigenvalues tell you how much variance each principal component captures

Large eigenvalue = that direction has a lot of variance = important direction = keep it.
Small eigenvalue = low variance direction = mostly noise = can discard.

---

## Why Does PCA Find Directions of Maximum Variance?

Here is the geometric intuition.

Imagine a cloud of data points scattered in 2D. They form an elongated ellipse — more spread out horizontally than vertically. You want to describe these points with just one number (reduce to 1D). Which direction should you project onto?

Option A: project onto the vertical axis. The points get squashed together. You lose most of the spread. A lot of information is lost.

Option B: project onto the horizontal axis (the long axis of the ellipse). The points spread out well along this axis. Most of the spread is preserved.

The horizontal axis captures the maximum variance. This is PC1.

After PC1, you look for the next direction of maximum variance — constrained to be perpendicular to PC1. This is PC2. And so on.

PCA is literally an algorithm that finds the axes of the ellipse formed by your data — from longest to shortest.

---

## The Shadow Analogy — Projecting 3D to 2D

Imagine a 3D object — a long cylindrical pencil held diagonally. It casts a shadow on the table below.

- If you shine the light straight down, the shadow is a circle (small and uninformative — you can't tell it's a pencil)
- If you shine the light from the side, the shadow is a long thin rectangle (informative — you can tell it's long and thin)

The shadow from the side captures the most information about the pencil's shape. The direction of the light that creates the most spread-out shadow is the first principal component.

PCA finds that optimal "direction to shine the light" for your data — the angle that casts the most informative shadow.

---

## What the Covariance Matrix Captures

Before PCA computes eigenvectors, it first computes the covariance matrix. This is a square matrix (features × features) where each entry tells you: "how much do feature i and feature j vary together?"

- High positive covariance: when feature i goes up, feature j tends to go up too
- High negative covariance: when feature i goes up, feature j tends to go down
- Near-zero covariance: the two features are mostly independent

Highly correlated features mean redundant information. PCA finds the compact directions that summarise this correlated structure. The principal components are guaranteed to be uncorrelated with each other — PCA removes the redundancy.

---

## Why PCA's Components Are Orthogonal

Orthogonal means perpendicular — at 90 degrees. Why must the principal components be perpendicular to each other?

Because if two directions are not perpendicular, they share some information. Direction A would overlap with direction B. When you project data onto both, you'd be counting some of the same variance twice.

Orthogonality guarantees that each principal component captures completely independent (non-overlapping) information. This is enforced mathematically — eigenvectors of a symmetric matrix (like the covariance matrix) are always orthogonal to each other.

After PCA, the projected features (principal components) have zero correlation with each other. The redundancy has been completely removed.

---

## The Kernel PCA Connection

Standard PCA is linear — it finds linear combinations of features. But what if the important structure in your data is non-linear?

Kernel PCA applies the kernel trick (same idea as in SVM) to perform PCA in a higher-dimensional space. Just like SVM uses kernels to find linear boundaries in non-linear problems, Kernel PCA uses kernels to find linear principal components in a space where the non-linear structure becomes linear.

Use `sklearn.decomposition.KernelPCA` with an RBF kernel when standard PCA fails to capture the structure of your data.

---

## Putting It All Together

```
Original data (high-dimensional)
        ↓
Subtract the mean (centre the data)
        ↓
Compute covariance matrix
        ↓
Find eigenvectors (principal component directions)
Find eigenvalues (variance each direction captures)
        ↓
Sort by eigenvalue — largest first
        ↓
Keep top N eigenvectors
        ↓
Project data: X_compressed = X_centred @ top_N_eigenvectors
        ↓
Result: N new features that capture the most variance
```

The "project" step is just matrix multiplication — computing dot products between each data point and each principal component direction. This is exactly the "shadow" step — measuring how far along each principal component axis each data point falls.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, curse of dimensionality, when to use PCA |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| **Math_Intuition.md** | ← you are here |
| [Code_Example.md](./Code_Example.md) | Full working Python example with Iris dataset |

⬅️ **Prev:** [06 K-Means Clustering](../06_K_Means_Clustering/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [08 Naive Bayes](../08_Naive_Bayes/Theory.md)
