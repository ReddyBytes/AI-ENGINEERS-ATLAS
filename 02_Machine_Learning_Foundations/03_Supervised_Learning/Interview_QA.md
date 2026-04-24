# Supervised Learning — Interview Q&A

## Beginner Level

**Q1: What is supervised learning and why is it called "supervised"?**

<details>
<summary>💡 Show Answer</summary>

A: Supervised learning is a type of machine learning where the model trains on labeled data — every example comes with the correct answer already attached. It is called "supervised" because a human supervisor has pre-labeled the data, telling the model what the right answer is for each example. The model learns by comparing its predictions to these known answers and adjusting until it gets good at predicting the right answer.

</details>

<br>

**Q2: What is the difference between classification and regression in supervised learning?**

<details>
<summary>💡 Show Answer</summary>

A: Both are supervised learning tasks. Classification predicts a discrete category — for example, is this email spam or not? Is this image a cat or a dog? Regression predicts a continuous number — for example, what will this house sell for? What temperature will it be tomorrow? The key question is: is the output a category or a number?

</details>

<br>

**Q3: What is a feature and what is a label in supervised learning?**

<details>
<summary>💡 Show Answer</summary>

A: Features are the input variables the model uses to make a prediction — for a loan application, features might be income, credit score, and debt amount. The label is the correct answer for each training example — for a loan application, the label might be "Approved" or "Rejected." During training the model sees both features and labels. During inference it only sees features and must predict the label.

</details>

---

## Intermediate Level

**Q4: How do you handle the problem of label noise (incorrect labels in your training data)?**

<details>
<summary>💡 Show Answer</summary>

A: First, you try to minimize it: use clear labeling guidelines, have multiple annotators label each example and use majority vote, and audit a random sample of labels regularly. For what remains, techniques include: label smoothing (treat labels as slightly probabilistic rather than absolute), training robust loss functions that are less sensitive to outliers, and filtering out examples with very high training loss (which often indicates a mislabeled example). Completely clean labels are unrealistic — the goal is to limit noise enough that the model learns true patterns.

</details>

<br>

**Q5: What is the train/test split and why do you need it?**

<details>
<summary>💡 Show Answer</summary>

A: The train/test split divides your labeled data into two parts. The model only sees the training set during training. The test set is held out completely and only used once — to evaluate how well the model performs on data it has never seen. This simulates real-world inference where the model faces new, unseen inputs. Without a proper split, you could end up with a model that scores 99% on training data but performs badly in production because it memorized examples rather than learning patterns.

</details>

<br>

**Q6: What is label leakage and why is it dangerous?**

<details>
<summary>💡 Show Answer</summary>

A: Label leakage is when information about the label accidentally ends up in the features. For example, including a patient's discharge date (which only exists for patients who recovered) in a model predicting survival. The model learns to exploit this leaked signal and scores perfectly in testing — then fails in production where the feature is not available yet. Leakage causes falsely optimistic evaluation and models that are useless in the real world. You prevent it by carefully auditing features for any information that would not be available at prediction time.

</details>

---

## Advanced Level

**Q7: How do you handle a severely imbalanced dataset in supervised classification?**

<details>
<summary>💡 Show Answer</summary>

A: Imbalanced datasets (e.g., 99% not-fraud, 1% fraud) cause models to predict the majority class always and still score 99% accuracy. Solutions include: resampling — oversampling the minority class (SMOTE generates synthetic examples) or undersampling the majority class; adjusting class weights in the loss function to penalize minority class errors more; using metrics like F1-score, precision-recall AUC, or Matthews Correlation Coefficient instead of accuracy; and threshold tuning — adjusting the probability threshold for the positive class.

</details>

<br>

**Q8: What is semi-supervised learning and when is it useful?**

<details>
<summary>💡 Show Answer</summary>

A: Semi-supervised learning uses a small amount of labeled data combined with a large amount of unlabeled data. It is useful when labeling is expensive or slow (medical imaging, legal documents) but unlabeled data is plentiful. A common approach: train on the labeled data, use the model to generate pseudo-labels for the unlabeled data, then retrain on both. Self-training, consistency regularization, and contrastive learning are other approaches. Modern large language models use a form of this — pre-training on massive unlabeled text, then fine-tuning on small labeled sets.

</details>

<br>

**Q9: How do you decide which supervised learning algorithm to use for a new problem?**

<details>
<summary>💡 Show Answer</summary>

A: Several factors guide the decision: dataset size (neural networks need large data; linear models work well on small data), interpretability requirements (decision trees and linear models are explainable; neural networks are not), feature type (tree-based methods handle mixed feature types natively; neural networks prefer numeric), presence of non-linear relationships (neural networks and kernel SVMs capture them; linear regression does not), and training/inference speed requirements. A good starting approach: begin with logistic/linear regression as a baseline, try gradient boosted trees (XGBoost) for tabular data, and move to neural networks only when the simpler approaches plateau.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |

⬅️ **Prev:** [02 Training vs Inference](../02_Training_vs_Inference/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Unsupervised Learning](../04_Unsupervised_Learning/Theory.md)
