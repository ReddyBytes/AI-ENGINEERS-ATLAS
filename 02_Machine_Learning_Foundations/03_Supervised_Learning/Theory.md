# Supervised Learning

## The Story 📖

It's your first week as a bank employee. Your job: approve or reject loan applications. Your manager doesn't give you a rulebook — they hand you 10,000 past applications, each with the details AND a note: "Approved ✅" or "Rejected ❌". After weeks of study, you notice: stable income + low debt = approved; multiple missed payments = rejected. You've learned the pattern from **labeled examples**.

👉 This is **Supervised Learning** — training a model using data where every example already has the correct answer attached.

---

## What is Supervised Learning?

**Supervised Learning** is the most common type of machine learning. You train a model on labeled data — examples where the input AND the correct output are both provided.

The model learns to map inputs → outputs by studying these pairs.

**Two flavors:**

| Type | Output | Example |
|---|---|---|
| **Classification** | A category/class | Spam or not spam? Dog or cat? |
| **Regression** | A number | What's the house price? |

```mermaid
flowchart TD
    SL[Supervised Learning] --> C[Classification\npredict a category]
    SL --> R[Regression\npredict a number]
    C --> C1[Binary\n2 classes: spam or not]
    C --> C2[Multi-class\n3+ classes: cat dog bird]
    R --> R1[House price prediction]
    R --> R2[Temperature forecasting]
```

---

## How It Works — Step by Step

1. **Labeled Data** — every example has an input and a known correct answer (the **label**)
2. **Train** — model studies thousands of pairs and adjusts to predict labels from inputs
3. **Predict** — give the model a new application; it predicts Approved or Rejected
4. **Evaluate** — check accuracy; retrain if wrong too often

```mermaid
flowchart TD
    A[🏷️ Labeled Data\ninput + correct answer] --> B[🏋️ Training]
    B --> C[🧠 Trained Model]
    D[🆕 New Input\nno label] --> C
    C --> E[🎯 Predicted Label]
    E --> F{Correct?}
    F -- No --> G[Adjust & Retrain]
    G --> B
    F -- Yes --> H[✅ Done]
```

---

## Real-World Examples

- **Email spam filter** — trained on emails labeled spam/not-spam
- **Image recognition** — trained on photos labeled "cat", "dog", "bird"
- **House price prediction** — trained on past sales (house features → sale price)
- **Medical diagnosis** — trained on patient records labeled with diagnoses
- **Sentiment analysis** — trained on reviews labeled positive/negative

---

## Why It Works (The Intuition)

The model learns a function `f(input) = output`. It doesn't know the formula in advance — it discovers it from enough examples. More examples = better approximation of the true pattern.

## The Catch: You Need Labels

**Getting labeled data** is the biggest challenge. Someone must manually attach correct answers to every training example — labeling 100,000 images takes real human effort, which is why labeled datasets are valuable.

---

## Common Mistakes to Avoid ⚠️

- **Bad labels = bad model** — if the labels are wrong or inconsistent, the model learns the wrong thing
- **Label leakage** — accidentally including information in the input that reveals the answer (makes the model look great in testing, useless in production)
- **Not enough label diversity** — if your training data only has one type of example, the model won't generalize

---

## Connection to Other Concepts 🔗

- **Unsupervised Learning** — the opposite: no labels, model finds patterns on its own
- **Loss Function** — measures how wrong the model's predictions are during training
- **Overfitting** — when a model memorizes labels instead of learning real patterns

---

✅ **What you just learned:** Supervised learning = training on labeled examples (input + correct answer) to predict outputs on new data.

🔨 **Build this now:** On [Kaggle](https://www.kaggle.com/datasets/uciml/iris), load the Iris dataset. It has flower measurements (inputs) and flower species (labels). This is a classic supervised learning dataset — just exploring it gives you the intuition.

➡️ **Next step:** What if you don't have labels? → `04_Unsupervised_Learning/Theory.md`


---

## 📝 Practice Questions

- 📝 [Q6 · supervised-learning](../../ai_practice_questions_100.md#q6--thinking--supervised-learning)


---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| 📄 **Theory.md** | ← you are here |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python example |

⬅️ **Prev:** [02 Training vs Inference](../02_Training_vs_Inference/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [04 Unsupervised Learning](../04_Unsupervised_Learning/Theory.md)
