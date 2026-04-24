# CNNs — Interview Q&A

## Beginner

**Q1: What is a convolution operation in a CNN?**

<details>
<summary>💡 Show Answer</summary>

A convolution is the operation of sliding a small filter (e.g., 3×3 grid of weights) across an input image. At each position, the filter is multiplied element-wise with the image patch beneath it, and all the products are summed into a single number. This number represents "how much does this patch match what the filter is looking for?" If the filter is designed to detect vertical edges, this number will be high where vertical edges exist and low elsewhere. The result of sliding the filter across the entire image is a 2D feature map showing where that pattern was detected.

</details>

---

**Q2: What is weight sharing and why is it important?**

<details>
<summary>💡 Show Answer</summary>

Weight sharing means the same filter weights are used at every position in the image. A 3×3 filter that detects horizontal edges uses the same 9 weights whether it is in the top-left corner or the bottom-right corner. This is important for two reasons. First, efficiency: instead of 200,000+ weights (as in a dense layer), a single filter only needs 9 weights regardless of image size. Second, translation invariance: the filter learns to detect its pattern anywhere in the image, which is what we want — a cat is a cat whether it appears on the left or right of the photo.

</details>

---

**Q3: What is max pooling and what does it do?**

<details>
<summary>💡 Show Answer</summary>

Max pooling divides the feature map into non-overlapping regions (e.g., 2×2 blocks) and keeps only the maximum value from each region. The output is half the height and half the width of the input. Max pooling does three things: it reduces the spatial dimensions (making subsequent computation cheaper), it provides a degree of translation invariance (if a feature is slightly shifted in the 2×2 region, the max is still detected), and it summarizes "was this feature present anywhere in this neighborhood?" without caring exactly where.

</details>

---

## Intermediate

**Q4: How do the layers of a CNN build increasingly complex features?**

<details>
<summary>💡 Show Answer</summary>

Early convolutional layers have small receptive fields and detect simple local patterns: edges (horizontal, vertical, diagonal), color blobs, simple textures. Middle layers combine those simple patterns into more complex structures: corners, curves, circles, simple shapes. Deep layers combine those into object parts: eyes, wheels, windows, fur patterns. The deepest layers represent whole objects or semantic concepts. This hierarchical feature learning is why CNNs are so effective at image recognition — each layer builds on the abstractions of the previous one, exactly mirroring how the human visual cortex processes visual information (as shown by Hubel & Wiesel's Nobel-winning work on the visual cortex).

</details>

---

**Q5: What is the receptive field and why does it matter?**

<details>
<summary>💡 Show Answer</summary>

The receptive field of a neuron is the region of the original input image that influences that neuron's output. A single neuron in the first conv layer (3×3 filter) has a 3×3 receptive field. After pooling, a neuron in the second conv layer (another 3×3 filter) sees a 7×7 region of the original image (the 3×3 filter over the post-pooling feature maps traces back to a larger area). Deep neurons have very large receptive fields — they effectively "see" large regions of the original image. This is why deep layers can detect whole faces or complete objects: their neurons have receptive fields large enough to encompass the entire object.

</details>

---

**Q6: What is the difference between same padding and valid padding?**

<details>
<summary>💡 Show Answer</summary>

With no padding (valid padding), the filter can only be placed fully within the image. A 3×3 filter on a 28×28 image produces a 26×26 output — you lose 2 pixels per side. With same padding (also called zero padding), zeros are added around the image border so the output has the same spatial dimensions as the input. For a 3×3 filter, you add 1 pixel of zeros on each side. This preserves spatial dimensions throughout the network and is important when you want to control exactly how the spatial size changes (e.g., only through pooling, not through convolutions).

</details>

---

## Advanced

**Q7: What are residual (skip) connections and why did they enable much deeper networks?**

<details>
<summary>💡 Show Answer</summary>

Residual connections (He et al., 2015, ResNet) add the input of a block directly to the output of that block: `output = F(x) + x`, where F(x) is the learned transformation. This creates a shortcut path for gradients to flow directly from output to early layers during backpropagation, bypassing the convolutional operations. Without skip connections, gradients must multiply through every layer's Jacobian — in very deep networks (50+ layers), this causes vanishing gradients and training stalls. With skip connections, gradients flow unimpeded along the shortcut path. ResNet-152 (152 layers) trained on ImageNet was previously impossible to converge — with residual connections it trained in hours. Skip connections also have a "depth ensemble" interpretation: the network can effectively choose to use or bypass any block, creating an implicit ensemble of paths through the network.

</details>

---

**Q8: How does object detection differ from image classification in CNN architecture?**

<details>
<summary>💡 Show Answer</summary>

Image classification takes an image and outputs a single label (what is in the image). Object detection must output multiple bounding boxes and class labels — where objects are and what they are. Classic CNNs output a fixed-size class vector. Detectors add spatial prediction heads. Two-stage detectors (Faster R-CNN): first propose regions of interest using a Region Proposal Network (RPN), then classify each region. One-stage detectors (YOLO, SSD): divide the image into a grid and predict boxes and classes directly at each grid cell — much faster. Modern detectors often add Feature Pyramid Networks (FPN) to detect objects at multiple scales using feature maps from multiple depths of the CNN.

</details>

---

**Q9: What are depthwise separable convolutions and why do efficient architectures use them?**

<details>
<summary>💡 Show Answer</summary>

A standard 3×3 convolution over C_in input channels to produce C_out output channels requires 3×3×C_in×C_out multiplications per output position. A depthwise separable convolution splits this into two steps: (1) depthwise convolution — apply one 3×3 filter per input channel independently (mixing spatial information within each channel), then (2) pointwise convolution — apply 1×1 filters to mix information across channels. Total cost: 3×3×C_in + 1×1×C_in×C_out ≈ 8–9× fewer operations than standard convolution. MobileNet, EfficientNet, and many mobile-friendly architectures use depthwise separable convolutions to reduce computational cost while maintaining accuracy.

</details>

---

## 📂 Navigation

**In this folder:**
| File | |
|---|---|
| [📄 Theory.md](./Theory.md) | Core concepts |
| [📄 Cheatsheet.md](./Cheatsheet.md) | Quick reference |
| 📄 **Interview_QA.md** | ← you are here |
| [📄 Code_Example.md](./Code_Example.md) | Python code examples |
| [📄 Architecture_Deep_Dive.md](./Architecture_Deep_Dive.md) | CNN architecture deep dive |

⬅️ **Prev:** [08 Regularization](../08_Regularization/Theory.md) &nbsp;&nbsp;&nbsp; ➡️ **Next:** [10 RNNs](../10_RNNs/Theory.md)
