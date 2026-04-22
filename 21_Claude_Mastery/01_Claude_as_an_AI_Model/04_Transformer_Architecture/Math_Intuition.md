# Transformer Architecture — Math Intuition

Attention is simple matrix math. This guide builds intuition step by step, from dot products to the full formula.

---

## Why dot products measure similarity

The dot product of two vectors measures how aligned they are:

```
a = [1, 0, 0]  (points in x direction)
b = [1, 0, 0]  (same direction)
a · b = 1×1 + 0×0 + 0×0 = 1   HIGH similarity

a = [1, 0, 0]
c = [0, 1, 0]  (perpendicular)
a · c = 0       ZERO similarity

a = [1, 0, 0]
d = [-1, 0, 0] (opposite direction)
a · d = -1      NEGATIVE similarity
```

Self-attention uses dot products to measure "how much should this token attend to that token?" — high dot product = strong attention.

---

## Building the attention formula piece by piece

### Step 1: Input matrices

Given a sequence of n tokens, each represented as a d-dimensional vector:

```
X = [x_1, x_2, ..., x_n]   shape: [n × d]
```

### Step 2: Project into Q, K, V spaces

```
Q = X × W_Q    shape: [n × d_k]   "What am I looking for?"
K = X × W_K    shape: [n × d_k]   "What do I offer?"
V = X × W_V    shape: [n × d_v]   "What is my content?"
```

W_Q, W_K, W_V are learned weight matrices. They project the token representations into specialized spaces for querying, labeling, and content.

### Step 3: Compute attention scores

```
Scores = Q × K^T    shape: [n × n]
```

Each element Scores[i, j] = dot product between query of token i and key of token j.
→ High value means token i wants to attend strongly to token j.

### Step 4: Scale

```
Scaled_scores = Scores / sqrt(d_k)
```

Why scale? With high-dimensional vectors, dot products grow large in magnitude. Large values make softmax output nearly one-hot — essentially greedy. Dividing by sqrt(d_k) keeps the scores in a reasonable range.

Example: d_k = 64 → divide by 8. If d_k = 1024 → divide by 32.

### Step 5: Apply causal mask (decoder-only)

```
Masked_scores[i, j] = Scaled_scores[i, j]    if j <= i
                     = -infinity              if j > i
```

After softmax, -infinity becomes 0 → future tokens get zero attention weight.

### Step 6: Softmax → attention weights

```
Weights = softmax(Masked_scores)    shape: [n × n]
```

Each row sums to 1.0. Weights[i, :] = how much token i attends to each token.

### Step 7: Aggregate values

```
Output = Weights × V    shape: [n × d_v]
```

Output[i] is a weighted average of all value vectors, weighted by how much token i attends to each position.

### Complete formula

```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) × V
```

---

## Concrete numerical example

Sequence: ["The", "cat", "sat"]
(Using d_k = 2 for simplicity)

After projections, say:

```
Q = [[0.8, 0.1],    (query for "The")
     [0.2, 0.9],    (query for "cat")
     [0.6, 0.5]]    (query for "sat")

K = [[0.7, 0.2],    (key for "The")
     [0.1, 0.8],    (key for "cat")
     [0.5, 0.6]]    (key for "sat")
```

Scores = Q × K^T:
```
Scores[0,0] = 0.8×0.7 + 0.1×0.2 = 0.56 + 0.02 = 0.58   (The→The)
Scores[0,1] = 0.8×0.1 + 0.1×0.8 = 0.08 + 0.08 = 0.16   (The→cat)
Scores[0,2] = 0.8×0.5 + 0.1×0.6 = 0.40 + 0.06 = 0.46   (The→sat)
Scores[1,0] = 0.2×0.7 + 0.9×0.2 = 0.14 + 0.18 = 0.32   (cat→The)
...
```

After scaling by sqrt(2) ≈ 1.41:
```
Scaled[0] = [0.41, 0.11, 0.33]
```

After causal mask (token 0 can only see token 0):
```
Masked[0] = [0.41, -inf, -inf]
```

After softmax:
```
Weights[0] = [1.0, 0.0, 0.0]   # "The" only attends to itself
```

Output[0] = 1.0 × V[0] + 0.0 × V[1] + 0.0 × V[2] = V[0]

Token 1 ("cat") can attend to tokens 0 and 1:
```
Masked[1] = [0.23, 0.xxx, -inf]
Weights[1] = [0.4, 0.6, 0.0]   # cat attends ~40% to The, ~60% to itself
Output[1] = 0.4 × V[0] + 0.6 × V[1]   # mix of "The" and "cat" content
```

This blended output is what gives contextual representations — "cat" now carries some information about "The" that came before it.

---

## Multi-head attention: splitting the space

With h heads and d_model = 512, d_k = d_model/h = 64:

```
Head 1: Q_1 = X × W_Q_1 ∈ [n × 64],  K_1 = X × W_K_1,  V_1 = X × W_V_1
Head 2: Q_2 = X × W_Q_2 ∈ [n × 64],  K_2 = X × W_K_2,  V_2 = X × W_V_2
...
Head 8: Q_8 = X × W_Q_8 ∈ [n × 64],  K_8 = X × W_K_8,  V_8 = X × W_V_8

Each head computes:  attention_i = Attention(Q_i, K_i, V_i)  → [n × 64]

Concatenate: [attention_1 || ... || attention_8] → [n × 512]
Project: × W_O → [n × 512]
```

Each head can learn different projection matrices W_Q, W_K, W_V — effectively learning to look for different types of relationships in different subspaces.

---

## Layer normalization — keeping activations stable

After many layers of computation, activations can drift to very large or very small values. Layer norm normalizes each token's feature vector independently:

```
For token i with feature vector h ∈ R^d:

μ = mean(h)                     # mean across d features
σ² = variance(h)                # variance across d features
h_norm = (h - μ) / sqrt(σ² + ε) # normalize to zero mean, unit variance
output = γ × h_norm + β         # learnable scale and shift
```

γ (gamma) and β (beta) are learned parameters — the model can learn to rescale and shift the normalized values to whatever range is useful.

Key property: unlike batch normalization, LayerNorm operates on a single sample (one token's features) — making it independent of batch size and sequence length.

---

## Residual connections — highway for gradients

Without residuals, information must flow through every layer:

```
Layer 3 → Layer 2 → Layer 1 → Input
```

If Layer 2 has a poor gradient (close to zero), signal from Layer 3 cannot reach Layer 1.

With residuals:

```
output = x + F(x)

During backpropagation:
∂output/∂x = 1 + ∂F(x)/∂x
```

The "1" term guarantees the gradient is at least 1 regardless of how poor ∂F(x)/∂x is. This creates a direct path for gradients all the way back to the embedding layer — enabling stable training of 96+ layer models.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | Full visual stack |
| 📄 **Math_Intuition.md** | ← you are here |

⬅️ **Prev:** [03 Tokens and Context Window](../03_Tokens_and_Context_Window/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [05 Pretraining](../05_Pretraining/Theory.md)
