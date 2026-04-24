# Unsupervised Learning — Interview Q&A

## Beginner Level

**Q1: What is unsupervised learning and how does it differ from supervised learning?**

<details>
<summary>💡 Show Answer</summary>

A: Unsupervised learning trains on data that has no labels — there are no correct answers attached. The model must discover structure, patterns, or groupings on its own. Supervised learning needs labeled data (input + correct answer). Unsupervised learning just gets inputs and finds patterns by itself. The result is not a prediction of a known target — it is the discovery of hidden structure like clusters, compressed representations, or anomalies.

</details>

**Q2: What is clustering and can you give a real-world example?**

<details>
<summary>💡 Show Answer</summary>

A: Clustering is grouping similar data points together based on their features, without being told what the groups should be. A real-world example: a retail company feeds purchase history data into a clustering algorithm without any predefined categories. The algorithm discovers that customers naturally fall into groups — frequent buyers of electronics, occasional grocery shoppers, discount hunters, etc. The company did not define those categories — the algorithm found them in the data.

</details>

**Q3: What is K-Means clustering and how does it work?**

<details>
<summary>💡 Show Answer</summary>

A: K-Means is the most common clustering algorithm. You specify K (the number of clusters you want). The algorithm: (1) places K random centroids (cluster centers), (2) assigns each data point to the nearest centroid, (3) moves each centroid to the average position of all points assigned to it, (4) repeats steps 2-3 until the centroids stop moving. The result is K groups where points within each group are as close to each other as possible.

</details>

---

## Intermediate Level

**Q4: How do you choose the right value of K in K-Means?**

<details>
<summary>💡 Show Answer</summary>

A: The most common method is the elbow method. You run K-Means for K = 1, 2, 3... up to some maximum, recording the inertia (total within-cluster distance) each time. As K increases, inertia always decreases. You plot inertia vs K and look for an "elbow" — a point where adding more clusters stops meaningfully reducing inertia. That elbow is a good choice for K. Other approaches include the silhouette score (measures how well-separated clusters are) and domain knowledge (if you know there are 3 customer types, K=3 makes sense).

</details>

**Q5: What is dimensionality reduction and why is it useful?**

<details>
<summary>💡 Show Answer</summary>

A: Dimensionality reduction compresses data with many features into fewer features while preserving the most important patterns. It is useful for three reasons: visualization (you can plot 2D/3D compressed data to see structure), speed (fewer features = faster training), and noise reduction (removing irrelevant features can improve model performance). PCA is the classic method — it finds new axes (principal components) that capture the most variance in the data and projects all data onto those axes.

</details>

**Q6: What is the difference between K-Means and hierarchical clustering?**

<details>
<summary>💡 Show Answer</summary>

A: K-Means requires you to specify K upfront and assigns each point to exactly one cluster. It is fast and scales to large datasets. Hierarchical clustering builds a tree of clusters (a dendrogram) by repeatedly merging the two closest groups (agglomerative) or splitting the largest group (divisive). You do not need to specify K in advance — you can cut the tree at any level to get any number of clusters. Hierarchical clustering is more flexible but much slower on large datasets. K-Means is standard for large data; hierarchical works better for small datasets where you want to explore structure.

</details>

---

## Advanced Level

**Q7: How is unsupervised learning used in modern large language models?**

<details>
<summary>💡 Show Answer</summary>

A: Modern LLMs use self-supervised learning — a form of unsupervised learning where the training signal is derived from the data itself. In masked language modeling (BERT), random words are hidden and the model must predict them. In causal language modeling (GPT), the model predicts the next word given all previous words. No human labels are needed — the text itself provides billions of training signals. This is why LLMs can train on the entire internet without any manual annotation.

</details>

**Q8: What are autoencoders and how do they relate to unsupervised learning?**

<details>
<summary>💡 Show Answer</summary>

A: An autoencoder is a neural network trained to compress input into a smaller "latent" representation (the encoder) and then reconstruct the original input from that compressed form (the decoder). No labels are needed — the reconstruction error (how different the output is from the input) is the loss. The compressed latent space is an unsupervised representation of the data. Applications include anomaly detection (unusual inputs reconstruct poorly), denoising, and generating compressed feature representations for downstream supervised tasks.

</details>

**Q9: How would you use unsupervised learning to build a fraud detection system?**

<details>
<summary>💡 Show Answer</summary>

A: One approach is anomaly detection. Train an autoencoder on normal transactions — it learns to reconstruct normal transaction patterns well. When a fraudulent transaction occurs, it does not fit the learned pattern, so the reconstruction error is high. You flag transactions above a threshold reconstruction error as potential fraud. This approach requires no labeled fraud examples — only a large collection of normal transactions. In practice, you would combine this with a supervised model (trained on labeled fraud cases) once you have enough confirmed labels. The unsupervised model handles novel fraud patterns; the supervised model handles known ones.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [03 Supervised Learning](../03_Supervised_Learning/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Model Evaluation](../05_Model_Evaluation/Theory.md)
