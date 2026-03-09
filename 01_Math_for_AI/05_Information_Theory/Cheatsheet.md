# Information Theory — Cheatsheet

**One-liner:** Information theory measures how surprising events are — and cross-entropy, built from this idea, is the most common loss function in all of AI.

---

## Key Terms

| Term | Definition | Formula |
|---|---|---|
| **Information content** | How surprising an event is — rarer = more informative | -log₂(P(x)) |
| **Entropy H(P)** | Average surprise of a distribution — measures uncertainty | -Σ P(x) log P(x) |
| **Cross-entropy H(P,Q)** | How surprised model Q is by true distribution P | -Σ P(x) log Q(x) |
| **KL Divergence** | How different Q is from P (always ≥ 0) | Σ P(x) log(P(x)/Q(x)) |
| **Bits** | Unit of information when using log base 2 | 1 bit = one yes/no question |
| **Nats** | Unit of information when using natural log (ln) | Used in most ML implementations |
| **Maximum entropy** | Uniform distribution — all outcomes equally likely | Most uncertain possible distribution |
| **Minimum entropy** | Deterministic — one outcome certain, rest zero | Zero surprise, zero information |

---

## Key Relationship

```
Cross-entropy H(P,Q) = Entropy H(P) + KL(P || Q)
                       ^fixed^          ^model error^
```

Since H(P) is fixed (it's the true data), minimizing cross-entropy = minimizing KL divergence.

---

## Intuition at a Glance

| Situation | Entropy | Meaning |
|---|---|---|
| All marbles same color | Low (≈ 0) | Totally predictable, no surprise |
| Half red, half blue | High (= 1 bit) | Maximum uncertainty for 2 options |
| Fair 6-sided die | Medium (≈ 2.58 bits) | 6 equally likely outcomes |
| True class label vs. model | Cross-entropy | How wrong the model is |

---

## When to Use / Not Use

| Use it when... | Watch out for... |
|---|---|
| Classification loss function | Log of zero is undefined — clip probabilities slightly above 0 |
| Measuring model uncertainty | KL divergence is NOT symmetric: KL(P||Q) ≠ KL(Q||P) |
| Language model training (next token prediction) | High entropy ≠ bad model — data may be genuinely uncertain |
| VAE training (KL divergence in loss) | Confusing entropy of the model vs. entropy of the data |

---

## Golden Rules

1. Cross-entropy loss is the default for classification. Almost always. Use it.
2. Lower cross-entropy = model's predicted distribution is closer to the true distribution.
3. Entropy measures uncertainty in the DATA. Cross-entropy measures model error.
4. A model predicting uniform probabilities (all classes equally likely) has maximum uncertainty.
5. KL divergence is always ≥ 0. Zero only when the two distributions are identical.
6. Language models are trained by minimizing cross-entropy over next-token prediction — trillions of times.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |

⬅️ **Prev:** [04 Calculus and Optimization](../04_Calculus_and_Optimization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 What is ML](../../02_Machine_Learning_Foundations/01_What_is_ML/Theory.md)
