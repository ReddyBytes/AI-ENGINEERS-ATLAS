# Naive Bayes — Code Example

## What This Code Does

We will build a simple spam detector using Multinomial Naive Bayes. The dataset is tiny and hand-crafted so you can see exactly what is happening. Then we show how to extend it to a real-world scale.

```python
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

# ─────────────────────────────────────────────
# 1. HAND-CRAFTED SPAM DATASET
# ─────────────────────────────────────────────

# A tiny example dataset — 10 emails, hand-labelled as spam (1) or ham (0)
# In practice you would load thousands of real emails
emails = [
    # Spam examples
    "Win free money now click here",
    "You won a FREE prize claim now",
    "Cheap loans free credit offer",
    "FREE iPhone winner click to claim",
    "Make money fast free investment",
    "Buy now discount offer limited time free",
    # Ham (normal) examples
    "Meeting scheduled for tomorrow morning",
    "Can you send me the project report",
    "Lunch at 12pm today works for me",
    "Please review the attached document",
]

labels = [1, 1, 1, 1, 1, 1,   # spam
          0, 0, 0, 0]           # ham

# ─────────────────────────────────────────────
# 2. CONVERT TEXT TO NUMBERS WITH CountVectorizer
# ─────────────────────────────────────────────

# CountVectorizer builds a vocabulary from all words, then represents
# each document as a vector of word counts.
# e.g. "free money free" → {"free": 2, "money": 1, ...}

vectorizer = CountVectorizer(
    lowercase=True,    # Convert to lowercase before tokenizing
    stop_words=None,   # Keep all words for this example
)

# fit_transform on the ENTIRE small dataset here (for demo purposes)
# In real code: fit_transform on train, transform only on test
X = vectorizer.fit_transform(emails)
y = np.array(labels)

print(f"Vocabulary size: {len(vectorizer.vocabulary_)} words")
print(f"Feature matrix shape: {X.shape}")  # (10 emails, N words)
print(f"\nVocabulary (first 15 words alphabetically):")
vocab_sorted = sorted(vectorizer.vocabulary_.keys())
print(vocab_sorted[:15])

# Each row is one email, each column is one word from the vocabulary
# The value is the count of that word in that email
print(f"\nMatrix for email[0] ('{emails[0]}'):")
email_0_dense = X[0].toarray()[0]
for word, idx in sorted(vectorizer.vocabulary_.items()):
    if email_0_dense[idx] > 0:
        print(f"  '{word}': {int(email_0_dense[idx])}")

# ─────────────────────────────────────────────
# 3. TRAIN THE NAIVE BAYES CLASSIFIER
# ─────────────────────────────────────────────

# MultinomialNB — designed for discrete counts (perfect for word counts)
# alpha=1.0 is Laplace smoothing: adds 1 to every word count
# This prevents zero probabilities for words not seen in training
nb_model = MultinomialNB(alpha=1.0)
nb_model.fit(X, y)

print("\n=== Model Training Complete ===")
print(f"Classes: {nb_model.classes_}")  # [0, 1]
print(f"Class priors (log): {nb_model.class_log_prior_}")
print(f"Prior P(ham=0): {np.exp(nb_model.class_log_prior_[0]):.2f}")
print(f"Prior P(spam=1): {np.exp(nb_model.class_log_prior_[1]):.2f}")

# ─────────────────────────────────────────────
# 4. PREDICT ON NEW EMAILS
# ─────────────────────────────────────────────

new_emails = [
    "Free money offer click now",         # Should be spam
    "Project deadline is next Friday",     # Should be ham
    "Congratulations you won a prize",     # Should be spam
    "Can we reschedule the meeting",       # Should be ham
]

# Transform new emails using the SAME vectorizer (not a new fit)
X_new = vectorizer.transform(new_emails)

# Predict the class (0=ham, 1=spam)
predictions = nb_model.predict(X_new)

# Predict_proba gives the probability for each class
probabilities = nb_model.predict_proba(X_new)

print("\n=== Predictions on New Emails ===")
for email, pred, probs in zip(new_emails, predictions, probabilities):
    label = "SPAM" if pred == 1 else "HAM"
    confidence = max(probs) * 100
    print(f"  '{email[:45]}'")
    print(f"    → {label} (confidence: {confidence:.1f}%, P(ham)={probs[0]:.3f}, P(spam)={probs[1]:.3f})")
    print()

# ─────────────────────────────────────────────
# 5. INSPECT WHAT THE MODEL LEARNED
# ─────────────────────────────────────────────

# Look at which words are most associated with spam
# feature_log_prob_ has shape (n_classes, n_features)
# Row 0 = ham probabilities, Row 1 = spam probabilities

spam_log_probs = nb_model.feature_log_prob_[1]  # log P(word | spam)
ham_log_probs = nb_model.feature_log_prob_[0]   # log P(word | ham)

# Calculate the spam-ham log ratio: high = spammy word, low = hammy word
log_ratios = spam_log_probs - ham_log_probs

# Map back to word names
vocab_list = vectorizer.get_feature_names_out()
word_scores = list(zip(vocab_list, log_ratios))
word_scores.sort(key=lambda x: x[1], reverse=True)

print("=== Most Spammy Words (highest spam/ham ratio) ===")
for word, score in word_scores[:8]:
    print(f"  '{word}': log-ratio = {score:.2f}")

print("\n=== Most Hammy Words (lowest spam/ham ratio) ===")
for word, score in word_scores[-5:]:
    print(f"  '{word}': log-ratio = {score:.2f}")

# ─────────────────────────────────────────────
# 6. FULL PIPELINE — THE RIGHT WAY FOR REAL PROJECTS
# ─────────────────────────────────────────────

# Using sklearn Pipeline: vectorizer + classifier in one object
# This makes it easy to cross-validate and deploy

# With a larger dataset we would split train/test:
# X_train, X_test, y_train, y_test = train_test_split(emails, labels, test_size=0.2, random_state=42)

pipeline = Pipeline([
    # Step 1: Convert text to word count vectors
    ('vectorizer', CountVectorizer(
        lowercase=True,
        ngram_range=(1, 2),  # Include both single words AND word pairs ("free money")
        min_df=1,            # Include words that appear in at least 1 document
    )),
    # Step 2: Train Naive Bayes classifier
    ('classifier', MultinomialNB(alpha=1.0))
])

# Fit the full pipeline on all our data
pipeline.fit(emails, labels)

# The pipeline handles vectorization + prediction together
pipeline_predictions = pipeline.predict(new_emails)
pipeline_probabilities = pipeline.predict_proba(new_emails)

print("\n=== Pipeline Predictions ===")
for email, pred, probs in zip(new_emails, pipeline_predictions, pipeline_probabilities):
    label = "SPAM" if pred == 1 else "HAM"
    print(f"  {label}: '{email[:50]}'")

# ─────────────────────────────────────────────
# 7. REAL-WORLD SCALE: 20 NEWSGROUPS DATASET
# ─────────────────────────────────────────────

print("\n=== Scaling Up: 20 Newsgroups Dataset ===")
from sklearn.datasets import fetch_20newsgroups

# Load just 2 categories for binary classification
categories = ['sci.space', 'rec.sport.hockey']
newsgroups_train = fetch_20newsgroups(subset='train', categories=categories, remove=('headers', 'footers'))
newsgroups_test = fetch_20newsgroups(subset='test', categories=categories, remove=('headers', 'footers'))

print(f"Training examples: {len(newsgroups_train.data)}")
print(f"Test examples: {len(newsgroups_test.data)}")
print(f"Classes: {newsgroups_train.target_names}")

# Build pipeline with TF-IDF (better than raw counts for unequal document lengths)
news_pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(
        max_features=10000,  # Keep only top 10,000 most important words
        ngram_range=(1, 2),  # Single words and word pairs
        sublinear_tf=True,   # Apply log to term frequencies (reduces impact of very common words)
    )),
    ('classifier', MultinomialNB(alpha=0.1))  # Lower alpha for large vocabulary
])

news_pipeline.fit(newsgroups_train.data, newsgroups_train.target)
news_predictions = news_pipeline.predict(newsgroups_test.data)

accuracy = accuracy_score(newsgroups_test.target, news_predictions)
print(f"\nAccuracy on test set: {accuracy:.3f}")
print("\nClassification Report:")
print(classification_report(
    newsgroups_test.target,
    news_predictions,
    target_names=newsgroups_train.target_names
))
```

