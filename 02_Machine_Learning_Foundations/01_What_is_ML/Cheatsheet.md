# What is ML — Cheatsheet

## The One-Line Definition
> Machine Learning = teaching computers with **examples**, not rules.

---

## Traditional Programming vs ML

| | Traditional | Machine Learning |
|---|---|---|
| You provide | Rules + Data | Data + Answers |
| Computer produces | Answers | Rules (learned) |
| Best for | Predictable logic | Pattern recognition |
| Breaks when | Rules are too complex | Data is too small/bad |

---

## The 3 Types of ML

| Type | How it learns | Example |
|---|---|---|
| **Supervised** | From labeled examples (input + correct answer) | Spam filter, image classifier |
| **Unsupervised** | Finds patterns in unlabeled data | Customer segmentation, anomaly detection |
| **Reinforcement** | From rewards and penalties | Game-playing AI, robots |

---

## Key Terms

| Term | Meaning |
|---|---|
| **Training** | Showing the model examples so it learns |
| **Inference** | Using the trained model to make predictions |
| **Model** | The learned pattern (the "brain" after training) |
| **Weights** | Internal dials the model adjusts during training |
| **Loss** | How wrong the model is (lower = better) |
| **Dataset** | The collection of examples used for training |
| **Features** | The input variables (e.g., email words, pixel values) |
| **Label** | The correct answer for each training example |

---

## When to Use ML

✅ Use ML when:
- Rules are too complex or numerous to write manually
- The problem has lots of historical examples to learn from
- The pattern changes over time (needs to adapt)

❌ Don't use ML when:
- Simple if/else logic works fine
- You have very little data
- You need to explain exactly why every decision was made

---

## Golden Rules

1. **Data quality > data quantity** — clean, relevant data beats more messy data
2. **Understand before you code** — know what "training" means before touching scikit-learn
3. **Always test on unseen data** — a model that only works on training data is useless

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Main explanation |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [01 Math for AI](../../01_Math_for_AI/Readme.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [02 Training vs Inference](../02_Training_vs_Inference/Theory.md)
