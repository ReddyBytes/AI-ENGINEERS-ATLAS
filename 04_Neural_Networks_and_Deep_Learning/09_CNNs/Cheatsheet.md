# CNNs — Cheatsheet

**One-liner:** A CNN is a neural network that uses small learnable filters to scan images, detecting local patterns at multiple scales and building hierarchical feature representations.

---

## Key Terms

| Term | What it means |
|------|---------------|
| Filter / Kernel | Small grid of weights (e.g., 3×3) that slides across the input |
| Convolution | Sliding a filter over the input and computing dot products |
| Feature map | The output of one filter applied to the input — shows where that pattern appears |
| Weight sharing | Same filter weights used at every position in the image |
| Stride | How many pixels the filter moves each step (stride=1: pixel-by-pixel, stride=2: skip one) |
| Padding | Adding zeros around the image border to control output size |
| Pooling | Downsampling spatial dimensions (max pooling keeps the maximum in each region) |
| Channels / Depth | Number of feature maps at each layer |
| Receptive field | Region of the original input that influences one output neuron |
| Feature hierarchy | Early layers = simple; deep layers = complex, abstract |

---

## Dimension Formula

```
Output size = floor( (input_size - filter_size + 2×padding) / stride ) + 1

Example: 28×28 image, 3×3 filter, stride=1, padding=0:
  output = floor((28 - 3 + 0) / 1) + 1 = 26
  → Output: 26×26 feature map
```

---

## Parameter Count

```
Params in one conv layer = filter_h × filter_w × in_channels × out_channels + out_channels
                                   ↑ weights                                     ↑ biases

Example: 3×3 filter, 1 input channel, 32 output channels:
  = 3 × 3 × 1 × 32 + 32 = 288 + 32 = 320 parameters

Compare to a dense layer: 28×28 → 32 neurons = 784×32+32 = 25,120 parameters
```

Weight sharing makes CNNs dramatically more efficient than MLPs for images.

---

## Typical Architecture Pattern

```
Input Image
→ [Conv → ReLU → Pool]  ×  N layers   (feature extraction)
→ Flatten
→ [Dense → ReLU]  ×  M layers         (classification head)
→ Dense → Softmax                      (output)
```

---

## When to Use / Not Use

| Use CNNs when... | Do NOT use when... |
|------------------|--------------------|
| Input is image or spatial data | Input is tabular/structured (use MLP) |
| Translation invariance is desired | Sequential data where order matters (use RNN) |
| Feature hierarchy matters | Small datasets with no augmentation (may overfit) |
| Object detection, classification, segmentation | 1D time-series (1D CNNs can work, but RNN is more natural) |

---

## Famous CNN Architectures

| Architecture | Year | Key Innovation |
|-------------|------|----------------|
| LeNet-5 | 1998 | First successful CNN — handwritten digits |
| AlexNet | 2012 | Deeper, ReLU, GPU training, dropout — won ImageNet |
| VGG-16/19 | 2014 | Very deep, 3×3 filters only |
| GoogLeNet/Inception | 2014 | Inception modules — multiple filter sizes in parallel |
| ResNet | 2015 | Residual/skip connections — enabled 100+ layer training |
| EfficientNet | 2019 | Compound scaling of depth, width, and resolution |

---

## Golden Rules

1. Start with Conv→ReLU→MaxPool blocks. Stack 2–4 of them.
2. Double the number of filters when you halve the spatial dimensions (common pattern).
3. Global Average Pooling (GAP) instead of Flatten is common in modern architectures — more parameter efficient.
4. Batch normalization after each conv layer stabilizes training dramatically.
5. Data augmentation (flips, crops, color jitter) is almost always needed for image tasks.
6. Transfer learning: use a pretrained ResNet or EfficientNet — fine-tune for your task. Don't train from scratch unless you have millions of images.

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| 📄 **Cheatsheet.md** | ← you are here |
| [📄 Interview_QA.md](./Interview_QA.md) | Interview prep |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | CNN architecture deep dive |

⬅️ **Prev:** [08 Regularization](../08_Regularization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 RNNs](../10_RNNs/Theory.md)
