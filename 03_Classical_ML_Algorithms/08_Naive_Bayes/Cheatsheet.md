# Naive Bayes — Cheatsheet

**One-liner:** Naive Bayes is a probabilistic classifier that uses Bayes' theorem with the assumption that all features are independent, making it extremely fast and effective for text classification.

---

## Key Terms

| Term | What It Means |
|---|---|
| Bayes' Theorem | Formula for updating probabilities given new evidence: P(class\|data) ∝ P(data\|class) × P(class) |
| Prior Probability | P(class) — how common each class is in the training data, before seeing any features |
| Likelihood | P(feature\|class) — how often this feature appears given this class |
| Posterior Probability | P(class\|features) — the final class probability after considering all features |
| Naive Assumption | All features are treated as independent given the class |
| Laplace Smoothing | Adding a small count (alpha) to all feature frequencies to avoid zero probabilities |
| alpha | Smoothing parameter in sklearn (default=1.0) — increase to smooth more, decrease for less smoothing |
| MultinomialNB | Best for text with word counts or frequencies |
| BernoulliNB | Best for binary features (word present/absent) |
| GaussianNB | Best for continuous normally-distributed features |

---

## When to Use vs When Not to Use

| Use Naive Bayes When | Avoid Naive Bayes When |
|---|---|
| Text classification (spam, sentiment, topics) | Features are strongly correlated (violates core assumption) |
| Very fast training and prediction needed | You need well-calibrated probability estimates |
| Small training datasets | Data has complex non-linear decision boundaries |
| High-dimensional sparse data | Continuous features that are not Gaussian (for GaussianNB) |
| First benchmark / baseline model | Class boundaries are subtle and nuanced |
| Streaming or real-time classification | Feature interactions matter a lot |

---

## The Three Variants

| Variant | sklearn Class | Feature Type | Typical Use |
|---|---|---|---|
| Multinomial | `MultinomialNB` | Word counts, integer frequencies | Spam detection, topic classification |
| Bernoulli | `BernoulliNB` | Binary 0/1 (word present or absent) | Short text, binary feature sets |
| Gaussian | `GaussianNB` | Real-valued, continuous | Sensor data, medical measurements |

---

## Key sklearn Parameters

| Parameter | Default | What It Controls |
|---|---|---|
| `alpha` (MultinomialNB, BernoulliNB) | 1.0 | Laplace smoothing — prevents zero probabilities |
| `fit_prior` | True | Whether to learn class priors from data or use uniform |
| `class_prior` | None | Manually set class probabilities if you know them |
| `var_smoothing` (GaussianNB) | 1e-9 | Small variance added for numerical stability |

---

## Golden Rules

1. **Naive Bayes is a great first model.** Always try it as a baseline before more complex algorithms, especially for text.
2. **Use `CountVectorizer` or `TfidfVectorizer` before `MultinomialNB`.** You need to convert raw text to numbers first.
3. **Adjust alpha if you have sparse data.** Higher alpha = more smoothing = less overfitting on rare words.
4. **It is NOT naive about being fast.** Training is O(N×D) — linear in data points and features. Extremely scalable.
5. **Class imbalance matters less** — Naive Bayes captures class frequency in the prior probability automatically.
6. **Do not use MultinomialNB with TF-IDF if TF-IDF produces negative values** — MultinomialNB requires non-negative features. Use `ComplementNB` instead, which handles TF-IDF and class imbalance better.
7. **The independence assumption rarely holds exactly** — but the algorithm often works surprisingly well despite this.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, Bayes' theorem, types of Naive Bayes |
| **Cheatsheet.md** | ← you are here |
| [Interview_QA.md](./Interview_QA.md) | Beginner to advanced interview questions |
| [Code_Example.md](./Code_Example.md) | Full working Python spam detector example |

⬅️ **Prev:** [07 PCA](../07_PCA_Dimensionality_Reduction/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Neural Networks and Deep Learning](../../04_Neural_Networks_and_Deep_Learning/Readme.md)
