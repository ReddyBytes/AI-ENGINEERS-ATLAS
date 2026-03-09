# Self-Attention — Math Walkthrough

## How a single word computes its attention scores

Let's walk through self-attention for a 4-word sentence, focusing on one word's full computation.

**Sentence:** "I love hot coffee"

We'll use 4-dimensional embeddings (unrealistically small, but good for readable math) and 3-dimensional Q/K/V projections.

---

## Step 1: Word embeddings (after positional encoding)

| Word | Embedding (4-dim) |
|---|---|
| I | [1, 0, 0, 1] |
| love | [0, 1, 0, 1] |
| hot | [1, 1, 0, 0] |
| coffee | [0, 0, 1, 1] |

---

## Step 2: Learned weight matrices

These are learned during training. For our example:

```
W_Q (4×3) =  [[1, 0, 0],    W_K (4×3) =  [[0, 1, 0],    W_V (4×3) =  [[1, 0, 0],
               [0, 1, 0],                   [1, 0, 0],                   [0, 1, 0],
               [0, 0, 1],                   [0, 0, 1],                   [0, 0, 1],
               [1, 0, 0]]                   [0, 1, 0]]                   [1, 1, 0]]
```

---

## Step 3: Compute Q, K, V for each word

Each word's embedding is multiplied by W_Q, W_K, W_V:

**For "coffee" (embedding = [0, 0, 1, 1]):**

```
Q_coffee = [0,0,1,1] × W_Q = [0+0+0+1, 0+0+0+0, 0+0+1+0] = [1, 0, 1]
K_coffee = [0,0,1,1] × W_K = [0+0+0+0, 0+0+0+1, 0+0+1+0] = [0, 1, 1]
V_coffee = [0,0,1,1] × W_V = [0+0+0+1, 0+0+0+1, 0+0+1+0] = [1, 1, 1]
```

**For all words (summarized):**

| Word | Q | K | V |
|---|---|---|---|
| I | [2, 0, 0] | [0, 2, 0] | [2, 0, 0] |
| love | [1, 1, 0] | [1, 1, 0] | [1, 1, 0] |
| hot | [1, 1, 0] | [1, 1, 0] | [1, 1, 0] |
| coffee | [1, 0, 1] | [0, 1, 1] | [1, 1, 1] |

---

## Step 4: Compute attention scores for "coffee"

We use Q_coffee = [1, 0, 1] and dot it with every Key:

```
score(coffee, I)      = [1,0,1] · [0,2,0] = 0+0+0 = 0
score(coffee, love)   = [1,0,1] · [1,1,0] = 1+0+0 = 1
score(coffee, hot)    = [1,0,1] · [1,1,0] = 1+0+0 = 1
score(coffee, coffee) = [1,0,1] · [0,1,1] = 0+0+1 = 1
```

---

## Step 5: Scale by √d_k

d_k = 3 (key dimension), √3 ≈ 1.73

```
scaled = [0/1.73, 1/1.73, 1/1.73, 1/1.73]
       = [0.00, 0.58, 0.58, 0.58]
```

---

## Step 6: Softmax → attention weights

```
exp(0.00) = 1.00
exp(0.58) = 1.79
exp(0.58) = 1.79
exp(0.58) = 1.79

sum = 1.00 + 1.79 + 1.79 + 1.79 = 6.37

weights = [1.00/6.37, 1.79/6.37, 1.79/6.37, 1.79/6.37]
        = [0.16, 0.28, 0.28, 0.28]
```

**Attention distribution for "coffee":**

| Attending to | Weight |
|---|---|
| I | 0.16 |
| love | 0.28 |
| hot | 0.28 |
| coffee (self) | 0.28 |

"coffee" attends roughly equally to "love", "hot", and itself — makes sense, "hot coffee" and "love...coffee" are the most relevant context words.

---

## Step 7: Compute updated representation for "coffee"

```
output_coffee = 0.16 × V_I + 0.28 × V_love + 0.28 × V_hot + 0.28 × V_coffee

= 0.16 × [2, 0, 0]
+ 0.28 × [1, 1, 0]
+ 0.28 × [1, 1, 0]
+ 0.28 × [1, 1, 1]

= [0.32, 0.00, 0.00]
+ [0.28, 0.28, 0.00]
+ [0.28, 0.28, 0.00]
+ [0.28, 0.28, 0.28]

= [1.16, 0.84, 0.28]
```

This [1.16, 0.84, 0.28] is the new enriched representation of "coffee" — it now contains information from "love" and "hot" (the descriptor + the verb), blended by learned relevance.

---

## The full attention matrix for this sentence

You'd do the same calculation for all 4 words. The result is a 4×4 matrix:

|  | I | love | hot | coffee |
|---|---|---|---|---|
| **I** | ? | ? | ? | ? |
| **love** | ? | ? | ? | ? |
| **hot** | ? | ? | ? | ? |
| **coffee** | 0.16 | 0.28 | 0.28 | 0.28 |

In practice the model computes all 4 rows simultaneously using matrix operations:

```python
import numpy as np

# Stacked Q, K, V matrices (4 words × 3 dims)
Q = np.array([[2,0,0],[1,1,0],[1,1,0],[1,0,1]])
K = np.array([[0,2,0],[1,1,0],[1,1,0],[0,1,1]])
V = np.array([[2,0,0],[1,1,0],[1,1,0],[1,1,1]])

d_k = 3

# Compute all attention scores at once
scores = Q @ K.T / np.sqrt(d_k)

# Softmax per row
def softmax(x):
    e = np.exp(x - x.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

weights = softmax(scores)

# Output
output = weights @ V

print("Attention weights:\n", weights.round(3))
print("\nOutput:\n", output.round(3))
```

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Walkthrough.md** | ← you are here |

⬅️ **Prev:** [02 Attention Mechanism](../02_Attention_Mechanism/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Multi-Head Attention](../04_Multi_Head_Attention/Theory.md)
