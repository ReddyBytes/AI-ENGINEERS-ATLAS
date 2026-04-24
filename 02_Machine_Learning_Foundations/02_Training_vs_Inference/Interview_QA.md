# Training vs Inference — Interview Q&A

## Beginner Level

**Q1: What is the difference between training and inference in machine learning?**

<details>
<summary>💡 Show Answer</summary>

A: Training is the learning phase — the model processes labeled data, makes predictions, measures how wrong it was, and adjusts its internal weights to improve. It happens once (or occasionally). Inference is the usage phase — the model applies its already-learned weights to new inputs to make predictions. No learning happens during inference; the weights are frozen.

</details>

<br>

**Q2: When you use a chatbot like ChatGPT, is that training or inference?**

<details>
<summary>💡 Show Answer</summary>

A: That is inference. The model was trained by OpenAI before you ever accessed it. When you send a message, the frozen model processes your input and generates a response. Your conversation does not update the model's weights or make it smarter.

</details>

<br>

**Q3: Why is training so much more expensive than inference?**

<details>
<summary>💡 Show Answer</summary>

A: Training requires processing massive datasets repeatedly (often millions of iterations), calculating gradients for billions of parameters, and updating weights on every pass. This needs large GPU clusters running for days or months. Inference just runs one forward pass through the network for each input, which takes milliseconds on much smaller hardware.

</details>

---

## Intermediate Level

**Q4: What is a training epoch, and how many do you typically need?**

<details>
<summary>💡 Show Answer</summary>

A: An epoch is one complete pass through the entire training dataset. How many you need depends on the problem and dataset size. Simple tasks might converge in 10–50 epochs. Deep learning on large datasets might need hundreds. You monitor validation loss to decide when to stop — if it stops improving or starts rising, you stop (early stopping).

</details>

<br>

**Q5: What is the difference between batch gradient descent, stochastic gradient descent, and mini-batch gradient descent?**

<details>
<summary>💡 Show Answer</summary>

A: Batch GD computes the gradient on the full dataset before updating weights — accurate but slow for large datasets. Stochastic GD updates weights after each individual example — fast but very noisy. Mini-batch GD (the standard) processes small batches (e.g. 32 or 128 examples) at a time — balances speed and stability. Mini-batch is what virtually all modern training uses.

</details>

<br>

**Q6: What is fine-tuning and how does it differ from training from scratch?**

<details>
<summary>💡 Show Answer</summary>

A: Fine-tuning is taking a model already trained on a large dataset and continuing to train it on a smaller, specific dataset. Instead of learning everything from random weights, fine-tuning starts from weights that already represent useful patterns. It is much faster and needs far less data than training from scratch. For example: take a model pre-trained on all of Wikipedia, fine-tune it on your company's legal documents to make it domain-specific.

</details>

---

## Advanced Level

**Q7: What considerations go into optimizing inference for production systems?**

<details>
<summary>💡 Show Answer</summary>

A: Several dimensions matter: latency (how fast each request completes), throughput (how many requests per second), cost (compute cost per inference), and hardware efficiency. Techniques include model quantization (reducing precision from float32 to int8), model distillation (training a smaller model to mimic a larger one), batching requests together, caching repeated queries, and using hardware-specific optimizations (TensorRT, ONNX). The right tradeoff depends on whether you need real-time responses or can tolerate batch processing.

</details>

<br>

**Q8: How does the training/inference distinction relate to the concept of train/test split?**

<details>
<summary>💡 Show Answer</summary>

A: The train/test split exists to simulate the training-inference divide during development. You train on the training set (model updates weights), then evaluate on the test set in "inference mode" (no weight updates) to measure real-world performance. The test set must never be seen during training — otherwise you are evaluating on data the model already learned from, which gives falsely optimistic accuracy. The test set mimics real inference conditions.

</details>

<br>

**Q9: What are the risks of "training-serving skew" and how do you address it?**

<details>
<summary>💡 Show Answer</summary>

A: Training-serving skew happens when the data distribution at inference time differs from what the model was trained on. For example, a fraud detection model trained on 2022 data deployed in 2025 may miss new fraud patterns. Solutions include: continuous monitoring of prediction distributions to detect drift, scheduled retraining pipelines, online learning (updating weights incrementally from new production data), and shadow deployments that compare old and new model outputs before switching over.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concept |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [01 What is ML](../01_What_is_ML/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [03 Supervised Learning](../03_Supervised_Learning/Theory.md)
