# Hidden Markov Models — Cheatsheet

**One-liner:** An HMM is a probabilistic model for sequences where the states you care about are hidden — you can only observe their outputs.

---

## Key Terms

| Term | Definition |
|---|---|
| Hidden state | The unobservable underlying state (e.g., weather, POS tag) |
| Observable output | What you can actually see (e.g., outfit, word) |
| Transition probability | P(next state | current state) |
| Emission probability | P(observation | hidden state) |
| Initial probability | P(starting state) |
| Markov assumption | Next state depends only on current state, not history |
| Viterbi algorithm | Dynamic programming algorithm to find the best hidden state sequence |
| Forward algorithm | Computes probability of an observation sequence |
| Baum-Welch | Expectation-Maximization algorithm to train HMM parameters |

---

## HMM components

| Component | Notation | Description |
|---|---|---|
| States | S = {s1, s2, ...} | The hidden states |
| Observations | O = {o1, o2, ...} | The visible outputs |
| Transition matrix | A | A[i][j] = P(state j | state i) |
| Emission matrix | B | B[i][k] = P(obs k | state i) |
| Initial distribution | π | π[i] = P(start in state i) |

---

## Three classic HMM problems

| Problem | Question | Algorithm |
|---|---|---|
| Evaluation | What is P(observations | model)? | Forward algorithm |
| Decoding | What hidden states caused these observations? | Viterbi |
| Learning | What parameters best explain the data? | Baum-Welch (EM) |

---

## NLP use cases

| Task | Hidden states | Observations |
|---|---|---|
| POS tagging | Part-of-speech tags | Words |
| Named entity recognition | Entity labels (PER, ORG, LOC) | Words |
| Speech recognition | Phonemes | Audio features |
| Gene finding | Gene/non-gene | DNA bases |

---

## When to use / not use HMM

| Use HMM | Avoid HMM |
|---|---|
| Sequence labeling with clear hidden structure | Complex contextual dependencies |
| Small datasets | Need bidirectional context |
| Speed is critical | Features beyond single word needed |
| Interpretability required | High accuracy is priority |

---

## Golden Rules

1. The Markov assumption limits HMMs — they can't look back more than one step.
2. HMMs assume emissions are independent given the state — no word context effects.
3. For POS tagging, CRFs and transformers outperform HMMs but are much heavier.
4. HMMs are still useful in speech recognition and bioinformatics.
5. Viterbi is efficient because of dynamic programming — O(N × T²) not O(T^N).

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind HMMs |

⬅️ **Prev:** [05 Semantic Similarity](../05_Semantic_Similarity/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Conditional Random Fields](../07_Conditional_Random_Fields/Theory.md)
