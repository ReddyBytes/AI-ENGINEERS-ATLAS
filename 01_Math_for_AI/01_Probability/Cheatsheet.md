# Probability — Cheatsheet

**One-liner:** Probability is a number from 0 to 1 that measures how likely an event is to occur.

---

## Key Terms

| Term | Definition | Example |
|---|---|---|
| **Probability P(A)** | Likelihood of event A, from 0 (impossible) to 1 (certain) | P(heads) = 0.5 |
| **Sample space** | The set of all possible outcomes | {H, T} for a coin |
| **Event** | A subset of the sample space | Getting heads |
| **Complement P(not A)** | Probability that A does NOT happen | P(not heads) = 0.5 |
| **Joint probability P(A and B)** | Both A and B happen | P(rain AND late bus) |
| **Union P(A or B)** | At least one of A or B happens | P(rain OR late bus) |
| **Conditional P(B given A)** | Probability of B, knowing A already happened | P(late\|raining) |
| **Independence** | A happening doesn't affect B's probability | Coin flips |

---

## Core Formulas

```
Complement:    P(not A) = 1 - P(A)

AND (independent):   P(A and B) = P(A) × P(B)

OR:            P(A or B) = P(A) + P(B) - P(A and B)

Conditional:   P(B | A) = P(A and B) / P(A)
```

---

## When to Use / Not Use

| Use it when... | Don't confuse it with... |
|---|---|
| Making predictions with uncertainty | Certainty / deterministic rules |
| Combining multiple uncertain events | Averages (that's statistics) |
| Updating beliefs with new evidence | Correlation (different concept) |
| Building any AI classifier or predictor | Causation ("because" not "likely") |

---

## Golden Rules

1. Probability is always between 0 and 1. Never negative. Never above 1.
2. All probabilities in a sample space must add up to 1.
3. The complement trick: if P(A) is hard to find, calculate 1 - P(not A) instead.
4. Conditional probability is NOT the same as AND. P(B|A) ≠ P(A and B).
5. Independent events can be multiplied. Dependent events cannot.
6. In AI: every model output is a probability distribution, not a single answer.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| [📄 Mini_Exercise.md](./Mini_Exercise.md) | Practice exercises |

⬅️ **Prev:** [00 Learning Guide](../../00_Learning_Guide/Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Statistics](../02_Statistics/Theory.md)
