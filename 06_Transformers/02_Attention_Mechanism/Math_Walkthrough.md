# Attention Mechanism — Math Walkthrough

## A tiny 3-word example

Let's walk through attention step by step with a simple 3-word sentence.

**Sentence:** "She loves cats"

We'll use 4-dimensional embeddings to keep the math manageable.

---

## Step 1: Start with word embeddings

After embedding + positional encoding, each word becomes a 4-dimensional vector:

| Word | Embedding vector |
|---|---|
| She | [1, 0, 1, 0] |
| loves | [0, 1, 0, 1] |
| cats | [1, 1, 0, 0] |

---

## Step 2: Compute Q, K, V using learned weight matrices

In attention, each word's embedding is projected three ways — into a Query, a Key, and a Value — using three separate weight matrices W_Q, W_K, W_V.

For simplicity, let's say we're using 3-dimensional Q, K, V vectors, and assume these learned weight matrices produce:

| Word | Query (Q) | Key (K) | Value (V) |
|---|---|---|---|
| She | [1, 0, 1] | [1, 0, 0] | [1, 2, 0] |
| loves | [0, 1, 0] | [0, 1, 1] | [0, 1, 1] |
| cats | [1, 1, 1] | [1, 0, 1] | [2, 0, 1] |

---

## Step 3: Compute attention scores for "She"

We want to find which words "She" should attend to. We use "She"'s Query and compute dot products with all Keys (including its own).

```
Q_She = [1, 0, 1]

score(She, She)   = Q_She · K_She   = [1,0,1]·[1,0,0] = 1×1 + 0×0 + 1×0 = 1
score(She, loves) = Q_She · K_loves = [1,0,1]·[0,1,1] = 1×0 + 0×1 + 1×1 = 1
score(She, cats)  = Q_She · K_cats  = [1,0,1]·[1,0,1] = 1×1 + 0×0 + 1×1 = 2
```

---

## Step 4: Scale the scores

We divide by √d_k where d_k = 3 (key dimension). √3 ≈ 1.73.

```
scaled scores = [1/1.73, 1/1.73, 2/1.73] = [0.58, 0.58, 1.15]
```

---

## Step 5: Apply softmax

Softmax converts scores to probabilities summing to 1.

```
softmax([0.58, 0.58, 1.15])

exp(0.58) ≈ 1.79
exp(0.58) ≈ 1.79
exp(1.15) ≈ 3.16

sum = 1.79 + 1.79 + 3.16 = 6.74

attention weights = [1.79/6.74, 1.79/6.74, 3.16/6.74]
                  = [0.27, 0.27, 0.47]
```

| Attending to | Weight |
|---|---|
| She (herself) | 0.27 |
| loves | 0.27 |
| **cats** | **0.47** |

"She" attends most strongly to "cats" — this makes sense if we think of the subject learning about its object relationship.

---

## Step 6: Compute the context vector

Multiply each Value by its attention weight and sum:

```
context_She = 0.27 × V_She + 0.27 × V_loves + 0.47 × V_cats

= 0.27 × [1, 2, 0]
+ 0.27 × [0, 1, 1]
+ 0.47 × [2, 0, 1]

= [0.27, 0.54, 0.00]
+ [0.00, 0.27, 0.27]
+ [0.94, 0.00, 0.47]

= [1.21, 0.81, 0.74]
```

This context vector for "She" now contains information from the whole sentence, weighted by relevance. It replaces the raw embedding of "She" and is richer.

---

## Full attention scores table

You'd do the same calculation for each word (loves, cats). The result is a 3×3 attention matrix:

|  | She | loves | cats |
|---|---|---|---|
| **She** | 0.27 | 0.27 | 0.47 |
| **loves** | ? | ? | ? |
| **cats** | ? | ? | ? |

Each row shows how that word distributes its attention across the sequence.

---

## Summary of the full formula

```
Attention(Q, K, V) = softmax( Q × K^T / √d_k ) × V

Step-by-step:
  1. scores = Q × K^T           ← dot product (similarity)
  2. scores = scores / √d_k     ← scale to prevent saturation
  3. weights = softmax(scores)  ← normalize to probabilities
  4. output = weights × V       ← weighted retrieval
```

---

## Visual intuition

```
Query: "What am I looking for?"     [1, 0, 1]
                                         ↓
Keys:  She  [1,0,0] → score 1.0 → weight 0.27
       loves[0,1,1] → score 1.0 → weight 0.27
       cats [1,0,1] → score 2.0 → weight 0.47
                                         ↓
Values weighted sum:  [1.21, 0.81, 0.74]  ← new representation of "She"
```

The new vector for "She" carries information from "cats" (high weight) and from itself and "loves" (equal lower weights). This enriched representation is what gets passed to the feed-forward layer in the transformer.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Walkthrough.md** | ← you are here |

⬅️ **Prev:** [01 Sequence Models Before Transformers](../01_Sequence_Models_Before_Transformers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Self Attention](../03_Self_Attention/Theory.md)
