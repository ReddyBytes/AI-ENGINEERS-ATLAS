# Probability — Interview Q&A

## Beginner Level

**Q1: What is probability and what values can it take?**

<details>
<summary>💡 Show Answer</summary>

Probability measures how likely an event is to occur. It's always a number between 0 and 1, where 0 means impossible and 1 means certain. A probability of 0.8 means the event happens 80% of the time on average.

</details>

<br>

**Q2: What is the difference between P(A and B) and P(A or B)?**

<details>
<summary>💡 Show Answer</summary>

P(A and B) is the probability that both events happen at the same time — it uses multiplication for independent events. P(A or B) is the probability that at least one of them happens — it uses addition but you subtract the overlap to avoid double-counting: P(A) + P(B) - P(A and B).

</details>

<br>

**Q3: What is a complement in probability?**

<details>
<summary>💡 Show Answer</summary>

The complement of event A is everything that is NOT A. P(not A) = 1 - P(A). It's useful when the event you want is hard to calculate directly but its opposite is easy. For example, "probability of rolling at least one 6 in three rolls" is easier as 1 - P(no 6 in three rolls).

</details>

---

## Intermediate Level

**Q4: What does conditional probability mean and why is it important in AI?**

<details>
<summary>💡 Show Answer</summary>

Conditional probability P(B|A) is the probability of B happening given that A has already happened. It's crucial in AI because most predictions are conditional — a spam filter asks "what's the probability this is spam, given the words it contains?" New evidence changes our probability estimate.

</details>

<br>

**Q5: What is the difference between independent and dependent events?**

<details>
<summary>💡 Show Answer</summary>

Two events are independent if knowing one happened gives you no information about the other — like two separate coin flips. They're dependent if one influences the other — like drawing cards from a deck without replacement. For independent events P(A and B) = P(A) × P(B). For dependent events you must use conditional probability: P(A and B) = P(A) × P(B|A).

</details>

<br>

**Q6: How does Bayes' Theorem relate to conditional probability?**

<details>
<summary>💡 Show Answer</summary>

Bayes' Theorem lets you reverse conditional probabilities: P(A|B) = P(B|A) × P(A) / P(B). In AI this is huge — you start with a prior belief P(A), observe evidence B, and update to a posterior P(A|B). Naïve Bayes classifiers, spam filters, and medical diagnosis tools all use this exact pattern of updating beliefs with evidence.

</details>

---

## Advanced Level

**Q7: What is the difference between frequentist and Bayesian interpretations of probability?**

<details>
<summary>💡 Show Answer</summary>

Frequentists say probability is the long-run frequency of an event — if you flip a coin a million times, heads should appear ~50% of the time. Bayesians say probability represents a degree of belief that can be updated with evidence. In AI, Bayesian thinking is powerful because it handles uncertainty even when you can't run millions of experiments. Most modern ML implicitly uses Bayesian ideas through priors, posteriors, and regularization.

</details>

<br>

**Q8: What is a probability distribution and why does every AI model output one?**

<details>
<summary>💡 Show Answer</summary>

A probability distribution assigns a probability to every possible outcome such that they all sum to 1. Every AI classifier outputs a distribution over classes — for example, a dog vs. cat model might output [dog: 0.92, cat: 0.08]. This is better than a hard yes/no because you also get confidence. Loss functions like cross-entropy compare the model's output distribution to the true distribution.

</details>

<br>

**Q9: What is the law of large numbers and why does it matter for training ML models?**

<details>
<summary>💡 Show Answer</summary>

The law of large numbers states that as you observe more samples, your empirical average converges to the true expected value. In ML training, this is why larger datasets produce better models — with more data, your estimated statistics (means, variances, probabilities) get closer to the true underlying distribution. It also justifies using mini-batches in gradient descent: even a small random sample gives a reasonable estimate of the true gradient.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |
| [📄 Mini_Exercise.md](./Mini_Exercise.md) | Practice exercises |

⬅️ **Prev:** [00 Learning Guide](../../00_Learning_Guide/Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Statistics](../02_Statistics/Theory.md)
