# Linear Algebra — Interview Q&A

## Beginner Level

**Q1: What is a vector and how is it used in AI?**

<details>
<summary>💡 Show Answer</summary>

A vector is an ordered list of numbers, like [0.2, -0.7, 0.5]. In AI, vectors represent things — a word's meaning, a user's preferences, an image's features. Each number in the vector captures one characteristic. Similar items end up as similar vectors, and the math of linear algebra lets the model work with all of them efficiently.

</details>

**Q2: What is a matrix and what does matrix multiplication do?**

<details>
<summary>💡 Show Answer</summary>

A matrix is a rectangular grid of numbers organized in rows and columns. Matrix multiplication combines two matrices to produce a new one. In neural networks, each layer applies a matrix multiplication to the input vector — the matrix contains the learned weights, and multiplying by the input produces the layer's output. It's how data gets transformed as it flows through a network.

</details>

**Q3: What is a dot product and what does it measure?**

<details>
<summary>💡 Show Answer</summary>

A dot product multiplies corresponding elements of two vectors and sums the results. For vectors [1,2,3] and [4,5,6], the dot product is (1×4)+(2×5)+(3×6) = 32. It measures how much two vectors point in the same direction — a large positive dot product means they're similar, near zero means they're unrelated. Recommendation systems use dot products to match users to items.

</details>

---

## Intermediate Level

**Q4: Why can't you always reverse (invert) a matrix transformation?**

<details>
<summary>💡 Show Answer</summary>

A matrix is invertible only if it doesn't "squish" the space — specifically, if it doesn't reduce the dimensionality of the data. A matrix that maps many different input vectors to the same output loses information and can't be reversed. In ML, non-invertible operations appear in dimensionality reduction (like going from 1000 features to 50) — you deliberately discard information, which is a one-way operation.

</details>

**Q5: What is cosine similarity and how does it relate to the dot product?**

<details>
<summary>💡 Show Answer</summary>

Cosine similarity measures the angle between two vectors, ignoring their lengths. It's computed as the dot product divided by the product of both vectors' lengths: similarity = (A · B) / (|A| × |B|). The result ranges from -1 (opposite) to +1 (identical direction). In NLP, cosine similarity between word embeddings measures semantic similarity — "king" and "queen" have high cosine similarity because they appear in similar contexts.

</details>

**Q6: What is an eigenvector and why does it matter for PCA?**

<details>
<summary>💡 Show Answer</summary>

An eigenvector is a special vector that, when transformed by a matrix, only changes in length (scales) — it doesn't rotate. The amount it scales is its eigenvalue. PCA (Principal Component Analysis) finds the eigenvectors of the data's covariance matrix — these are the directions of maximum variance in the data. By keeping only the top eigenvectors (those with highest eigenvalues), you compress the data to its most important dimensions while losing minimal information.

</details>

---

## Advanced Level

**Q7: How does the transformer's attention mechanism use linear algebra?**

<details>
<summary>💡 Show Answer</summary>

The attention mechanism computes compatibility between every pair of tokens using dot products. Each token is projected into three vectors — Query, Key, and Value — using learned weight matrices. The attention score between two tokens is their Query-Key dot product, scaled and softmaxed. The output is a weighted sum of Value vectors. Every step is matrix multiplication, and processing the full sequence at once is why transformers are so parallelizable on GPUs.

</details>

**Q8: What is the relationship between matrix rank and information loss in neural networks?**

<details>
<summary>💡 Show Answer</summary>

The rank of a matrix is the number of linearly independent rows or columns — it measures how much "information capacity" the matrix has. A low-rank matrix compresses data into fewer dimensions. Neural network layers are often approximately low-rank, meaning they can be compressed. Techniques like LoRA (Low-Rank Adaptation) exploit this: instead of fine-tuning all weights of a large model, they add small low-rank matrices, dramatically reducing the number of trainable parameters while preserving most of the model's capability.

</details>

**Q9: What is Singular Value Decomposition (SVD) and where is it used in ML?**

<details>
<summary>💡 Show Answer</summary>

SVD decomposes any matrix A into three matrices: A = U × Σ × Vᵀ, where Σ contains the "singular values" — ranked from largest to smallest. Keeping only the top k singular values and their corresponding columns gives the best rank-k approximation of the original matrix. In ML, SVD powers collaborative filtering (Netflix-style recommendations), PCA, and noise reduction. Large language models use it for model compression, and it's behind the theory of why word embeddings work — the semantic structure of language appears in the top singular vectors of word co-occurrence matrices.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| [📄 Vectors_and_Matrices.md](./Vectors_and_Matrices.md) | Visual reference for vectors and matrices |

⬅️ **Prev:** [02 Statistics](../02_Statistics/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Calculus and Optimization](../04_Calculus_and_Optimization/Theory.md)
