# Hidden Markov Models (HMMs)

Imagine you are building a **speech recognition system**. You have audio signals that correspond to spoken words, but you cannot directly observe the words—they are **hidden**. Instead, you observe acoustic signals (features like pitch, frequency, or amplitude) and need to infer the most likely sequence of words. This is where **Hidden Markov Models (HMMs)** come in—they are used to model **sequences where the underlying states are hidden but generate observable data**.

# What is a Hidden Markov Model?

A Hidden Markov Model (HMM) is a **probabilistic model for sequential data** where the system is assumed to be a **Markov process with hidden states**. Each hidden state generates an observable output according to a probability distribution.

### Components of an HMM:
1. **States (hidden):** Represent the unobserved variables we want to infer.  
   - Example: Part-of-speech tags, phonemes in speech, sentiment labels.
2. **Observations:** The visible data influenced by hidden states.  
   - Example: Words in a sentence, audio signal features.
3. **Transition Probabilities (A):** Probability of moving from one hidden state to another.  
   - Example: Probability that a noun is followed by a verb.
4. **Emission Probabilities (B):** Probability of observing a particular observation given a hidden state.  
   - Example: Probability that the word “dog” is emitted given the state NOUN.
5. **Initial State Probabilities (π):** Probability distribution over starting states.

 

## How HMMs Work

1. **Training (Learning):** Learn transition and emission probabilities from labeled sequences or using unsupervised methods (like the Baum-Welch algorithm).  
2. **Decoding:** Given a sequence of observations, find the **most likely sequence of hidden states** using algorithms like **Viterbi**.  
3. **Evaluation:** Calculate likelihood of sequences using the **Forward-Backward algorithm**.

### Example:

Sentence: “John runs fast”

- Hidden states (POS tags): [NN, VB, RB] → [Noun, Verb, Adverb]  
- Observations: [“John”, “runs”, “fast”]  
- HMM predicts the **sequence of POS tags** based on learned transition and emission probabilities.

 

### Types of HMMs

1. **Discrete HMM:** Observations are from a discrete set (e.g., words, POS tags).  
2. **Continuous HMM:** Observations are continuous, modeled by probability density functions (e.g., audio features in speech recognition).  
3. **Ergodic / Fully Connected HMM:** Any state can transition to any other state.  
4. **Left-Right HMM:** States progress in a forward direction only, commonly used in speech and gesture recognition.

 

## Why do we need Hidden Markov Models?

- Many NLP and sequential tasks involve **hidden states that generate observable data**.  
- HMMs model **temporal dependencies and sequential patterns**, which simpler models cannot capture.  
- Without HMMs:
  - Tasks like POS tagging, speech recognition, and gene prediction would lack **sequence-aware probabilistic modeling**.
  - Models may incorrectly predict states by ignoring context or transitions.

*Example:* In POS tagging, predicting tags independently may assign “dog” → Verb and “runs” → Noun. HMM uses transition probabilities to correct it to “dog” → Noun and “runs” → Verb.

 

## Interview Q&A

**Q1. What is a Hidden Markov Model (HMM)?**  
A: HMM is a probabilistic sequence model where the **true states are hidden** and generate observable data. It captures **temporal dependencies** in sequences.

**Q2. What are the main components of an HMM?**  
A: Hidden states, observations, transition probabilities (A), emission probabilities (B), and initial state probabilities (π).

**Q3. How is an HMM different from CRF?**  
A: HMM is a **generative model**, modeling joint probability P(X, Y). CRF is a **discriminative model**, modeling P(Y|X). HMMs assume independence of observations given the state; CRFs allow overlapping and rich features.

**Q4. What algorithms are used in HMMs?**  
A:  
- **Viterbi Algorithm:** Decoding most probable state sequence.  
- **Forward-Backward Algorithm:** Computing likelihoods and training.  
- **Baum-Welch Algorithm:** Parameter estimation from unlabeled data.

**Q5. Give NLP applications of HMMs.**  
A: POS tagging, named entity recognition, speech recognition, text segmentation, bioinformatics sequence analysis.

 

## Key Takeaways

- HMMs are **probabilistic models for sequential data with hidden states**.  
- They use **transition and emission probabilities** to model sequences.  
- Useful in NLP, speech, bioinformatics, and other sequential tasks.  
- HMMs capture **context and temporal dependencies**, improving prediction over independent models.  
- Variants include **discrete, continuous, left-right, and fully connected HMMs**.
