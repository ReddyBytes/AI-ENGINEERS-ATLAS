# Bag of Words & TF-IDF — Interview Q&A

## Beginner

**Q1. What is Bag of Words and what are its main limitations?**

Bag of Words represents a document as a vector of word counts. Each word in the vocabulary gets a column, and each document gets a row showing how many times each word appears.

Main limitations:

- No word order: "dog bites man" and "man bites dog" have identical BoW vectors
- No meaning: it doesn't know "happy" and "joyful" are related
- Common words dominate: "the" and "is" get huge counts even though they're meaningless
- High dimensionality: with a large vocabulary, each vector has thousands of mostly-zero values

---

**Q2. What is TF-IDF and how does it improve on BoW?**

TF-IDF (Term Frequency — Inverse Document Frequency) is a smarter weighting scheme. Instead of just counting words, it weights each word by how distinctive it is for a specific document.

- TF (Term Frequency): how often the word appears in *this* document
- IDF (Inverse Document Frequency): how rare the word is across *all* documents
- Score = TF × IDF

A word that appears often in one document but rarely in others gets a high score — it's a distinctive signal. A word like "the" that appears everywhere gets an IDF near zero, so its TF-IDF score stays low even if it appears many times.

---

**Q3. If "the" appears 50 times in a 100-word document, will it have a high TF-IDF score?**

No. TF would be 0.5 (high), but IDF would be very close to zero because "the" appears in virtually every document. TF × IDF ≈ 0.5 × 0 ≈ 0. The IDF component wipes out the high TF. That's exactly what TF-IDF is designed to do — suppress common, uninformative words without you needing to manually list them as stopwords.

---

## Intermediate

**Q4. How would you use TF-IDF for a text classification task like spam detection?**

1. Collect labeled data: spam and non-spam emails
2. Preprocess: lowercase, remove punctuation, optionally remove stopwords
3. Fit a `TfidfVectorizer` on the training data — it learns the vocabulary and IDF weights
4. Transform training documents into TF-IDF vectors
5. Train a classifier (Logistic Regression, Naive Bayes, or SVM work well)
6. Apply the same vectorizer (don't refit) to transform test/new emails
7. Predict with the trained classifier

The TF-IDF features capture words like "free", "win", "prize", "click" as high-scoring signals in spam, making them easy for the classifier to learn.

---

**Q5. What are n-grams and why are they useful with BoW/TF-IDF?**

N-grams are sequences of n consecutive words treated as one token.

- Unigrams (n=1): "New", "York" — two separate tokens
- Bigrams (n=2): "New York" — one token representing the city
- Trigrams (n=3): "not very good" — captures negation

BoW and TF-IDF lose word order. Adding bigrams partially restores it. "Not good" as a bigram is very different from "not" and "good" as separate unigrams. In sklearn: `TfidfVectorizer(ngram_range=(1, 2))` includes both unigrams and bigrams.

---

**Q6. How does TF-IDF perform compared to word embeddings for NLP tasks?**

For traditional ML tasks on clean, mid-sized text datasets, TF-IDF + Logistic Regression is surprisingly competitive. It's fast, interpretable, and requires no GPU.

However, TF-IDF falls short when:
- Semantic understanding is needed ("happy" ≠ "joyful" to TF-IDF)
- Word relationships matter (king − man + woman = queen is impossible)
- Context matters ("bank" in finance vs geography is one word to TF-IDF)

Word embeddings and transformers dominate all of these cases. TF-IDF is still useful as a baseline and in resource-constrained environments.

---

## Advanced

**Q7. How would you handle a high-dimensional sparse TF-IDF matrix efficiently in production?**

A corpus of 100k documents with a 50k-word vocabulary creates a 100k × 50k matrix — 5 billion cells. Storing this as a dense matrix is impossible.

Key approaches:
- Use scipy sparse matrices (sklearn does this automatically)
- Limit vocabulary: `max_features=10000` keeps only the top 10k words by frequency
- Use `min_df` and `max_df`: ignore words that appear in fewer than 5 docs or more than 90% of docs
- Dimensionality reduction: apply Truncated SVD (LSA) to reduce to 100-300 dense dimensions
- For very large corpora, use hashing trick (`HashingVectorizer`) — no vocabulary stored in memory

---

**Q8. Explain Latent Semantic Analysis (LSA) and how it relates to TF-IDF.**

LSA takes a TF-IDF matrix and applies Truncated SVD (a matrix decomposition) to reduce it to a lower-dimensional dense representation.

Why? TF-IDF vectors are sparse and don't capture synonymy. "Car" and "automobile" have no overlap in a BoW matrix. After LSA, documents that use "car" and documents that use "automobile" will be closer in the reduced space because they tend to appear in similar contexts across the corpus.

LSA is essentially a precursor to word embeddings. It's less powerful (linear transformation only) but can work well on smaller datasets and is fully interpretable.

---

**Q9. When should you choose TF-IDF over a transformer like BERT for a production system?**

Choose TF-IDF when:
- Latency is critical and you need sub-millisecond inference
- You have very limited compute (no GPU, edge deployment)
- The dataset is small (under 10k examples) — transformers may overfit
- The task is simple and vocabulary-driven (keyword matching, document routing)
- Interpretability is required — you can inspect which words drive predictions
- You need a fast baseline to validate the task is solvable

Choose BERT/transformers when:
- Accuracy is the priority and compute is available
- Context and meaning matter (disambiguation, NER, QA)
- You have enough labeled data to fine-tune
- The task involves complex language understanding

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [02 Tokenization](../02_Tokenization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Word Embeddings](../04_Word_Embeddings/Theory.md)
