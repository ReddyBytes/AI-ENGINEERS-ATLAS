# Hidden Markov Models — Math Intuition

## What does "probabilistic" actually mean here?

Before the matrices, let's anchor the intuition.

You have a sequence of days. Each day the weather is either Sunny or Rainy. You never see the weather directly — you see what your friend is wearing (T-shirt, Jacket, or Umbrella).

You need to answer: "Given the outfit sequence I observed this week, what was the weather each day?"

That's exactly what HMM math solves.

---

## The three probability tables

### Table 1: Initial probabilities (π)

What's the probability of starting in each state?

| Starting State | Probability |
|---|---|
| Sunny | 0.6 |
| Rainy | 0.4 |

Total must sum to 1.0.

---

### Table 2: Transition matrix (A)

What's the probability of moving from one state to another?

| From \ To | Sunny | Rainy |
|---|---|---|
| Sunny | 0.7 | 0.3 |
| Rainy | 0.4 | 0.6 |

Reading row 1: if it's Sunny today, there's a 70% chance it's Sunny tomorrow and 30% chance it's Rainy tomorrow.

Each row must sum to 1.0 (you have to go somewhere).

**Why the Markov assumption makes this work:** This table is complete. To know tomorrow's probabilities, you only need to know today's state. You don't need last week's weather history. That's the memoryless property.

---

### Table 3: Emission matrix (B)

Given the hidden state, what's the probability of each observation?

| Hidden State \ Observation | T-shirt | Jacket | Umbrella |
|---|---|---|---|
| Sunny | 0.6 | 0.3 | 0.1 |
| Rainy | 0.1 | 0.3 | 0.6 |

Reading row 1: if it's Sunny, there's a 60% chance your friend wears a T-shirt.

Each row sums to 1.0 (some outfit must be worn).

---

## Worked example: calculating probability of an observation

Observation sequence: [T-shirt, Umbrella]

We want: P(T-shirt on day 1, Umbrella on day 2)

There are 4 possible hidden state paths:
1. Sunny → Sunny
2. Sunny → Rainy
3. Rainy → Sunny
4. Rainy → Rainy

For path Sunny → Rainy:

```
P(start=Sunny) × P(T-shirt | Sunny) × P(Rainy | Sunny) × P(Umbrella | Rainy)
= 0.6 × 0.6 × 0.3 × 0.6
= 0.0648
```

For path Rainy → Rainy:

```
P(start=Rainy) × P(T-shirt | Rainy) × P(Rainy | Rainy) × P(Umbrella | Rainy)
= 0.4 × 0.1 × 0.6 × 0.6
= 0.0144
```

Sum all 4 paths = total probability of this observation sequence.

The Forward algorithm automates this calculation efficiently for long sequences.

---

## Why Viterbi doesn't try all paths

For a sequence of length T with N states, there are N^T possible paths.

For N=10 states and T=20 words: 10^20 = 100,000,000,000,000,000,000 paths.

Viterbi uses dynamic programming. Key insight: you don't need to remember how you got to a state — only the probability of the best way to get there.

**Viterbi table for our 2-state example, observation [T-shirt, Umbrella]:**

| Time | Sunny (best probability) | Rainy (best probability) |
|---|---|---|
| t=1 | 0.6 × 0.6 = 0.36 | 0.4 × 0.1 = 0.04 |
| t=2 | max(0.36 × 0.7, 0.04 × 0.4) × 0.1 | max(0.36 × 0.3, 0.04 × 0.6) × 0.6 |

At t=2 for Rainy:
- Via Sunny: 0.36 × 0.3 × 0.6 = 0.0648 ← winner
- Via Rainy: 0.04 × 0.6 × 0.6 = 0.0144

Best path: Sunny → Rainy. Makes sense — T-shirt suggests Sunny, Umbrella suggests Rainy.

---

## POS tagging: what the matrices look like

In a real POS tagger:

**Emission matrix excerpt** (probability of word given POS tag):

| Tag \ Word | "the" | "run" | "fast" | "dog" |
|---|---|---|---|---|
| DET | 0.35 | 0.00 | 0.00 | 0.00 |
| NOUN | 0.00 | 0.02 | 0.01 | 0.08 |
| VERB | 0.00 | 0.05 | 0.02 | 0.00 |
| ADJ | 0.00 | 0.00 | 0.04 | 0.00 |

"the" has very high probability only under DET. "run" has nonzero probability under NOUN and VERB (it can be both). This ambiguity is what Viterbi resolves by considering the full sequence.

**Transition matrix excerpt:**

| From \ To | DET | NOUN | VERB | ADJ |
|---|---|---|---|---|
| DET | 0.01 | 0.55 | 0.05 | 0.35 |
| NOUN | 0.05 | 0.10 | 0.45 | 0.05 |
| VERB | 0.15 | 0.35 | 0.05 | 0.20 |

DET is usually followed by NOUN (0.55) or ADJ (0.35). NOUN is usually followed by VERB (0.45). These learned transition probabilities reflect English grammar structure.

---

## Key insight: why this works

The magic of HMMs is combining two types of evidence:

1. **Local evidence:** "run" looks like a VERB based on emission probabilities
2. **Sequential evidence:** it's preceded by "the" which is DET, and DET rarely precedes VERB → it's probably NOUN

Viterbi combines both sources to find the globally best tag sequence, not just locally greedy choices.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Math_Intuition.md** | ← you are here |

⬅️ **Prev:** [05 Semantic Similarity](../05_Semantic_Similarity/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Conditional Random Fields](../07_Conditional_Random_Fields/Theory.md)
