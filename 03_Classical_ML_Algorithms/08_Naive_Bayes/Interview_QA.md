# Naive Bayes — Interview Q&A

## Beginner Level

**Q1. What is Naive Bayes and what makes it "naive"?**

<details>
<summary>💡 Show Answer</summary>

Naive Bayes is a probabilistic classification algorithm based on Bayes' theorem. It calculates the probability of each class given the observed features, then predicts the most probable class. The "naive" part comes from its core assumption: it treats all features as completely independent from each other, given the class. In reality, features are often correlated (words in a sentence are related to each other), but this naive assumption simplifies the math enormously and often produces surprisingly good results anyway.

</details>

**Q2. Explain Bayes' theorem in plain English.**

<details>
<summary>💡 Show Answer</summary>

Bayes' theorem says: your belief about something should update when you see new evidence, and the update is proportional to how likely that evidence was given your belief.

For classification: `P(class | features) ∝ P(features | class) × P(class)`

- P(class | features): probability of this class given what I observed — this is what we want
- P(features | class): how often do these features appear with this class — learned from training data
- P(class): how common is this class in general — the prior

Example: if 40% of emails are spam and the word "FREE" appears in 80% of spam but only 5% of normal emails, seeing "FREE" gives strong evidence for spam.

</details>

**Q3. What is Laplace smoothing and why is it needed?**

<details>
<summary>💡 Show Answer</summary>

If a word appears in test data that was never seen during training, its probability estimate would be 0. Multiplying 0 anywhere in the probability chain makes the whole class probability 0 — regardless of all other evidence. Laplace smoothing prevents this by adding a small count (typically 1, controlled by the `alpha` parameter in sklearn) to every feature's count for every class. This ensures every probability is at least a small positive number, never exactly 0.

</details>

---

## Intermediate Level

**Q4. Why is Naive Bayes so effective for text classification despite its naive assumption?**

<details>
<summary>💡 Show Answer</summary>

Several reasons work in its favour for text:
- **Scale**: documents can have thousands of words. Treating them independently makes the problem tractable — 10,000 independent probability lookups vs an impossible joint distribution over 10,000 words.
- **Sparse features**: most words appear rarely. The independence assumption causes less harm when features are sparse.
- **The right structure**: even if words are somewhat correlated, the *direction* of the probability calculation (which class has higher combined probability) is often still correct, even if the absolute probabilities are wrong.
- **Speed**: training is just counting word frequencies per class. No gradient descent, no matrix operations. You can train on millions of documents in seconds.

</details>

**Q5. What are the differences between MultinomialNB, BernoulliNB, and GaussianNB?**

<details>
<summary>💡 Show Answer</summary>

- **MultinomialNB**: models feature counts or frequencies. Best for text where each word can appear multiple times. It models P(word | class) as a multinomial distribution. "How many times did this word appear?"
- **BernoulliNB**: models binary features (0 or 1). Best for short text or cases where you only care whether a word appeared, not how often. It penalises the absence of features that are common in the class. "Did this word appear at all?"
- **GaussianNB**: assumes each feature follows a Gaussian (normal) distribution within each class. Best for continuous features like measurements, sensor data, or medical readings.

</details>

**Q6. What are the key limitations of Naive Bayes?**

<details>
<summary>💡 Show Answer</summary>

- **Independence assumption often violated**: in text, words are strongly correlated (e.g. "San" and "Francisco" always appear together). The algorithm compensates somewhat, but calibration suffers.
- **Probability estimates are often poorly calibrated**: Naive Bayes often outputs probabilities very close to 0 or 1, even when the true probability is 0.7. Good for ranking but bad for actual probability estimates.
- **Feature interaction ignored**: Naive Bayes cannot learn that "not + good" means negative sentiment — it sees "not" and "good" as separate positive signals.
- **Continuous features require Gaussian assumption**: GaussianNB works poorly for skewed or multi-modal distributions.

</details>

---

## Advanced Level

**Q7. How does Naive Bayes handle class imbalance?**

<details>
<summary>💡 Show Answer</summary>

Naive Bayes naturally incorporates class frequency through the prior probability P(class). If 95% of your emails are ham and 5% are spam, the model learns `P(spam) = 0.05` from the training data. This means even if all the word evidence points slightly toward spam, the low prior pulls the final probability down. This can cause Naive Bayes to under-predict the minority class. Solutions include: setting `class_prior` manually to equal weights, using `fit_prior=False` for uniform priors, or using `ComplementNB` which is specifically designed to handle imbalanced text datasets by modelling the complement of each class.

</details>

**Q8. What is ComplementNB and when should you use it?**

<details>
<summary>💡 Show Answer</summary>

ComplementNB is a variant of Multinomial NB that trains each classifier using data from all *other* classes (the complement) instead of just the target class. This helps when training data is imbalanced — instead of estimating P(word | spam) from the small spam sample, it estimates P(word | NOT spam) from the large ham sample, which is more reliable. ComplementNB tends to outperform MultinomialNB on imbalanced datasets and when combined with TF-IDF features. It also works with negative TF-IDF values (handled differently than MultinomialNB).

</details>

**Q9. How does Naive Bayes relate to logistic regression, and when would you choose one over the other?**

<details>
<summary>💡 Show Answer</summary>

Both are linear classifiers for text when used with bag-of-words features. The key differences:
- **Naive Bayes is a generative model** — it models P(features | class) and uses Bayes' rule. It makes strong distributional assumptions but trains on very little data.
- **Logistic Regression is a discriminative model** — it directly models P(class | features) without assumptions about feature distributions. It is more flexible but needs more data.

In practice:
- With very little training data: Naive Bayes wins — it can learn from a handful of examples.
- With medium to large training data: Logistic Regression usually outperforms Naive Bayes because the independence assumption becomes a bottleneck.
- For speed and streaming data: Naive Bayes wins — it is much faster to train and update.
- The two can be complementary: use Naive Bayes features as input to Logistic Regression (NBLogistic, a known effective combination).

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [Theory.md](./Theory.md) | Core concepts, Bayes' theorem, types of Naive Bayes |
| [Cheatsheet.md](./Cheatsheet.md) | Key terms, when to use, golden rules |
| **Interview_QA.md** | ← you are here |
| [Code_Example.md](./Code_Example.md) | Full working Python spam detector example |

⬅️ **Prev:** [07 PCA](../07_PCA_Dimensionality_Reduction/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Neural Networks and Deep Learning](../../04_Neural_Networks_and_Deep_Learning/Readme.md)
