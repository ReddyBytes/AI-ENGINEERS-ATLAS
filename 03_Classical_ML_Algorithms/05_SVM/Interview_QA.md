# SVM — Interview Q&A

## Beginner Level

**Q1. What is a Support Vector Machine in simple terms?**

<details>
<summary>💡 Show Answer</summary>

SVM is a classification algorithm that finds the best boundary (hyperplane) between two classes. "Best" means the boundary has the maximum distance (margin) from the nearest data points on each side. Those nearest points are the support vectors.

</details>

**Q2. What are support vectors?**

<details>
<summary>💡 Show Answer</summary>

Support vectors are the training data points that lie closest to the decision boundary. They are the only points that actually determine where the boundary goes. If you removed all other training points (keeping just the support vectors), the model would not change at all.

</details>

**Q3. What is a kernel in SVM?**

<details>
<summary>💡 Show Answer</summary>

A kernel is a function that measures similarity between two data points. SVM uses kernels to handle non-linear data. The kernel trick allows SVM to find a linear boundary in a higher-dimensional space, which corresponds to a curved boundary in the original space. Common kernels: linear, RBF, polynomial.

</details>

---

## Intermediate Level

**Q4. What is the difference between hard margin and soft margin SVM?**

<details>
<summary>💡 Show Answer</summary>

Hard margin SVM requires that all training points are correctly classified with no violations of the margin. This only works when the data is perfectly linearly separable. Soft margin SVM (controlled by the C parameter) allows some points to fall inside the margin or even be misclassified, in exchange for a wider, more generalizable boundary. Real-world data is almost always noisy, so soft margin is used in practice.

</details>

**Q5. What does the C parameter control, and how do you choose it?**

<details>
<summary>💡 Show Answer</summary>

C is the regularization parameter. It controls the trade-off between maximizing the margin and minimizing classification errors:
- High C: penalizes misclassifications heavily → smaller margin, more complex boundary, risk of overfitting
- Low C: tolerates misclassifications → larger margin, simpler boundary, better generalization

Choose C using cross-validation (e.g. `GridSearchCV`). If your model overfits, try lowering C.

</details>

**Q6. Why do you need to scale features before using SVM?**

<details>
<summary>💡 Show Answer</summary>

SVM computes distances between data points to find the margin. If one feature ranges from 0 to 1 and another from 0 to 10,000, the large-scale feature will dominate the distance calculation. The model will essentially ignore the small-scale feature. Scaling (e.g. `StandardScaler`) puts all features on equal footing, so the algorithm can make fair comparisons.

</details>

---

## Advanced Level

**Q7. Explain the kernel trick. Why does it work without explicitly computing high-dimensional coordinates?**

<details>
<summary>💡 Show Answer</summary>

The kernel trick works because SVM's optimization only ever needs to compute dot products between pairs of data points, not the actual coordinates in the high-dimensional space. A kernel function `K(x, z)` computes the dot product in the transformed high-dimensional space directly from the original coordinates `x` and `z`. For example, the RBF kernel `K(x, z) = exp(-gamma * ||x-z||^2)` implicitly maps data into an infinite-dimensional space — but we never need to compute that infinite representation explicitly. This makes it computationally feasible.

</details>

**Q8. How does SVM handle multi-class classification? What are the trade-offs?**

<details>
<summary>💡 Show Answer</summary>

SVM is inherently a binary classifier. For multi-class problems, sklearn uses two strategies:
- **One-vs-One (OvO)**: trains one classifier for every pair of classes → `n*(n-1)/2` classifiers. More accurate but slower to train with many classes.
- **One-vs-Rest (OvR)**: trains one classifier per class vs all others → `n` classifiers. Faster but can struggle with class imbalance.

sklearn `SVC` defaults to OvO. `LinearSVC` defaults to OvR. For large numbers of classes, OvR is generally preferred.

</details>

**Q9. What is the dual formulation of SVM, and why does it matter for kernels?**

<details>
<summary>💡 Show Answer</summary>

The primal SVM problem optimizes the weight vector `w` directly. The dual formulation re-expresses the problem in terms of dot products between training examples. This is important because: (1) the dual problem's complexity depends on the number of training examples rather than the number of features — useful when you have more features than examples; and (2) the dual formulation is where kernel functions can be substituted in, replacing every dot product `x_i · x_j` with `K(x_i, x_j)`. Without the dual form, the kernel trick would not be possible.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, how SVM works, when to use |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| **Interview_QA.md** | ← you are here |
| [Math_Intuition.md](./Math_Intuition.md) | Hyperplane geometry, kernel trick, C parameter |

⬅️ **Prev:** [04 Random Forests](../04_Random_Forests/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 K-Means Clustering](../06_K_Means_Clustering/Theory.md)
