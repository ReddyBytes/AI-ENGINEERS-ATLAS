# Linear Algebra — Cheatsheet

**One-liner:** Linear algebra is the math of vectors (lists of numbers) and matrices (grids of numbers) — the language AI uses to represent and transform everything.

---

## Key Terms

| Term | Definition | AI Example |
|---|---|---|
| **Vector** | An ordered list of numbers with direction and magnitude | Word embedding [0.2, -0.7, 0.5] |
| **Matrix** | A rectangular grid of numbers (rows × columns) | Weight matrix in a neural network layer |
| **Dot product** | Multiply matching elements and sum — measures similarity | Similarity between two word vectors |
| **Matrix multiplication** | Combines two matrices — transforms data | Applying a neural network layer |
| **Transpose** | Flip a matrix — rows become columns | Used in backpropagation |
| **Identity matrix** | All 1s on diagonal, 0s elsewhere — leaves vectors unchanged | Like multiplying by 1 |
| **Inverse matrix** | Undoes a transformation | Solving systems of equations |
| **Eigenvalue/vector** | Special vectors that only scale (don't rotate) under a matrix | PCA for dimensionality reduction |
| **Norm** | The "length" of a vector | L2 norm = √(x₁² + x₂² + ...) |

---

## Core Operations

```
Vector addition:      [a,b] + [c,d] = [a+c, b+d]
Scalar multiplication: k × [a,b] = [ka, kb]
Dot product:          [a,b,c] · [d,e,f] = ad + be + cf
Matrix × vector:      Transforms the vector (new representation)
Matrix × matrix:      Combines two transformations
```

---

## Dot Product Interpretation

| Dot Product Value | Meaning |
|---|---|
| Large positive | Vectors point in similar direction (similar items) |
| Near zero | Vectors are perpendicular (unrelated) |
| Large negative | Vectors point in opposite directions (dissimilar) |

---

## When to Use / Not Use

| Use it when... | Watch out for... |
|---|---|
| Representing data as features | Confusing rows and columns in matrix multiply |
| Measuring similarity between items | Matrix multiplication is NOT commutative (A×B ≠ B×A) |
| Transforming data through network layers | Dimensionality mismatches crash matrix multiply |
| Dimensionality reduction (PCA) | Not all matrices are invertible |

---

## Golden Rules

1. Matrix multiplication requires the inner dimensions to match: (m×n) × (n×p) = (m×p).
2. Dot product = cosine similarity (when vectors are normalized). High dot product = similar.
3. Every neural network layer is: output = activation(W × input + b). That W is a matrix.
4. Word embeddings are vectors — similar words have high dot products.
5. Transpose notation: Aᵀ means rows and columns are swapped.
6. The number of parameters in a layer = rows × columns of its weight matrix.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| [📄 Vectors_and_Matrices.md](./Vectors_and_Matrices.md) | Visual reference for vectors and matrices |

⬅️ **Prev:** [02 Statistics](../02_Statistics/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Calculus and Optimization](../04_Calculus_and_Optimization/Theory.md)
