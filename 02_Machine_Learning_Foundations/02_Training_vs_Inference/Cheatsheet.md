# Training vs Inference — Cheatsheet

**One-liner:** Training is when the model learns. Inference is when the model works.

---

## Key Terms

| Term | What It Means |
|---|---|
| **Training** | The learning phase — model sees data, makes guesses, gets corrected, adjusts |
| **Inference** | The production phase — model applies what it learned to new inputs |
| **Weights** | The numbers inside the model that store what it learned |
| **Loss** | How wrong the model's prediction is (used only during training) |
| **Epoch** | One full pass through the entire training dataset |
| **Batch** | A small chunk of training data processed at once |
| **Fine-tuning** | Training an already-trained model a bit more on new/specific data |
| **Latency** | How fast the model responds — only matters during inference |
| **Frozen weights** | Weights that are NOT being updated — describes inference mode |

---

## When to Use / Not Use Each

| Situation | What's Happening |
|---|---|
| You're using ChatGPT | Inference — the model is already trained |
| A company is training GPT-5 | Training — on millions of GPUs for months |
| Your app calls an API for a prediction | Inference |
| You're fine-tuning a model on your company's docs | Training (a smaller version of it) |
| An image is being classified in real-time | Inference |

---

## Golden Rules

1. **Training is slow and expensive. Inference is fast and cheap (per call).**
2. **During inference, weights never change.** The model is read-only.
3. **Training happens once (or rarely). Inference happens millions of times.**
4. **The quality of training determines the quality of all future inference.**
5. **Fine-tuning is training — just starting from existing weights, not from scratch.**

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |

⬅️ **Prev:** [01 What is ML](../01_What_is_ML/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Supervised Learning](../03_Supervised_Learning/Theory.md)
