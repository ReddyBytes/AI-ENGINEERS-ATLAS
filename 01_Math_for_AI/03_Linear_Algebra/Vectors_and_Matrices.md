# Vectors and Matrices — Visual Reference

No proofs. No derivations. Just visual, concrete representations to build intuition.

---

## A Vector Is a List

A vector is simply an ordered list of numbers. Each number is one dimension (one feature).

```
2D vector (location):
  v = [3, 5]
       ^  ^
       |  north (y)
       east (x)

Visually:
  y
  |
5 |     * (3, 5)
  |    /
  |   /
  |  /
  | /
  +------------ x
  0    3


4D vector (a simple user profile):
  u = [4.2,  0.8,  7.1,  2.0]
       ^     ^     ^     ^
       age   price action comedy
       pref  sens  love  love
```

---

## A Matrix Is a Grid

A matrix is a table of numbers with rows and columns.

```
3x3 matrix:

     Col1  Col2  Col3
Row1 |  1    2    3  |
Row2 |  4    5    6  |
Row3 |  7    8    9  |

Shape: (3 rows) × (3 columns) → "3 by 3"


2x4 matrix (2 data examples, 4 features each):

          age  height  score  days_active
Person1 | 25    172     88       14      |
Person2 | 31    165     72       30      |
```

---

## Matrix × Vector = Transformation

This is the most important operation. A matrix transforms a vector into a new vector.

```
Matrix W (2×2):        Input vector x:
| 2  0 |               | 3 |
| 0  3 |               | 1 |

Calculation (row by row):
  New x = (2×3) + (0×1) = 6
  New y = (0×3) + (3×1) = 3

Output vector: | 6 |
               | 3 |

The point moved from (3,1) to (6,3).
The x-axis was stretched by 2, the y-axis by 3.
```

Think of the matrix as a set of "instructions" for how to reshape space.

---

## Neural Network Layer = Matrix × Vector

Here's a real neural network layer, visualized:

```
Input layer (3 features):          Hidden layer (2 neurons):
  x = [x1, x2, x3]                   h = [h1, h2]

Weight matrix W (2×3):
  W = | w11  w12  w13 |     h1 = (w11 * x1) + (w12 * x2) + (w13 * x3)
      | w21  w22  w23 |     h2 = (w21 * x1) + (w22 * x2) + (w23 * x3)

Written as: h = W × x
```

Training the network = learning the values w11, w12, w13, w21, w22, w23.

---

## How a Word Embedding Is a Vector

Words don't have natural numerical values. So AI converts them.

```
Word: "king"
Embedding (simplified to 5 dimensions):

  royalty  gender  power  age   formal
  [ 0.95,  -0.2,   0.88,  0.3,   0.7 ]

Word: "queen"
  royalty  gender  power  age   formal
  [ 0.93,   0.2,   0.85,  0.3,   0.7 ]

Word: "dog"
  royalty  gender  power  age   formal
  [ 0.01,   0.0,   0.1,  -0.2,   0.1 ]
```

"king" and "queen" have very similar vectors — most dimensions are almost identical.
"dog" has a completely different pattern.

A dot product between "king" and "queen" would be very high.
A dot product between "king" and "dog" would be low.

This is how AI measures whether two words are semantically related.

---

## Common Matrix Shapes in AI

```
Dataset matrix:      (n_samples × n_features)
                     e.g., 1000 examples, 50 features → shape (1000, 50)

Weight matrix:       (n_outputs × n_inputs)
                     e.g., 512 neurons taking 768-dim input → shape (512, 768)

Attention matrix:    (sequence_length × sequence_length)
                     e.g., 128 tokens → shape (128, 128)
                     Every token attends to every other token

Batch matrix:        (batch_size × sequence_length × embedding_dim)
                     e.g., (32 × 128 × 768) — a common transformer shape
```

---

## Visual Summary

```
VECTOR:                MATRIX:                TRANSFORMATION:
[ a ]                 | a  b  c |             | 2  0 |   | 3 |   | 6 |
[ b ]                 | d  e  f |         ×   |     | × |   | = |   |
[ c ]                 | g  h  i |             | 0  3 |   | 1 |   | 3 |

A list of numbers.    A grid of numbers.     Matrix changes vector.
Represents a point    Represents weights,    This is what every
or feature set.       a transformation,      neural network layer
                      or a dataset.          does to your data.
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| 📄 **Vectors_and_Matrices.md** | ← you are here |

⬅️ **Prev:** [02 Statistics](../02_Statistics/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Calculus and Optimization](../04_Calculus_and_Optimization/Theory.md)
