# 04 — Neural Networks and Deep Learning

This section takes you from the very first building block of a neural network (the perceptron) all the way to advanced architectures like CNNs, RNNs, and GANs. By the end you will understand how modern deep learning systems are built, trained, and debugged.

---

## Topics

| # | Topic | What you will learn |
|---|-------|---------------------|
| 01 | [Perceptron](./01_Perceptron/) | Single neuron, weights, bias, step function, linear separability |
| 02 | [MLPs](./02_MLPs/) | Multiple layers, hidden layers, non-linearity, fully connected nets |
| 03 | [Activation Functions](./03_Activation_Functions/) | ReLU, Sigmoid, Tanh, Softmax — when and why to use each |
| 04 | [Loss Functions](./04_Loss_Functions/) | MSE, Cross-Entropy — measuring how wrong the model is |
| 05 | [Forward Propagation](./05_Forward_Propagation/) | How data flows through a network layer by layer |
| 06 | [Backpropagation](./06_Backpropagation/) | How error flows backward to update weights |
| 07 | [Optimizers](./07_Optimizers/) | SGD, Momentum, RMSProp, Adam — how the model learns |
| 08 | [Regularization](./08_Regularization/) | L1, L2, Dropout, Early Stopping — preventing overfitting |
| 09 | [CNNs](./09_CNNs/) | Convolutional networks for images — filters, pooling, feature maps |
| 10 | [RNNs](./10_RNNs/) | Recurrent networks for sequences — hidden state, LSTM, GRU |
| 11 | [GANs](./11_GANs/) | Generator vs discriminator, adversarial training, AI art |
| 12 | [Training Techniques](./12_Training_Techniques/) | Batch size, epochs, LR schedules, transfer learning, debugging |

---

## Recommended Order

Follow the numbers. Topics 01–06 form the core theory loop:
**Perceptron → MLP → Activations → Loss → Forward Prop → Backprop**

Then 07–08 teach you how to train well.
Then 09–11 are the big architectures.
Topic 12 ties everything together with practical training know-how.

---

## Files in Each Topic

- **Theory.md** — core concept explained simply, with a diagram
- **Cheatsheet.md** — quick reference for revision or interviews
- **Interview_QA.md** — 9 questions across Beginner / Intermediate / Advanced
- **Comparison.md** *(where applicable)* — side-by-side comparison table
- **Math_Walkthrough.md** *(where applicable)* — step-by-step numbers
- **Architecture_Deep_Dive.md** *(where applicable)* — layer-by-layer breakdown
- **Code_Example.md** *(where applicable)* — heavily commented code you can run
- **Troubleshooting_Guide.md** *(where applicable)* — symptom → cause → fix

---

> **Prerequisite:** 03_Classical_ML_Algorithms — specifically linear regression, gradient descent, and the concept of a decision boundary.
