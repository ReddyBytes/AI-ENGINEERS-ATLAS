# Information Theory — Interview Q&A

## Beginner Level

**Q1: What is entropy in information theory?**

Entropy measures the average uncertainty or surprise in a distribution. If all outcomes are equally likely (like a fair coin), entropy is at its maximum — you can never predict what's coming. If one outcome is almost certain, entropy is near zero — there's little surprise. Shannon entropy is calculated as H = -Σ P(x) log P(x), where we weight each outcome's surprise by how often it occurs.

**Q2: What does it mean for an event to carry "a lot of information"?**

Information content is inversely related to probability — rare events carry more information than common ones. If your city always has sunny weather and the forecast says "sunny tomorrow," that tells you nothing new. But if the forecast says "tornado warning," that's highly surprising and very informative. Mathematically, information = -log P(event): the lower the probability, the higher the information content.

**Q3: What is cross-entropy loss and where is it used?**

Cross-entropy loss measures how surprised a model's predicted probability distribution is by the true labels. If a model predicts P(cat)=0.9 and the true label is "cat," the loss is small — the model wasn't surprised. If the model predicted P(cat)=0.1 but the true label is "cat," the loss is large. Cross-entropy is the standard loss function for classification tasks and is the training objective for language models like GPT.

---

## Intermediate Level

**Q4: What is the difference between entropy and cross-entropy?**

Entropy H(P) measures the uncertainty in the true distribution P — it's a property of the data itself, not the model. Cross-entropy H(P,Q) measures how well a model distribution Q approximates the true distribution P. If the model is perfect (Q=P), cross-entropy equals entropy. If the model is wrong, cross-entropy is higher. The gap between them is the KL divergence: H(P,Q) = H(P) + KL(P||Q). Training minimizes cross-entropy, which also minimizes the model's divergence from reality.

**Q5: What is KL divergence and when does it appear in ML?**

KL divergence (Kullback-Leibler divergence) measures how different probability distribution Q is from distribution P. It's always non-negative and equals zero only when P and Q are identical. It appears explicitly in Variational Autoencoders (VAEs), where the loss has a reconstruction term plus a KL term that keeps the latent distribution close to a standard normal. It also appears in reinforcement learning from human feedback (RLHF), where KL divergence keeps the fine-tuned model from drifting too far from the original base model.

**Q6: How is information theory connected to model compression and efficient coding?**

Shannon's source coding theorem says that the minimum average number of bits needed to represent outcomes from a distribution is exactly equal to the entropy. If you know the distribution, you can create efficient codes: assign short codes to common events, long codes to rare ones (this is how ZIP compression works). In ML, model compression uses similar ideas — a model with high entropy in its weights contains more information and is harder to compress. Techniques like quantization and pruning reduce the information content (and thus memory footprint) while preserving as much useful behavior as possible.

---

## Advanced Level

**Q7: Why is cross-entropy the natural choice as a loss function for classification?**

From an information-theoretic view, minimizing cross-entropy loss is equivalent to minimizing KL divergence between the model's output distribution and the true label distribution. From a probabilistic view, minimizing cross-entropy is the same as maximum likelihood estimation — finding model parameters that maximize the probability of observing the training data. From a practical view, cross-entropy has well-behaved gradients for neural networks with softmax outputs: when the model is wrong, gradients are large; when the model is correct, gradients naturally shrink. All three perspectives converge on the same conclusion.

**Q8: How does information theory apply to the training of large language models?**

Language models are trained by predicting the next token in a sequence. At each step, the model outputs a probability distribution over the entire vocabulary (50,000+ tokens). The true "distribution" is a one-hot vector — probability 1 for the actual next token, 0 for everything else. Cross-entropy loss is computed between these two distributions. Minimizing it over trillions of token predictions teaches the model the statistical structure of language. Perplexity — a common LLM evaluation metric — is just 2^(cross-entropy), measuring how "surprised" the model is by real text on average.

**Q9: What is mutual information and why is it useful in feature selection?**

Mutual information I(X;Y) measures how much knowing X reduces uncertainty about Y. It's defined as I(X;Y) = H(Y) - H(Y|X) — the entropy of Y minus the entropy of Y given X. If X and Y are completely independent, I(X;Y) = 0 — knowing X tells you nothing about Y. High mutual information means X is highly predictive of Y. In feature selection, you compute mutual information between each feature and the target label to identify the most informative features. Unlike correlation, mutual information captures non-linear relationships, making it more powerful for complex ML datasets.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Full explanation |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Intuition_First.md](./Intuition_First.md) | No-formula intuition primer |

⬅️ **Prev:** [04 Calculus and Optimization](../04_Calculus_and_Optimization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [01 What is ML](../../02_Machine_Learning_Foundations/01_What_is_ML/Theory.md)