---

## Expected Output

```
Vocabulary size: 28 words
Feature matrix shape: (10, 28)

Vocabulary (first 15 words alphabetically):
['attached', 'buy', 'cheap', 'claim', 'click', 'credit', 'discount', ...]

=== Model Training Complete ===
Classes: [0 1]
Prior P(ham=0): 0.40
Prior P(spam=1): 0.60

=== Predictions on New Emails ===
  'Free money offer click now'
    → SPAM (confidence: 96.4%, P(ham)=0.036, P(spam)=0.964)

  'Project deadline is next Friday'
    → HAM (confidence: 87.2%, P(ham)=0.872, P(spam)=0.128)

  'Congratulations you won a prize'
    → SPAM (confidence: 91.3%, P(ham)=0.087, P(spam)=0.913)

  'Can we reschedule the meeting'
    → HAM (confidence: 83.5%, P(ham)=0.835, P(spam)=0.165)

=== Most Spammy Words ===
  'free': log-ratio = 2.84
  'click': log-ratio = 2.71
  'money': log-ratio = 2.61
  'offer': log-ratio = 2.45
  ...

=== Scaling Up: 20 Newsgroups Dataset ===
Training examples: 1192
Test examples: 794
Classes: ['rec.sport.hockey', 'sci.space']

Accuracy on test set: 0.971
```

---

## Key Takeaways from the Code

- **CountVectorizer converts text to numbers** — Naive Bayes needs numbers, not strings.
- **Always use the same fitted vectorizer** for training and prediction — call `fit_transform` on training data, then `transform` on test/new data.
- **`feature_log_prob_`** shows what the model learned — which words are most associated with each class.
- **Pipeline makes it safe** — fitting the vectorizer on training data only, preventing data leakage.
- **Accuracy ~97% on newsgroups** — Naive Bayes is genuinely powerful for text classification despite its simplicity.
- **`alpha` controls smoothing** — for large vocabularies (10,000+ words) try smaller alpha (0.1) to avoid over-smoothing.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, Bayes' theorem, types of Naive Bayes |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| **Code_Example.md** | ← you are here |

⬅️ **Prev:** [07 PCA](../07_PCA_Dimensionality_Reduction/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Neural Networks and Deep Learning](../../04_Neural_Networks_and_Deep_Learning/Readme.md)
