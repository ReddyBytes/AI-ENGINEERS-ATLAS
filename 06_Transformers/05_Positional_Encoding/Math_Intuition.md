# Positional Encoding — Math Intuition

## Step 1: The problem in plain English

Attention computes scores by comparing Q and K vectors. If two identical words appear at positions 3 and 10, they produce the same Q and K vectors. The model can't tell them apart.

We need to "stamp" each position with a unique signal that gets mixed into the word embedding. Position 3's signal must be different from position 10's signal. And the signals must be smooth — position 5 should look more like position 6 than like position 500.

---

## Step 2: Why not just use a number?

Simple idea: just add the integer position to the embedding. Position 1 → add 1.0. Position 100 → add 100.0.

Problems:
- Values grow arbitrarily large — position 1000 adds 1000.0, drowning out the word meaning
- Doesn't generalize — what does 1000 mean? Is 1001 one step further or very different?

We need bounded, smooth, unique signals. Enter sine and cosine.

---

## Step 3: A single sine wave doesn't work

If you use `sin(position)`, you get values between -1 and 1. Bounded. But sine cycles every 2π ≈ 6.28 steps. Position 1 and position 7 would get very similar values. Not unique.

If you slow the wave down: `sin(position / 10000)`, it cycles every 62,832 steps — unique for all practical sequence lengths. But you only have one number, not a vector.

---

## Step 4: Use many sine waves at different frequencies

The original transformer uses a different sine/cosine pair for each dimension:

```
PE[pos, 2i]   = sin(pos / 10000^(2i / d_model))
PE[pos, 2i+1] = cos(pos / 10000^(2i / d_model))
```

- Dimensions 0,1: high frequency — changes fast between positions
- Dimensions 2,3: slower frequency
- ...
- Dimensions d-2, d-1: very slow — changes barely at all over 1000 positions

---

## Step 5: What the vectors actually look like

For d_model = 8 (so we have 4 sin/cos pairs), let's compute PE for positions 0, 1, 2:

```
Frequencies: 1/10000^(0/8)=1.0, 1/10000^(2/8)≈0.1, 1/10000^(4/8)≈0.01, 1/10000^(6/8)≈0.001

PE[0] = [sin(0×1.0), cos(0×1.0), sin(0×0.1), cos(0×0.1), sin(0×0.01), ...]
      = [0.000, 1.000, 0.000, 1.000, 0.000, 1.000, 0.000, 1.000]

PE[1] = [sin(1×1.0), cos(1×1.0), sin(1×0.1), cos(1×0.1), sin(1×0.01), ...]
      = [0.841, 0.540, 0.100, 0.995, 0.010, 1.000, 0.001, 1.000]

PE[2] = [sin(2×1.0), cos(2×1.0), sin(2×0.1), cos(2×0.1), sin(2×0.01), ...]
      = [0.909, -0.416, 0.199, 0.980, 0.020, 1.000, 0.002, 1.000]
```

| Position | dim 0 (sin, fast) | dim 1 (cos, fast) | dim 6 (sin, slow) | dim 7 (cos, slow) |
|---|---|---|---|---|
| 0 | 0.000 | 1.000 | 0.000 | 1.000 |
| 1 | 0.841 | 0.540 | 0.001 | 1.000 |
| 2 | 0.909 | -0.416 | 0.002 | 1.000 |
| 50 | -0.262 | 0.965 | 0.050 | 0.999 |
| 100 | -0.506 | -0.863 | 0.100 | 0.995 |

Early dimensions (dim 0, 1) change dramatically between adjacent positions. Late dimensions (dim 6, 7) barely change — they provide "macro" position information.

Together, the full 512-dimensional vector creates a unique fingerprint for each position.

---

## Step 6: Why relative positions can be expressed linearly

A subtle but powerful property: PE(pos + k) can be written as a linear function of PE(pos).

This means the dot product Q · K can capture "these two words are k positions apart" without the model needing to see every (i, j) combination separately. The model can learn "subject is usually 3 positions before its verb" in terms of position offsets.

This is why transformer attention can figure out syntactic relationships between positions even without explicit position arithmetic.

---

## Step 7: Visualizing the encoding matrix

Imagine a d_model × max_length matrix. Each column is the PE vector for one position. Each row is one dimension.

The first few rows show fast oscillations — lots of stripes. The last few rows show very slow oscillations — nearly flat bands. The full matrix creates a unique visual pattern for every column (position).

```
Row 0 (fastest): ░▒▓█▓▒░▒▓█▓▒░▒▓█  (changes every 1-2 positions)
Row 1 (medium):  ░░▒▒▒▓▓▓▓▓▒▒▒░░   (changes every 10 positions)
Row 7 (slowest): ░░░░░░░░░░░░░░░░   (barely changes over 100 positions)
```

Each column in this matrix is the positional encoding for one position.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Intuition.md** | ← you are here |

⬅️ **Prev:** [04 Multi-Head Attention](../04_Multi_Head_Attention/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [06 Transformer Architecture](../06_Transformer_Architecture/Theory.md)
