# Unsupervised Learning — Cheatsheet

**One-liner:** Unsupervised learning = let the model find patterns in data without being told what to look for.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Clustering** | Grouping similar data points together |
| **Dimensionality reduction** | Compressing many features into fewer while keeping the important patterns |
| **Cluster** | A group of data points the model decided are similar to each other |
| **Centroid** | The center point of a cluster (used in K-Means) |
| **K** | The number of clusters you tell the algorithm to find |
| **PCA** | Principal Component Analysis — the most common dimensionality reduction method |
| **Anomaly detection** | Finding data points that don't fit any cluster (outliers) |
| **Latent structure** | Hidden patterns in data that are not obvious from raw features |
| **Inertia** | In K-Means: the total distance of all points from their cluster centers (lower = tighter clusters) |

---

## When to Use / Not Use

| Use Unsupervised Learning When... | Avoid When... |
|---|---|
| You have no labels | You have labels and a clear prediction target |
| You want to discover natural groupings | You need to predict a specific known outcome |
| You want to reduce noise before supervised ML | Your data is already low-dimensional |
| Exploratory data analysis | Accuracy on a specific task is the priority |
| Examples: customer segmentation, topic modeling, anomaly detection | Examples: spam detection, price prediction |

---

## Golden Rules

1. **No labels required.** The model discovers structure on its own.
2. **You must choose K in K-Means.** Use the elbow method to find a good number.
3. **Results are descriptive, not predictive.** Clusters tell you what groups exist — not what to do about them.
4. **Scale your features first.** K-Means is distance-based — big-number features dominate without normalization.
5. **Unsupervised + supervised = a powerful combo.** Use clustering to create labels, then train a supervised model.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Supervised Learning](../03_Supervised_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Model Evaluation](../05_Model_Evaluation/Theory.md)
