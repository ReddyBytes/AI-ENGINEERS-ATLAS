# Conditional Random Fields — Interview Q&A

## Beginner

**Q1. What is a Conditional Random Field (CRF) and what is it used for?**

<details>
<summary>💡 Show Answer</summary>

A CRF is a discriminative sequence labeling model. It takes a sequence of inputs (words in a sentence) and assigns a label to each one (like a part-of-speech tag or named entity label).

What makes it "conditional" is that it directly models the probability of the label sequence given the input sequence: P(labels | words). It doesn't try to model how the words were generated — it just learns the best labeling.

Common uses: Named Entity Recognition (labeling spans as Person, Organization, Location), Part-of-Speech tagging, text chunking, and slot filling in dialogue systems.

</details>

---

**Q2. How is a CRF different from an HMM?**

<details>
<summary>💡 Show Answer</summary>

The key difference is that HMMs are generative and CRFs are discriminative.

An HMM models P(words, tags) — the joint probability of words and tags together. This forces the model to also model how words are generated, which is complex and often unnecessary.

A CRF models P(tags | words) — the conditional probability of tags given the words. It skips modeling word generation and focuses entirely on predicting the best labels.

This lets CRFs use much richer features. An HMM can only use the current word and the previous tag. A CRF can use anything: surrounding words, word shapes, capitalization, prefixes, suffixes — anything you can extract from the input.

</details>

---

**Q3. What is the BIO labeling scheme and why is it needed for NER?**

<details>
<summary>💡 Show Answer</summary>

BIO stands for Beginning, Inside, Outside.

Named entities often span multiple words ("Barack Obama" = 2 words, one person). A simple tag per word can't represent this. BIO solves it:

- B-XXX: the first word of an entity of type XXX
- I-XXX: a continuation word inside an entity of type XXX
- O: not part of any entity

Example: "Apple launched a new iPhone in Cupertino."
```
Apple     → B-ORG
launched  → O
a         → O
new       → O
iPhone    → B-PROD
in        → O
Cupertino → B-LOC
```

The BIO scheme allows the model to represent multi-word entities precisely while still doing word-level classification.

</details>

---

## Intermediate

**Q4. What kind of features does a CRF typically use for NER?**

<details>
<summary>💡 Show Answer</summary>

CRFs can use any function of the input. Common feature categories:

**Word-level features:**
- The word itself: word = "Obama"
- Lowercased word: lower = "obama"
- Whether it's capitalized: is_upper = True
- Whether it contains digits: has_digit = False

**Contextual features:**
- Previous word: word[-1] = "Barack"
- Next word: word[+1] = "visited"
- Previous 2 words window

**Morphological features:**
- Prefix: word[:3] = "Oba"
- Suffix: word[-3:] = "ama"
- Word shape: "Xxxx" (first letter uppercase, rest lowercase)

**Label history:**
- Previous label: prev_label = "B-PER"

**Lexicon features:**
- Is the word in a gazetteer (list of known persons/places)?

The CRF learns weights for each feature function — features correlated with correct labels get high weights.

</details>

---

**Q5. How does decoding work in a CRF? How is it similar to HMM decoding?**

<details>
<summary>💡 Show Answer</summary>

CRF decoding (finding the most probable label sequence) also uses the Viterbi algorithm — the same dynamic programming approach used in HMMs.

At each position in the sequence, Viterbi tracks the best partial label assignment that ends in each possible label. It combines the score of the current assignment with the feature-based potential for the current position.

The difference from HMM: instead of simple transition and emission probabilities, CRFs compute a score by summing weighted feature functions over all positions and label pairs. The Viterbi algorithm still finds the path with the highest total score in O(N² × T) time.

</details>

---

**Q6. What is a BiLSTM-CRF and why is it better than a standalone CRF?**

<details>
<summary>💡 Show Answer</summary>

BiLSTM-CRF combines two components:

1. **BiLSTM (Bidirectional LSTM):** reads the sentence in both directions and produces rich contextual representations for each word. These representations capture much more context than hand-crafted features.

2. **CRF layer:** sits on top of the BiLSTM and decodes the best label sequence from the LSTM outputs. It ensures the output labels follow valid transitions (e.g., I-PER can't follow B-ORG).

Why better than standalone CRF:
- Feature engineering is automated by the neural network — no need to manually define prefixes, suffixes, etc.
- Contextual representations from BiLSTM are richer than anything hand-crafted

Why better than BiLSTM alone:
- The CRF enforces label consistency across the sequence
- "O I-PER" would be an invalid output — a standalone LSTM might produce this, but a CRF layer prevents it

This architecture was state-of-the-art for NER before BERT arrived.

</details>

---

## Advanced

**Q7. How does training a CRF differ from training an HMM?**

<details>
<summary>💡 Show Answer</summary>

HMM training: with labeled data, just count. Count how often tag A follows tag B (transitions), count how often word W appears with tag T (emissions). Normalize to get probabilities. Very simple maximum likelihood.

CRF training: maximize the conditional log-likelihood of the training labels given the training words. This requires:
1. Computing the partition function Z (sum of scores over all possible label sequences) — done with the Forward algorithm
2. Computing gradients with respect to feature weights
3. Gradient-based optimization (L-BFGS is common for CRFs, SGD for neural CRFs)

CRF training is more expensive but directly optimizes the discriminative objective.

Regularization (L1 or L2 penalty on feature weights) is usually needed to prevent overfitting, especially with many sparse features.

</details>

---

**Q8. How does BERT+CRF work for NER and why is it better than BiLSTM-CRF?**

<details>
<summary>💡 Show Answer</summary>

BERT+CRF replaces the BiLSTM with BERT:

1. BERT takes the tokenized sentence and produces contextual embeddings for each token
2. A linear layer projects BERT embeddings to label scores (one score per label per token)
3. The CRF layer decodes the best label sequence from these scores

Advantages over BiLSTM-CRF:
- BERT provides deeply contextual representations pretrained on massive text — much richer than anything a BiLSTM trained on small labeled NER data can learn
- BERT's subword tokenization handles rare and OOV words
- Transfer learning: BERT starts with general language understanding, CRF fine-tunes for the specific labeling task

One challenge: BERT tokenizes into subwords. "Obama" might become ["O", "##bama"]. You need to align these subword tokens back to original word positions before applying the CRF.

</details>

---

**Q9. When would you choose a CRF over BERT for a production NER system?**

<details>
<summary>💡 Show Answer</summary>

Choose a CRF (possibly with lightweight neural features) when:

- **Very limited labeled data:** BERT needs thousands of labeled examples to fine-tune well. CRFs with domain-specific features can work with hundreds.
- **Strict latency requirements:** CRF inference is microseconds; BERT takes milliseconds and requires a GPU for high-throughput.
- **Edge/embedded deployment:** BERT is hundreds of megabytes. A CRF model can be kilobytes.
- **Interpretability is critical:** you can inspect CRF feature weights directly. Medical or legal applications often require explaining model decisions.
- **Domain-specific rules:** if your domain has clear patterns (e.g., medical dosage: "500mg" is always a DRUG_DOSE), encoding these as features in a CRF can be more reliable than relying on BERT to learn them.

In practice, BERT+CRF is the default for high-accuracy systems, and standalone CRF is the choice for resource-constrained or data-scarce settings.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [06 Hidden Markov Models](../06_Hidden_Markov_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Sequence Models Before Transformers](../../06_Transformers/01_Sequence_Models_Before_Transformers/Theory.md)
