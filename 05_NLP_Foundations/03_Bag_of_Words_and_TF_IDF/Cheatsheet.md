# Bag of Words & TF-IDF — Cheatsheet

**One-liner:** Bag of Words counts word occurrences per document; TF-IDF improves on this by down-weighting common words and up-weighting rare, distinctive ones.

---

## Key Terms

| Term | Definition |
|---|---|
| Bag of Words (BoW) | Represents a document as a vector of word frequencies |
| Vocabulary | The complete set of unique words across all documents |
| TF (Term Frequency) | How often a word appears in one document |
| IDF (Inverse Document Frequency) | How rare a word is across all documents |
| TF-IDF | TF × IDF — ranks word importance within a document |
| Sparse vector | A vector mostly full of zeros (typical in BoW) |
| Document-term matrix | The full matrix of all documents × all vocabulary words |
| n-gram | A sequence of n words treated as one token ("New York") |

---

## Formulas

```
TF(word, doc)  = count(word in doc) / total words in doc

IDF(word)      = log(total docs / docs containing word)

TF-IDF(word, doc) = TF × IDF
```

---

## When to use / not use

| Method | Use when | Avoid when |
|---|---|---|
| BoW | Quick baseline, small datasets | You need word relationships |
| TF-IDF | Text classification, search | You need semantic understanding |
| Both | Traditional ML pipelines | Deep learning (use embeddings instead) |

---

## Limitations summary

| Limitation | BoW | TF-IDF |
|---|---|---|
| Ignores word order | Yes | Yes |
| No semantic meaning | Yes | Yes |
| Common words dominate | Yes | Partially fixed |
| High dimensionality | Yes | Yes |
| Sparse vectors | Yes | Yes |

---

## sklearn quick reference

```python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# BoW
cv = CountVectorizer()
X_bow = cv.fit_transform(corpus)

# TF-IDF
tv = TfidfVectorizer()
X_tfidf = tv.fit_transform(corpus)

# n-grams
tv_ngram = TfidfVectorizer(ngram_range=(1, 2))  # unigrams + bigrams
```

---

## Golden Rules

1. Always remove stopwords before BoW/TF-IDF — they waste vocabulary slots.
2. TF-IDF is almost always better than raw BoW for classification tasks.
3. Add bigrams (ngram_range=(1,2)) to partially recover word-order information.
4. BoW and TF-IDF create sparse vectors — use sparse matrix libraries, not dense arrays.
5. For any task requiring semantic understanding, move to word embeddings instead.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [02 Tokenization](../02_Tokenization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Word Embeddings](../04_Word_Embeddings/Theory.md)
