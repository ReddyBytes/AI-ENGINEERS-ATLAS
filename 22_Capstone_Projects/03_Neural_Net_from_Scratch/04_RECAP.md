# 🏁 Project 3 — Recap

## What You Built

A 2-layer neural network (MLP) implemented in pure numpy that solves the XOR problem. The network implements every component from scratch: activation functions, weight initialization, forward pass, binary cross-entropy loss, backpropagation via the chain rule, gradient descent weight updates, and a training loop that plots its own loss curve.

---

## Concepts Applied

| Concept | Where You Used It | Why It Matters |
|---|---|---|
| Activation functions | `relu()` and `sigmoid()` | Non-linearity is what separates deep learning from linear regression |
| Symmetry breaking | `np.random.randn() * 0.01` for W1, W2 | Zero init causes all neurons to learn identically — random init lets them specialize |
| Forward pass | `forward_pass()` — four matrix ops in sequence | All neural network inference is just this, repeated at scale |
| Binary cross-entropy | `compute_loss()` | The loss function used by every binary classifier from logistic regression to GPT |
| Backpropagation | `backward_pass()` — chain rule applied layer by layer | The algorithm that makes neural network training computationally feasible |
| Gradient descent | `update_parameters()` — `W -= lr * dW` | The optimizer loop behind every framework: PyTorch, TensorFlow, JAX |
| Learning rate | 0.5 used in `train()` | Too high diverges, too low is slow — hyperparameter tuning starts here |
| Loss curve analysis | `plot_loss_curve()` | A smooth downward curve = healthy training; plateau or spikes = a bug |
| XOR non-linearity | Two-layer architecture vs. single perceptron | Direct proof that depth enables non-linear decision boundaries |

---

## Extension Ideas

- Replace the XOR dataset with the MNIST digit dataset (flatten 28x28 images to 784 features, use 10 output neurons with softmax, re-derive the multi-class backprop equations) — this is how the first practical deep networks were built
- Add L2 regularization by adding `lambda * W` to each weight gradient — observe whether it reduces train/test overfitting when you move beyond XOR to a noisier dataset
- Implement momentum gradient descent: instead of `W -= lr * dW`, maintain a velocity `v = beta * v + (1 - beta) * dW` and update `W -= lr * v` — observe whether the loss curve reaches minimum faster

---

## Job Mapping

| Role | How This Shows Up Daily |
|---|---|
| ML Engineer | Understands why framework training loops behave the way they do — essential for debugging loss explosions, vanishing gradients, and dead ReLU problems |
| AI Research Engineer | Reads and reproduces model architectures from papers that describe backprop equations — impossible without this foundation |
| Deep Learning Engineer | Tunes learning rates, initializes custom layers, and writes custom loss functions — all built on exactly what you implemented here |
| MLOps / Production ML | Reads training logs and loss curves to diagnose training failures — the loss curve you plotted is what production dashboards show at scale |

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 01_MISSION.md](./01_MISSION.md) | Context and objectives |
| [📄 02_ARCHITECTURE.md](./02_ARCHITECTURE.md) | System design and diagrams |
| [📄 03_GUIDE.md](./03_GUIDE.md) | Step-by-step build guide |
| [📄 src/starter.py](./src/starter.py) | Starter code with TODOs |
| 📄 **04_RECAP.md** | You are here |

⬅️ **Previous:** [02 — ML Model Comparison](../02_ML_Model_Comparison/01_MISSION.md)
➡️ **Next:** [04 — LLM Chatbot with Memory](../04_LLM_Chatbot_with_Memory/01_MISSION.md)
