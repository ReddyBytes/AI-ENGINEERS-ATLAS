# Hidden Markov Models — Interview Q&A

## Beginner

**Q1. What is a Hidden Markov Model and what makes the states "hidden"?**

<details>
<summary>💡 Show Answer</summary>

A Hidden Markov Model is a probabilistic model for sequences. It assumes there's an underlying sequence of states that you can't observe directly — that's what makes them "hidden". What you can observe are outputs that the hidden states generate.

Classic example: weather is the hidden state (you can't see weather directly from inside a room). What someone wears is the observable output. If they come in wearing a raincoat, you infer it's probably raining even though you didn't observe the weather directly.

In NLP, the hidden states are things like part-of-speech tags. You can see the words (observations), but the grammar tags are what the model needs to infer.

</details>

---

**Q2. What are the three components of an HMM?**

<details>
<summary>💡 Show Answer</summary>

An HMM has three core components:

1. **Transition probabilities:** How likely is the model to move from one hidden state to another? Example: P(Rainy → Sunny) = 0.4.

2. **Emission probabilities:** Given a hidden state, how likely is each observable output? Example: P("umbrella" | Rainy) = 0.7.

3. **Initial probabilities:** What's the probability of starting in each state? Example: P(start=Sunny) = 0.6.

With these three components, you can calculate the probability of any observation sequence and find the most likely sequence of hidden states.

</details>

---

**Q3. What is the Markov assumption and why is it important?**

<details>
<summary>💡 Show Answer</summary>

The Markov assumption states that the next state depends only on the current state — not on any earlier states. Mathematically: P(state_t | state_t-1, state_t-2, ..., state_1) = P(state_t | state_t-1).

This is important because it makes computation tractable. Without it, you'd need to consider all possible paths through all previous states, which grows exponentially with sequence length. The Markov assumption collapses this to just looking one step back, which allows efficient algorithms like Viterbi and the Forward algorithm.

The downside: real language often has long-range dependencies. "The keys on the table are..." — the verb "are" depends on "keys" many words back. HMMs can't capture this.

</details>

---

## Intermediate

**Q4. What are the three classic HMM problems and how are they solved?**

<details>
<summary>💡 Show Answer</summary>

1. **Evaluation problem:** Given a model and a sequence of observations, what is the probability of this sequence? Solved by the **Forward algorithm** (dynamic programming).

2. **Decoding problem:** Given a model and observations, what is the most likely sequence of hidden states? Solved by the **Viterbi algorithm** (dynamic programming).

3. **Learning problem:** Given observations and the model structure, how do you find the optimal transition and emission probabilities? Solved by **Baum-Welch** (Expectation-Maximization algorithm for HMMs).

In NLP, POS tagging typically uses Viterbi for decoding after learning parameters from labeled data with maximum likelihood estimation.

</details>

---

**Q5. How does the Viterbi algorithm work?**

<details>
<summary>💡 Show Answer</summary>

Viterbi finds the most likely hidden state sequence given observations using dynamic programming.

Intuition: at each time step, for each possible hidden state, Viterbi tracks the probability of the best path that ends in that state. It does this by combining the best probability from the previous step (via transition) with the emission probability for the current observation.

A backpointer table records which state was the best predecessor at each step. After processing the full sequence, you trace back through the pointers to recover the best path.

Efficiency: instead of calculating all T^N possible paths (exponential), Viterbi is O(N² × T) where N is number of states and T is sequence length.

</details>

---

**Q6. How is an HMM used for Part-of-Speech (POS) tagging?**

<details>
<summary>💡 Show Answer</summary>

POS tagging assigns grammar tags to each word: "The/DET quick/ADJ fox/NOUN jumped/VERB."

In the HMM formulation:
- Hidden states = POS tags (NOUN, VERB, ADJ, DET...)
- Observations = words

Training: count tag-to-tag transitions and word-given-tag emissions in a labeled corpus (like Penn Treebank). These counts become probabilities.

Inference: given a new sentence, run Viterbi to find the most probable tag sequence.

Example transition knowledge learned: DET is almost always followed by NOUN or ADJ. VERB is rarely followed by DET. These patterns help the model disambiguate words like "run" (NOUN or VERB?).

</details>

---

## Advanced

**Q7. What are the main limitations of HMMs for NLP tasks compared to modern approaches?**

<details>
<summary>💡 Show Answer</summary>

Several key limitations:

1. **Strong independence assumptions:** emission probabilities are computed only from the current hidden state. The word "bank" gets the same emission distribution regardless of whether "river" or "money" is nearby.

2. **First-order Markov limitation:** can only look one step back. Long-range dependencies ("keys...are") are invisible.

3. **Generative model:** HMMs model P(observations, states) — the joint distribution. For classification/tagging, you really want P(states | observations). CRFs model this directly.

4. **Overlapping features:** HMMs can't easily incorporate arbitrary features (prefix/suffix, capitalization, context window) without explicit probability estimates for each.

CRFs address problems 3 and 4. Transformers address all of them.

</details>

---

**Q8. Explain the Forward-Backward algorithm and when it's used.**

<details>
<summary>💡 Show Answer</summary>

The Forward-Backward algorithm is used in the **Baum-Welch** learning algorithm to train HMM parameters from unlabeled data.

- **Forward pass:** compute α(t, s) = probability of seeing observations 1..t and being in state s at time t
- **Backward pass:** compute β(t, s) = probability of seeing observations t+1..T given state s at time t

Combining these gives the posterior probability of being in each state at each time step given all observations: P(state_t = s | all observations).

This is the E-step of the EM algorithm. The M-step updates transition and emission parameters using these posterior probabilities.

Use when: you have sequence observations but no state labels (unsupervised HMM training).

</details>

---

**Q9. When would you still choose an HMM over a CRF or transformer for a sequence labeling task?**

<details>
<summary>💡 Show Answer</summary>

Situations where HMMs are preferable:

1. **Very small dataset:** HMMs with maximum likelihood estimation have strong inductive biases that help when data is scarce. Transformers need lots of data.

2. **Real-time inference with minimal resources:** Viterbi on a small HMM is extremely fast and runs on a microcontroller. BERT requires gigabytes of RAM and a GPU.

3. **Online (streaming) inference:** the Forward algorithm can process sequences incrementally as they arrive. Transformers need the full sequence.

4. **Interpretability:** HMM parameters (transition and emission matrices) are directly inspectable. You can look at the numbers and understand what the model learned.

5. **Probabilistic outputs:** HMMs naturally provide well-calibrated probabilities over state sequences — useful in domains like medical diagnosis or speech recognition where uncertainty quantification matters.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Math_Intuition.md](./Math_Intuition.md) | Math intuition behind HMMs |

⬅️ **Prev:** [05 Semantic Similarity](../05_Semantic_Similarity/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [07 Conditional Random Fields](../07_Conditional_Random_Fields/Theory.md)
