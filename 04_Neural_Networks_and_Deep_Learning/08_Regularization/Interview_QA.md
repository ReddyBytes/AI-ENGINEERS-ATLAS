# Regularization — Interview Q&A

## Beginner

**Q1: What is overfitting and how do you detect it?**

<details>
<summary>💡 Show Answer</summary>

Overfitting is when a model learns the training data too well — including its noise, outliers, and specific quirks — and fails to generalize to new, unseen data. You detect it by comparing training loss and validation loss during training. If training loss keeps decreasing but validation loss starts increasing (or stagnates while training loss drops further), the model is overfitting. The gap between them is the signal. Other signs: near-perfect training accuracy paired with much lower test accuracy.

</details>

---

<br>

**Q2: What is L2 regularization and how does it work?**

<details>
<summary>💡 Show Answer</summary>

L2 regularization adds a penalty term to the loss function equal to the sum of squared weights multiplied by a regularization coefficient (lambda): `Total loss = original loss + λ × Σw²`. During training, the optimizer minimizes this combined loss, which means it is penalized for having large weights. The result: the optimizer shrinks all weights toward zero (though not exactly to zero). Smaller weights mean the model cannot rely too heavily on any single feature, leading to smoother decision boundaries and better generalization.

</details>

---

<br>

**Q3: What is dropout and when is it applied?**

<details>
<summary>💡 Show Answer</summary>

Dropout is a regularization technique where, during each training forward pass, a random fraction of neurons are set to zero (disabled). If the dropout rate is 0.5, each neuron has a 50% chance of being zeroed for that particular training example. This prevents the network from co-adapting — forming specific pathways that memorize training examples. Each neuron must learn to be useful on its own. At inference time, dropout is disabled (all neurons active) and outputs are scaled to compensate. In PyTorch: `model.train()` enables dropout, `model.eval()` disables it.

</details>

---

## Intermediate

**Q4: What is the difference between L1 and L2 regularization, and when would you choose one over the other?**

<details>
<summary>💡 Show Answer</summary>

Both add a penalty to large weights. L1 adds `λ × Σ|w|` (sum of absolute values). L2 adds `λ × Σw²` (sum of squares). The key difference in effect: L2 penalizes large weights quadratically — it strongly shrinks large weights but barely touches small ones. All weights tend toward zero but never exactly reach it. L1's gradient is constant (±λ) regardless of weight size — it pushes every weight toward zero with equal force, and small weights can be driven all the way to exactly zero. This creates sparse solutions (many zero weights). Choose L1 when you have many features and expect most to be irrelevant (it acts as feature selection). Choose L2 for deep networks — it works better empirically and is included in optimizers as "weight decay."

</details>

---

<br>

**Q5: How does data augmentation work as a regularizer?**

<details>
<summary>💡 Show Answer</summary>

Data augmentation creates new training examples by applying transformations to existing ones: flipping images, rotating, cropping, adjusting brightness, adding noise, etc. From the model's perspective, each augmented version is a slightly different example. The model cannot memorize exact pixel patterns because those patterns are different every time it sees the same image. It must learn the underlying concept (what a cat looks like) rather than the specific training instance. This forces the model to learn invariances — representations that are robust to small changes — which is exactly what good generalization requires. Data augmentation is often the most cost-effective regularizer because real data is always better than any mathematical penalty.

</details>

---

<br>

**Q6: What is early stopping and what are its practical considerations?**

<details>
<summary>💡 Show Answer</summary>

Early stopping monitors validation loss during training and stops training when the validation loss stops improving (based on a "patience" parameter — e.g., stop after 10 epochs with no improvement). The model's weights from the best validation epoch are saved. Practical considerations: (1) You must always maintain a separate validation set — never use test data for early stopping decisions. (2) Set patience appropriately — too low and you stop prematurely (the loss might recover); too high and you waste compute and may overfit. (3) Save checkpoints — you need the weights from the best epoch, not the final epoch. (4) Early stopping implicitly limits model capacity without changing architecture — it is a form of regularization that works on any model.

</details>

---

## Advanced

**Q7: How does batch normalization regularize a model, and how does it interact with dropout?**

<details>
<summary>💡 Show Answer</summary>

Batch normalization normalizes each layer's activations to have mean 0 and standard deviation 1 within each mini-batch. This introduces noise: the batch statistics (mean, variance) are estimates based on the mini-batch, not the full dataset. This stochasticity acts as a regularizer, similar to dropout. Empirically, using both batch normalization and dropout often provides less benefit than either alone — their regularization effects overlap and can interact badly. Batch normalization's noise can conflict with dropout's noise, sometimes harming convergence. Modern practice: use batch normalization in convolutional layers, use dropout in fully-connected layers, but be cautious about combining them.

</details>

---

<br>

**Q8: What is the relationship between model capacity and regularization?**

<details>
<summary>💡 Show Answer</summary>

Model capacity refers to the range of functions a model can represent — more parameters = higher capacity. A high-capacity model can perfectly fit any training set, which is exactly why overfitting occurs. Regularization and capacity are complementary tools for the bias-variance tradeoff. You have two options when overfitting: reduce capacity (smaller model) or add regularization (constrain the existing model). Reducing capacity is a hard constraint — the model literally cannot express overly complex functions. Regularization is a soft constraint — the model can technically express them but is penalized for doing so. In practice: start with more capacity than needed (to reduce underfitting risk), then add regularization to control overfitting.

</details>

---

<br>

**Q9: What is DropConnect and how does it differ from standard Dropout?**

<details>
<summary>💡 Show Answer</summary>

Standard Dropout zeros entire neurons (all of a neuron's outputs). DropConnect (Wan et al., 2013) zeros individual weights — the connections — instead of entire neurons. During training, each weight has a probability p of being set to zero. A neuron can still fire and contribute to the next layer, but only through a random subset of its connections. DropConnect creates a much larger ensemble of sub-networks than dropout (the number of possible masked weight sets is exponentially larger). Empirically DropConnect performs comparably to or slightly better than dropout, but it is more computationally expensive since you must maintain a binary mask for every weight during training. It is rarely used in practice due to this overhead.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |

⬅️ **Prev:** [07 Optimizers](../07_Optimizers/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [09 CNNs](../09_CNNs/Theory.md)
