# Conditional Random Fields — Cheatsheet

**One-liner:** CRFs are discriminative sequence labeling models that predict label sequences conditioned on the full input sequence, using arbitrary contextual features.

---

## Key Terms

| Term | Definition |
|---|---|
| CRF | Conditional Random Field — discriminative sequence labeling model |
| Discriminative model | Models P(labels | input) directly |
| Generative model | Models P(input, labels) jointly |
| Feature function | A function that extracts a feature from the input + label context |
| BIO scheme | B=Begin, I=Inside, O=Outside — standard NER labeling |
| NER | Named Entity Recognition — labeling spans as persons, orgs, locations |
| Linear-chain CRF | CRF where each label depends only on adjacent labels |
| BiLSTM-CRF | Deep learning architecture combining BiLSTM features with CRF decoding |

---

## CRF vs HMM comparison

| Feature | HMM | CRF |
|---|---|---|
| Model type | Generative | Discriminative |
| What it models | P(words, tags) | P(tags | words) |
| Feature flexibility | Limited (word + prev tag) | Arbitrary features |
| Uses whole sequence? | No (only past) | Yes |
| Better for NER/POS? | Decent | Yes |
| Interpretable? | Yes | Yes |
| Still used? | Some | Yes (in hybrid models) |

---

## Features CRFs can use (HMMs cannot)

```
Current word:        word[i] = "Obama"
Previous word:       word[i-1] = "Barack"
Next word:           word[i+1] = "visited"
Word shape:          is_capitalized, has_digit, all_caps
Prefix/suffix:       word[:2]="Ob", word[-3:]="ama"
Previous label:      label[i-1] = B-PER
POS tag:             pos[i] = NNP
Is it first/last?:   is_first_word = False
```

---

## BIO labeling for NER

```
"Barack Obama visited London yesterday"
 B-PER  I-PER  O       B-LOC   O
```

| Label | Meaning |
|---|---|
| B-PER | Beginning of Person entity |
| I-PER | Inside (continuing) Person entity |
| B-ORG | Beginning of Organization |
| B-LOC | Beginning of Location |
| O | Outside — not an entity |

---

## NLP tasks that use CRFs

| Task | Labels |
|---|---|
| Named Entity Recognition | PER, ORG, LOC, O |
| POS tagging | NOUN, VERB, ADJ... |
| Chunking | NP, VP, PP... |
| Slot filling | intent slots in dialogue |
| Information extraction | KEY, VALUE, O |

---

## Golden Rules

1. CRFs outperform HMMs on NLP labeling tasks because they model P(labels | words) directly.
2. The power of CRFs is in feature engineering — the more informative your features, the better the model.
3. Modern NER often uses BERT + CRF: BERT provides contextual features, CRF ensures valid label sequences.
4. CRFs require labeled training data — they're supervised models.
5. Viterbi decoding works for CRFs too — finding the best label sequence is the same dynamic programming idea.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [06 Hidden Markov Models](../06_Hidden_Markov_Models/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 Sequence Models Before Transformers](../../06_Transformers/01_Sequence_Models_Before_Transformers/Theory.md)
