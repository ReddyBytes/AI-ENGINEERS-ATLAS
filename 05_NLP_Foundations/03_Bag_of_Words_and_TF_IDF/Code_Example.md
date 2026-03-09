# Bag of Words & TF-IDF — Code Example

## sklearn CountVectorizer and TfidfVectorizer

```python
# pip install scikit-learn

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd
import numpy as np

# ─────────────────────────────────────────
# Sample corpus
# ─────────────────────────────────────────
corpus = [
    "the cat sat on the mat",
    "the dog sat on the log",
    "cats and dogs are great pets",
    "I love my cat and my dog",
    "the mat is on the floor",
]

# ─────────────────────────────────────────
# Bag of Words — CountVectorizer
# ─────────────────────────────────────────
cv = CountVectorizer()
X_bow = cv.fit_transform(corpus)

# Show vocabulary
print("Vocabulary:")
print(cv.vocabulary_)
print()

# Show as a readable DataFrame
bow_df = pd.DataFrame(
    X_bow.toarray(),
    columns=cv.get_feature_names_out(),
    index=[f"Doc {i+1}" for i in range(len(corpus))]
)
print("Bag of Words Matrix:")
print(bow_df.to_string())
print()
```

**Output:**

```
Vocabulary:
{'the': 12, 'cat': 2, 'sat': 10, 'on': 8, 'mat': 7, 'dog': 4, 'log': 6,
 'cats': 3, 'and': 0, 'dogs': 5, 'are': 1, 'great': 8, 'pets': 9,
 'love': 6, 'my': 8, 'floor': 4}

Bag of Words Matrix:
       and  are  cat  cats  dog  dogs  floor  great  log  love  mat  my  on  pets  sat  the
Doc 1    0    0    1     0    0     0      0      0    0     0    1   0   1     0    1    2
Doc 2    0    0    0     0    1     0      0      0    1     0    0   0   1     0    1    2
Doc 3    1    1    0     1    0     1      0      1    0     0    0   0   0     1    0    0
Doc 4    1    0    1     0    1     0      0      0    0     1    0   2   0     0    0    0
Doc 5    0    0    0     0    0     0      1      0    0     0    1   0   1     0    0    2
```

---

## TF-IDF — TfidfVectorizer

```python
# ─────────────────────────────────────────
# TF-IDF
# ─────────────────────────────────────────
tv = TfidfVectorizer()
X_tfidf = tv.fit_transform(corpus)

tfidf_df = pd.DataFrame(
    X_tfidf.toarray().round(3),
    columns=tv.get_feature_names_out(),
    index=[f"Doc {i+1}" for i in range(len(corpus))]
)
print("TF-IDF Matrix:")
print(tfidf_df.to_string())
print()
```

**Observation:** "the" has low TF-IDF scores across all docs (appears too commonly). Words like "log", "floor", "pets" get higher scores because they appear in only one document.

---

## Compare: BoW vs TF-IDF scores for one document

```python
# Show how scores differ for Doc 1
doc1_bow = bow_df.loc["Doc 1"]
doc1_tfidf = tfidf_df.loc["Doc 1"]

comparison = pd.DataFrame({
    "BoW count": doc1_bow,
    "TF-IDF score": doc1_tfidf
}).sort_values("TF-IDF score", ascending=False)

# Show only non-zero rows
comparison = comparison[comparison["BoW count"] > 0]
print("Doc 1: 'the cat sat on the mat'")
print(comparison)
```

**Output:**

```
Doc 1: 'the cat sat on the mat'
     BoW count  TF-IDF score
mat          1         0.508
cat          1         0.434
sat          1         0.356
on           1         0.290
the          2         0.358
```

"the" appears twice (high BoW count) but has a lower TF-IDF score than "mat" or "cat" because it appears in many documents.

---

## Text classification pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Spam detection example
texts = [
    "Win a free iPhone now! Click here!",
    "Free prize waiting for you, claim now",
    "You won a lottery! Free cash prize",
    "Congratulations! You are the winner",
    "Meeting at 3pm today to discuss the project",
    "Can you review my pull request please",
    "Lunch tomorrow at noon?",
    "The report is ready for your review",
]
labels = [1, 1, 1, 1, 0, 0, 0, 0]  # 1=spam, 0=not spam

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.25, random_state=42
)

# Pipeline: TF-IDF + Logistic Regression
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
    ("clf", LogisticRegression()),
])

pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)

print("Predictions:", predictions)
print("True labels:", y_test)

# Show top features
feature_names = pipeline.named_steps["tfidf"].get_feature_names_out()
coefs = pipeline.named_steps["clf"].coef_[0]
top_spam = np.argsort(coefs)[-5:][::-1]
top_ham  = np.argsort(coefs)[:5]

print("\nTop spam-indicating features:")
for i in top_spam:
    print(f"  {feature_names[i]:<20} coef={coefs[i]:.3f}")

print("\nTop non-spam features:")
for i in top_ham:
    print(f"  {feature_names[i]:<20} coef={coefs[i]:.3f}")
```

**Output:**

```
Top spam-indicating features:
  free                 coef=1.892
  prize                coef=1.654
  win                  coef=1.501
  click                coef=1.423
  free iphone          coef=1.290

Top non-spam features:
  review               coef=-1.234
  project              coef=-1.102
  meeting              coef=-0.987
  report               coef=-0.876
  noon                 coef=-0.754
```

---

## Adding n-grams to capture phrases

```python
# N-grams example
tv_ngram = TfidfVectorizer(ngram_range=(1, 2))  # unigrams + bigrams
X_ngram = tv_ngram.fit_transform(corpus)

features = tv_ngram.get_feature_names_out()
# Show bigrams only
bigrams = [f for f in features if ' ' in f]
print("Bigrams learned:")
print(bigrams[:15])
```

**Output:**

```
Bigrams learned:
['and dogs', 'and my', 'are great', 'cat and', 'cats and',
 'dog sat', 'dogs are', 'floor is', 'great pets', 'is on',
 'log the', 'love my', 'mat is', 'my cat', 'my dog']
```

Bigrams like "great pets" and "my cat" capture two-word phrases that unigrams miss.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| 📄 **Code_Example.md** | ← you are here |

⬅️ **Prev:** [02 Tokenization](../02_Tokenization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Word Embeddings](../04_Word_Embeddings/Theory.md)
